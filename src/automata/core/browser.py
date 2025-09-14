"""
Browser management module for launching and controlling Chromium.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
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
        self.session_dir = Path.home() / ".automata" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)

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
            
        with open(path, 'r') as f:
            cookies = json.load(f)
        await self.context.add_cookies(cookies)
        logger.info(f"Cookies loaded from {path}")

    async def save_session(self, session_id: str, include_storage: bool = True) -> str:
        """
        Save the current browser session to a file.

        Args:
            session_id: ID for the session
            include_storage: Whether to include localStorage and sessionStorage

        Returns:
            Path to the saved session file
        """
        logger.info(f"DEBUG: save_session called - browser: {self.browser is not None}, context: {self.context is not None}, current_page: {self.current_page is not None}")
        
        if not self.context:
            logger.error("DEBUG: save_session failed - Browser not started or context already closed")
            raise RuntimeError("Browser not started.")
            
        session_path = self.session_dir / f"{session_id}.json"
        logger.info(f"DEBUG: Saving session to: {session_path}")
        
        try:
            # Get cookies
            logger.info(f"DEBUG: Starting to get cookies...")
            cookies = await self.context.cookies()
            logger.info(f"DEBUG: Successfully retrieved {len(cookies)} cookies")
            
            # Create session data
            logger.info(f"DEBUG: Creating session data structure...")
            session_data = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "cookies": cookies,
                "viewport": self.viewport,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            logger.info(f"DEBUG: Session data structure created")
            
            # Include storage if requested
            if include_storage and self.current_page:
                logger.info(f"DEBUG: Starting to get localStorage...")
                try:
                    # Get localStorage
                    logger.info(f"DEBUG: Evaluating localStorage script...")
                    local_storage = await self.current_page.evaluate("() => ({ ...Object.entries(localStorage).reduce((obj, [k, v]) => (obj[k] = v, obj), {}) })")
                    session_data["local_storage"] = local_storage
                    logger.info(f"DEBUG: Successfully retrieved localStorage with {len(local_storage)} items")
                except Exception as e:
                    logger.warning(f"DEBUG: Error getting localStorage data: {e}")
                
                logger.info(f"DEBUG: Starting to get sessionStorage...")
                try:
                    # Get sessionStorage
                    logger.info(f"DEBUG: Evaluating sessionStorage script...")
                    session_storage = await self.current_page.evaluate("() => ({ ...Object.entries(sessionStorage).reduce((obj, [k, v]) => (obj[k] = v, obj), {}) })")
                    session_data["session_storage"] = session_storage
                    logger.info(f"DEBUG: Successfully retrieved sessionStorage with {len(session_storage)} items")
                except Exception as e:
                    logger.warning(f"DEBUG: Error getting sessionStorage data: {e}")
            else:
                logger.info(f"DEBUG: Skipping storage retrieval - include_storage: {include_storage}, current_page: {self.current_page is not None}")
            
            # Save session data
            logger.info(f"DEBUG: Starting to write session data to file...")
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, default=str)
            logger.info(f"DEBUG: Session data written to file successfully")
            
            logger.info(f"DEBUG: Session save process completed successfully: {session_path}")
            return str(session_path)
        
        except Exception as e:
            logger.error(f"DEBUG: Error during session save process: {e}")
            logger.error(f"DEBUG: Error type: {type(e).__name__}")
            import traceback
            logger.error(f"DEBUG: Traceback: {traceback.format_exc()}")
            raise

    async def load_session(self, session_id: str, include_storage: bool = True) -> bool:
        """
        Load a browser session from a file.

        Args:
            session_id: ID of the session to load
            include_storage: Whether to load localStorage and sessionStorage

        Returns:
            True if session was loaded successfully, False otherwise
        """
        if not self.context:
            raise RuntimeError("Browser not started.")
            
        session_path = self.session_dir / f"{session_id}.json"
        
        if not session_path.exists():
            logger.warning(f"Session file not found: {session_path}")
            return False
        
        logger.info(f"Loading session from: {session_path}")
        
        try:
            # Load session data
            with open(session_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            # Load cookies
            if "cookies" in session_data:
                await self.context.add_cookies(session_data["cookies"])
                logger.info(f"Cookies loaded from session: {session_path}")
            
            # Load storage if requested and if we have a current page
            if include_storage and self.current_page:
                try:
                    # Set localStorage
                    if "local_storage" in session_data:
                        local_storage = session_data["local_storage"]
                        await self.current_page.evaluate("(data) => { localStorage.clear(); Object.entries(data).forEach(([k, v]) => localStorage.setItem(k, v)); }", local_storage)
                        logger.info("Local storage loaded from session")
                    
                    # Set sessionStorage
                    if "session_storage" in session_data:
                        session_storage = session_data["session_storage"]
                        await self.current_page.evaluate("(data) => { sessionStorage.clear(); Object.entries(data).forEach(([k, v]) => sessionStorage.setItem(k, v)); }", session_storage)
                        logger.info("Session storage loaded from session")
                except Exception as e:
                    logger.warning(f"Error setting storage data: {e}")
            
            logger.info(f"Session loaded successfully: {session_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error loading session from {session_path}: {e}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a saved session.

        Args:
            session_id: ID of the session to delete

        Returns:
            True if session was deleted successfully, False otherwise
        """
        session_path = self.session_dir / f"{session_id}.json"
        
        logger.info(f"Deleting session: {session_path}")
        
        try:
            if session_path.exists():
                session_path.unlink()
                logger.info(f"Session deleted successfully: {session_path}")
                return True
            else:
                logger.warning(f"Session file not found: {session_path}")
                return False
        
        except Exception as e:
            logger.error(f"Error deleting session {session_path}: {e}")
            return False

    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all saved sessions.

        Returns:
            List of session information
        """
        sessions = []
        
        try:
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        session_data = json.load(f)
                    
                    session_info = {
                        "session_id": session_data.get("session_id"),
                        "created_at": session_data.get("created_at"),
                        "path": str(session_file),
                        "cookie_count": len(session_data.get("cookies", [])),
                        "has_local_storage": "local_storage" in session_data,
                        "has_session_storage": "session_storage" in session_data
                    }
                    
                    sessions.append(session_info)
                
                except Exception as e:
                    logger.error(f"Error reading session file {session_file}: {e}")
            
            logger.info(f"Found {len(sessions)} sessions")
            return sessions
        
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []

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