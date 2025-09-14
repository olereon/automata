"""
Element selection strategies with fallback mechanisms.
"""

import asyncio
from typing import List, Optional, Union, Dict, Any
from playwright.async_api import Page, ElementHandle, Locator
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)


class SelectorStrategy:
    """Base class for element selection strategies."""

    async def find_element(self, page: Page, selector: str, **kwargs) -> Optional[ElementHandle]:
        """
        Find an element on the page.

        Args:
            page: The Playwright Page object
            selector: The selector string
            **kwargs: Additional arguments

        Returns:
            ElementHandle if found, None otherwise
        """
        raise NotImplementedError

    async def find_elements(self, page: Page, selector: str, **kwargs) -> List[ElementHandle]:
        """
        Find all elements matching the selector on the page.

        Args:
            page: The Playwright Page object
            selector: The selector string
            **kwargs: Additional arguments

        Returns:
            List of ElementHandle objects
        """
        raise NotImplementedError


class CSSSelectorStrategy(SelectorStrategy):
    """CSS selector strategy."""

    async def find_element(self, page: Page, selector: str, **kwargs) -> Optional[ElementHandle]:
        try:
            return await page.query_selector(selector)
        except Exception as e:
            logger.debug(f"CSS selector failed: {e}")
            return None

    async def find_elements(self, page: Page, selector: str, **kwargs) -> List[ElementHandle]:
        try:
            return await page.query_selector_all(selector)
        except Exception as e:
            logger.debug(f"CSS selector all failed: {e}")
            return []


class XPathSelectorStrategy(SelectorStrategy):
    """XPath selector strategy."""

    async def find_element(self, page: Page, selector: str, **kwargs) -> Optional[ElementHandle]:
        try:
            return await page.query_selector(f"xpath={selector}")
        except Exception as e:
            logger.debug(f"XPath selector failed: {e}")
            return None

    async def find_elements(self, page: Page, selector: str, **kwargs) -> List[ElementHandle]:
        try:
            return await page.query_selector_all(f"xpath={selector}")
        except Exception as e:
            logger.debug(f"XPath selector all failed: {e}")
            return []


class TextSelectorStrategy(SelectorStrategy):
    """Text-based selector strategy."""

    async def find_element(self, page: Page, selector: str, **kwargs) -> Optional[ElementHandle]:
        try:
            # Try to find element by exact text
            locator = page.get_by_text(selector, exact=True)
            if await locator.count() > 0:
                return await locator.first.element_handle()
            
            # Try to find element by partial text
            locator = page.get_by_text(selector, exact=False)
            if await locator.count() > 0:
                return await locator.first.element_handle()
                
            return None
        except Exception as e:
            logger.debug(f"Text selector failed: {e}")
            return None

    async def find_elements(self, page: Page, selector: str, **kwargs) -> List[ElementHandle]:
        try:
            # Find elements by exact text
            locator = page.get_by_text(selector, exact=True)
            elements = []
            
            for i in range(await locator.count()):
                elements.append(await locator.nth(i).element_handle())
            
            if elements:
                return elements
                
            # Find elements by partial text
            locator = page.get_by_text(selector, exact=False)
            elements = []
            
            for i in range(await locator.count()):
                elements.append(await locator.nth(i).element_handle())
                
            return elements
        except Exception as e:
            logger.debug(f"Text selector all failed: {e}")
            return []


class AttributeSelectorStrategy(SelectorStrategy):
    """Attribute-based selector strategy."""

    async def find_element(self, page: Page, selector: str, **kwargs) -> Optional[ElementHandle]:
        try:
            # Parse selector as attribute=value
            if "=" in selector:
                attr, value = selector.split("=", 1)
                # Try different attribute selectors
                css_selectors = [
                    f"[{attr}='{value}']",
                    f"[{attr}=\"{value}\"]",
                    f"[{attr}*='{value}']",  # contains
                ]
                
                for css_selector in css_selectors:
                    element = await page.query_selector(css_selector)
                    if element:
                        return element
            return None
        except Exception as e:
            logger.debug(f"Attribute selector failed: {e}")
            return None

    async def find_elements(self, page: Page, selector: str, **kwargs) -> List[ElementHandle]:
        try:
            # Parse selector as attribute=value
            if "=" in selector:
                attr, value = selector.split("=", 1)
                # Try different attribute selectors
                css_selectors = [
                    f"[{attr}='{value}']",
                    f"[{attr}=\"{value}\"]",
                    f"[{attr}*='{value}']",  # contains
                ]
                
                for css_selector in css_selectors:
                    elements = await page.query_selector_all(css_selector)
                    if elements:
                        return elements
            return []
        except Exception as e:
            logger.debug(f"Attribute selector all failed: {e}")
            return []


