"""
Session persistence and cookie management.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging
from playwright.async_api import BrowserContext, Cookie

from .base import AuthenticationProvider, AuthResult, AuthMethod
from ..core.logger import get_logger

logger = get_logger(__name__)


class SessionAuthProvider(AuthenticationProvider):
    """Authentication provider using saved sessions."""

    def __init__(self):
        """Initialize the session authentication provider."""
        super().__init__("Saved Session")
        self.default_session_dir = Path.home() / ".automata" / "sessions"
        self.default_session_dir.mkdir(parents=True, exist_ok=True)
        self.session_expiry_days = 7

    async def is_available(self, **kwargs) -> bool:
        """
        Check if session authentication is available.

        Args:
            **kwargs: Check parameters:
                - session_path: Path to the session file
                - session_id: Session ID

        Returns:
            True if available, False otherwise
        """
        session_path = kwargs.get("session_path")
        session_id = kwargs.get("session_id")
        
        if not session_path and session_id:
            session_path = self._get_session_path(session_id)
        
        if not session_path:
            logger.debug("No session path provided")
            return False
        
        # Check if session file exists
        session_file = Path(session_path).expanduser()
        if not session_file.exists():
            logger.debug(f"Session file not found: {session_path}")
            return False
        
        # Check if session file is readable
        if not os.access(session_file, os.R_OK):
            logger.debug(f"Session file not readable: {session_path}")
            return False
        
        # Check if session is expired
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            created_at = datetime.fromisoformat(session_data.get("created_at", ""))
            expiry_date = created_at + timedelta(days=self.session_expiry_days)
            
            if datetime.now() > expiry_date:
                logger.debug(f"Session expired: {session_path}")
                return False
            
            logger.debug(f"Session found and valid: {session_path}")
            return True
        except Exception as e:
            logger.debug(f"Error checking session: {e}")
            return False

    async def authenticate(self, **kwargs) -> AuthResult:
        """
        Authenticate using a saved session.

        Args:
            **kwargs: Authentication parameters:
                - session_path: Path to the session file
                - session_id: Session ID
                - context: Browser context to load cookies into

        Returns:
            Authentication result
        """
        session_path = kwargs.get("session_path")
        session_id = kwargs.get("session_id")
        context = kwargs.get("context")
        
        logger.info("Attempting session authentication")
        
        # Get session path
        if not session_path and session_id:
            session_path = self._get_session_path(session_id)
        
        if not session_path:
            error_msg = "No session path provided"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Load session data
        try:
            session_file = Path(session_path).expanduser()
            
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            
            # Check if session is expired
            created_at = datetime.fromisoformat(session_data.get("created_at", ""))
            expiry_date = created_at + timedelta(days=self.session_expiry_days)
            
            if datetime.now() > expiry_date:
                error_msg = f"Session expired: {session_path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Load cookies into context if provided
            if context and "cookies" in session_data:
                await context.add_cookies(session_data["cookies"])
                logger.info(f"Cookies loaded from session: {session_path}")
            
            # Create session data
            session_info = {
                "username": session_data.get("username"),
                "auth_method": AuthMethod.SESSION.value,
                "session_path": session_path,
                "created_at": session_data.get("created_at"),
                "last_used": datetime.now().isoformat()
            }
            
            # Create result data
            data = {
                "username": session_data.get("username"),
                "session_path": session_path,
                "created_at": session_data.get("created_at")
            }
            
            logger.info(f"Session authentication successful for user: {session_data.get('username')}")
            
            return AuthResult(
                success=True,
                message=f"Authenticated using saved session for user: {session_data.get('username')}",
                data=data,
                session_data=session_info
            )
        
        except Exception as e:
            error_msg = f"Error loading session from {session_path}: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)

    def _get_session_path(self, session_id: str) -> str:
        """
        Get the path to a session file by session ID.

        Args:
            session_id: Session ID

        Returns:
            Path to the session file
        """
        return str(self.default_session_dir / f"{session_id}.json")

    async def save_session(
        self,
        session_id: str,
        context: BrowserContext,
        username: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a session to a file.

        Args:
            session_id: Session ID
            context: Browser context with cookies
            username: Username associated with the session
            additional_data: Additional data to save with the session

        Returns:
            Path to the saved session file
        """
        session_path = self._get_session_path(session_id)
        
        logger.info(f"Saving session to: {session_path}")
        
        try:
            # Get cookies from context
            cookies = await context.cookies()
            
            # Create session data
            session_data = {
                "session_id": session_id,
                "username": username,
                "created_at": datetime.now().isoformat(),
                "cookies": cookies
            }
            
            # Add additional data if provided
            if additional_data:
                session_data.update(additional_data)
            
            # Save session data
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2, default=str)
            
            logger.info(f"Session saved successfully: {session_path}")
            return session_path
        
        except Exception as e:
            logger.error(f"Error saving session to {session_path}: {e}")
            raise

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session file.

        Args:
            session_id: Session ID

        Returns:
            True if successful, False otherwise
        """
        session_path = self._get_session_path(session_id)
        
        logger.info(f"Deleting session: {session_path}")
        
        try:
            session_file = Path(session_path).expanduser()
            
            if session_file.exists():
                session_file.unlink()
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
        List all available sessions.

        Returns:
            List of session information
        """
        sessions = []
        
        try:
            for session_file in self.default_session_dir.glob("*.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        session_data = json.load(f)
                    
                    # Check if session is expired
                    created_at = datetime.fromisoformat(session_data.get("created_at", ""))
                    expiry_date = created_at + timedelta(days=self.session_expiry_days)
                    is_expired = datetime.now() > expiry_date
                    
                    session_info = {
                        "session_id": session_data.get("session_id"),
                        "username": session_data.get("username"),
                        "created_at": session_data.get("created_at"),
                        "path": str(session_file),
                        "is_expired": is_expired
                    }
                    
                    sessions.append(session_info)
                
                except Exception as e:
                    logger.error(f"Error reading session file {session_file}: {e}")
            
            logger.info(f"Found {len(sessions)} sessions")
            return sessions
        
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []

    async def cleanup_expired_sessions(self) -> int:
        """
        Delete all expired sessions.

        Returns:
            Number of deleted sessions
        """
        sessions = await self.list_sessions()
        deleted_count = 0
        
        for session in sessions:
            if session.get("is_expired", False):
                session_id = session.get("session_id")
                if await self.delete_session(session_id):
                    deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} expired sessions")
        return deleted_count


