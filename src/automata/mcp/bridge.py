"""
MCP Bridge connector module.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Union

import aiohttp
from aiohttp import web, WSMsgType, ClientSession

from ..core.logger import get_logger
from .config import MCPConfiguration

logger = get_logger(__name__)


class MCPBridgeConnectionError(Exception):
    """Exception raised when MCP Bridge connection fails."""
    pass


class MCPBridgeConnector:
    """MCP Bridge connector for browser automation."""

    def __init__(self, config: MCPConfiguration):
        """Initialize MCP Bridge connector.
        
        Args:
            config: MCP configuration
        """
        self.config = config
        self.session: Optional[ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.connected = False
        self.extension_mode = config.is_bridge_extension_enabled()
        self.extension_port = config.get_bridge_extension_port()
        self.server_url = config.get_server_url()
        self.timeout = config.get_timeout() / 1000  # Convert to seconds
        self.retry_attempts = config.get_retry_attempts()
        self.retry_delay = config.get_retry_delay() / 1000  # Convert to seconds
        self.message_queue = asyncio.Queue()
        self.response_handlers = {}
        self.message_id = 0
        self._listen_task = None
        self._sse_task = None

    async def connect(self, test_mode: bool = False) -> bool:
        """Connect to MCP server.
        
        Args:
            test_mode: If True, don't fail if connection is unsuccessful
            
        Returns:
            True if connection was successful, False otherwise
            
        Raises:
            MCPBridgeConnectionError: If connection fails and not in test_mode
        """
        logger.info(f"Connecting to MCP Bridge")
        
        # Create session
        self.session = aiohttp.ClientSession()
        
        # Try to connect to MCP server
        if self.extension_mode:
            # In extension mode, we don't connect to a server
            # but we do check if the extension is available
            success = await self._check_extension_availability()
        else:
            # In server mode, we connect to the MCP server
            success = await self._connect_to_server(test_mode)
        
        if success:
            self.connected = True
            # Start listening for messages
            self._listen_task = asyncio.create_task(self._listen_for_messages())
            logger.info("Connected to MCP Bridge")
        else:
            if test_mode:
                logger.warning("MCP Bridge test mode: Connection failed but continuing")
                return False
            else:
                error_msg = "Failed to connect to MCP Bridge"
                logger.error(error_msg)
                raise MCPBridgeConnectionError(error_msg)
        
        return success

    async def _check_extension_availability(self) -> bool:
        """Check if the browser extension is available.
        
        Returns:
            True if extension is available, False otherwise
        """
        logger.info(f"Checking browser extension availability on port {self.extension_port}")
        
        try:
            # Try to connect to the browser extension
            extension_url = f"http://localhost:{self.extension_port}/json"
            async with self.session.get(extension_url, timeout=self.timeout) as response:
                if response.status == 200:
                    logger.info("Browser extension is available")
                    return True
                else:
                    logger.warning(f"Browser extension returned status {response.status}")
                    return False
        except Exception as e:
            logger.warning(f"Failed to connect to browser extension: {e}")
            return False

    async def _connect_to_server(self, test_mode: bool = False) -> bool:
        """Connect to MCP server.
        
        Args:
            test_mode: If True, don't fail if connection is unsuccessful
            
        Returns:
            True if connection was successful, False otherwise
        """
        logger.info(f"Connecting to MCP server at {self.server_url}")
        
        # Check if server is available
        try:
            health_url = self.server_url.rstrip('/mcp') + '/health'
            async with self.session.get(health_url, timeout=self.timeout) as response:
                if response.status == 200:
                    logger.info("MCP server health check passed")
                else:
                    logger.warning(f"MCP server health check returned status {response.status}")
                    if not test_mode:
                        return False
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            if not test_mode:
                return False
        
        # Try to establish WebSocket connection
        ws_url = self.server_url.replace('http://', 'ws://').replace('https://', 'wss://')
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Attempting to connect to WebSocket at {ws_url} (attempt {attempt + 1}/{self.retry_attempts})")
                self.ws = await self.session.ws_connect(ws_url, timeout=self.timeout)
                logger.info("WebSocket connection established")
                return True
            except Exception as e:
                logger.warning(f"WebSocket connection attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All WebSocket connection attempts failed")
                    return False
        
        return False

    async def _listen_for_messages(self):
        """Listen for messages from MCP server."""
        if self.extension_mode:
            # In extension mode, we listen for SSE messages
            await self._listen_for_sse_messages()
        else:
            # In server mode, we listen for WebSocket messages
            await self._listen_for_ws_messages()

    async def _listen_for_ws_messages(self):
        """Listen for WebSocket messages from MCP server."""
        if not self.ws:
            logger.error("WebSocket connection not established")
            return
        
        logger.info("Listening for WebSocket messages")
        
        try:
            async for msg in self.ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_message(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode WebSocket message: {e}")
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self.ws.exception()}")
                    break
                elif msg.type == WSMsgType.CLOSED:
                    logger.info("WebSocket connection closed")
                    break
        except Exception as e:
            logger.error(f"Error listening for WebSocket messages: {e}")
        finally:
            self.connected = False
            logger.info("Stopped listening for WebSocket messages")

    async def _listen_for_sse_messages(self):
        """Listen for SSE messages from browser extension."""
        sse_url = f"http://localhost:{self.extension_port}/sse"
        
        logger.info("Listening for SSE messages")
        
        try:
            async with self.session.get(sse_url, timeout=self.timeout) as response:
                if response.status != 200:
                    logger.error(f"Failed to connect to SSE endpoint: {response.status}")
                    return
                
                async for line in response.content:
                    if line:
                        try:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]  # Remove 'data: ' prefix
                                if data_str:  # Ignore empty data
                                    data = json.loads(data_str)
                                    await self._handle_message(data)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode SSE message: {e}")
                        except Exception as e:
                            logger.error(f"Error processing SSE message: {e}")
        except Exception as e:
            logger.error(f"Error listening for SSE messages: {e}")
        finally:
            self.connected = False
            logger.info("Stopped listening for SSE messages")

    async def _handle_message(self, data: Dict[str, Any]):
        """Handle message from MCP server.
        
        Args:
            data: Message data
        """
        logger.debug(f"Received message: {data}")
        
        # Check if this is a response to a request
        if 'id' in data and data['id'] in self.response_handlers:
            handler = self.response_handlers.pop(data['id'])
            asyncio.create_task(handler(data))
        else:
            # Put message in queue for general processing
            await self.message_queue.put(data)

    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send request to MCP server.
        
        Args:
            method: RPC method name
            params: RPC method parameters
            
        Returns:
            Response from MCP server
            
        Raises:
            MCPBridgeConnectionError: If not connected to MCP server
        """
        if not self.connected:
            error_msg = "Not connected to MCP server"
            logger.error(error_msg)
            raise MCPBridgeConnectionError(error_msg)
        
        # Generate unique ID for this request
        self.message_id += 1
        request_id = str(self.message_id)
        
        # Create request
        request = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': method
        }
        
        if params is not None:
            request['params'] = params
        
        logger.debug(f"Sending request: {request}")
        
        # Create future for response
        response_future = asyncio.Future()
        
        # Register response handler
        self.response_handlers[request_id] = self._create_response_handler(response_future)
        
        # Send request
        try:
            if self.extension_mode:
                # In extension mode, send request via HTTP POST
                post_url = f"http://localhost:{self.extension_port}/rpc"
                async with self.session.post(post_url, json=request, timeout=self.timeout) as response:
                    if response.status != 200:
                        error_msg = f"Failed to send request: HTTP {response.status}"
                        logger.error(error_msg)
                        raise MCPBridgeConnectionError(error_msg)
            else:
                # In server mode, send request via WebSocket
                await self.ws.send_str(json.dumps(request))
        except Exception as e:
            error_msg = f"Failed to send request: {e}"
            logger.error(error_msg)
            self.response_handlers.pop(request_id, None)
            raise MCPBridgeConnectionError(error_msg)
        
        # Wait for response
        try:
            response = await asyncio.wait_for(response_future, timeout=self.timeout)
            return response
        except asyncio.TimeoutError:
            error_msg = "Request timed out"
            logger.error(error_msg)
            self.response_handlers.pop(request_id, None)
            raise MCPBridgeConnectionError(error_msg)

    def _create_response_handler(self, future: asyncio.Future):
        """Create response handler for a request.
        
        Args:
            future: Future to set with response
            
        Returns:
            Response handler function
        """
        async def handler(data: Dict[str, Any]):
            if 'error' in data:
                future.set_exception(MCPBridgeConnectionError(f"RPC error: {data['error']}"))
            else:
                future.set_result(data)
        
        return handler

    async def get_next_message(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Get next message from MCP server.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Message from MCP server
            
        Raises:
            asyncio.TimeoutError: If no message received within timeout
        """
        return await asyncio.wait_for(self.message_queue.get(), timeout=timeout)

    async def disconnect(self):
        """Disconnect from MCP server."""
        logger.info("Disconnecting from MCP Bridge")
        
        # Cancel listen tasks
        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass
        
        if self._sse_task:
            self._sse_task.cancel()
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket connection
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        # Close session
        if self.session:
            await self.session.close()
            self.session = None
        
        self.connected = False
        logger.info("Disconnected from MCP Bridge")

    async def __aenter__(self):
        """Enter context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        await self.disconnect()
