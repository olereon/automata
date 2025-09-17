"""
Extension mode functionality for MCP Server.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ExtensionMode:
    """
    Extension mode functionality for browser automation.
    
    This class handles the Chrome DevTools Protocol connection
    and provides tools for tab management when in extension mode.
    """

    def __init__(self, extension_id: Optional[str] = None, extension_websocket_url: Optional[str] = None):
        """
        Initialize extension mode.
        
        Args:
            extension_id: Browser extension ID
            extension_websocket_url: WebSocket URL for extension communication
        """
        self.extension_id = extension_id
        self.extension_websocket_url = extension_websocket_url
        self.cdp_client = None
        self.tabs = {}
        self.current_tab_id = None
    
    async def initialize(self) -> bool:
        """
        Initialize extension mode components.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Initializing extension mode...")
        
        if not self.extension_id:
            logger.warning("Extension ID not provided, extension mode may not work properly")
        
        if not self.extension_websocket_url:
            logger.warning("Extension WebSocket URL not provided, extension mode may not work properly")
        
        # Try to connect to the extension
        try:
            if self.extension_websocket_url:
                # Import here to avoid dependency issues if not in extension mode
                import websockets
                
                self.cdp_client = await websockets.connect(self.extension_websocket_url)
                logger.info("Connected to extension WebSocket")
                
                # Get initial list of tabs
                await self.refresh_tabs()
                
                return True
            else:
                logger.warning("No extension WebSocket URL provided, cannot connect to extension")
                return False
        except Exception as e:
            logger.error(f"Error connecting to extension: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop extension mode components."""
        logger.info("Stopping extension mode...")
        
        if self.cdp_client:
            try:
                await self.cdp_client.close()
            except Exception as e:
                logger.warning(f"Error closing extension connection: {e}")
            self.cdp_client = None
        
        self.tabs.clear()
        self.current_tab_id = None
    
    async def refresh_tabs(self) -> None:
        """Refresh the list of available tabs."""
        if not self.cdp_client:
            logger.warning("No CDP client connection, cannot refresh tabs")
            return
        
        try:
            # Send command to get all tabs
            await self.cdp_client.send(json.dumps({
                "id": 1,
                "method": "Target.getTargets",
                "params": {}
            }))
            
            # Wait for response
            response = await self.cdp_client.recv()
            response_data = json.loads(response)
            
            if "result" in response_data and "targetInfos" in response_data["result"]:
                # Clear existing tabs
                self.tabs.clear()
                
                # Process tab information
                for target_info in response_data["result"]["targetInfos"]:
                    if target_info["type"] == "page":
                        tab_id = target_info["targetId"]
                        self.tabs[tab_id] = {
                            "id": tab_id,
                            "url": target_info.get("url", ""),
                            "title": target_info.get("title", ""),
                            "type": target_info["type"],
                            "attached": target_info.get("attached", False)
                        }
                
                # Set current tab if not already set
                if not self.current_tab_id and self.tabs:
                    self.current_tab_id = next(iter(self.tabs.keys()))
                
                logger.info(f"Refreshed tabs, found {len(self.tabs)} tabs")
            else:
                logger.error(f"Unexpected response when getting tabs: {response_data}")
        except Exception as e:
            logger.error(f"Error refreshing tabs: {e}")
    
    async def attach_to_tab(self, tab_id: str) -> bool:
        """
        Attach to a specific tab.
        
        Args:
            tab_id: ID of the tab to attach to
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cdp_client:
            logger.warning("No CDP client connection, cannot attach to tab")
            return False
        
        try:
            # Send command to attach to tab
            await self.cdp_client.send(json.dumps({
                "id": 2,
                "method": "Target.attachToTarget",
                "params": {
                    "targetId": tab_id,
                    "flatten": True
                }
            }))
            
            # Wait for response
            response = await self.cdp_client.recv()
            response_data = json.loads(response)
            
            if "result" in response_data and "sessionId" in response_data["result"]:
                session_id = response_data["result"]["sessionId"]
                
                # Update tab info
                if tab_id in self.tabs:
                    self.tabs[tab_id]["attached"] = True
                    self.tabs[tab_id]["sessionId"] = session_id
                
                logger.info(f"Attached to tab {tab_id}")
                return True
            else:
                logger.error(f"Unexpected response when attaching to tab: {response_data}")
                return False
        except Exception as e:
            logger.error(f"Error attaching to tab: {e}")
            return False
    
    async def detach_from_tab(self, tab_id: str) -> bool:
        """
        Detach from a specific tab.
        
        Args:
            tab_id: ID of the tab to detach from
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cdp_client:
            logger.warning("No CDP client connection, cannot detach from tab")
            return False
        
        try:
            # Get session ID for tab
            session_id = None
            if tab_id in self.tabs and "sessionId" in self.tabs[tab_id]:
                session_id = self.tabs[tab_id]["sessionId"]
            
            if not session_id:
                logger.warning(f"No session ID for tab {tab_id}, cannot detach")
                return False
            
            # Send command to detach from tab
            await self.cdp_client.send(json.dumps({
                "id": 3,
                "method": "Target.detachFromTarget",
                "params": {
                    "sessionId": session_id
                }
            }))
            
            # Wait for response
            response = await self.cdp_client.recv()
            response_data = json.loads(response)
            
            if "result" in response_data:
                # Update tab info
                if tab_id in self.tabs:
                    self.tabs[tab_id]["attached"] = False
                    if "sessionId" in self.tabs[tab_id]:
                        del self.tabs[tab_id]["sessionId"]
                
                logger.info(f"Detached from tab {tab_id}")
                return True
            else:
                logger.error(f"Unexpected response when detaching from tab: {response_data}")
                return False
        except Exception as e:
            logger.error(f"Error detaching from tab: {e}")
            return False
    
    async def send_command_to_tab(self, tab_id: str, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send a command to a specific tab.
        
        Args:
            tab_id: ID of the tab
            method: Command method
            params: Command parameters
            
        Returns:
            Command response
        """
        if not self.cdp_client:
            raise RuntimeError("No CDP client connection")
        
        # Get session ID for tab
        session_id = None
        if tab_id in self.tabs and "sessionId" in self.tabs[tab_id]:
            session_id = self.tabs[tab_id]["sessionId"]
        
        if not session_id:
            # Try to attach to tab
            if not await self.attach_to_tab(tab_id):
                raise RuntimeError(f"Could not attach to tab {tab_id}")
            
            # Get session ID
            if tab_id in self.tabs and "sessionId" in self.tabs[tab_id]:
                session_id = self.tabs[tab_id]["sessionId"]
            else:
                raise RuntimeError(f"Could not get session ID for tab {tab_id}")
        
        try:
            # Prepare command
            import uuid
            command_id = int(uuid.uuid4().hex[:8], 16)  # Generate a unique command ID
            command = {
                "id": command_id,
                "method": method,
                "params": params or {}
            }
            
            if session_id:
                command["sessionId"] = session_id
            
            # Send command
            await self.cdp_client.send(json.dumps(command))
            
            # Wait for response
            response = await self.cdp_client.recv()
            response_data = json.loads(response)
            
            if response_data.get("id") == command_id:
                return response_data
            else:
                raise RuntimeError(f"Unexpected response ID: {response_data}")
        except Exception as e:
            logger.error(f"Error sending command to tab: {e}")
            raise
    
    async def list_tabs(self, filter_url: Optional[str] = None, filter_title: Optional[str] = None) -> Dict[str, Any]:
        """
        List all available browser tabs.
        
        Args:
            filter_url: Filter tabs by URL (partial match)
            filter_title: Filter tabs by title (partial match)
            
        Returns:
            Dictionary with tabs information
        """
        # Refresh tabs
        await self.refresh_tabs()
        
        # Filter tabs
        filtered_tabs = {}
        for tab_id, tab_info in self.tabs.items():
            include_tab = True
            
            if filter_url and filter_url not in tab_info.get("url", ""):
                include_tab = False
            
            if filter_title and filter_title not in tab_info.get("title", ""):
                include_tab = False
            
            if include_tab:
                filtered_tabs[tab_id] = tab_info
        
        return {
            "tabs": list(filtered_tabs.values()),
            "current_tab_id": self.current_tab_id
        }
    
    async def get_tab_info(self, tab_id: str) -> Dict[str, Any]:
        """
        Get information about a specific tab.
        
        Args:
            tab_id: ID of the tab
            
        Returns:
            Tab information
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        return self.tabs[tab_id]
    
    async def connect_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Connect to a specific tab.
        
        Args:
            tab_id: ID of the tab to connect to
            
        Returns:
            Connection result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Attach to tab
        success = await self.attach_to_tab(tab_id)
        
        if success:
            # Set as current tab
            self.current_tab_id = tab_id
        
        return {
            "success": success,
            "tab_id": tab_id
        }
    
    async def disconnect_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Disconnect from a tab.
        
        Args:
            tab_id: ID of the tab to disconnect from
            
        Returns:
            Disconnection result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Detach from tab
        success = await self.detach_from_tab(tab_id)
        
        return {
            "success": success,
            "tab_id": tab_id
        }
    
    async def switch_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Switch to a different tab.
        
        Args:
            tab_id: ID of the tab to switch to
            
        Returns:
            Switch result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Set as current tab
        self.current_tab_id = tab_id
        
        return {
            "success": True,
            "tab_id": tab_id
        }
    
    async def create_tab(self, url: str = "about:blank") -> Dict[str, Any]:
        """
        Create a new tab.
        
        Args:
            url: URL to navigate to in the new tab
            
        Returns:
            Tab creation result
        """
        # Send command to create new tab
        response = await self.send_command_to_tab(
            next(iter(self.tabs.keys())) if self.tabs else None,
            "Target.createTarget",
            {
                "url": url
            }
        )
        
        if "result" in response and "targetId" in response["result"]:
            new_tab_id = response["result"]["targetId"]
            
            # Refresh tabs
            await self.refresh_tabs()
            
            # Set as current tab
            self.current_tab_id = new_tab_id
            
            return {
                "success": True,
                "tab_id": new_tab_id
            }
        else:
            raise RuntimeError(f"Error creating tab: {response}")
    
    async def close_tab(self, tab_id: str) -> Dict[str, Any]:
        """
        Close a tab.
        
        Args:
            tab_id: ID of the tab to close
            
        Returns:
            Tab closure result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Send command to close tab
        response = await self.send_command_to_tab(
            tab_id,
            "Target.closeTarget",
            {
                "targetId": tab_id
            }
        )
        
        if "result" in response:
            # Refresh tabs
            await self.refresh_tabs()
            
            # Clear current tab if it was the closed tab
            if self.current_tab_id == tab_id:
                self.current_tab_id = next(iter(self.tabs.keys())) if self.tabs else None
            
            return {
                "success": True,
                "tab_id": tab_id
            }
        else:
            raise RuntimeError(f"Error closing tab: {response}")
    
    async def reload_tab(self, tab_id: str, ignore_cache: bool = False) -> Dict[str, Any]:
        """
        Reload a tab.
        
        Args:
            tab_id: ID of the tab to reload
            ignore_cache: Whether to ignore cache
            
        Returns:
            Tab reload result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Send command to reload tab
        response = await self.send_command_to_tab(
            tab_id,
            "Page.reload",
            {
                "ignoreCache": ignore_cache
            }
        )
        
        if "result" in response:
            return {
                "success": True,
                "tab_id": tab_id
            }
        else:
            raise RuntimeError(f"Error reloading tab: {response}")
    
    async def navigate_tab(self, tab_id: str, url: str, wait_until: str = "load", timeout: int = 30000) -> Dict[str, Any]:
        """
        Navigate a tab to a URL.
        
        Args:
            tab_id: ID of the tab to navigate
            url: URL to navigate to
            wait_until: When to consider navigation complete
            timeout: Navigation timeout in milliseconds
            
        Returns:
            Navigation result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Send command to navigate tab
        response = await self.send_command_to_tab(
            tab_id,
            "Page.navigate",
            {
                "url": url,
                "waitUntil": wait_until,
                "timeout": timeout
            }
        )
        
        if "result" in response:
            # Update tab info
            if tab_id in self.tabs:
                self.tabs[tab_id]["url"] = url
            
            return {
                "success": True,
                "tab_id": tab_id,
                "url": url
            }
        else:
            raise RuntimeError(f"Error navigating tab: {response}")
    
    async def navigate_tab_history(self, tab_id: str, direction: str, delta: int = 1) -> Dict[str, Any]:
        """
        Navigate back or forward in tab history.
        
        Args:
            tab_id: ID of the tab
            direction: Direction to navigate
            delta: Number of entries to navigate
            
        Returns:
            History navigation result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Send command to navigate history
        if direction == "back":
            response = await self.send_command_to_tab(
                tab_id,
                "Page.goBack",
                {
                    "delta": delta
                }
            )
        elif direction == "forward":
            response = await self.send_command_to_tab(
                tab_id,
                "Page.goForward",
                {
                    "delta": delta
                }
            )
        else:
            raise ValueError(f"Invalid direction: {direction}")
        
        if "result" in response:
            return {
                "success": True,
                "tab_id": tab_id,
                "direction": direction,
                "delta": delta
            }
        else:
            raise RuntimeError(f"Error navigating tab history: {response}")
    
    async def get_tab_cookies(self, tab_id: str, urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get cookies from a tab.
        
        Args:
            tab_id: ID of the tab
            urls: List of URLs to get cookies for
            
        Returns:
            Cookies information
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Send command to get cookies
        response = await self.send_command_to_tab(
            tab_id,
            "Network.getCookies",
            {
                "urls": urls or []
            }
        )
        
        if "result" in response:
            return {
                "success": True,
                "tab_id": tab_id,
                "cookies": response["result"].get("cookies", [])
            }
        else:
            raise RuntimeError(f"Error getting tab cookies: {response}")
    
    async def set_tab_cookies(self, tab_id: str, cookies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Set cookies for a tab.
        
        Args:
            tab_id: ID of the tab
            cookies: List of cookies to set
            
        Returns:
            Cookie setting result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Send command to set cookies
        response = await self.send_command_to_tab(
            tab_id,
            "Network.setCookies",
            {
                "cookies": cookies
            }
        )
        
        if "result" in response:
            return {
                "success": True,
                "tab_id": tab_id,
                "cookies": cookies
            }
        else:
            raise RuntimeError(f"Error setting tab cookies: {response}")
    
    async def clear_tab_cookies(self, tab_id: str, urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Clear cookies for a tab.
        
        Args:
            tab_id: ID of the tab
            urls: List of URLs to clear cookies for
            
        Returns:
            Cookie clearing result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Send command to clear cookies
        response = await self.send_command_to_tab(
            tab_id,
            "Network.clearBrowserCookies",
            {
                "urls": urls or []
            }
        )
        
        if "result" in response:
            return {
                "success": True,
                "tab_id": tab_id,
                "urls": urls
            }
        else:
            raise RuntimeError(f"Error clearing tab cookies: {response}")
    
    async def get_tab_storage(self, tab_id: str, origin: str) -> Dict[str, Any]:
        """
        Get localStorage from a tab.
        
        Args:
            tab_id: ID of the tab
            origin: Security origin
            
        Returns:
            Storage information
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Send command to get DOM storage
        response = await self.send_command_to_tab(
            tab_id,
            "DOMStorage.getDOMStorageItems",
            {
                "storageId": {
                    "securityOrigin": origin,
                    "isLocalStorage": True
                }
            }
        )
        
        if "result" in response:
            # Convert to dictionary
            storage = {}
            for i in range(0, len(response["result"].get("entries", [])), 2):
                if i + 1 < len(response["result"]["entries"]):
                    key = response["result"]["entries"][i]
                    value = response["result"]["entries"][i + 1]
                    storage[key] = value
            
            return {
                "success": True,
                "tab_id": tab_id,
                "origin": origin,
                "storage": storage
            }
        else:
            raise RuntimeError(f"Error getting tab storage: {response}")
    
    async def set_tab_storage(self, tab_id: str, origin: str, key: str, value: Any) -> Dict[str, Any]:
        """
        Set localStorage for a tab.
        
        Args:
            tab_id: ID of the tab
            origin: Security origin
            key: Storage key
            value: Storage value
            
        Returns:
            Storage setting result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Send command to set DOM storage
        response = await self.send_command_to_tab(
            tab_id,
            "DOMStorage.setDOMStorageItem",
            {
                "storageId": {
                    "securityOrigin": origin,
                    "isLocalStorage": True
                },
                "key": key,
                "value": value
            }
        )
        
        if "result" in response:
            return {
                "success": True,
                "tab_id": tab_id,
                "origin": origin,
                "key": key,
                "value": value
            }
        else:
            raise RuntimeError(f"Error setting tab storage: {response}")
    
    async def clear_tab_storage(self, tab_id: str, origin: str, key: Optional[str] = None) -> Dict[str, Any]:
        """
        Clear localStorage for a tab.
        
        Args:
            tab_id: ID of the tab
            origin: Security origin
            key: Storage key to clear (if not provided, clears all storage)
            
        Returns:
            Storage clearing result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        if key:
            # Send command to remove DOM storage item
            response = await self.send_command_to_tab(
                tab_id,
                "DOMStorage.removeDOMStorageItem",
                {
                    "storageId": {
                        "securityOrigin": origin,
                        "isLocalStorage": True
                    },
                    "key": key
                }
            )
        else:
            # Send command to clear DOM storage
            response = await self.send_command_to_tab(
                tab_id,
                "DOMStorage.clear",
                {
                    "storageId": {
                        "securityOrigin": origin,
                        "isLocalStorage": True
                    }
                }
            )
        
        if "result" in response:
            return {
                "success": True,
                "tab_id": tab_id,
                "origin": origin,
                "key": key
            }
        else:
            raise RuntimeError(f"Error clearing tab storage: {response}")
    
    async def get_tab_screenshot(self, tab_id: str, screenshot_format: str = "png", 
                               screenshot_quality: int = 80, full_page: bool = False,
                               clip: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Take a screenshot of a tab.
        
        Args:
            tab_id: ID of the tab
            screenshot_format: Screenshot format
            screenshot_quality: Screenshot quality (for jpeg)
            full_page: Take a screenshot of the full scrollable page
            clip: Specify clipping region of the page
            
        Returns:
            Screenshot result
        """
        if tab_id not in self.tabs:
            raise ValueError(f"Tab not found: {tab_id}")
        
        # Prepare screenshot options
        screenshot_options = {
            "format": screenshot_format
        }
        
        if screenshot_format == "jpeg":
            screenshot_options["quality"] = screenshot_quality
        
        if full_page:
            screenshot_options["captureBeyondViewport"] = True
        
        if clip:
            screenshot_options["clip"] = clip
        
        # Send command to take screenshot
        response = await self.send_command_to_tab(
            tab_id,
            "Page.captureScreenshot",
            screenshot_options
        )
        
        if "result" in response and "data" in response["result"]:
            screenshot_data = response["result"]["data"]
            
            return {
                "success": True,
                "tab_id": tab_id,
                "screenshot": {
                    "format": screenshot_format,
                    "data": screenshot_data
                }
            }
        else:
            raise RuntimeError(f"Error taking tab screenshot: {response}")
