"""
Browser management module for launching and controlling Chromium.
"""

import asyncio
from typing import Optional, Dict, Any
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright
import logging

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages browser instances and contexts for web automation."""

    def __init__(self, headless: bool = True, viewport: Optional[Dict[str, int]] = None):
        """
        Initialize the browser manager.

        Args:
            headless: Whether to run browser in headless mode
            viewport: Viewport size as dict with width and height
        """
        self.headless = headless
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.current_page: Optional[Page] = None

    async def start(self) -> None:
        """Start the browser and create a context."""
        logger.info("Starting browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        
        # Create context with default options
        context_options = {
            "viewport": self.viewport,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.context = await self.browser.new_context(**context_options)
        
        # Set default timeout for all operations
        self.context.set_default_timeout(30000)  # 30 seconds
        
        logger.info("Browser started successfully")

    async def stop(self) -> None:
        """Stop the browser and clean up resources."""
        logger.info("Stopping browser...")
        
        if self.context:
            await self.context.close()
            self.context = None
            
        if self.browser:
            await self.browser.close()
            self.browser = None
            
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            
        self.current_page = None
        logger.info("Browser stopped successfully")

    async def new_page(self, url: Optional[str] = None) -> Page:
        """
        Create a new page and optionally navigate to a URL.

        Args:
            url: URL to navigate to after creating the page

        Returns:
            The new Page object
        """
        if not self.context:
            raise RuntimeError("Browser not started. Call start() first.")
            
        self.current_page = await self.context.new_page()
        
        if url:
            await self.current_page.goto(url)
            
        return self.current_page

    async def get_current_page(self) -> Page:
        """
        Get the current active page.

        Returns:
            The current Page object

        Raises:
            RuntimeError: If no page is active
        """
        if not self.current_page:
            raise RuntimeError("No active page. Call new_page() first.")
        return self.current_page

    async def save_cookies(self, path: str) -> None:
        """
        Save cookies to a file.

        Args:
            path: Path to save cookies to
        """
        if not self.context:
            raise RuntimeError("Browser not started.")
            
        cookies = await self.context.cookies()
        import json
        with open(path, 'w') as f:
            json.dump(cookies, f)
        logger.info(f"Cookies saved to {path}")

    async def load_cookies(self, path: str) -> None:
        """
        Load cookies from a file.

        Args:
            path: Path to load cookies from
        """
        if not self.context:
            raise RuntimeError("Browser not started.")
            
        import json
        with open(path, 'r') as f:
            cookies = json.load(f)
        await self.context.add_cookies(cookies)
        logger.info(f"Cookies loaded from {path}")

    async def set_extra_headers(self, headers: Dict[str, str]) -> None:
        """
        Set extra HTTP headers for all requests.

        Args:
            headers: Dictionary of headers to set
        """
        if not self.context:
            raise RuntimeError("Browser not started.")
            
        await self.context.set_extra_http_headers(headers)
        logger.info(f"Extra headers set: {headers}")

    async def set_geolocation(self, latitude: float, longitude: float) -> None:
        """
        Set geolocation for the context.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        """
        if not self.context:
            raise RuntimeError("Browser not started.")
            
        await self.context.set_geolocation({"latitude": latitude, "longitude": longitude})
        logger.info(f"Geolocation set to: {latitude}, {longitude}")