class CookieManager:
    """Manages cookies for browser contexts."""

    def __init__(self):
        """Initialize the cookie manager."""
        self.default_cookie_dir = Path.home() / ".automata" / "cookies"
        self.default_cookie_dir.mkdir(parents=True, exist_ok=True)

    async def save_cookies(
        self,
        context: BrowserContext,
        name: str,
        filter_func: Optional[callable] = None
    ) -> str:
        """
        Save cookies from a browser context.

        Args:
            context: Browser context with cookies
            name: Name for the cookie file
            filter_func: Optional function to filter cookies

        Returns:
            Path to the saved cookie file
        """
        cookie_path = self.default_cookie_dir / f"{name}.json"
        
        logger.info(f"Saving cookies to: {cookie_path}")
        
        try:
            # Get cookies from context
            cookies = await context.cookies()
            
            # Filter cookies if filter function is provided
            if filter_func:
                cookies = [cookie for cookie in cookies if filter_func(cookie)]
            
            # Save cookies
            with open(cookie_path, "w", encoding="utf-8") as f:
                json.dump(cookies, f, indent=2, default=str)
            
            logger.info(f"Cookies saved successfully: {cookie_path}")
            return str(cookie_path)
        
        except Exception as e:
            logger.error(f"Error saving cookies to {cookie_path}: {e}")
            raise

    async def load_cookies(
        self,
        context: BrowserContext,
        name: str,
        filter_func: Optional[callable] = None
    ) -> int:
        """
        Load cookies into a browser context.

        Args:
            context: Browser context to load cookies into
            name: Name of the cookie file
            filter_func: Optional function to filter cookies

        Returns:
            Number of loaded cookies
        """
        cookie_path = self.default_cookie_dir / f"{name}.json"
        
        logger.info(f"Loading cookies from: {cookie_path}")
        
        try:
            # Check if cookie file exists
            if not cookie_path.exists():
                logger.warning(f"Cookie file not found: {cookie_path}")
                return 0
            
            # Load cookies
            with open(cookie_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            
            # Filter cookies if filter function is provided
            if filter_func:
                cookies = [cookie for cookie in cookies if filter_func(cookie)]
            
            # Load cookies into context
            await context.add_cookies(cookies)
            
            logger.info(f"Loaded {len(cookies)} cookies from: {cookie_path}")
            return len(cookies)
        
        except Exception as e:
            logger.error(f"Error loading cookies from {cookie_path}: {e}")
            raise

    async def delete_cookies(self, name: str) -> bool:
        """
        Delete a cookie file.

        Args:
            name: Name of the cookie file

        Returns:
            True if successful, False otherwise
        """
        cookie_path = self.default_cookie_dir / f"{name}.json"
        
        logger.info(f"Deleting cookies: {cookie_path}")
        
        try:
            if cookie_path.exists():
                cookie_path.unlink()
                logger.info(f"Cookies deleted successfully: {cookie_path}")
                return True
            else:
                logger.warning(f"Cookie file not found: {cookie_path}")
                return False
        
        except Exception as e:
            logger.error(f"Error deleting cookies {cookie_path}: {e}")
            return False

    async def list_cookies(self) -> List[Dict[str, Any]]:
        """
        List all available cookie files.

        Returns:
            List of cookie file information
        """
        cookie_files = []
        
        try:
            for cookie_file in self.default_cookie_dir.glob("*.json"):
                try:
                    # Get file stats
                    stat = cookie_file.stat()
                    
                    cookie_info = {
                        "name": cookie_file.stem,
                        "path": str(cookie_file),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                    
                    cookie_files.append(cookie_info)
                
                except Exception as e:
                    logger.error(f"Error reading cookie file {cookie_file}: {e}")
            
            logger.info(f"Found {len(cookie_files)} cookie files")
            return cookie_files
        
        except Exception as e:
            logger.error(f"Error listing cookie files: {e}")
            return []

    def create_domain_filter(self, domain: str) -> callable:
        """
        Create a filter function for cookies from a specific domain.

        Args:
            domain: Domain to filter cookies for

        Returns:
            Filter function
        """
        def filter_func(cookie: Cookie) -> bool:
            return cookie.get("domain", "").endswith(domain)
        
        return filter_func

    def create_name_filter(self, name: str) -> callable:
        """
        Create a filter function for cookies with a specific name.

        Args:
            name: Name to filter cookies for

        Returns:
            Filter function
        """
        def filter_func(cookie: Cookie) -> bool:
            return cookie.get("name") == name
        
        return filter_func
