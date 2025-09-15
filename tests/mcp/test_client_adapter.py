"""
Unit tests for MCP client adapter.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from automata.mcp.client_adapter import (
    MCPClientAdapter,
    MCPConnectionError,
    MCPProtocolError,
    MCPToolError,
)


class TestMCPClientAdapter:
    """Test cases for MCPClientAdapter class."""

    @pytest.fixture
    def adapter(self):
        """Create a test adapter instance."""
        return MCPClientAdapter(
            server_url="ws://localhost:8080",
            timeout=5000,
            retry_attempts=2,
            retry_delay=500
        )

    @pytest.mark.asyncio
    async def test_connect_success(self, adapter):
        """Test successful connection to MCP server."""
        # Mock websockets.connect
        mock_websocket = AsyncMock()
        mock_websocket.send = AsyncMock()
        mock_websocket.closed = False
        
        with patch('websockets.connect') as mock_connect, \
             patch('aiohttp.ClientSession') as mock_session_class, \
             patch.object(adapter, '_send_message') as mock_send, \
             patch.object(adapter, '_wait_for_response') as mock_wait:
            
            # Configure mocks
            mock_connect.return_value = asyncio.Future()
            mock_connect.return_value.set_result(mock_websocket)
            
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session
            mock_wait.return_value = {"success": True}
            
            # Connect
            await adapter.connect()
            
            # Verify connection was established
            assert adapter._connected is True
            assert adapter._connection is mock_websocket
            assert adapter._listen_task is not None
            
            # Verify initialization message was sent
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["type"] == "initialize"
            assert call_args["protocolVersion"] == "2024-11-05"

    @pytest.mark.asyncio
    async def test_connect_health_check_failure(self, adapter):
        """Test connection failure when health check fails."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            # Configure mock to return non-200 status
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session
            
            # Verify connection fails
            with pytest.raises(MCPConnectionError, match="MCP server health check failed"):
                await adapter.connect()
            
            # Verify connection state
            assert adapter._connected is False

    @pytest.mark.asyncio
    async def test_connect_initialization_failure(self, adapter):
        """Test connection failure when initialization fails."""
        # Mock websockets.connect
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        
        with patch('websockets.connect') as mock_connect, \
             patch('aiohttp.ClientSession') as mock_session_class, \
             patch.object(adapter, '_send_message') as mock_send, \
             patch.object(adapter, '_wait_for_response') as mock_wait:
            
            # Configure mocks
            mock_connect.return_value = asyncio.Future()
            mock_connect.return_value.set_result(mock_websocket)
            
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session
            mock_wait.return_value = {"success": False, "message": "Initialization failed"}
            
            # Verify connection fails
            with pytest.raises(MCPConnectionError, match="Failed to initialize MCP connection"):
                await adapter.connect()
            
            # Verify disconnect was called
            assert adapter._connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self, adapter):
        """Test disconnection from MCP server."""
        # Set up adapter as if connected
        adapter._connected = True
        adapter._connection = AsyncMock()
        adapter._connection.closed = False
        adapter._listen_task = asyncio.create_task(asyncio.sleep(0.1))
        adapter._session = AsyncMock()
        
        with patch.object(adapter, '_send_message') as mock_send:
            # Disconnect
            await adapter.disconnect()
            
            # Verify disconnection
            assert adapter._connected is False
            assert adapter._connection is None
            assert adapter._session is None
            
            # Verify close message was sent
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["type"] == "close"

    @pytest.mark.asyncio
    async def test_is_connected(self, adapter):
        """Test connection status check."""
        # Test when not connected
        assert await adapter.is_connected() is False
        
        # Set up adapter as if connected
        adapter._connected = True
        adapter._connection = AsyncMock()
        adapter._connection.closed = False
        
        # Test when connected
        assert await adapter.is_connected() is True
        
        # Test when connection is closed
        adapter._connection.closed = True
        assert await adapter.is_connected() is False

    @pytest.mark.asyncio
    async def test_call_tool_success(self, adapter):
        """Test successful tool call."""
        # Set up adapter as if connected
        adapter._connected = True
        adapter._connection = AsyncMock()
        adapter._connection.closed = False
        
        with patch.object(adapter, '_send_message') as mock_send, \
             patch.object(adapter, '_wait_for_response') as mock_wait:
            
            # Configure mocks
            mock_wait.return_value = {"success": True, "result": {"output": "Tool result"}}
            
            # Call tool
            result = await adapter.call_tool("test_tool", {"param": "value"})
            
            # Verify result
            assert result == {"output": "Tool result"}
            
            # Verify tool call message was sent
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["type"] == "tool/call"
            assert call_args["toolName"] == "test_tool"
            assert call_args["arguments"] == {"param": "value"}

    @pytest.mark.asyncio
    async def test_call_tool_not_connected(self, adapter):
        """Test tool call when not connected."""
        # Verify tool call fails when not connected
        with pytest.raises(MCPConnectionError, match="Not connected to MCP server"):
            await adapter.call_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_call_tool_failure(self, adapter):
        """Test tool call failure."""
        # Set up adapter as if connected
        adapter._connected = True
        adapter._connection = AsyncMock()
        adapter._connection.closed = False
        
        with patch.object(adapter, '_send_message') as mock_send, \
             patch.object(adapter, '_wait_for_response') as mock_wait:
            
            # Configure mocks
            mock_wait.return_value = {"success": False, "message": "Tool execution failed"}
            
            # Verify tool call fails
            with pytest.raises(MCPToolError, match="Tool call failed: Tool execution failed"):
                await adapter.call_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_list_tools_success(self, adapter):
        """Test successful tools listing."""
        # Set up adapter as if connected
        adapter._connected = True
        adapter._connection = AsyncMock()
        adapter._connection.closed = False
        
        with patch.object(adapter, '_send_message') as mock_send, \
             patch.object(adapter, '_wait_for_response') as mock_wait:
            
            # Configure mocks
            mock_wait.return_value = {
                "success": True,
                "tools": [
                    {"name": "tool1", "description": "Tool 1"},
                    {"name": "tool2", "description": "Tool 2"}
                ]
            }
            
            # List tools
            tools = await adapter.list_tools()
            
            # Verify result
            assert len(tools) == 2
            assert tools[0]["name"] == "tool1"
            assert tools[1]["name"] == "tool2"
            
            # Verify list tools message was sent
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["type"] == "tools/list"

    @pytest.mark.asyncio
    async def test_list_tools_not_connected(self, adapter):
        """Test tools listing when not connected."""
        # Verify tools listing fails when not connected
        with pytest.raises(MCPConnectionError, match="Not connected to MCP server"):
            await adapter.list_tools()

    @pytest.mark.asyncio
    async def test_list_tools_failure(self, adapter):
        """Test tools listing failure."""
        # Set up adapter as if connected
        adapter._connected = True
        adapter._connection = AsyncMock()
        adapter._connection.closed = False
        
        with patch.object(adapter, '_send_message') as mock_send, \
             patch.object(adapter, '_wait_for_response') as mock_wait:
            
            # Configure mocks
            mock_wait.return_value = {"success": False, "message": "Failed to list tools"}
            
            # Verify tools listing fails
            with pytest.raises(MCPProtocolError, match="Failed to list tools: Failed to list tools"):
                await adapter.list_tools()

    @pytest.mark.asyncio
    async def test_send_message(self, adapter):
        """Test message sending."""
        # Set up adapter as if connected
        adapter._connected = True
        adapter._connection = AsyncMock()
        adapter._connection.closed = False
        
        # Send message
        message = {"type": "test", "data": "value"}
        await adapter._send_message(message)
        
        # Verify message was sent
        adapter._connection.send.assert_called_once_with(json.dumps(message))

    @pytest.mark.asyncio
    async def test_send_message_not_connected(self, adapter):
        """Test message sending when not connected."""
        # Verify message sending fails when not connected
        with pytest.raises(MCPConnectionError, match="Not connected to MCP server"):
            await adapter._send_message({"type": "test"})

    @pytest.mark.asyncio
    async def test_listen_for_messages(self, adapter):
        """Test message listening."""
        # Set up adapter as if connected
        adapter._connected = True
        adapter._connection = AsyncMock()
        adapter._connection.closed = False
        
        # Create a future for testing
        test_future = asyncio.Future()
        adapter._response_handlers["test_id"] = test_future
        
        # Mock messages
        messages = [
            json.dumps({"type": "response", "id": "test_id", "success": True}),
            json.dumps({"type": "error", "message": "Test error"}),
            json.dumps({"type": "unknown", "data": "value"})
        ]
        
        # Configure mock to return messages then raise ConnectionClosed
        adapter._connection.__aiter__.return_value = iter(messages)
        
        # Start listening
        listen_task = asyncio.create_task(adapter._listen_for_messages())
        
        # Wait a bit for processing
        await asyncio.sleep(0.1)
        
        # Verify future was resolved
        assert test_future.done()
        assert test_future.result() == {"type": "response", "id": "test_id", "success": True}
        
        # Cancel and wait for task to complete
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_wait_for_response_success(self, adapter):
        """Test successful response waiting."""
        # Create a future and add it to response handlers
        test_future = asyncio.Future()
        adapter._response_handlers["test_id"] = test_future
        
        # Set up the future to return a result
        test_result = {"type": "response", "id": "test_id", "success": True}
        test_future.set_result(test_result)
        
        # Set a longer timeout for testing
        original_timeout = adapter.timeout
        adapter.timeout = 1.0
        
        try:
            # Wait for response
            result = await adapter._wait_for_response("test_id")
            
            # Verify result
            assert result == test_result
            
            # Verify response handler was cleaned up
            assert "test_id" not in adapter._response_handlers
        finally:
            # Restore original timeout
            adapter.timeout = original_timeout

    @pytest.mark.asyncio
    async def test_wait_for_response_timeout(self, adapter):
        """Test response waiting timeout."""
        # Create a future that never completes
        test_future = asyncio.Future()
        adapter._response_handlers["test_id"] = test_future
        
        # Set a very short timeout for testing
        original_timeout = adapter.timeout
        adapter.timeout = 0.01
        
        try:
            # Verify timeout raises error
            with pytest.raises(MCPConnectionError, match="Timeout waiting for response"):
                await adapter._wait_for_response("test_id")
        finally:
            # Restore original timeout
            adapter.timeout = original_timeout
        
        # Verify response handler was cleaned up
        assert "test_id" not in adapter._response_handlers

    @pytest.mark.asyncio
    async def test_wait_for_response_error(self, adapter):
        """Test response waiting error."""
        # Create a future that raises an exception
        test_future = asyncio.Future()
        adapter._response_handlers["test_id"] = test_future
        
        # Set up the future to raise an exception
        test_future.set_exception(ValueError("Test error"))
        
        # Set a longer timeout for testing
        original_timeout = adapter.timeout
        adapter.timeout = 1.0
        
        try:
            # Verify error is propagated
            with pytest.raises(MCPConnectionError, match="Error waiting for response"):
                await adapter._wait_for_response("test_id")
        finally:
            # Restore original timeout
            adapter.timeout = original_timeout
        
        # Verify response handler was cleaned up
        assert "test_id" not in adapter._response_handlers