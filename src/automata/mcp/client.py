"""
MCP client module for communicating with Playwright MCP server.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Union

import aiohttp
import websockets

from ..core.logger import get_logger

logger = get_logger(__name__)


class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    pass


class MCPConnectionError(MCPClientError):
    """Exception raised when MCP connection fails."""
    pass


class MCPProtocolError(MCPClientError):
    """Exception raised when MCP protocol error occurs."""
    pass


class MCPToolError(MCPClientError):
    """Exception raised when MCP tool execution fails."""
    pass


class MCPClient:
    """
    Client for communicating with Playwright MCP server.
    
    This class handles connection establishment, management, and message passing
    for MCP protocol, supporting both standard and extension modes.
    """

    def __init__(
        self,
        server_url: str = "ws://localhost:8080",
        timeout: int = 30000,
        retry_attempts: int = 3,
        retry_delay: int = 1000,
        extension_mode: bool = False,
        extension_port: int = 9222
    ):
        """
        Initialize the MCP client.
        
        Args:
            server_url: URL of the MCP server
            timeout: Timeout in milliseconds
            retry_attempts: Number of retry attempts
            retry_delay: Delay between retries in milliseconds
            extension_mode: Whether to use extension mode
            extension_port: Port for extension mode
        """
        self.server_url = server_url
        self.timeout = timeout / 1000  # Convert to seconds
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay / 1000  # Convert to seconds
        self.extension_mode = extension_mode
        self.extension_port = extension_port
        
        # Connection state
        self._connected = False
        self._connection = None
        self._session = None
        self._listen_task = None
        
        # Response handlers
        self._response_handlers = {}
        self._request_counter = 0
        
        # Server capabilities
        self._capabilities = {}
        self._tools = []

    async def connect(self) -> None:
        """
        Connect to the MCP server.
        
        Raises:
            MCPConnectionError: If connection fails
        """
        if self._connected:
            logger.warning("Already connected to MCP server")
            return

        logger.info(f"Connecting to MCP server at {self.server_url}")

        try:
            # Create HTTP session for REST API calls
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))

            # Check if server is reachable
            http_url = self.server_url
            if http_url.startswith("ws://"):
                http_url = http_url.replace("ws://", "http://")
            elif http_url.startswith("wss://"):
                http_url = http_url.replace("wss://", "https://")
            
            try:
                response = await self._session.get(f"{http_url}/health")
                if response.status != 200:
                    logger.warning(f"MCP server health check returned status: {response.status}")
            except Exception as e:
                logger.warning(f"Health check failed: {e}")

            # Connect via WebSocket for real-time communication
            self._connection = await websockets.connect(self.server_url)

            # Start listening for messages
            self._listen_task = asyncio.create_task(self._listen_for_messages())

            # Send initialize message with extension mode if enabled
            init_message = {
                "type": "initialize",
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                }
            }
            
            if self.extension_mode:
                init_message["capabilities"]["browser"] = {
                    "extension": True,
                    "port": self.extension_port
                }

            await self._send_message(init_message)

            # Wait for initialized response
            response = await self._wait_for_response("initialized")
            if not response.get("success", False):
                raise MCPConnectionError(f"Failed to initialize MCP connection: {response.get('message', 'Unknown error')}")

            # Store server capabilities
            if "capabilities" in response:
                self._capabilities = response["capabilities"]

            self._connected = True
            logger.info("Successfully connected to MCP server")

        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            await self.disconnect()
            raise MCPConnectionError(f"Failed to connect to MCP server: {e}")

    async def disconnect(self) -> None:
        """
        Disconnect from the MCP server.
        """
        if not self._connected:
            return

        logger.info("Disconnecting from MCP server")

        try:
            # Send close message if connected
            if self._connection:
                await self._send_message({"type": "close"})
        except Exception as e:
            logger.warning(f"Failed to send close message: {e}")

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

        self._connected = False
        logger.info("Disconnected from MCP server")

    async def is_connected(self) -> bool:
        """
        Check if connected to the MCP server.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected and self._connection and not self._connection.closed

    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get server capabilities.
        
        Returns:
            Server capabilities dictionary
        """
        if not await self.is_connected():
            raise MCPConnectionError("Not connected to MCP server")
        
        return self._capabilities.copy()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools on the MCP server.
        
        Returns:
            List of available tools
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPProtocolError: If listing tools fails
        """
        if not await self.is_connected():
            raise MCPConnectionError("Not connected to MCP server")

        request_id = str(uuid.uuid4())
        message = {
            "type": "tools/list",
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPProtocolError(f"Failed to list tools: {response.get('message', 'Unknown error')}")

        tools = response.get("tools", [])
        self._tools = tools
        return tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
        
        Returns:
            Tool execution result
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPToolError: If tool execution fails
        """
        if not await self.is_connected():
            raise MCPConnectionError("Not connected to MCP server")

        request_id = str(uuid.uuid4())
        message = {
            "type": "tool/call",
            "toolName": tool_name,
            "arguments": arguments,
            "id": request_id
        }

        await self._send_message(message)
        response = await self._wait_for_response(request_id)

        if not response.get("success", False):
            raise MCPToolError(f"Tool call failed: {response.get('message', 'Unknown error')}")

        return response.get("result", {})

    async def list_tabs(self) -> List[Dict[str, Any]]:
        """
        List available browser tabs (extension mode only).
        
        Returns:
            List of browser tabs
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPProtocolError: If listing tabs fails
        """
        if not self.extension_mode:
            raise MCPProtocolError("Tab listing is only available in extension mode")

        return await self.call_tool("list_tabs", {})

    async def select_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Select a browser tab (extension mode only).
        
        Args:
            tab_id: ID of the tab to select
        
        Returns:
            Selection result
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPToolError: If tab selection fails
        """
        if not self.extension_mode:
            raise MCPProtocolError("Tab selection is only available in extension mode")

        return await self.call_tool("select_tab", {"tabId": tab_id})

    async def take_snapshot(self) -> Dict[str, Any]:
        """
        Take a snapshot of the current page.
        
        Returns:
            Page snapshot
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPToolError: If snapshot fails
        """
        return await self.call_tool("browser_snapshot", {})

    async def navigate_to(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
        
        Returns:
            Navigation result
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPToolError: If navigation fails
        """
        return await self.call_tool("browser_navigate", {"url": url})

    async def click_element(self, element: str, ref: str) -> Dict[str, Any]:
        """
        Click on an element.
        
        Args:
            element: Human-readable element description
            ref: Element reference from snapshot
        
        Returns:
            Click result
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPToolError: If click fails
        """
        return await self.call_tool("browser_click", {
            "element": element,
            "ref": ref
        })

    async def fill_form(self, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fill form fields.
        
        Args:
            fields: List of field dictionaries with name, type, ref, and value
        
        Returns:
            Form fill result
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPToolError: If form fill fails
        """
        return await self.call_tool("browser_fill_form", {
            "fields": fields
        })

    async def type_text(self, element: str, ref: str, text: str) -> Dict[str, Any]:
        """
        Type text into an element.
        
        Args:
            element: Human-readable element description
            ref: Element reference from snapshot
            text: Text to type
        
        Returns:
            Type result
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPToolError: If typing fails
        """
        return await self.call_tool("browser_type", {
            "element": element,
            "ref": ref,
            "text": text
        })

    async def wait_for(self, time: Optional[float] = None, text: Optional[str] = None, 
                      text_gone: Optional[str] = None) -> Dict[str, Any]:
        """
        Wait for a condition.
        
        Args:
            time: Time to wait in seconds
            text: Text to wait for
            text_gone: Text to wait for to disappear
        
        Returns:
            Wait result
        
        Raises:
            MCPConnectionError: If not connected to server
            MCPToolError: If wait fails
        """
        arguments = {}
        if time is not None:
            arguments["time"] = time
        if text is not None:
            arguments["text"] = text
        if text_gone is not None:
            arguments["textGone"] = text_gone
        
        return await self.call_tool("browser_wait_for", arguments)

    async def _send_message(self, message: Dict[str, Any]) -> None:
        """
        Send a message to the MCP server.
        
        Args:
            message: Message to send
        
        Raises:
            MCPConnectionError: If not connected to server
        """
        if not await self.is_connected():
            raise MCPConnectionError("Not connected to MCP server")

        # Add ID if not present
        if "id" not in message:
            self._request_counter += 1
            message["id"] = str(self._request_counter)

        try:
            await self._connection.send(json.dumps(message))
            logger.debug(f"Sent message: {message}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise MCPConnectionError(f"Failed to send message: {e}")

    async def _listen_for_messages(self) -> None:
        """
        Listen for messages from the MCP server.
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
        except Exception as e:
            logger.error(f"Error listening for messages: {e}")
        finally:
            self._connected = False
            logger.info("Stopped listening for messages")

    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """
        Handle a message from the MCP server.
        
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
        elif message_type == "error":
            # Handle error message
            logger.error(f"Received error message: {message}")
        else:
            # Handle other message types
            logger.debug(f"Received unhandled message: {message}")

    async def _wait_for_response(self, request_id: str) -> Dict[str, Any]:
        """
        Wait for a response to a specific request.
        
        Args:
            request_id: ID of the request to wait for
        
        Returns:
            Response message
        
        Raises:
            MCPConnectionError: If waiting times out or connection is lost
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
            raise MCPConnectionError(f"Timeout waiting for response to request {request_id}")
        except Exception as e:
            logger.error(f"Error waiting for response to request {request_id}: {e}")
            raise MCPConnectionError(f"Error waiting for response to request {request_id}: {e}")
        finally:
            # Clean up response handler
            if request_id in self._response_handlers:
                del self._response_handlers[request_id]