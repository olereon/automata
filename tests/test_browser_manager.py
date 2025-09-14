"""
Unit tests for the browser manager component.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from playwright.async_api import Browser, BrowserContext, Page
from src.automata.core.browser import BrowserManager
from src.automata.core.errors import AutomationError


@pytest.mark.unit
class TestBrowserManager:
    """Test cases for BrowserManager."""

    def test_init(self):
        """Test BrowserManager initialization."""
        browser_manager = BrowserManager()
        assert browser_manager is not None
        assert browser_manager.browser_config == {
            "headless": True,
            "viewport": {"width": 1280, "height": 720}
        }

    def test_init_with_custom_config(self):
        """Test BrowserManager initialization with custom config."""
        custom_config = {
            "headless": False,
            "viewport": {"width": 1920, "height": 1080}
        }
        browser_manager = BrowserManager(browser_config=custom_config)
        assert browser_manager.browser_config == custom_config

    @pytest.mark.asyncio
    async def test_launch_browser(self):
        """Test browser launching."""
        browser_manager = BrowserManager()
        
        # Mock playwright
        with patch('playwright.async_api.async_playwright') as mock_playwright:
            # Setup mocks
            mock_browser = AsyncMock(spec=Browser)
            mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
            
            # Test
            browser = await browser_manager.launch_browser()
            
            # Verify
            assert browser is mock_browser
            mock_playwright.return_value.__aenter__.return_value.chromium.launch.assert_called_once_with(
                headless=True,
                viewport={"width": 1280, "height": 720}
            )

    @pytest.mark.asyncio
    async def test_launch_browser_with_custom_config(self):
        """Test browser launching with custom config."""
        custom_config = {
            "headless": False,
            "viewport": {"width": 1920, "height": 1080}
        }
        browser_manager = BrowserManager(browser_config=custom_config)
        
        # Mock playwright
        with patch('playwright.async_api.async_playwright') as mock_playwright:
            # Setup mocks
            mock_browser = AsyncMock(spec=Browser)
            mock_playwright.return_value.__aenter__.return_value.chromium.launch.return_value = mock_browser
            
            # Test
            browser = await browser_manager.launch_browser()
            
            # Verify
            assert browser is mock_browser
            mock_playwright.return_value.__aenter__.return_value.chromium.launch.assert_called_once_with(
                headless=False,
                viewport={"width": 1920, "height": 1080}
            )

    @pytest.mark.asyncio
    async def test_create_context(self):
        """Test browser context creation."""
        browser_manager = BrowserManager()
        
        # Mock browser
        mock_browser = AsyncMock(spec=Browser)
        mock_context = AsyncMock(spec=BrowserContext)
        mock_browser.new_context.return_value = mock_context
        
        # Test
        context = await browser_manager.create_context(mock_browser)
        
        # Verify
        assert context is mock_context
        mock_browser.new_context.assert_called_once_with(
            viewport={"width": 1280, "height": 720}
        )

    @pytest.mark.asyncio
    async def test_create_context_with_custom_config(self):
        """Test browser context creation with custom config."""
        custom_config = {
            "headless": False,
            "viewport": {"width": 1920, "height": 1080}
        }
        browser_manager = BrowserManager(browser_config=custom_config)
        
        # Mock browser
        mock_browser = AsyncMock(spec=Browser)
        mock_context = AsyncMock(spec=BrowserContext)
        mock_browser.new_context.return_value = mock_context
        
        # Test
        context = await browser_manager.create_context(mock_browser)
        
        # Verify
        assert context is mock_context
        mock_browser.new_context.assert_called_once_with(
            viewport={"width": 1920, "height": 1080}
        )

    @pytest.mark.asyncio
    async def test_create_page(self):
        """Test page creation."""
        browser_manager = BrowserManager()
        
        # Mock context
        mock_context = AsyncMock(spec=BrowserContext)
        mock_page = AsyncMock(spec=Page)
        mock_context.new_page.return_value = mock_page
        
        # Test
        page = await browser_manager.create_page(mock_context)
        
        # Verify
        assert page is mock_page
        mock_context.new_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_browser(self):
        """Test browser closing."""
        browser_manager = BrowserManager()
        
        # Mock browser
        mock_browser = AsyncMock(spec=Browser)
        
        # Test
        await browser_manager.close_browser(mock_browser)
        
        # Verify
        mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_context(self):
        """Test context closing."""
        browser_manager = BrowserManager()
        
        # Mock context
        mock_context = AsyncMock(spec=BrowserContext)
        
        # Test
        await browser_manager.close_context(mock_context)
        
        # Verify
        mock_context.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_page(self):
        """Test page closing."""
        browser_manager = BrowserManager()
        
        # Mock page
        mock_page = AsyncMock(spec=Page)
        
        # Test
        await browser_manager.close_page(mock_page)
        
        # Verify
        mock_page.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_launch_browser_error(self):
        """Test browser launching error handling."""
        browser_manager = BrowserManager()
        
        # Mock playwright to raise an exception
        with patch('playwright.async_api.async_playwright') as mock_playwright:
            mock_playwright.return_value.__aenter__.return_value.chromium.launch.side_effect = Exception("Launch error")
            
            # Test and verify exception
            with pytest.raises(AutomationError, match="Error launching browser"):
                await browser_manager.launch_browser()

    @pytest.mark.asyncio
    async def test_create_context_error(self):
        """Test context creation error handling."""
        browser_manager = BrowserManager()
        
        # Mock browser to raise an exception
        mock_browser = AsyncMock(spec=Browser)
        mock_browser.new_context.side_effect = Exception("Context error")
            
        # Test and verify exception
        with pytest.raises(AutomationError, match="Error creating browser context"):
            await browser_manager.create_context(mock_browser)

    @pytest.mark.asyncio
    async def test_create_page_error(self):
        """Test page creation error handling."""
        browser_manager = BrowserManager()
        
        # Mock context to raise an exception
        mock_context = AsyncMock(spec=BrowserContext)
        mock_context.new_page.side_effect = Exception("Page error")
            
        # Test and verify exception
        with pytest.raises(AutomationError, match="Error creating page"):
            await browser_manager.create_page(mock_context)
