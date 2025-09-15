"""
Automation engine module.
"""

import json
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from playwright.async_api import Page, Browser, BrowserContext, Response, Request

from .browser import BrowserManager
from .selector import ElementSelector
from .wait import WaitUtils
from .errors import ErrorHandler, AutomationError, with_error_handling, RecoveryStrategy
from .logger import get_logger

logger = get_logger(__name__)


class AutomationEngine:
    """Main automation engine for browser automation."""

    def __init__(
        self,
        headless: bool = True,
        viewport: Optional[Dict[str, int]] = None,
        default_timeout: int = 30000,
        screenshot_on_error: bool = True,
        retry_attempts: int = 3,
        retry_delay: int = 1000
    ):
        """Initialize automation engine.
        
        Args:
            headless: Whether to run browser in headless mode
            viewport: Viewport size (width, height)
            default_timeout: Default timeout in milliseconds
            screenshot_on_error: Whether to take screenshots on errors
            retry_attempts: Number of retry attempts for failed operations
            retry_delay: Delay between retries in milliseconds
        """
        self.browser_manager = BrowserManager(headless=headless)
        self.element_selector = ElementSelector()
        self.wait_utils = WaitUtils(default_timeout=default_timeout)
        self.error_handler = ErrorHandler(max_retries=retry_attempts, retry_delay=retry_delay)
        
        self.default_timeout = default_timeout
        self.screenshot_on_error = screenshot_on_error
        self.viewport = viewport
        
        # Set viewport if provided
        if viewport:
            self.browser_manager.viewport = viewport

    async def start(self):
        """Start automation engine."""
        logger.info("Starting automation engine")
        await self.browser_manager.start()
        
        # Set viewport if provided
        if self.viewport:
            await self.browser_manager.context.set_viewport_size(self.viewport)
        
        logger.info("Automation engine started")

    async def stop(self):
        """Stop automation engine."""
        logger.info("Stopping automation engine")
        await self.browser_manager.stop()
        logger.info("Automation engine stopped")

    async def navigate_to(self, url: str):
        """Navigate to URL.
        
        Args:
            url: URL to navigate to
        """
        logger.info(f"Navigating to: {url}")
        await self.browser_manager.page.goto(url)
        await self.wait_for_page_load()

    async def wait_for_page_load(self, timeout: Optional[int] = None):
        """Wait for page to load.
        
        Args:
            timeout: Timeout in milliseconds
        """
        timeout = timeout or self.default_timeout
        await self.browser_manager.wait_for_navigation(timeout=timeout)

    async def click(self, selector: str, timeout: Optional[int] = None):
        """Click on element.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        timeout = timeout or self.default_timeout
        await self.browser_manager.wait_for_selector(selector, timeout=timeout)
        await self.browser_manager.click(selector)

    async def fill(self, selector: str, value: str, timeout: Optional[int] = None):
        """Fill form field.
        
        Args:
            selector: CSS selector
            value: Value to fill
            timeout: Timeout in milliseconds
        """
        timeout = timeout or self.default_timeout
        await self.browser_manager.wait_for_selector(selector, timeout=timeout)
        await self.browser_manager.fill(selector, value)

    async def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """Get text from element.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
            
        Returns:
            Element text
        """
        timeout = timeout or self.default_timeout
        await self.browser_manager.wait_for_selector(selector, timeout=timeout)
        return await self.browser_manager.page.text_content(selector)

    async def get_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> str:
        """Get attribute from element.
        
        Args:
            selector: CSS selector
            attribute: Attribute name
            timeout: Timeout in milliseconds
            
        Returns:
            Attribute value
        """
        timeout = timeout or self.default_timeout
        await self.browser_manager.wait_for_selector(selector, timeout=timeout)
        return await self.browser_manager.page.get_attribute(selector, attribute)

    async def is_visible(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if element is visible.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
            
        Returns:
            True if element is visible, False otherwise
        """
        timeout = timeout or self.default_timeout
        try:
            await self.browser_manager.wait_for_selector(selector, timeout=timeout)
            return await self.browser_manager.page.is_visible(selector)
        except Exception:
            return False

    async def is_enabled(self, selector: str, timeout: Optional[int] = None) -> bool:
        """Check if element is enabled.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
            
        Returns:
            True if element is enabled, False otherwise
        """
        timeout = timeout or self.default_timeout
        try:
            await self.browser_manager.wait_for_selector(selector, timeout=timeout)
            return await self.browser_manager.page.is_enabled(selector)
        except Exception:
            return False

    async def screenshot(self, path: Optional[str] = None) -> bytes:
        """Take screenshot.
        
        Args:
            path: Path to save screenshot
            
        Returns:
            Screenshot as bytes
        """
        return await self.browser_manager.screenshot(path=path)

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript.
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Script result
        """
        return await self.browser_manager.execute_script(script)

    async def wait_for_condition(self, condition: Callable[[], bool], timeout: Optional[int] = None):
        """Wait for condition to be true.
        
        Args:
            condition: Condition function
            timeout: Timeout in milliseconds
        """
        timeout = timeout or self.default_timeout
        await self.wait_utils.wait_for_condition(condition, timeout=timeout)

    async def wait_for_text(self, selector: str, text: str, timeout: Optional[int] = None):
        """Wait for element to contain text.
        
        Args:
            selector: CSS selector
            text: Text to wait for
            timeout: Timeout in milliseconds
        """
        timeout = timeout or self.default_timeout
        await self.wait_utils.wait_for_text(self.browser_manager.page, selector, text, timeout=timeout)

    async def wait_for_element_to_disappear(self, selector: str, timeout: Optional[int] = None):
        """Wait for element to disappear.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        timeout = timeout or self.default_timeout
        await self.wait_utils.wait_for_element_to_disappear(self.browser_manager.page, selector, timeout=timeout)

    async def get_page_title(self) -> str:
        """Get page title.
        
        Returns:
            Page title
        """
        return await self.browser_manager.get_page_title()

    async def get_page_url(self) -> str:
        """Get page URL.
        
        Returns:
            Page URL
        """
        return await self.browser_manager.get_page_url()

    async def take_snapshot(self) -> Dict[str, Any]:
        """Take page snapshot.
        
        Returns:
            Page snapshot
        """
        return await self.browser_manager.take_snapshot()

    async def new_page(self, url: Optional[str] = None) -> Page:
        """Create new page.
        
        Args:
            url: URL to navigate to
            
        Returns:
            New page
        """
        return await self.browser_manager.new_page(url)

    async def switch_to_page(self, index: int) -> Page:
        """Switch to page by index.
        
        Args:
            index: Page index
            
        Returns:
            Page
        """
        return await self.browser_manager.switch_to_page(index)

    async def close_page(self, index: Optional[int] = None):
        """Close page by index.
        
        Args:
            index: Page index (default: current page)
        """
        await self.browser_manager.close_page(index)

    @with_error_handling
    async def perform_action(self, action: Dict[str, Any]) -> Any:
        """Perform action.
        
        Args:
            action: Action to perform
            
        Returns:
            Action result
        """
        action_type = action.get("type")
        
        if action_type == "navigate":
            url = action.get("url")
            await self.navigate_to(url)
            return {"success": True}
        
        elif action_type == "click":
            selector = action.get("selector")
            timeout = action.get("timeout")
            await self.click(selector, timeout)
            return {"success": True}
        
        elif action_type == "fill":
            selector = action.get("selector")
            value = action.get("value")
            timeout = action.get("timeout")
            await self.fill(selector, value, timeout)
            return {"success": True}
        
        elif action_type == "get_text":
            selector = action.get("selector")
            timeout = action.get("timeout")
            text = await self.get_text(selector, timeout)
            return {"success": True, "text": text}
        
        elif action_type == "get_attribute":
            selector = action.get("selector")
            attribute = action.get("attribute")
            timeout = action.get("timeout")
            value = await self.get_attribute(selector, attribute, timeout)
            return {"success": True, "value": value}
        
        elif action_type == "is_visible":
            selector = action.get("selector")
            timeout = action.get("timeout")
            visible = await self.is_visible(selector, timeout)
            return {"success": True, "visible": visible}
        
        elif action_type == "is_enabled":
            selector = action.get("selector")
            timeout = action.get("timeout")
            enabled = await self.is_enabled(selector, timeout)
            return {"success": True, "enabled": enabled}
        
        elif action_type == "screenshot":
            path = action.get("path")
            screenshot_bytes = await self.screenshot(path)
            return {"success": True, "screenshot": screenshot_bytes}
        
        elif action_type == "execute_script":
            script = action.get("script")
            result = await self.execute_script(script)
            return {"success": True, "result": result}
        
        elif action_type == "wait_for_text":
            selector = action.get("selector")
            text = action.get("text")
            timeout = action.get("timeout")
            await self.wait_for_text(selector, text, timeout)
            return {"success": True}
        
        elif action_type == "wait_for_element_to_disappear":
            selector = action.get("selector")
            timeout = action.get("timeout")
            await self.wait_for_element_to_disappear(selector, timeout)
            return {"success": True}
        
        elif action_type == "get_page_title":
            title = await self.get_page_title()
            return {"success": True, "title": title}
        
        elif action_type == "get_page_url":
            url = await self.get_page_url()
            return {"success": True, "url": url}
        
        elif action_type == "take_snapshot":
            snapshot = await self.take_snapshot()
            return {"success": True, "snapshot": snapshot}
        
        elif action_type == "new_page":
            url = action.get("url")
            page = await self.new_page(url)
            return {"success": True, "page": page}
        
        elif action_type == "switch_to_page":
            index = action.get("index")
            page = await self.switch_to_page(index)
            return {"success": True, "page": page}
        
        elif action_type == "close_page":
            index = action.get("index")
            await self.close_page(index)
            return {"success": True}
        
        else:
            raise AutomationError(f"Unknown action type: {action_type}")

    async def __aenter__(self):
        """Enter context manager."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        await self.stop()
