"""
Wait and timing utilities for handling dynamic content.
"""

import asyncio
import time
from typing import Callable, Optional, Any, Union, Dict, List
from playwright.async_api import Page, ElementHandle, Frame, Locator
import logging

logger = logging.getLogger(__name__)


class WaitUtils:
    """Utilities for waiting and handling dynamic content."""

    def __init__(self, default_timeout: int = 30000):
        """
        Initialize wait utilities.

        Args:
            default_timeout: Default timeout in milliseconds
        """
        self.default_timeout = default_timeout

    async def sleep(self, milliseconds: int) -> None:
        """
        Sleep for a specified number of milliseconds.

        Args:
            milliseconds: Number of milliseconds to sleep
        """
        await asyncio.sleep(milliseconds / 1000)

    async def wait_for_function(
        self,
        page: Page,
        js_function: str,
        *args,
        timeout: Optional[int] = None,
        polling: Union[int, str] = "raf"
    ) -> Any:
        """
        Wait for a JavaScript function to return a truthy value.

        Args:
            page: The Playwright Page object
            js_function: JavaScript function to execute
            *args: Arguments to pass to the function
            timeout: Timeout in milliseconds
            polling: Polling interval in milliseconds or 'raf'

        Returns:
            The result of the function call
        """
        timeout = timeout or self.default_timeout
        return await page.wait_for_function(js_function, *args, timeout=timeout, polling=polling)

    async def wait_for_load_state(
        self,
        page: Page,
        state: str = "load",
        timeout: Optional[int] = None
    ) -> None:
        """
        Wait for a specific load state.

        Args:
            page: The Playwright Page object
            state: Load state to wait for ('load', 'domcontentloaded', 'networkidle')
            timeout: Timeout in milliseconds
        """
        timeout = timeout or self.default_timeout
        await page.wait_for_load_state(state, timeout=timeout)

    async def wait_for_url(
        self,
        page: Page,
        url: str,
        timeout: Optional[int] = None,
        wait_until: str = "load"
    ) -> None:
        """
        Wait for the page to navigate to a specific URL.

        Args:
            page: The Playwright Page object
            url: URL to wait for
            timeout: Timeout in milliseconds
            wait_until: When to consider navigation succeeded
        """
        timeout = timeout or self.default_timeout
        await page.wait_for_url(url, timeout=timeout, wait_until=wait_until)

    async def wait_for_selector(
        self,
        page: Page,
        selector: str,
        timeout: Optional[int] = None,
        state: str = "attached"
    ) -> Optional[ElementHandle]:
        """
        Wait for an element matching the selector to appear.

        Args:
            page: The Playwright Page object
            selector: CSS selector to wait for
            timeout: Timeout in milliseconds
            state: Element state to wait for ('attached', 'detached', 'visible', 'hidden')

        Returns:
            ElementHandle if found, None otherwise
        """
        timeout = timeout or self.default_timeout
        try:
            return await page.wait_for_selector(selector, timeout=timeout, state=state)
        except Exception as e:
            logger.debug(f"Wait for selector failed: {e}")
            return None

    async def wait_for_hidden(
        self,
        page: Page,
        selector: str,
        timeout: Optional[int] = None
    ) -> None:
        """
        Wait for an element to become hidden.

        Args:
            page: The Playwright Page object
            selector: CSS selector to wait for
            timeout: Timeout in milliseconds
        """
        timeout = timeout or self.default_timeout
        await page.wait_for_selector(selector, timeout=timeout, state="hidden")

    async def wait_for_navigation(
        self,
        page: Page,
        timeout: Optional[int] = None,
        wait_until: str = "load",
        url: Optional[str] = None
    ) -> None:
        """
        Wait for navigation to complete.

        Args:
            page: The Playwright Page object
            timeout: Timeout in milliseconds
            wait_until: When to consider navigation succeeded
            url: URL to wait for
        """
        timeout = timeout or self.default_timeout
        
        if url:
            await page.wait_for_url(url, timeout=timeout, wait_until=wait_until)
        else:
            await page.wait_for_load_state(wait_until, timeout=timeout)

    async def wait_for_frame(
        self,
        page: Page,
        frame_selector: str,
        timeout: Optional[int] = None
    ) -> Optional[Frame]:
        """
        Wait for a frame to be available.

        Args:
            page: The Playwright Page object
            frame_selector: Frame selector (name or URL)
            timeout: Timeout in milliseconds

        Returns:
            Frame if found, None otherwise
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            frame = page.frame(frame_selector)
            if frame:
                return frame
            await self.sleep(100)
        
        return None

    async def wait_for_event(
        self,
        page: Page,
        event: str,
        timeout: Optional[int] = None,
        predicate: Optional[Callable] = None
    ) -> Any:
        """
        Wait for a specific event to occur.

        Args:
            page: The Playwright Page object
            event: Event name to wait for
            timeout: Timeout in milliseconds
            predicate: Function to filter events

        Returns:
            Event data
        """
        timeout = timeout or self.default_timeout
        return await page.wait_for_event(event, timeout=timeout, predicate=predicate)

    async def wait_for_response(
        self,
        page: Page,
        url_or_predicate: Union[str, Callable],
        timeout: Optional[int] = None
    ) -> Any:
        """
        Wait for a network response.

        Args:
            page: The Playwright Page object
            url_or_predicate: URL or predicate function to match response
            timeout: Timeout in milliseconds

        Returns:
            Response object
        """
        timeout = timeout or self.default_timeout
        return await page.wait_for_response(url_or_predicate, timeout=timeout)

    async def wait_for_request(
        self,
        page: Page,
        url_or_predicate: Union[str, Callable],
        timeout: Optional[int] = None
    ) -> Any:
        """
        Wait for a network request.

        Args:
            page: The Playwright Page object
            url_or_predicate: URL or predicate function to match request
            timeout: Timeout in milliseconds

        Returns:
            Request object
        """
        timeout = timeout or self.default_timeout
        return await page.wait_for_request(url_or_predicate, timeout=timeout)

    async def wait_for_element_count(
        self,
        page: Page,
        selector: str,
        count: int,
        timeout: Optional[int] = None,
        operator: str = "=="  # ==, >, <, >=, <=
    ) -> bool:
        """
        Wait for the number of elements matching a selector to reach a specific count.

        Args:
            page: The Playwright Page object
            selector: CSS selector
            count: Expected count
            timeout: Timeout in milliseconds
            operator: Comparison operator

        Returns:
            True if condition met, False otherwise
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            elements = await page.query_selector_all(selector)
            actual_count = len(elements)
            
            if operator == "==" and actual_count == count:
                return True
            elif operator == ">" and actual_count > count:
                return True
            elif operator == "<" and actual_count < count:
                return True
            elif operator == ">=" and actual_count >= count:
                return True
            elif operator == "<=" and actual_count <= count:
                return True
            
            await self.sleep(100)
        
        return False

    async def wait_for_text(
        self,
        page: Page,
        selector: str,
        text: str,
        timeout: Optional[int] = None,
        exact: bool = True
    ) -> bool:
        """
        Wait for an element to contain specific text.

        Args:
            page: The Playwright Page object
            selector: CSS selector
            text: Text to wait for
            timeout: Timeout in milliseconds
            exact: Whether to match exact text

        Returns:
            True if text found, False otherwise
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            element = await page.query_selector(selector)
            if element:
                element_text = await element.text_content() or ""
                if exact and element_text == text:
                    return True
                elif not exact and text in element_text:
                    return True
            
            await self.sleep(100)
        
        return False

    async def wait_for_attribute(
        self,
        page: Page,
        selector: str,
        attribute: str,
        value: str,
        timeout: Optional[int] = None,
        exact: bool = True
    ) -> bool:
        """
        Wait for an element to have a specific attribute value.

        Args:
            page: The Playwright Page object
            selector: CSS selector
            attribute: Attribute name
            value: Attribute value to wait for
            timeout: Timeout in milliseconds
            exact: Whether to match exact value

        Returns:
            True if attribute value found, False otherwise
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            element = await page.query_selector(selector)
            if element:
                attr_value = await element.get_attribute(attribute) or ""
                if exact and attr_value == value:
                    return True
                elif not exact and value in attr_value:
                    return True
            
            await self.sleep(100)
        
        return False

    async def wait_for_class(
        self,
        page: Page,
        selector: str,
        class_name: str,
        timeout: Optional[int] = None,
        present: bool = True
    ) -> bool:
        """
        Wait for an element to have or not have a specific class.

        Args:
            page: The Playwright Page object
            selector: CSS selector
            class_name: Class name to wait for
            timeout: Timeout in milliseconds
            present: Whether to wait for class to be present or absent

        Returns:
            True if condition met, False otherwise
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            element = await page.query_selector(selector)
            if element:
                classes = (await element.get_attribute("class") or "").split()
                has_class = class_name in classes
                
                if present and has_class:
                    return True
                elif not present and not has_class:
                    return True
            
            await self.sleep(100)
        
        return False

    async def retry_until_success(
        self,
        func: Callable,
        timeout: Optional[int] = None,
        interval: int = 1000,
        exceptions: tuple = (Exception,)
    ) -> Any:
        """
        Retry a function until it succeeds or times out.

        Args:
            func: Function to retry
            timeout: Timeout in milliseconds
            interval: Retry interval in milliseconds
            exceptions: Exceptions to catch and retry on

        Returns:
            Result of the function call

        Raises:
            The last exception if all retries fail
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        last_exception = None
        
        while (time.time() - start_time) * 1000 < timeout:
            try:
                result = await func()
                return result
            except exceptions as e:
                last_exception = e
                await self.sleep(interval)
        
        if last_exception:
            raise last_exception
        else:
            raise TimeoutError("Retry operation timed out")

    async def wait_for_any(
        self,
        page: Page,
        selectors: List[str],
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, ElementHandle]]:
        """
        Wait for any of the selectors to be available.

        Args:
            page: The Playwright Page object
            selectors: List of CSS selectors
            timeout: Timeout in milliseconds

        Returns:
            Dictionary with found selector and element, or None
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            for selector in selectors:
                element = await page.query_selector(selector)
                if element:
                    return {"selector": selector, "element": element}
            
            await self.sleep(100)
        
        return None

    async def wait_for_all(
        self,
        page: Page,
        selectors: List[str],
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, ElementHandle]]:
        """
        Wait for all selectors to be available.

        Args:
            page: The Playwright Page object
            selectors: List of CSS selectors
            timeout: Timeout in milliseconds

        Returns:
            Dictionary with selectors and elements, or None
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            result = {}
            all_found = True
            
            for selector in selectors:
                element = await page.query_selector(selector)
                if element:
                    result[selector] = element
                else:
                    all_found = False
                    break
            
            if all_found:
                return result
            
            await self.sleep(100)
        
        return None
