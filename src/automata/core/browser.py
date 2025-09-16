"""
Browser manager module.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Union

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from .logger import get_logger
from ..mcp.config import MCPConfiguration
from ..mcp.bridge import MCPBridgeConnector, MCPBridgeConnectionError
from ..mcp_server.server import MCPServer
from ..mcp_server.config import MCPServerConfig

logger = get_logger(__name__)


class BrowserManager:
    """Browser manager for controlling browser instances."""

    def __init__(
        self,
        headless: bool = True,
        browser_type: str = "chromium",
        use_mcp_bridge: bool = False,
        mcp_config: Optional[MCPConfiguration] = None,
        use_mcp_server: bool = False,
        mcp_server_config: Optional[MCPServerConfig] = None
    ):
        """Initialize browser manager.
        
        Args:
            headless: Whether to run browser in headless mode
            browser_type: Type of browser to use (chromium, firefox, webkit)
            use_mcp_bridge: Whether to use MCP Bridge for browser automation
            mcp_config: MCP configuration
            use_mcp_server: Whether to use MCP Server for browser automation
            mcp_server_config: MCP Server configuration
        """
        """Initialize browser manager.
        
        Args:
            headless: Whether to run browser in headless mode
            browser_type: Type of browser to use (chromium, firefox, webkit)
            use_mcp_bridge: Whether to use MCP Bridge for browser automation
            mcp_config: MCP configuration
        """
        self.headless = headless
        self.browser_type = browser_type
        self.use_mcp_bridge = use_mcp_bridge
        self.mcp_config = mcp_config or MCPConfiguration.load_default()
        
        self.mcp_bridge_test_mode = getattr(self, 'mcp_bridge_test_mode', False)
        
        # Set MCP server parameters
        self.use_mcp_server = use_mcp_server
        self.mcp_server_config = mcp_server_config or MCPServerConfig.load_default()
        self.mcp_server = None
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.mcp_bridge: Optional[MCPBridgeConnector] = None
        
        self.pages: List[Page] = []
        self.current_page_index = 0

    async def start(self):
        """Start browser and MCP Bridge/MCP Server if enabled."""
        """Start browser and MCP Bridge if enabled."""
        logger.info(f"Starting browser (headless={self.headless}, type={self.browser_type})")
        
        # Start Playwright
        self.playwright = await async_playwright().start()
        
        # Get browser type
        if self.browser_type == "chromium":
            browser_launcher = self.playwright.chromium
        elif self.browser_type == "firefox":
            browser_launcher = self.playwright.firefox
        elif self.browser_type == "webkit":
            browser_launcher = self.playwright.webkit
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
        
        # Launch browser
        self.browser = await browser_launcher.launch(headless=self.headless)
        
        # Create context
        self.context = await self.browser.new_context()
        
        # Create initial page
        self.page = await self.context.new_page()
        self.pages.append(self.page)
        
        # Start MCP Bridge if enabled
        if self.use_mcp_bridge:
            logger.info("Starting MCP Bridge")
            self.mcp_bridge = MCPBridgeConnector(self.mcp_config)
            
            # Connect to MCP server
            if self.mcp_bridge_test_mode:
                logger.info("MCP Bridge test mode enabled")
                connected = await self.mcp_bridge.connect(test_mode=True)
                if not connected:
                    logger.warning("MCP Bridge connection failed (expected in test mode)")
            else:
                await self.mcp_bridge.connect()
        
        logger.info("Browser started successfully")
        
        # Start MCP Server if enabled
        if self.use_mcp_server:
            logger.info("Starting MCP Server")
            self.mcp_server = MCPServer(self.mcp_server_config)
            await self.mcp_server.start()
            logger.info("MCP Server started successfully")

    async def stop(self):
        """Stop browser and MCP Bridge if enabled."""
        logger.info("Stopping browser")
        
        # Stop MCP Bridge if enabled
        if self.use_mcp_bridge and self.mcp_bridge:
            logger.info("Stopping MCP Bridge")
            await self.mcp_bridge.disconnect()
            self.mcp_bridge = None
        
        # Close all pages
        for page in self.pages:
            try:
                await page.close()
            except Exception as e:
                logger.warning(f"Error closing page: {e}")
        
        # Close context
        if self.context:
            try:
                await self.context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {e}")
            self.context = None
        
        # Close browser
        if self.browser:
            try:
                await self.browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            self.browser = None
        
        # Stop Playwright
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping Playwright: {e}")
            self.playwright = None
        
        # Clear pages
        self.pages = []
        self.page = None
        
        logger.info("Browser stopped successfully")
        
        # Stop MCP Server if enabled
        if self.use_mcp_server and self.mcp_server:
            logger.info("Stopping MCP Server")
            await self.mcp_server.stop()
            self.mcp_server = None
            logger.info("MCP Server stopped successfully")

    async def new_page(self, url: Optional[str] = None) -> Page:
        """Create new page.
        
        Args:
            url: URL to navigate to
            
        Returns:
            New page
        """
        if not self.context:
            raise RuntimeError("Browser not started")
        
        # Create new page
        page = await self.context.new_page()
        self.pages.append(page)
        
        # Set as current page
        self.page = page
        self.current_page_index = len(self.pages) - 1
        
        # Navigate to URL if provided
        if url:
            await page.goto(url)
        
        return page

    async def switch_to_page(self, index: int) -> Page:
        """Switch to page by index.
        
        Args:
            index: Page index
            
        Returns:
            Page
        """
        if index < 0 or index >= len(self.pages):
            raise IndexError(f"Page index out of range: {index}")
        
        self.page = self.pages[index]
        self.current_page_index = index
        
        return self.page

    async def close_page(self, index: Optional[int] = None) -> None:
        """Close page by index.
        
        Args:
            index: Page index (default: current page)
        """
        if index is None:
            index = self.current_page_index
        
        if index < 0 or index >= len(self.pages):
            raise IndexError(f"Page index out of range: {index}")
        
        # Close page
        await self.pages[index].close()
        
        # Remove from list
        self.pages.pop(index)
        
        # Update current page index
        if self.current_page_index >= len(self.pages):
            self.current_page_index = len(self.pages) - 1
        
        # Update current page
        if self.pages:
            self.page = self.pages[self.current_page_index]
        else:
            self.page = None

    async def get_page_title(self) -> str:
        """Get current page title.
        
        Returns:
            Page title
        """
        if not self.page:
            raise RuntimeError("No page available")
        
        return await self.page.title()

    async def get_page_url(self) -> str:
        """Get current page URL.
        
        Returns:
            Page URL
        """
        if not self.page:
            raise RuntimeError("No page available")
        
        return self.page.url

    async def take_snapshot(self) -> Dict[str, Any]:
        """Take snapshot of current page.
        
        Returns:
            Page snapshot
        """
        if not self.page:
            raise RuntimeError("No page available")
        
        # Get page content
        content = await self.page.content()
        
        # Get page title
        title = await self.page.title()
        
        # Get page URL
        url = self.page.url
        
        # Create snapshot
        snapshot = {
            "title": title,
            "url": url,
            "content": content,
        }
        
        return snapshot

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on current page.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Script result
        """
        if not self.page:
            raise RuntimeError("No page available")
        
        return await self.page.evaluate(script)

    async def wait_for_navigation(self, timeout: Optional[int] = None) -> None:
        """Wait for navigation to complete.
        
        Args:
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("No page available")
        
        await self.page.wait_for_load_state("networkidle", timeout=timeout)

    async def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> None:
        """Wait for selector to be available.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("No page available")
        
        await self.page.wait_for_selector(selector, timeout=timeout)

    async def click(self, selector: str) -> None:
        """Click on element.
        
        Args:
            selector: CSS selector
        """
        if not self.page:
            raise RuntimeError("No page available")
        
        await self.page.click(selector)

    async def fill(self, selector: str, value: str) -> None:
        """Fill form field.
        
        Args:
            selector: CSS selector
            value: Value to fill
        """
        if not self.page:
            raise RuntimeError("No page available")
        
        await self.page.fill(selector, value)

    async def screenshot(self, path: Optional[str] = None) -> bytes:
        """Take screenshot of current page.
        
        Args:
            path: Path to save screenshot
            
        Returns:
            Screenshot as bytes
        """
        if not self.page:
            raise RuntimeError("No page available")
        
        return await self.page.screenshot(path=path)

    async def __aenter__(self):
        """Enter context manager."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        await self.stop()
