"""
Browser automation module for the MCP Server.
"""

import asyncio
import os
import platform
import tempfile
from typing import Dict, Any, List, Optional, Union, BinaryIO
from pathlib import Path
from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from ..core.logger import get_logger
from .exceptions import BrowserAutomationError
from .config import MCPServerConfig

logger = get_logger(__name__)


class BrowserAutomation:
    """Browser automation class for executing commands."""

    def __init__(self, config: MCPServerConfig):
        """
        Initialize browser automation.

        Args:
            config: MCP server configuration
        """
        self.config = config
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pages: List[Page] = []
        self.current_page_index = 0
        self._started = False

    async def start(self) -> None:
        """Start browser automation."""
        if self._started:
            logger.warning("Browser automation already started")
            return

        logger.info("Starting browser automation")

        # Start Playwright
        self.playwright = await async_playwright().start()

        # Get browser type
        browser_type = self.config.get_browser_type()
        if browser_type == "chromium":
            browser_launcher = self.playwright.chromium
        elif browser_type == "firefox":
            browser_launcher = self.playwright.firefox
        elif browser_type == "webkit":
            browser_launcher = self.playwright.webkit
        else:
            raise BrowserAutomationError(f"Unsupported browser type: {browser_type}")

        # Prepare launch options
        launch_options = {
            "headless": self.config.is_headless(),
            "timeout": self.config.get_browser_timeout()
        }

        # Add platform-specific options
        system = platform.system().lower()
        if system == "windows":
            executable_path = self.config.get_windows_executable_path()
            if executable_path:
                launch_options["executable_path"] = executable_path
        elif system == "linux":
            executable_path = self.config.get_linux_executable_path()
            if executable_path:
                launch_options["executable_path"] = executable_path

        # Launch browser
        self.browser = await browser_launcher.launch(**launch_options)

        # Create context with viewport
        viewport = self.config.get_viewport()
        context_options = {
            "viewport": viewport,
            "timeout": self.config.get_browser_timeout()
        }

        self.context = await self.browser.new_context(**context_options)

        # Create initial page
        page = await self.context.new_page()
        self.pages.append(page)
        self.current_page_index = 0

        self._started = True
        logger.info("Browser automation started")

    async def stop(self) -> None:
        """Stop browser automation."""
        if not self._started:
            logger.warning("Browser automation not started")
            return

        logger.info("Stopping browser automation")

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
        self.current_page_index = 0
        self._started = False

        logger.info("Browser automation stopped")

    @property
    def current_page(self) -> Page:
        """Get current page."""
        if not self.pages:
            raise BrowserAutomationError("No pages available")
        return self.pages[self.current_page_index]

    async def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a browser automation command.

        Args:
            command: Command to execute

        Returns:
            Command execution result

        Raises:
            BrowserAutomationError: If command execution fails
        """
        if not self._started:
            raise BrowserAutomationError("Browser automation not started")

        command_type = command.get("type")
        logger.debug(f"Executing command: {command_type}")

        try:
            if command_type == "navigate":
                return await self._navigate(command)
            elif command_type == "click":
                return await self._click(command)
            elif command_type == "type":
                return await self._type_text(command)
            elif command_type == "hover":
                return await self._hover(command)
            elif command_type == "wait":
                return await self._wait(command)
            elif command_type == "screenshot":
                return await self._screenshot(command)
            elif command_type == "execute_script":
                return await self._execute_script(command)
            elif command_type == "get_text":
                return await self._get_text(command)
            elif command_type == "get_attribute":
                return await self._get_attribute(command)
            elif command_type == "back":
                return await self._back(command)
            elif command_type == "forward":
                return await self._forward(command)
            elif command_type == "refresh":
                return await self._refresh(command)
            elif command_type == "get_cookies":
                return await self._get_cookies(command)
            elif command_type == "set_cookie":
                return await self._set_cookie(command)
            elif command_type == "delete_cookies":
                return await self._delete_cookies(command)
            elif command_type == "new_tab":
                return await self._new_tab(command)
            elif command_type == "switch_tab":
                return await self._switch_tab(command)
            elif command_type == "close_tab":
                return await self._close_tab(command)
            elif command_type == "get_tabs":
                return await self._get_tabs(command)
            else:
                raise BrowserAutomationError(f"Unknown command type: {command_type}", command)
        except Exception as e:
            logger.error(f"Error executing command {command_type}: {e}")
            if self.config.is_screenshot_on_error():
                try:
                    screenshot_path = await self._take_error_screenshot()
                    logger.info(f"Error screenshot saved: {screenshot_path}")
                except Exception as screenshot_error:
                    logger.warning(f"Failed to take error screenshot: {screenshot_error}")
            raise BrowserAutomationError(f"Command execution failed: {e}", command)

    async def _navigate(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to URL."""
        url = command["url"]
        timeout = command.get("timeout", self.config.get_browser_timeout())
        wait_until = command.get("wait_until", "load")

        logger.info(f"Navigating to: {url}")
        await self.current_page.goto(url, timeout=timeout, wait_until=wait_until)
        return {"success": True}

    async def _click(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Click on element."""
        timeout = command.get("timeout", self.config.get_browser_timeout())
        button = command.get("button", "left")
        click_count = command.get("click_count", 1)
        position = command.get("position")

        # Get element locator
        element = await self._get_element(command, timeout)
        if not element:
            raise BrowserAutomationError("Element not found", command)

        # Click on element
        click_options = {
            "button": button,
            "click_count": click_count,
            "timeout": timeout
        }
        if position:
            click_options["position"] = position

        await element.click(**click_options)
        return {"success": True}

    async def _type_text(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Type text into element."""
        value = command["value"]
        timeout = command.get("timeout", self.config.get_browser_timeout())
        delay = command.get("delay", 0)
        clear = command.get("clear", True)

        # Get element locator
        element = await self._get_element(command, timeout)
        if not element:
            raise BrowserAutomationError("Element not found", command)

        # Type text
        if clear:
            await element.clear()
        await element.type(value, delay=delay)
        return {"success": True}

    async def _hover(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Hover over element."""
        timeout = command.get("timeout", self.config.get_browser_timeout())
        position = command.get("position")

        # Get element locator
        element = await self._get_element(command, timeout)
        if not element:
            raise BrowserAutomationError("Element not found", command)

        # Hover over element
        hover_options = {"timeout": timeout}
        if position:
            hover_options["position"] = position

        await element.hover(**hover_options)
        return {"success": True}

    async def _wait(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for condition."""
        timeout = command.get("timeout", self.config.get_browser_timeout())

        # Wait for time
        if "for" in command:
            wait_time = command["for"]
            await asyncio.sleep(wait_time / 1000)  # Convert to seconds
            return {"success": True}

        # Wait for element
        element = await self._get_element(command, timeout)
        if not element:
            raise BrowserAutomationError("Element not found", command)

        # Wait for element state
        state = command.get("state")
        if state:
            if state == "visible":
                await element.wait_for(state="visible", timeout=timeout)
            elif state == "hidden":
                await element.wait_for(state="hidden", timeout=timeout)
            elif state == "enabled":
                await element.wait_for(state="enabled", timeout=timeout)
            elif state == "disabled":
                await element.wait_for(state="disabled", timeout=timeout)

        return {"success": True}

    async def _screenshot(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Take screenshot."""
        path = command.get("path")
        format_type = command.get("format", "png")
        quality = command.get("quality", 100)
        full_page = command.get("full_page", False)
        timeout = command.get("timeout", self.config.get_browser_timeout())

        # Get element if specified
        element = None
        if "selector" in command or "xpath" in command or "text" in command:
            element = await self._get_element(command, timeout)
            if not element:
                raise BrowserAutomationError("Element not found", command)

        # Prepare screenshot options
        screenshot_options = {
            "type": format_type,
            "quality": quality if format_type == "jpeg" else None,
            "full_page": full_page if not element else False
        }

        # Take screenshot
        if element:
            screenshot = await element.screenshot(**screenshot_options)
        else:
            screenshot = await self.current_page.screenshot(**screenshot_options)

        # Save screenshot if path specified
        if path:
            # Ensure directory exists
            path_obj = Path(path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(screenshot)
            return {"success": True, "path": path}
        else:
            # Return screenshot as base64
            import base64
            screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
            return {"success": True, "screenshot": screenshot_base64}

    async def _execute_script(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Execute JavaScript."""
        script = command["script"]
        args = command.get("args", [])

        result = await self.current_page.evaluate(script, *args)
        return {"success": True, "result": result}

    async def _get_text(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Get element text."""
        timeout = command.get("timeout", self.config.get_browser_timeout())

        # Get element locator
        element = await self._get_element(command, timeout)
        if not element:
            raise BrowserAutomationError("Element not found", command)

        text = await element.text_content()
        return {"success": True, "text": text}

    async def _get_attribute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Get element attribute."""
        attribute = command["attribute"]
        timeout = command.get("timeout", self.config.get_browser_timeout())

        # Get element locator
        element = await self._get_element(command, timeout)
        if not element:
            raise BrowserAutomationError("Element not found", command)

        value = await element.get_attribute(attribute)
        return {"success": True, "value": value}

    async def _back(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate back."""
        wait_until = command.get("wait_until", "load")
        await self.current_page.go_back(wait_until=wait_until)
        return {"success": True}

    async def _forward(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate forward."""
        wait_until = command.get("wait_until", "load")
        await self.current_page.go_forward(wait_until=wait_until)
        return {"success": True}

    async def _refresh(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh page."""
        wait_until = command.get("wait_until", "load")
        await self.current_page.reload(wait_until=wait_until)
        return {"success": True}

    async def _get_cookies(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Get cookies."""
        urls = command.get("urls")
        names = command.get("names")

        cookies = await self.context.cookies(urls)

        # Filter by names if specified
        if names:
            cookies = [cookie for cookie in cookies if cookie.get("name") in names]

        return {"success": True, "cookies": cookies}

    async def _set_cookie(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Set cookie."""
        name = command["name"]
        value = command["value"]
        url = command.get("url")
        domain = command.get("domain")
        path = command.get("path")
        expires = command.get("expires")
        http_only = command.get("http_only", False)
        secure = command.get("secure", False)
        same_site = command.get("same_site")

        cookie = {
            "name": name,
            "value": value,
            "url": url,
            "domain": domain,
            "path": path,
            "expires": expires,
            "httpOnly": http_only,
            "secure": secure,
            "sameSite": same_site
        }

        # Remove None values
        cookie = {k: v for k, v in cookie.items() if v is not None}

        await self.context.add_cookies([cookie])
        return {"success": True}

    async def _delete_cookies(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Delete cookies."""
        urls = command.get("urls")
        names = command.get("names")

        await self.context.clear_cookies(urls, names)
        return {"success": True}

    async def _new_tab(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Create new tab."""
        url = command.get("url")

        # Create new page
        page = await self.context.new_page()
        self.pages.append(page)
        self.current_page_index = len(self.pages) - 1

        # Navigate to URL if specified
        if url:
            await page.goto(url)

        return {"success": True, "index": self.current_page_index}

    async def _switch_tab(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Switch to tab."""
        if "index" in command:
            index = command["index"]
            if index < 0 or index >= len(self.pages):
                raise BrowserAutomationError(f"Invalid tab index: {index}", command)
            self.current_page_index = index
        elif "url" in command:
            url = command["url"]
            for i, page in enumerate(self.pages):
                if page.url == url:
                    self.current_page_index = i
                    break
            else:
                raise BrowserAutomationError(f"No tab found with URL: {url}", command)
        elif "title" in command:
            title = command["title"]
            for i, page in enumerate(self.pages):
                if await page.title() == title:
                    self.current_page_index = i
                    break
            else:
                raise BrowserAutomationError(f"No tab found with title: {title}", command)

        return {"success": True, "index": self.current_page_index}

    async def _close_tab(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Close tab."""
        index = command.get("index", self.current_page_index)
        if index < 0 or index >= len(self.pages):
            raise BrowserAutomationError(f"Invalid tab index: {index}", command)

        # Close page
        await self.pages[index].close()

        # Remove from list
        self.pages.pop(index)

        # Update current page index
        if self.current_page_index >= len(self.pages):
            self.current_page_index = len(self.pages) - 1

        return {"success": True}

    async def _get_tabs(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of tabs."""
        tabs = []
        for i, page in enumerate(self.pages):
            tabs.append({
                "index": i,
                "url": page.url,
                "title": await page.title(),
                "current": i == self.current_page_index
            })

        return {"success": True, "tabs": tabs}

    async def _get_element(self, command: Dict[str, Any], timeout: int):
        """Get element locator."""
        if "selector" in command:
            return await self.current_page.wait_for_selector(command["selector"], timeout=timeout)
        elif "xpath" in command:
            return await self.current_page.wait_for_selector(f"xpath={command['xpath']}", timeout=timeout)
        elif "text" in command:
            return await self.current_page.wait_for_selector(f"text={command['text']}", timeout=timeout)
        else:
            raise BrowserAutomationError("No element selector specified", command)

    async def _take_error_screenshot(self) -> str:
        """Take screenshot for error reporting."""
        # Generate timestamp for filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Get temp directory based on platform
        system = platform.system().lower()
        if system == "windows":
            temp_dir = self.config.get_windows_temp_dir() or tempfile.gettempdir()
        else:
            temp_dir = self.config.get_linux_temp_dir() or tempfile.gettempdir()
        
        # Create filename
        filename = f"error_{timestamp}.png"
        screenshot_path = os.path.join(temp_dir, filename)
        
        # Take screenshot
        await self.current_page.screenshot(path=screenshot_path)
        
        return screenshot_path

    async def __aenter__(self):
        """Enter context manager."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        await self.stop()