class ElementSelector:
    """Main element selector with fallback mechanisms."""

    def __init__(self):
        """Initialize the element selector with default strategies."""
        self.strategies = [
            CSSSelectorStrategy(),
            XPathSelectorStrategy(),
            TextSelectorStrategy(),
            AttributeSelectorStrategy(),
        ]

    def add_strategy(self, strategy: SelectorStrategy) -> None:
        """
        Add a custom selection strategy.

        Args:
            strategy: The selection strategy to add
        """
        self.strategies.insert(0, strategy)  # Insert at beginning for priority

    async def find_element(
        self,
        page: Page,
        selector: str,
        timeout: int = 5000,
        use_fallbacks: bool = True,
        **kwargs
    ) -> Optional[ElementHandle]:
        """
        Find an element using multiple strategies with fallback.

        Args:
            page: The Playwright Page object
            selector: The selector string
            timeout: Timeout in milliseconds
            use_fallbacks: Whether to use fallback strategies
            **kwargs: Additional arguments

        Returns:
            ElementHandle if found, None otherwise
        """
        # Try each strategy in order
        for strategy in self.strategies:
            try:
                element = await strategy.find_element(page, selector, **kwargs)
                if element:
                    logger.debug(f"Found element using {strategy.__class__.__name__}")
                    return element
                
                if not use_fallbacks:
                    break
            except Exception as e:
                logger.warning(f"Strategy {strategy.__class__.__name__} failed: {e}")
                if not use_fallbacks:
                    break

        logger.debug(f"Element not found with selector: {selector}")
        return None

    async def find_elements(
        self,
        page: Page,
        selector: str,
        timeout: int = 5000,
        use_fallbacks: bool = True,
        **kwargs
    ) -> List[ElementHandle]:
        """
        Find all elements using multiple strategies with fallback.

        Args:
            page: The Playwright Page object
            selector: The selector string
            timeout: Timeout in milliseconds
            use_fallbacks: Whether to use fallback strategies
            **kwargs: Additional arguments

        Returns:
            List of ElementHandle objects
        """
        # Try each strategy in order
        for strategy in self.strategies:
            try:
                elements = await strategy.find_elements(page, selector, **kwargs)
                if elements:
                    logger.debug(f"Found {len(elements)} elements using {strategy.__class__.__name__}")
                    return elements
                
                if not use_fallbacks:
                    break
            except Exception as e:
                logger.warning(f"Strategy {strategy.__class__.__name__} failed: {e}")
                if not use_fallbacks:
                    break

        logger.debug(f"No elements found with selector: {selector}")
        return []

    async def wait_for_element(
        self,
        page: Page,
        selector: str,
        timeout: int = 30000,
        use_fallbacks: bool = True,
        **kwargs
    ) -> Optional[ElementHandle]:
        """
        Wait for an element to be available.

        Args:
            page: The Playwright Page object
            selector: The selector string
            timeout: Timeout in milliseconds
            use_fallbacks: Whether to use fallback strategies
            **kwargs: Additional arguments

        Returns:
            ElementHandle if found, None otherwise
        """
        start_time = asyncio.get_event_loop().time()
        remaining_timeout = timeout
        
        while remaining_timeout > 0:
            element = await self.find_element(
                page, selector, timeout=min(1000, remaining_timeout), 
                use_fallbacks=use_fallbacks, **kwargs
            )
            if element:
                return element
            
            # Wait a bit before retrying
            await asyncio.sleep(0.5)
            elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
            remaining_timeout = timeout - elapsed

        logger.debug(f"Element not found within timeout: {selector}")
        return None

    async def is_element_visible(self, page: Page, selector: str, **kwargs) -> bool:
        """
        Check if an element is visible.

        Args:
            page: The Playwright Page object
            selector: The selector string
            **kwargs: Additional arguments

        Returns:
            True if element is visible, False otherwise
        """
        element = await self.find_element(page, selector, **kwargs)
        if not element:
            return False
        
        try:
            return await element.is_visible()
        except Exception:
            return False

    async def get_element_text(self, page: Page, selector: str, **kwargs) -> Optional[str]:
        """
        Get the text content of an element.

        Args:
            page: The Playwright Page object
            selector: The selector string
            **kwargs: Additional arguments

        Returns:
            Text content if found, None otherwise
        """
        element = await self.find_element(page, selector, **kwargs)
        if not element:
            return None
        
        try:
            return await element.text_content()
        except Exception:
            return None
