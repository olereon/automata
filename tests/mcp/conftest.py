"""
Fixtures for MCP bridge tests.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from src.automata.mcp.config import MCPConfiguration
from src.automata.mcp.bridge import MCPBridgeConnector
from src.automata.core.mcp_bridge import MCPBridgeConnector as CoreMCPBridgeConnector


@pytest.fixture
def mcp_config():
    """Create a basic MCP bridge config for testing."""
    config = MCPConfiguration()
    config.set_server_url("ws://localhost:8080/mcp")
    config.set_timeout(5000)
    config.set_retry_attempts(3)
    config.set_retry_delay(1000)
    config.set_bridge_extension_enabled(False)
    config.set_bridge_extension_port(9222)
    return config


@pytest.fixture
def mcp_config_extension():
    """Create an MCP bridge config with extension mode enabled for testing."""
    config = MCPConfiguration()
    config.set_server_url("ws://localhost:8080/mcp")
    config.set_timeout(5000)
    config.set_retry_attempts(3)
    config.set_retry_delay(1000)
    config.set_bridge_extension_enabled(True)
    config.set_bridge_extension_port(9222)
    return config


@pytest_asyncio.fixture
async def mock_websocket():
    """Create a mock WebSocket for testing."""
    ws = AsyncMock()
    ws.send_str = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest_asyncio.fixture
async def mock_http_response():
    """Create a mock HTTP response for testing."""
    response = AsyncMock()
    response.status = 200
    response.json = AsyncMock(return_value={"result": "success"})
    return response


@pytest_asyncio.fixture
async def mock_http_get(mock_http_response):
    """Create a mock HTTP GET request for testing."""
    get = AsyncMock()
    get.__aenter__ = AsyncMock(return_value=mock_http_response)
    get.__aexit__ = AsyncMock(return_value=None)
    return get


@pytest_asyncio.fixture
async def mock_http_post(mock_http_response):
    """Create a mock HTTP POST request for testing."""
    post = AsyncMock()
    post.__aenter__ = AsyncMock(return_value=mock_http_response)
    post.__aexit__ = AsyncMock(return_value=None)
    return post


@pytest_asyncio.fixture
async def mock_http_session(mock_http_get, mock_http_post):
    """Create a mock HTTP session for testing."""
    session = AsyncMock()
    session.get = MagicMock(return_value=mock_http_get)
    session.post = MagicMock(return_value=mock_http_post)
    session.close = AsyncMock()
    
    # Mock ws_connect to return a coroutine
    mock_ws = AsyncMock()
    
    async def mock_ws_connect(*args, **kwargs):
        return mock_ws
    
    session.ws_connect = mock_ws_connect
    
    return session


@pytest_asyncio.fixture
async def mcp_bridge_connector(mcp_config, mock_http_session, mock_websocket):
    """Create an MCP bridge connector for testing."""
    with patch('aiohttp.ClientSession', return_value=mock_http_session):
        connector = MCPBridgeConnector(config=mcp_config)
        yield connector


@pytest_asyncio.fixture
async def core_mcp_bridge_connector(mcp_config):
    """Create a core MCP bridge connector for testing."""
    with patch('src.automata.core.mcp_client.MCPClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client.is_connected = AsyncMock(return_value=True)
        mock_client.get_capabilities = AsyncMock(return_value={"tools": {}})
        mock_client.list_tools = AsyncMock(return_value=[])
        mock_client_class.return_value = mock_client
        
        connector = CoreMCPBridgeConnector(config=mcp_config)
        connector._client = mock_client
        connector._connected = False  # Set to False so connect method will be called
        
        yield connector


@pytest_asyncio.fixture
async def core_mcp_client(mock_http_session, mock_websocket):
    """Create a core MCP client for testing."""
    from src.automata.core.mcp_client import MCPClient
    
    with patch('aiohttp.ClientSession', return_value=mock_http_session):
        client = MCPClient(server_url="ws://localhost:8080/mcp")
        yield client
