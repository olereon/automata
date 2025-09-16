"""
MCP Bridge Extension Client for connecting to Playwright MCP Bridge extension.

This module provides enhanced WebSocket communication capabilities for connecting
to the Playwright MCP Bridge extension, including message protocols, connection
management, and support for multiple browser tabs and contexts.
"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable, Awaitable

import aiohttp
import websockets
from aiohttp import WSMsgType, ClientWebSocketResponse

from ..core.logger import get_logger
from .client import MCPClientError, MCPConnectionError, MCPProtocolError, MCPToolError
from .bridge_extension_security import (
    MCPBridgeExtensionSecurity,
    AuthenticationError,
    SecurityConfigurationError
)
from .bridge_extension_platform import (
    PlatformManager,
    UnsupportedPlatformError,
    PlatformConfigurationError
)

logger = get_logger(__name__)


class MCPBridgeExtensionError(MCPClientError):
    """Base exception for MCP Bridge extension errors."""
    pass


class MCPBridgeExtensionConnectionError(MCPBridgeExtensionError):
    """Exception raised when MCP Bridge extension connection fails."""
    pass


class MCPBridgeExtensionProtocolError(MCPBridgeExtensionError):
    """Exception raised when MCP Bridge extension protocol error occurs."""
    pass


class MCPBridgeExtensionClient:
    """
    Client for communicating with the Playwright MCP Bridge extension.
    
    This client handles WebSocket communication with the browser extension,
    including connection establishment, message protocols, and tab management.
    """

    def __init__(
        self,
        extension_id: str = None,
        websocket_url: str = "ws://localhost:9222",
        timeout: int = 30000,
        retry_attempts: int = 3,
        retry_delay: int = 1000,
        auth_token: str = None,
        enable_security: bool = True,
        token_file: str = None
    ):
        """
        Initialize the MCP Bridge extension client.
        
        Args:
            extension_id: ID of the browser extension
            websocket_url: WebSocket URL for the extension
            timeout: Connection timeout in milliseconds
            retry_attempts: Number of retry attempts
            retry_delay: Delay between retries in milliseconds
            auth_token: Authentication token for secure connection
            enable_security: Whether to enable security features
            token_file: Path to the token file
        """
        self.extension_id = extension_id
        self.websocket_url = websocket_url
        self.timeout = timeout / 1000  # Convert to seconds
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay / 1000  # Convert to seconds
        self.auth_token = auth_token
        self.enable_security = enable_security
        
        # Platform manager
        self._platform_manager = PlatformManager()
        
        # Check platform compatibility
        is_compatible, compatibility_issues = self._platform_manager.check_compatibility()
        if not is_compatible:
            logger.error(f"Platform compatibility issues: {compatibility_issues}")
            raise UnsupportedPlatformError(
                f"Current platform is not compatible: {compatibility_issues}"
            )
        
        # Security manager
        self._security = None
        if self.enable_security:
            # Use platform-specific token file path if not provided
            if token_file is None:
                config_path = self._platform_manager.get_path("config")
                token_file = str(Path(config_path) / "mcp_bridge_tokens.json")
            
            self._security = MCPBridgeExtensionSecurity(token_file)
        
        # Connection state
        self._connected = False
        self._connection = None
        self._session = None
        self._listen_task = None
        self._reconnect_task = None
        
        # Response handlers
        self._response_handlers = {}
        self._request_counter = 0
        
        # Extension capabilities
        self._capabilities = {}
        self._tabs = []
        self._current_tab_id = None
        
        # Message queue for incoming messages
        self._message_queue = asyncio.Queue()
        
        # Event handlers
        self._event_handlers = {}

    async def connect(self) -> None:
        """
        Connect to the MCP Bridge extension.
        
        Raises:
            MCPBridgeExtensionConnectionError: If connection fails
        """
        if self._connected:
            logger.warning("Already connected to MCP Bridge extension")
            return

        logger.info(f"Connecting to MCP Bridge extension at {self.websocket_url}")

        try:
            # Initialize security if enabled
            if self.enable_security and self._security:
                await self._security.initialize()
                
                # Authenticate with the extension
                if self.extension_id:
                    authenticated = await self._security.authenticate_extension(
                        self.extension_id, self.auth_token
                    )
                    if not authenticated:
                        raise MCPBridgeExtensionConnectionError(
                            "Failed to authenticate with MCP Bridge extension"
                        )
                    
                    # Get the token from the security manager
                    self.auth_token = self._security.token_manager.get_token(self.extension_id)

            # Create HTTP session for REST API calls
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))

            # Check if extension is available
            await self._check_extension_availability()

            # Connect via WebSocket for real-time communication
            if self.enable_security and self._security:
                # Use secure WebSocket connection
                self._connection, init_response = await self._security.establish_secure_websocket(
                    self.websocket_url, self.extension_id, self.auth_token
                )
                
                # Process the initialization response from the secure connection
                if init_response.get("type") == "initialized":
                    self._capabilities = init_response.get("capabilities", {})
                elif init_response.get("type") == "error":
                    raise MCPBridgeExtensionConnectionError(
                        f"Failed to initialize secure connection: {init_response.get('message', 'Unknown error')}"
                    )
            else:
                # Use standard WebSocket connection
                self._connection = await websockets.connect(self.websocket_url)

                # Send initialize message with authentication if provided
                init_message = {
                    "type": "initialize",
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "bridgeExtension": True
                    }
                }
                
                if self.extension_id:
                    init_message["extensionId"] = self.extension_id
                    
                if self.auth_token:
                    init_message["authToken"] = self.auth_token

                await self._send_message(init_message)

                # Wait for initialized response
                response = await self._wait_for_response("initialized")
                if not response.get("success", False):
                    raise MCPBridgeExtensionConnectionError(
                        f"Failed to initialize MCP Bridge extension connection: {response.get('message', 'Unknown error')}"
                    )

                # Store extension capabilities
                if "capabilities" in response:
                    self._capabilities = response["capabilities"]

            # Start listening for messages
            self._listen_task = asyncio.create_task(self._listen_for_messages())

            # Get initial list of tabs
            await self._refresh_tabs()

            self._connected = True
            logger.info("Successfully connected to MCP Bridge extension")

        except Exception as e:
            logger.error(f"Failed to connect to MCP Bridge extension: {e}")
            await self.disconnect()
            raise MCPBridgeExtensionConnectionError(f"Failed to connect to MCP Bridge extension: {e}")

    async def _check_extension_availability(self) -> None:
        """
        Check if the MCP Bridge extension is available.
        
        Raises:
            MCPBridgeExtensionConnectionError: If extension is not available
        """
        # Convert WebSocket URL to HTTP URL for health check
        http_url = self.websocket_url
        if http_url.startswith("ws://"):
            http_url = http_url.replace("ws://", "http://")
        elif http_url.startswith("wss://"):
            http_url = http_url.replace("wss://", "https://")
        
        try:
            async with self._session.get(f"{http_url}/health") as response:
                if response.status != 200:
                    raise MCPBridgeExtensionConnectionError(
                        f"MCP Bridge extension health check failed with status: {response.status}"
                    )
        except Exception as e:
            raise MCPBridgeExtensionConnectionError(
                f"Failed to check MCP Bridge extension availability: {e}"
            )

    async def disconnect(self) -> None:
        """
        Disconnect from the MCP Bridge extension.
        """
        if not self._connected:
            return

        logger.info("Disconnecting from MCP Bridge extension")

        try:
            # Send close message if connected
            if self._connection:
                await self._send_message({"type": "close"})
        except Exception as e:
            logger.warning(f"Failed to send close message: {e}")

        # Cancel reconnect task if running
        if self._reconnect_task:
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
            self._reconnect_task = None

        # Cancel listen task
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None

        # Close connection
        if self._connection:
            try:
                await self._connection.close()
            except Exception as e:
                logger.warning(f"Failed to close connection: {e}")
            self._connection = None

        # Close session
        if self._session:
            try:
                await self._session.close()
            except Exception as e:
                logger.warning(f"Failed to close session: {e}")
            self._session = None

        # Close security manager
        if self._security:
            try:
                await self._security.close()
            except Exception as e:
                logger.warning(f"Failed to close security manager: {e}")

        self._connected = False
        logger.info("Disconnected from MCP Bridge extension")

    async def is_connected(self) -> bool:
        """
        Check if connected to the MCP Bridge extension.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected and self._connection and not self._connection.closed

    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get extension capabilities.
        
        Returns:
            Extension capabilities dictionary
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")
        
        return self._capabilities.copy()

    async def list_tabs(self) -> List[Dict[str, Any]]:
        """
        List available browser tabs.
        
        Returns:
            List of browser tabs
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        await self._refresh_tabs()
        return self._tabs.copy()

    async def _refresh_tabs(self) -> None:
        """
        Refresh the list of available tabs.
        """
        request_id = str(uuid.uuid4())
        message = {
            "type": "tabs/list",
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to list tabs: {response.get('message', 'Unknown error')}"
            )

        self._tabs = response.get("tabs", [])

    async def select_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Select a browser tab.
        
        Args:
            tab_id: ID of the tab to select
            
        Returns:
            Selection result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "tabs/select",
            "tabId": tab_id,
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to select tab: {response.get('message', 'Unknown error')}"
            )

        self._current_tab_id = tab_id
        return response.get("result", {})

    async def get_current_tab(self) -> Optional[str]:
        """
        Get the currently selected tab ID.
        
        Returns:
            Current tab ID, or None if no tab is selected
        """
        return self._current_tab_id

    async def create_tab(self, url: str = None) -> Dict[str, Any]:
        """
        Create a new browser tab.
        
        Args:
            url: URL to navigate to in the new tab
            
        Returns:
            Creation result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "tabs/create",
            "id": request_id
        }
        
        if url:
            message["url"] = url

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to create tab: {response.get('message', 'Unknown error')}"
            )

        # Refresh tabs list
        await self._refresh_tabs()
        
        return response.get("result", {})

    async def close_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Close a browser tab.
        
        Args:
            tab_id: ID of the tab to close
            
        Returns:
            Close result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "tabs/close",
            "tabId": tab_id,
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to close tab: {response.get('message', 'Unknown error')}"
            )

        # If we closed the current tab, reset current tab ID
        if self._current_tab_id == tab_id:
            self._current_tab_id = None

        # Refresh tabs list
        await self._refresh_tabs()
        
        return response.get("result", {})

    async def reload_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Reload a browser tab.
        
        Args:
            tab_id: ID of the tab to reload
            
        Returns:
            Reload result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "tabs/reload",
            "tabId": tab_id,
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to reload tab: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("result", {})

    async def navigate_to(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL in the current tab.
        
        Args:
            url: URL to navigate to
            
        Returns:
            Navigation result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "navigation/navigate",
            "url": url,
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to navigate: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("result", {})

    async def navigate_back(self) -> Dict[str, Any]:
        """
        Navigate back in the current tab's history.
        
        Returns:
            Navigation result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "navigation/back",
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to navigate back: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("result", {})

    async def navigate_forward(self) -> Dict[str, Any]:
        """
        Navigate forward in the current tab's history.
        
        Returns:
            Navigation result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "navigation/forward",
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to navigate forward: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("result", {})

    async def get_cookies(self, urls: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get cookies from the current tab.
        
        Args:
            urls: List of URLs to get cookies for (optional)
            
        Returns:
            List of cookies
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "cookies/get",
            "id": request_id
        }
        
        if urls:
            message["urls"] = urls

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to get cookies: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("cookies", [])

    async def set_cookies(self, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Set cookies in the current tab.
        
        Args:
            cookies: List of cookies to set
            
        Returns:
            Set cookies result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "cookies/set",
            "cookies": cookies,
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to set cookies: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("result", {})

    async def clear_cookies(self, urls: List[str] = None) -> Dict[str, Any]:
        """
        Clear cookies from the current tab.
        
        Args:
            urls: List of URLs to clear cookies for (optional)
            
        Returns:
            Clear cookies result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "cookies/clear",
            "id": request_id
        }
        
        if urls:
            message["urls"] = urls

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to clear cookies: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("result", {})

    async def get_local_storage(self) -> Dict[str, Any]:
        """
        Get LocalStorage data from the current tab.
        
        Returns:
            LocalStorage data
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "localStorage/get",
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to get LocalStorage: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("storage", {})

    async def set_local_storage(self, data: Dict[str, str]) -> Dict[str, Any]:
        """
        Set LocalStorage data in the current tab.
        
        Args:
            data: Dictionary of key-value pairs to set
            
        Returns:
            Set LocalStorage result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "localStorage/set",
            "data": data,
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to set LocalStorage: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("result", {})

    async def clear_local_storage(self) -> Dict[str, Any]:
        """
        Clear LocalStorage data from the current tab.
        
        Returns:
            Clear LocalStorage result
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "localStorage/clear",
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to clear LocalStorage: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("result", {})

    async def take_screenshot(
        self,
        format: str = "png",
        quality: int = 80,
        full_page: bool = False,
        clip: Dict[str, int] = None
    ) -> bytes:
        """
        Take a screenshot of the current tab.
        
        Args:
            format: Image format (png, jpeg, webp)
            quality: Image quality (0-100)
            full_page: Whether to capture the full page
            clip: Clipping region (x, y, width, height)
            
        Returns:
            Screenshot image data
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        request_id = str(uuid.uuid4())
        message = {
            "type": "screenshot/take",
            "format": format,
            "quality": quality,
            "fullPage": full_page,
            "id": request_id
        }
        
        if clip:
            message["clip"] = clip

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPBridgeExtensionProtocolError(
                f"Failed to take screenshot: {response.get('message', 'Unknown error')}"
            )
        
        return response.get("imageData", b"")

    async def _send_message(self, message: Dict[str, Any]) -> None:
        """
        Send a message to the MCP Bridge extension.
        
        Args:
            message: Message to send
            
        Raises:
            MCPBridgeExtensionConnectionError: If not connected to extension
        """
        if not await self.is_connected():
            raise MCPBridgeExtensionConnectionError("Not connected to MCP Bridge extension")

        # Add ID if not present
        if "id" not in message:
            self._request_counter += 1
            message["id"] = str(self._request_counter)

        try:
            await self._connection.send(json.dumps(message))
            logger.debug(f"Sent message: {message}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise MCPBridgeExtensionConnectionError(f"Failed to send message: {e}")

    async def _listen_for_messages(self) -> None:
        """
        Listen for messages from the MCP Bridge extension.
        """
        try:
            async for message in self._connection:
                try:
                    data = json.loads(message)
                    logger.debug(f"Received message: {data}")
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                except Exception as e:
                    logger.error(f"Failed to handle message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection closed")
            # Attempt to reconnect if connection is lost
            if self._connected:
                self._reconnect_task = asyncio.create_task(self._reconnect())
        except Exception as e:
            logger.error(f"Error listening for messages: {e}")
        finally:
            self._connected = False
            logger.info("Stopped listening for messages")

    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """
        Handle a message from the MCP Bridge extension.
        
        Args:
            message: Message to handle
        """
        message_type = message.get("type")
        message_id = message.get("id")

        if message_id in self._response_handlers:
            # This is a response to a request
            future = self._response_handlers[message_id]
            if not future.done():
                future.set_result(message)
            del self._response_handlers[message_id]
        elif message_type == "event":
            # Handle event message
            event_name = message.get("event")
            if event_name in self._event_handlers:
                for handler in self._event_handlers[event_name]:
                    asyncio.create_task(handler(message))
            else:
                # Put event in message queue for general processing
                await self._message_queue.put(message)
        elif message_type == "error":
            # Handle error message
            logger.error(f"Received error message: {message}")
        else:
            # Handle other message types
            await self._message_queue.put(message)

    async def _wait_for_response(self, request_id: str) -> Dict[str, Any]:
        """
        Wait for a response to a specific request.
        
        Args:
            request_id: ID of the request to wait for
            
        Returns:
            Response message
            
        Raises:
            MCPBridgeExtensionConnectionError: If waiting times out or connection is lost
        """
        # Check if we already have a future for this request
        if request_id in self._response_handlers:
            future = self._response_handlers[request_id]
        else:
            # Create a new future for the response
            future = asyncio.Future()
            self._response_handlers[request_id] = future

        try:
            # Wait for the response with timeout
            return await asyncio.wait_for(future, timeout=self.timeout)
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for response to request {request_id}")
            raise MCPBridgeExtensionConnectionError(f"Timeout waiting for response to request {request_id}")
        except Exception as e:
            logger.error(f"Error waiting for response to request {request_id}: {e}")
            raise MCPBridgeExtensionConnectionError(f"Error waiting for response to request {request_id}: {e}")
        finally:
            # Clean up response handler
            if request_id in self._response_handlers:
                del self._response_handlers[request_id]

    async def _reconnect(self) -> None:
        """
        Attempt to reconnect to the MCP Bridge extension.
        """
        logger.info("Attempting to reconnect to MCP Bridge extension")
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Reconnection attempt {attempt + 1}/{self.retry_attempts}")
                await self.disconnect()
                await self.connect()
                logger.info("Successfully reconnected to MCP Bridge extension")
                return
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
        
        logger.error("Failed to reconnect to MCP Bridge extension after all attempts")

    def register_event_handler(self, event_name: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_name: Name of the event to handle
            handler: Async function to handle the event
        """
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)

    def unregister_event_handler(self, event_name: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """
        Unregister an event handler for a specific event type.
        
        Args:
            event_name: Name of the event
            handler: Handler function to unregister
        """
        if event_name in self._event_handlers:
            if handler in self._event_handlers[event_name]:
                self._event_handlers[event_name].remove(handler)

    async def get_next_message(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Get the next message from the message queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Next message from the queue
            
        Raises:
            asyncio.TimeoutError: If no message is received within the timeout
        """
        return await asyncio.wait_for(self._message_queue.get(), timeout=timeout)