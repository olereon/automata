"""
MCP Bridge Connector for interfacing with MCP server and managing browser tabs.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Union

from ..core.logger import get_logger
from .mcp_client import MCPClient, MCPConnectionError, MCPToolError
from ..mcp.config import MCPConfiguration
from .connection_error_handler import ConnectionError, ConnectionErrorContext

logger = get_logger(__name__)


class MCPBridgeError(Exception):
    """Base exception for MCP Bridge errors."""
    pass


class MCPBridgeConnectionError(MCPBridgeError):
    """Exception raised when MCP Bridge connection fails."""
    def __init__(self, message: str, context: Optional[ConnectionErrorContext] = None):
        super().__init__(message)
        self.context = context


class MCPBridgeTabError(MCPBridgeError):
    """Exception raised when tab operation fails."""
    pass


class MCPBridgeConnector:
    """
    Bridge connector that interfaces with the MCP server and manages browser tabs.
    
    This class handles tab selection, management, and translates between existing
    automation commands and MCP tools.
    """

    def __init__(
        self,
        server_url: str = None,
        timeout: int = None,
        retry_attempts: int = None,
        retry_delay: int = None,
        extension_mode: bool = None,
        extension_port: int = None,
        config: MCPConfiguration = None
    ):
        """
        Initialize the MCP Bridge connector.
        
        Args:
            server_url: URL of the MCP server
            timeout: Timeout in milliseconds
            retry_attempts: Number of retry attempts
            retry_delay: Delay between retries in milliseconds
            extension_mode: Whether to use extension mode
            extension_port: Port for extension mode
            config: MCP configuration object
        """
        # Load configuration if provided
        if config:
            self.config = config
        else:
            self.config = MCPConfiguration.load_default()
        
        # Set parameters from config or use provided values
        self.server_url = server_url or self.config.get_server_url()
        self.timeout = timeout or self.config.get_timeout()
        self.retry_attempts = retry_attempts or self.config.get_retry_attempts()
        self.retry_delay = retry_delay or self.config.get_retry_delay()
        self.extension_mode = extension_mode if extension_mode is not None else self.config.is_bridge_extension_enabled()
        self.extension_port = extension_port or self.config.get_bridge_extension_port()
        
        # MCP client
        self._client = None
        
        # Current tab state
        self._current_tab = None
        self._available_tabs = []
        self._current_snapshot = None
        
        # Connection state
        self._connected = False

    async def connect(self, test_mode: bool = False) -> bool:
        """
        Connect to the MCP server and initialize the bridge.
        
        Args:
            test_mode: If True, don't fail if connection is unsuccessful
            
        Returns:
            True if connection was successful, False otherwise
            
        Raises:
            MCPBridgeConnectionError: If connection fails and not in test_mode
        """
        if self._connected:
            logger.warning("Already connected to MCP Bridge")
            return True

        logger.info("Connecting to MCP Bridge")

        try:
            # Initialize MCP client
            self._client = MCPClient(
                server_url=self.server_url,
                timeout=self.timeout,
                retry_attempts=self.retry_attempts,
                retry_delay=self.retry_delay,
                extension_mode=self.extension_mode,
                extension_port=self.extension_port
            )

            # Connect to MCP server
            await self._client.connect()

            # Get server capabilities
            capabilities = await self._client.get_capabilities()
            logger.info(f"Server capabilities: {capabilities}")

            # List available tools
            tools = await self._client.list_tools()
            logger.info(f"Available tools: {[tool.get('name', 'unknown') for tool in tools]}")

            # If in extension mode, list available tabs
            if self.extension_mode:
                await self._refresh_tabs()

            self._connected = True
            logger.info("Successfully connected to MCP Bridge")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MCP Bridge: {e}")
            await self.disconnect()
            
            # Create a more detailed error message if we have connection error context
            error_message = "Failed to connect to MCP Bridge"
            context = None
            
            if isinstance(e, MCPConnectionError) and hasattr(e, 'context') and e.context:
                context = e.context
                error_message = (
                    f"Failed to connect to MCP Bridge at {self.server_url}. "
                    f"Error type: {context.error_type.value}. "
                    f"Connection attempts: {context.connection_attempts}. "
                    f"Last error: {context.error_message}. "
                    f"Please check the server status and network connection."
                )
            elif isinstance(e, ConnectionError) and hasattr(e, 'context') and e.context:
                context = e.context
                error_message = (
                    f"Failed to connect to MCP Bridge at {self.server_url}. "
                    f"Error type: {context.error_type.value}. "
                    f"Connection attempts: {context.connection_attempts}. "
                    f"Last error: {context.error_message}. "
                    f"Please check the server status and network connection."
                )
            else:
                error_message = f"Failed to connect to MCP Bridge: {e}"
            
            if test_mode:
                return False
            else:
                raise MCPBridgeConnectionError(error_message, context)

    async def disconnect(self) -> None:
        """
        Disconnect from the MCP server and clean up resources.
        """
        if not self._connected:
            return

        logger.info("Disconnecting from MCP Bridge")

        try:
            # Disconnect MCP client
            if self._client:
                await self._client.disconnect()
                self._client = None
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

        # Reset state
        self._current_tab = None
        self._available_tabs = []
        self._current_snapshot = None
        self._connected = False

        logger.info("Disconnected from MCP Bridge")

    async def is_connected(self) -> bool:
        """
        Check if connected to the MCP Bridge.
        
        Returns:
            True if connected, False otherwise
        """
        return self._connected and self._client and await self._client.is_connected()

    async def _refresh_tabs(self) -> None:
        """
        Refresh the list of available tabs.
        
        Raises:
            MCPBridgeTabError: If tab listing fails
        """
        if not self.extension_mode:
            return

        try:
            tabs = await self._client.list_tabs()
            self._available_tabs = tabs
            logger.info(f"Refreshed tabs: {len(tabs)} tabs available")
        except Exception as e:
            logger.error(f"Failed to refresh tabs: {e}")
            raise MCPBridgeTabError(f"Failed to refresh tabs: {e}")

    async def list_tabs(self) -> List[Dict[str, Any]]:
        """
        List available browser tabs.
        
        Returns:
            List of browser tabs
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeTabError: If tab listing fails
        """
        if not await self.is_connected():
            raise MCPBridgeConnectionError("Not connected to MCP Bridge")

        if not self.extension_mode:
            raise MCPBridgeTabError("Tab management is only available in extension mode")

        await self._refresh_tabs()
        return self._available_tabs.copy()

    async def select_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Select a browser tab.
        
        Args:
            tab_id: ID of the tab to select
        
        Returns:
            Selection result
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeTabError: If tab selection fails
        """
        if not await self.is_connected():
            raise MCPBridgeConnectionError("Not connected to MCP Bridge")

        if not self.extension_mode:
            raise MCPBridgeTabError("Tab selection is only available in extension mode")

        try:
            # Select the tab
            result = await self._client.select_tab(tab_id)
            
            # Update current tab
            self._current_tab = tab_id
            
            # Take a fresh snapshot
            await self.take_snapshot()
            
            logger.info(f"Selected tab: {tab_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to select tab {tab_id}: {e}")
            raise MCPBridgeTabError(f"Failed to select tab {tab_id}: {e}")

    async def get_current_tab(self) -> Optional[str]:
        """
        Get the currently selected tab ID.
        
        Returns:
            Current tab ID, or None if no tab is selected
        """
        return self._current_tab

    async def take_snapshot(self) -> Dict[str, Any]:
        """
        Take a snapshot of the current page.
        
        Returns:
            Page snapshot
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeError: If snapshot fails
        """
        if not await self.is_connected():
            raise MCPBridgeConnectionError("Not connected to MCP Bridge")

        try:
            snapshot = await self._client.take_snapshot()
            self._current_snapshot = snapshot
            logger.debug("Took page snapshot")
            return snapshot
        except Exception as e:
            logger.error(f"Failed to take snapshot: {e}")
            raise MCPBridgeError(f"Failed to take snapshot: {e}")

    async def get_current_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Get the current page snapshot.
        
        Returns:
            Current snapshot, or None if no snapshot is available
        """
        return self._current_snapshot

    async def navigate_to(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
        
        Returns:
            Navigation result
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeError: If navigation fails
        """
        if not await self.is_connected():
            raise MCPBridgeConnectionError("Not connected to MCP Bridge")

        try:
            result = await self._client.navigate_to(url)
            logger.info(f"Navigated to: {url}")
            
            # Take a fresh snapshot after navigation
            await self.take_snapshot()
            
            return result
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise MCPBridgeError(f"Failed to navigate to {url}: {e}")

    async def click_element(self, element_description: str, element_ref: str) -> Dict[str, Any]:
        """
        Click on an element.
        
        Args:
            element_description: Human-readable element description
            element_ref: Element reference from snapshot
        
        Returns:
            Click result
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeError: If click fails
        """
        if not await self.is_connected():
            raise MCPBridgeConnectionError("Not connected to MCP Bridge")

        try:
            result = await self._client.click_element(element_description, element_ref)
            logger.info(f"Clicked element: {element_description}")
            
            # Take a fresh snapshot after interaction
            await self.take_snapshot()
            
            return result
        except Exception as e:
            logger.error(f"Failed to click element {element_description}: {e}")
            raise MCPBridgeError(f"Failed to click element {element_description}: {e}")

    async def fill_form(self, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fill form fields.
        
        Args:
            fields: List of field dictionaries with name, type, ref, and value
        
        Returns:
            Form fill result
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeError: If form fill fails
        """
        if not await self.is_connected():
            raise MCPBridgeConnectionError("Not connected to MCP Bridge")

        try:
            result = await self._client.fill_form(fields)
            logger.info(f"Filled form with {len(fields)} fields")
            
            # Take a fresh snapshot after interaction
            await self.take_snapshot()
            
            return result
        except Exception as e:
            logger.error(f"Failed to fill form: {e}")
            raise MCPBridgeError(f"Failed to fill form: {e}")

    async def type_text(self, element_description: str, element_ref: str, text: str) -> Dict[str, Any]:
        """
        Type text into an element.
        
        Args:
            element_description: Human-readable element description
            element_ref: Element reference from snapshot
            text: Text to type
        
        Returns:
            Type result
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeError: If typing fails
        """
        if not await self.is_connected():
            raise MCPBridgeConnectionError("Not connected to MCP Bridge")

        try:
            result = await self._client.type_text(element_description, element_ref, text)
            logger.info(f"Typed text into element: {element_description}")
            
            # Take a fresh snapshot after interaction
            await self.take_snapshot()
            
            return result
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            raise MCPBridgeError(f"Failed to type text: {e}")

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
            MCPBridgeConnectionError: If not connected
            MCPBridgeError: If wait fails
        """
        if not await self.is_connected():
            raise MCPBridgeConnectionError("Not connected to MCP Bridge")

        try:
            result = await self._client.wait_for(time, text, text_gone)
            
            if text is not None or text_gone is not None:
                # Take a fresh snapshot after waiting for text changes
                await self.take_snapshot()
            
            return result
        except Exception as e:
            logger.error(f"Failed to wait: {e}")
            raise MCPBridgeError(f"Failed to wait: {e}")

    async def find_element_by_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Find an element by its text content.
        
        Args:
            text: Text to search for
        
        Returns:
            Element information if found, None otherwise
        """
        snapshot = await self.take_snapshot()
        
        if not snapshot:
            return None
            
        # Search through the snapshot for the text
        # This is a simplified implementation - in practice, you'd want to
        # traverse the snapshot structure more carefully
        if "text" in snapshot and text in snapshot["text"]:
            return {"text": text, "found": True}
            
        return None

    async def find_element_by_role(self, role: str, accessible_name: str) -> Optional[Dict[str, Any]]:
        """
        Find an element by its role and accessible name.
        
        Args:
            role: Element role (e.g., "button", "link", "textbox")
            accessible_name: Accessible name of the element
        
        Returns:
            Element information if found, None otherwise
        """
        snapshot = await self.take_snapshot()
        
        if not snapshot:
            return None
            
        # Search through the snapshot for the element
        # This is a simplified implementation
        if "elements" in snapshot:
            for element in snapshot["elements"]:
                if element.get("role") == role and element.get("accessibleName") == accessible_name:
                    return element
                    
        return None

    async def execute_script(self, script: str) -> Any:
        """
        Execute JavaScript in the current page.
        
        Args:
            script: JavaScript code to execute
        
        Returns:
            Script execution result
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeError: If script execution fails
        """
        if not await self.is_connected():
            raise MCPBridgeConnectionError("Not connected to MCP Bridge")

        try:
            # Use the browser_evaluate tool if available
            result = await self._client.call_tool("browser_evaluate", {
                "function": script
            })
            
            # Take a fresh snapshot after script execution
            await self.take_snapshot()
            
            return result
        except Exception as e:
            logger.error(f"Failed to execute script: {e}")
            raise MCPBridgeError(f"Failed to execute script: {e}")

    async def get_page_title(self) -> str:
        """
        Get the title of the current page.
        
        Returns:
            Page title
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeError: If getting title fails
        """
        try:
            result = await self.execute_script("return document.title;")
            return str(result.get("result", ""))
        except Exception as e:
            logger.error(f"Failed to get page title: {e}")
            raise MCPBridgeError(f"Failed to get page title: {e}")

    async def get_page_url(self) -> str:
        """
        Get the URL of the current page.
        
        Returns:
            Page URL
        
        Raises:
            MCPBridgeConnectionError: If not connected
            MCPBridgeError: If getting URL fails
        """
        try:
            result = await self.execute_script("return window.location.href;")
            return str(result.get("result", ""))
        except Exception as e:
            logger.error(f"Failed to get page URL: {e}")
            raise MCPBridgeError(f"Failed to get page URL: {e}")
