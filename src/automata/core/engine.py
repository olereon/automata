"""
Core automation engine with Playwright integration.
"""

import asyncio
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
    """Main automation engine that integrates all components."""

    def __init__(
        self,
        headless: bool = True,
        viewport: Optional[Dict[str, int]] = None,
        default_timeout: int = 30000,
        screenshot_on_error: bool = True,
        retry_attempts: int = 3,
        retry_delay: int = 1000
    ):
        """
        Initialize the automation engine.

        Args:
            headless: Whether to run browser in headless mode
            viewport: Viewport size as dict with width and height
            default_timeout: Default timeout in milliseconds
            screenshot_on_error: Whether to take screenshots on errors
            retry_attempts: Number of retry attempts for failed operations
            retry_delay: Delay between retries in milliseconds
        """
        self.browser_manager = BrowserManager(headless=headless, viewport=viewport)
        self.element_selector = ElementSelector()
        self.wait_utils = WaitUtils(default_timeout=default_timeout)
        self.error_handler = ErrorHandler(max_retries=retry_attempts, retry_delay=retry_delay)
        
        self.default_timeout = default_timeout
        self.screenshot_on_error = screenshot_on_error
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        self.is_running = False
        self.current_page: Optional[Page] = None
        self.session_data: Dict[str, Any] = {}

    async def start(self) -> None:
        """Start the automation engine."""
        if self.is_running:
            logger.warning("Automation engine is already running")
            return
        
        logger.info("Starting automation engine...")
        
        try:
            # Start browser manager
            await self.browser_manager.start()
            self.is_running = True
            
            logger.info("Automation engine started successfully")
        except Exception as e:
            logger.error(f"Failed to start automation engine: {e}")
            raise AutomationError(f"Failed to start automation engine: {e}")

    async def stop(self) -> None:
        """Stop the automation engine."""
        if not self.is_running:
            logger.warning("Automation engine is not running")
            return
        
        logger.info("Stopping automation engine...")
        
        try:
            # Stop browser manager
            await self.browser_manager.stop()
            self.is_running = False
            self.current_page = None
            
            logger.info("Automation engine stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop automation engine: {e}")
            raise AutomationError(f"Failed to stop automation engine: {e}")

    async def new_page(self, url: Optional[str] = None) -> Page:
        """
        Create a new page and optionally navigate to a URL.

        Args:
            url: URL to navigate to after creating the page

        Returns:
            The new Page object
        """
        if not self.is_running:
            raise AutomationError("Automation engine is not running")
        
        try:
            self.current_page = await self.browser_manager.new_page(url)
            
            # Set up page event listeners
            await self._setup_page_listeners(self.current_page)
            
            logger.info(f"New page created: {url or 'about:blank'}")
            return self.current_page
        except Exception as e:
            logger.error(f"Failed to create new page: {e}")
            raise AutomationError(f"Failed to create new page: {e}")

    async def get_current_page(self) -> Page:
        """
        Get the current active page.

        Returns:
            The current Page object

        Raises:
            AutomationError: If no page is active
        """
        if not self.current_page:
            raise AutomationError("No active page")
        return self.current_page

    async def _setup_page_listeners(self, page: Page) -> None:
        """
        Set up event listeners for a page.

        Args:
            page: The Playwright Page object
        """
        # Log page errors
        page.on("pageerror", lambda error: logger.error(f"Page error: {error}"))
        
        # Log console messages
        page.on("console", lambda msg: logger.debug(f"Console {msg.type}: {msg.text}"))
        
        # Log requests
        page.on("request", lambda request: logger.debug(f"Request: {request.url}"))
        
        # Log responses
        page.on("response", lambda response: logger.debug(f"Response: {response.url} ({response.status})"))

    @with_error_handling()
    async def navigate_to(self, url: str, wait_until: str = "load") -> None:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to
            wait_until: When to consider navigation succeeded
        """
        page = await self.get_current_page()
        
        logger.info(f"Navigating to: {url}")
        
        try:
            await page.goto(url, wait_until=wait_until, timeout=self.default_timeout)
            logger.info(f"Successfully navigated to: {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            raise AutomationError(f"Failed to navigate to {url}: {e}")

    @with_error_handling()
    async def click(self, selector: str, timeout: Optional[int] = None, **kwargs) -> None:
        """
        Click on an element.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
            **kwargs: Additional arguments for click
        """
        page = await self.get_current_page()
        timeout = timeout or self.default_timeout
        
        logger.debug(f"Clicking on element: {selector}")
        
        try:
            # Find element with fallback strategies
            element = await self.element_selector.wait_for_element(
                page, selector, timeout=timeout
            )
            
            if not element:
                raise AutomationError(f"Element not found: {selector}")
            
            # Click the element
            await element.click(**kwargs)
            logger.debug(f"Successfully clicked on element: {selector}")
        except Exception as e:
            logger.error(f"Failed to click on element {selector}: {e}")
            raise AutomationError(f"Failed to click on element {selector}: {e}")

    @with_error_handling()
    async def fill(self, selector: str, value: str, timeout: Optional[int] = None, **kwargs) -> None:
        """
        Fill a form field with a value.

        Args:
            selector: Element selector
            value: Value to fill
            timeout: Timeout in milliseconds
            **kwargs: Additional arguments for fill
        """
        page = await self.get_current_page()
        timeout = timeout or self.default_timeout
        
        logger.debug(f"Filling element {selector} with value: {value}")
        
        try:
            # Find element with fallback strategies
            element = await self.element_selector.wait_for_element(
                page, selector, timeout=timeout
            )
            
            if not element:
                raise AutomationError(f"Element not found: {selector}")
            
            # Fill the element
            await element.fill(value, **kwargs)
            logger.debug(f"Successfully filled element {selector}")
        except Exception as e:
            logger.error(f"Failed to fill element {selector}: {e}")
            raise AutomationError(f"Failed to fill element {selector}: {e}")

    @with_error_handling()
    async def get_text(self, selector: str, timeout: Optional[int] = None) -> str:
        """
        Get the text content of an element.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds

        Returns:
            Text content of the element
        """
        page = await self.get_current_page()
        timeout = timeout or self.default_timeout
        
        logger.debug(f"Getting text from element: {selector}")
        
        try:
            # Find element with fallback strategies
            element = await self.element_selector.wait_for_element(
                page, selector, timeout=timeout
            )
            
            if not element:
                raise AutomationError(f"Element not found: {selector}")
            
            # Get text content
            text = await element.text_content() or ""
            logger.debug(f"Got text from element {selector}: {text[:100]}...")
            return text
        except Exception as e:
            logger.error(f"Failed to get text from element {selector}: {e}")
            raise AutomationError(f"Failed to get text from element {selector}: {e}")

    @with_error_handling()
    async def get_attribute(self, selector: str, attribute: str, timeout: Optional[int] = None) -> Optional[str]:
        """
        Get an attribute value from an element.

        Args:
            selector: Element selector
            attribute: Attribute name
            timeout: Timeout in milliseconds

        Returns:
            Attribute value or None if not found
        """
        page = await self.get_current_page()
        timeout = timeout or self.default_timeout
        
        logger.debug(f"Getting attribute {attribute} from element: {selector}")
        
        try:
            # Find element with fallback strategies
            element = await self.element_selector.wait_for_element(
                page, selector, timeout=timeout
            )
            
            if not element:
                raise AutomationError(f"Element not found: {selector}")
            
            # Get attribute value
            value = await element.get_attribute(attribute)
            logger.debug(f"Got attribute {attribute} from element {selector}: {value}")
            return value
        except Exception as e:
            logger.error(f"Failed to get attribute {attribute} from element {selector}: {e}")
            raise AutomationError(f"Failed to get attribute {attribute} from element {selector}: {e}")

    @with_error_handling()
    async def wait_for_element(self, selector: str, timeout: Optional[int] = None, **kwargs) -> bool:
        """
        Wait for an element to be available.

        Args:
            selector: Element selector
            timeout: Timeout in milliseconds
            **kwargs: Additional arguments

        Returns:
            True if element is found, False otherwise
        """
        page = await self.get_current_page()
        timeout = timeout or self.default_timeout
        
        logger.debug(f"Waiting for element: {selector}")
        
        try:
            element = await self.element_selector.wait_for_element(
                page, selector, timeout=timeout, **kwargs
            )
            result = element is not None
            logger.debug(f"Element {selector} found: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to wait for element {selector}: {e}")
            raise AutomationError(f"Failed to wait for element {selector}: {e}")

    @with_error_handling()
    async def wait_for_navigation(self, timeout: Optional[int] = None, **kwargs) -> None:
        """
        Wait for navigation to complete.

        Args:
            timeout: Timeout in milliseconds
            **kwargs: Additional arguments
        """
        page = await self.get_current_page()
        timeout = timeout or self.default_timeout
        
        logger.debug("Waiting for navigation")
        
        try:
            await self.wait_utils.wait_for_navigation(page, timeout=timeout, **kwargs)
            logger.debug("Navigation completed")
        except Exception as e:
            logger.error(f"Failed to wait for navigation: {e}")
            raise AutomationError(f"Failed to wait for navigation: {e}")

    @with_error_handling()
    async def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript on the page.

        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script

        Returns:
            Result of the script execution
        """
        page = await self.get_current_page()
        
        logger.debug(f"Executing script: {script[:100]}...")
        
        try:
            result = await page.evaluate(script, *args)
            logger.debug(f"Script execution result: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute script: {e}")
            raise AutomationError(f"Failed to execute script: {e}")

    @with_error_handling()
    async def take_screenshot(self, name: Optional[str] = None) -> str:
        """
        Take a screenshot of the current page.

        Args:
            name: Screenshot name (auto-generated if not provided)

        Returns:
            Path to the screenshot file
        """
        page = await self.get_current_page()
        
        logger.debug("Taking screenshot")
        
        try:
            # Use logger to take screenshot
            screenshot_path = logger.log_screenshot(page, name)
            logger.debug(f"Screenshot taken: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            raise AutomationError(f"Failed to take screenshot: {e}")

    async def save_session(self, path: str) -> None:
        """
        Save the current session data to a file.

        Args:
            path: Path to save the session data
        """
        try:
            # Save cookies
            await self.browser_manager.save_cookies(f"{path}.cookies")
            
            # Save session data
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.session_data, f, indent=2, default=str)
            
            logger.info(f"Session saved to: {path}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            raise AutomationError(f"Failed to save session: {e}")

    async def load_session(self, path: str) -> None:
        """
        Load session data from a file.

        Args:
            path: Path to load the session data from
        """
        try:
            # Load cookies
            await self.browser_manager.load_cookies(f"{path}.cookies")
            
            # Load session data
            with open(path, "r", encoding="utf-8") as f:
                self.session_data = json.load(f)
            
            logger.info(f"Session loaded from: {path}")
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            raise AutomationError(f"Failed to load session: {e}")

    async def set_session_data(self, key: str, value: Any) -> None:
        """
        Set a session data value.

        Args:
            key: Data key
            value: Data value
        """
        self.session_data[key] = value
        logger.debug(f"Session data set: {key} = {value}")

    async def get_session_data(self, key: str, default: Any = None) -> Any:
        """
        Get a session data value.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Data value or default
        """
        value = self.session_data.get(key, default)
        logger.debug(f"Session data retrieved: {key} = {value}")
        return value

    async def run_custom_action(self, action: Callable, *args, **kwargs) -> Any:
        """
        Run a custom action with error handling.

        Args:
            action: Action function to run
            *args: Action arguments
            **kwargs: Action keyword arguments

        Returns:
            Result of the action
        """
        logger.debug(f"Running custom action: {action.__name__}")
        
        try:
            # Run with error handling
            result = await with_error_handling()(action)(*args, **kwargs)
            logger.debug(f"Custom action completed: {action.__name__}")
            return result
        except Exception as e:
            logger.error(f"Custom action failed: {action.__name__}: {e}")
            raise AutomationError(f"Custom action failed: {action.__name__}: {e}")

    async def run_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run a workflow defined as a list of actions.

        Args:
            workflow: List of action dictionaries

        Returns:
            Workflow result
        """
        if not self.is_running:
            raise AutomationError("Automation engine is not running")
        
        logger.info(f"Running workflow with {len(workflow)} actions")
        
        # Start workflow step
        workflow_step = logger.start_step("workflow", f"Running workflow with {len(workflow)} actions")
        
        try:
            results = []
            
            for i, action in enumerate(workflow):
                action_name = action.get("name", f"action_{i}")
                action_type = action.get("type")
                action_params = action.get("params", {})
                
                logger.info(f"Executing action {i+1}/{len(workflow)}: {action_name} ({action_type})")
                
                # Start action step
                action_step = logger.start_step(action_name, f"Type: {action_type}")
                
                try:
                    # Execute action based on type
                    if action_type == "navigate":
                        url = action_params.get("url")
                        wait_until = action_params.get("wait_until", "load")
                        await self.navigate_to(url, wait_until=wait_until)
                        result = {"status": "success"}
                    
                    elif action_type == "click":
                        selector = action_params.get("selector")
                        timeout = action_params.get("timeout")
                        await self.click(selector, timeout=timeout)
                        result = {"status": "success"}
                    
                    elif action_type == "fill":
                        selector = action_params.get("selector")
                        value = action_params.get("value")
                        timeout = action_params.get("timeout")
                        await self.fill(selector, value, timeout=timeout)
                        result = {"status": "success"}
                    
                    elif action_type == "get_text":
                        selector = action_params.get("selector")
                        timeout = action_params.get("timeout")
                        text = await self.get_text(selector, timeout=timeout)
                        result = {"status": "success", "value": text}
                    
                    elif action_type == "wait":
                        selector = action_params.get("selector")
                        timeout = action_params.get("timeout")
                        await self.wait_for_element(selector, timeout=timeout)
                        result = {"status": "success"}
                    
                    elif action_type == "wait_for_navigation":
                        timeout = action_params.get("timeout")
                        await self.wait_for_navigation(timeout=timeout)
                        result = {"status": "success"}
                    
                    elif action_type == "screenshot":
                        name = action_params.get("name")
                        path = await self.take_screenshot(name)
                        result = {"status": "success", "path": path}
                    
                    elif action_type == "execute_script":
                        script = action_params.get("script")
                        script_args = action_params.get("args", [])
                        script_result = await self.execute_script(script, *script_args)
                        result = {"status": "success", "value": script_result}
                    
                    elif action_type == "custom":
                        action_func = action_params.get("function")
                        action_args = action_params.get("args", [])
                        action_kwargs = action_params.get("kwargs", {})
                        custom_result = await self.run_custom_action(action_func, *action_args, **action_kwargs)
                        result = {"status": "success", "value": custom_result}
                    
                    else:
                        raise AutomationError(f"Unknown action type: {action_type}")
                    
                    # End action step with success
                    logger.end_step("completed")
                    results.append({"action": action_name, "result": result})
                
                except Exception as e:
                    # End action step with failure
                    logger.end_step("failed", str(e))
                    results.append({"action": action_name, "result": {"status": "failed", "error": str(e)}})
                    
                    # Take screenshot if enabled
                    if self.screenshot_on_error:
                        try:
                            await self.take_screenshot(f"error_{action_name}")
                        except Exception:
                            pass
                    
                    # Re-raise exception to stop workflow
                    raise
            
            # End workflow step with success
            logger.end_step("completed")
            
            workflow_result = {
                "status": "completed",
                "results": results
            }
            
            logger.info("Workflow completed successfully")
            return workflow_result
        
        except Exception as e:
            # End workflow step with failure
            logger.end_step("failed", str(e))
            
            workflow_result = {
                "status": "failed",
                "error": str(e),
                "results": results
            }
            
            logger.error(f"Workflow failed: {e}")
            return workflow_result
