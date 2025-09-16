"""
MCP client for communicating with the MCP server.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Awaitable

import aiohttp
from aiohttp import WSMsgType, ClientWebSocketResponse

from src.automata.mcp.client import MCPConnectionError, MCPClientError, MCPToolError
from src.automata.core.connection_error_handler import ConnectionErrorHandler


logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for communicating with the MCP server.
    
    This client handles the connection to the MCP server, including
    connection retries and error handling.
    """
    
    def __init__(
        self,
        server_url: str,
        timeout: int = 5000,
        retry_attempts: int = 3,
        retry_delay: int = 1000,
        extension_mode: bool = False,
        extension_port: int = 9222
    ):
        """
        Initialize the MCP client.
        
        Args:
            server_url: URL of the MCP server
            timeout: Connection timeout in milliseconds
            retry_attempts: Number of connection retry attempts
            retry_delay: Delay between retry attempts in milliseconds
            extension_mode: Whether to connect in extension mode
            extension_port: Port to use for extension mode
        """
        self.server_url = server_url
        self.timeout = timeout / 1000  # Convert to seconds
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay / 1000  # Convert to seconds
        self.extension_mode = extension_mode
        self.extension_port = extension_port
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[ClientWebSocketResponse] = None
        self._connected = False
        self._message_id = 0
        self._response_handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
        self._listen_task: Optional[asyncio.Task] = None
        self._error_handler = ConnectionErrorHandler(
            max_retries=retry_attempts,
            retry_delay=self.retry_delay
        )
    
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

        # First attempt without retry mechanism
        initial_error = None
        try:
            await self._establish_connection()
            logger.info("Successfully connected to MCP server")
            return
        except Exception as e:
            logger.error(f"Initial connection attempt failed: {e}")
            initial_error = e
            # Don't disconnect yet, we'll try again with the error handler
        
        # If the first attempt fails, use the error handler to manage retries
        try:
            await self._error_handler.handle_connection_error(
                initial_error,  # Pass the original error
                self.server_url,
                self._establish_connection
            )
            
            logger.info("Successfully connected to MCP server after retries")

        except Exception as retry_error:
            logger.error(f"Failed to connect to MCP server after retries: {retry_error}")
            await self.disconnect()
            
            # Create a more detailed error message
            if isinstance(retry_error, ConnectionError) and hasattr(retry_error, 'context') and retry_error.context:
                context = retry_error.context
                error_message = (
                    f"Failed to connect to MCP server at {self.server_url}. "
                    f"Error type: {context.error_type.value}. "
                    f"Connection attempts: {context.connection_attempts}. "
                    f"Last error: {context.error_message}. "
                    f"Please check the server status and network connection."
                )
                raise MCPConnectionError(error_message, context)
            else:
                raise MCPConnectionError(f"Failed to connect to MCP server: {retry_error}")
    
    async def _establish_connection(self) -> None:
        """
        Establish a connection to the MCP server.
        
        Raises:
            MCPConnectionError: If connection fails
        """
        # Create a new session
        self._session = aiohttp.ClientSession()
        
        if self.extension_mode:
            # In extension mode, connect to the browser extension via HTTP
            try:
                # First check if the extension is available
                async with self._session.get(
                    f"http://localhost:{self.extension_port}/json"
                ) as response:
                    if response.status != 200:
                        raise MCPConnectionError(
                            f"Browser extension not available at port {self.extension_port}"
                        )
                
                logger.info("Browser extension is available")
            except Exception as e:
                await self._session.close()
                self._session = None
                raise MCPConnectionError(f"Failed to connect to browser extension: {e}")
        else:
            # In server mode, connect to the MCP server via WebSocket
            try:
                # First check if the server is available
                async with self._session.get(self.server_url.replace('ws://', 'http://').replace('wss://', 'https://')) as response:
                    if response.status != 200:
                        raise MCPConnectionError(
                            f"MCP server not available at {self.server_url}"
                        )
                
                # Connect to the WebSocket
                self._ws = await self._session.ws_connect(self.server_url)
                logger.info("WebSocket connection established")
                
                # Start listening for messages
                self._listen_task = asyncio.create_task(self._listen_for_messages())
            except Exception as e:
                await self._session.close()
                self._session = None
                raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
        
        self._connected = True
    
    async def disconnect(self) -> None:
        """
        Disconnect from the MCP server.
        """
        if not self._connected:
            return
        
        logger.info("Disconnecting from MCP server")
        
        # Cancel the listen task if it's running
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
            self._listen_task = None
        
        # Close the WebSocket connection if it's open
        if self._ws:
            await self._ws.close()
            self._ws = None
        
        # Close the HTTP session if it's open
        if self._session:
            await self._session.close()
            self._session = None
        
        self._connected = False
        logger.info("Disconnected from MCP server")
    
    async def is_connected(self) -> bool:
        """
        Check if the client is connected to the MCP server.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected
    
    async def _listen_for_messages(self) -> None:
        """
        Listen for messages from the MCP server.
        
        This method runs in a separate task and handles incoming messages.
        """
        if not self._ws:
            return
        
        try:
            async for msg in self._ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_message(data)
                    except json.JSONDecodeError:
                        logger.error(f"Received invalid JSON: {msg.data}")
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {msg.data}")
                    break
                elif msg.type == WSMsgType.CLOSED:
                    logger.info("WebSocket connection closed")
                    break
        except Exception as e:
            logger.error(f"Error listening for messages: {e}")
        finally:
            self._connected = False
    
    async def _handle_message(self, data: Dict[str, Any]) -> None:
        """
        Handle a message from the MCP server.
        
        Args:
            data: The message data
        """
        message_id = data.get("id")
        
        if message_id and message_id in self._response_handlers:
            # This is a response to a request
            handler = self._response_handlers.pop(message_id)
            await handler(data)
        else:
            # This is a notification or unsolicited message
            logger.debug(f"Received message: {data}")
    
    async def send_request(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a request to the MCP server.
        
        Args:
            method: The method name
            params: The method parameters
            
        Returns:
            The response from the server
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        if not self._connected:
            raise MCPConnectionError("Not connected to MCP server")
        
        # Generate a unique ID for this request
        self._message_id += 1
        message_id = str(self._message_id)
        
        # Create the request message
        request = {
            "jsonrpc": "2.0",
            "id": message_id,
            "method": method
        }
        
        if params:
            request["params"] = params
        
        # Create a future to wait for the response
        future = asyncio.Future()
        
        # Create a response handler
        async def response_handler(data: Dict[str, Any]) -> None:
            if "error" in data:
                future.set_exception(MCPClientError(f"RPC error: {data['error']}"))
            else:
                future.set_result(data)
        
        # Register the response handler
        self._response_handlers[message_id] = response_handler
        
        try:
            # Send the request
            if self.extension_mode:
                # In extension mode, send the request via HTTP POST
                async with self._session.post(
                    f"http://localhost:{self.extension_port}/rpc",
                    json=request
                ) as response:
                    if response.status != 200:
                        raise MCPConnectionError(
                            f"HTTP request failed with status {response.status}"
                        )
                    
                    # Parse the response
                    response_data = await response.json()
                    await response_handler(response_data)
            else:
                # In server mode, send the request via WebSocket
                await self._ws.send_str(json.dumps(request))
            
            # Wait for the response
            return await asyncio.wait_for(future, timeout=self.timeout)
        
        except Exception as e:
            # Remove the response handler if the request fails
            if message_id in self._response_handlers:
                del self._response_handlers[message_id]
            
            # Cancel the future if it's not done
            if not future.done():
                future.cancel()
            
            raise MCPConnectionError(f"Request failed: {e}")
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the MCP server.
        
        Returns:
            The server capabilities
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        response = await self.send_request("get_capabilities")
        return response.get("result", {})
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List the available tools on the MCP server.
        
        Returns:
            A list of available tools
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        response = await self.send_request("list_tools")
        return response.get("result", [])
    
    async def call_tool(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: The name of the tool to call
            params: The parameters to pass to the tool
            
        Returns:
            The result of the tool call
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        response = await self.send_request("call_tool", {
            "name": tool_name,
            "arguments": params
        })
        return response.get("result", {})
    
    # Browser-specific methods
    
    async def list_tabs(self) -> List[Dict[str, Any]]:
        """
        List the available browser tabs.
        
        Returns:
            A list of available tabs
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        response = await self.send_request("list_tabs")
        return response.get("result", [])
    
    async def select_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Select a browser tab.
        
        Args:
            tab_id: The ID of the tab to select
            
        Returns:
            The result of the tab selection
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        response = await self.send_request("select_tab", {"tab_id": tab_id})
        return response.get("result", {})
    
    async def take_snapshot(self) -> Dict[str, Any]:
        """
        Take a snapshot of the current browser state.
        
        Returns:
            The browser snapshot
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        response = await self.send_request("take_snapshot")
        return response.get("result", {})
    
    async def navigate_to(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            The result of the navigation
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        response = await self.send_request("navigate_to", {"url": url})
        return response.get("result", {})
    
    async def click_element(
        self,
        element_description: str,
        element_ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Click an element on the page.
        
        Args:
            element_description: A description of the element to click
            element_ref: A reference to the element (optional)
            
        Returns:
            The result of the click
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        params = {"element_description": element_description}
        if element_ref:
            params["element_ref"] = element_ref
        
        response = await self.send_request("click_element", params)
        return response.get("result", {})
    
    async def fill_form(self, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fill a form on the page.
        
        Args:
            fields: A list of form fields to fill
            
        Returns:
            The result of the form filling
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        response = await self.send_request("fill_form", {"fields": fields})
        return response.get("result", {})
    
    async def type_text(
        self,
        element_description: str,
        element_ref: Optional[str] = None,
        text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Type text into an element on the page.
        
        Args:
            element_description: A description of the element to type into
            element_ref: A reference to the element (optional)
            text: The text to type (optional)
            
        Returns:
            The result of the typing
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        params = {"element_description": element_description}
        if element_ref:
            params["element_ref"] = element_ref
        if text:
            params["text"] = text
        
        response = await self.send_request("type_text", params)
        return response.get("result", {})
    
    async def wait_for(
        self,
        time: Optional[float] = None,
        text: Optional[str] = None,
        text_gone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Wait for a condition to be met.
        
        Args:
            time: Time to wait in seconds (optional)
            text: Text to wait for (optional)
            text_gone: Text to wait for to disappear (optional)
            
        Returns:
            The result of the wait
            
        Raises:
            MCPConnectionError: If not connected or if the request fails
        """
        params = {}
        if time is not None:
            params["time"] = time
        if text is not None:
            params["text"] = text
        if text_gone is not None:
            params["text_gone"] = text_gone
        
        response = await self.send_request("wait_for", params)
        return response.get("result", {})
