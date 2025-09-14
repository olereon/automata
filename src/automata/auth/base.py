"""
Base authentication framework supporting multiple methods.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from enum import Enum
import logging

from ..core.logger import get_logger

logger = get_logger(__name__)


class AuthMethod(Enum):
    """Enumeration of authentication methods."""
    ENVIRONMENT = "environment"
    CREDENTIAL_FILE = "credential_file"
    CREDENTIALS_JSON = "credentials_json"
    INTERACTIVE = "interactive"
    SESSION = "session"


class AuthResult:
    """Result of an authentication attempt."""

    def __init__(
        self,
        success: bool,
        message: str = "",
        data: Optional[Dict[str, Any]] = None,
        session_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize authentication result.

        Args:
            success: Whether authentication was successful
            message: Result message
            data: Additional authentication data
            session_data: Session data to persist
        """
        self.success = success
        self.message = message
        self.data = data or {}
        self.session_data = session_data or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "session_data": self.session_data
        }


class AuthenticationProvider(ABC):
    """Base class for authentication providers."""

    def __init__(self, name: str):
        """
        Initialize the authentication provider.

        Args:
            name: Provider name
        """
        self.name = name

    @abstractmethod
    async def authenticate(self, **kwargs) -> AuthResult:
        """
        Authenticate using this provider.

        Args:
            **kwargs: Authentication parameters

        Returns:
            Authentication result
        """
        pass

    @abstractmethod
    async def is_available(self, **kwargs) -> bool:
        """
        Check if this authentication method is available.

        Args:
            **kwargs: Check parameters

        Returns:
            True if available, False otherwise
        """
        pass


class AuthenticationManager:
    """Manages multiple authentication methods."""

    def __init__(self):
        """Initialize the authentication manager."""
        self.providers: Dict[AuthMethod, AuthenticationProvider] = {}
        self.session_data: Dict[str, Any] = {}

    def register_provider(self, method: AuthMethod, provider: AuthenticationProvider) -> None:
        """
        Register an authentication provider.

        Args:
            method: Authentication method
            provider: Authentication provider
        """
        self.providers[method] = provider
        logger.info(f"Registered authentication provider: {method.value} -> {provider.name}")

    def unregister_provider(self, method: AuthMethod) -> None:
        """
        Unregister an authentication provider.

        Args:
            method: Authentication method to unregister
        """
        if method in self.providers:
            provider = self.providers.pop(method)
            logger.info(f"Unregistered authentication provider: {method.value} -> {provider.name}")

    def get_provider(self, method: AuthMethod) -> Optional[AuthenticationProvider]:
        """
        Get an authentication provider by method.

        Args:
            method: Authentication method

        Returns:
            Authentication provider or None if not found
        """
        return self.providers.get(method)

    def list_providers(self) -> List[Dict[str, Any]]:
        """
        List all registered authentication providers.

        Returns:
            List of provider information
        """
        return [
            {
                "method": method.value,
                "name": provider.name
            }
            for method, provider in self.providers.items()
        ]

    async def check_availability(self, method: AuthMethod, **kwargs) -> bool:
        """
        Check if an authentication method is available.

        Args:
            method: Authentication method
            **kwargs: Check parameters

        Returns:
            True if available, False otherwise
        """
        provider = self.get_provider(method)
        if not provider:
            logger.warning(f"Authentication provider not found: {method.value}")
            return False

        try:
            return await provider.is_available(**kwargs)
        except Exception as e:
            logger.error(f"Error checking availability for {method.value}: {e}")
            return False

    async def authenticate(
        self,
        method: AuthMethod,
        **kwargs
    ) -> AuthResult:
        """
        Authenticate using the specified method.

        Args:
            method: Authentication method
            **kwargs: Authentication parameters

        Returns:
            Authentication result
        """
        provider = self.get_provider(method)
        if not provider:
            error_msg = f"Authentication provider not found: {method.value}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)

        logger.info(f"Attempting authentication with method: {method.value}")

        try:
            result = await provider.authenticate(**kwargs)
            
            if result.success:
                # Update session data
                if result.session_data:
                    self.session_data.update(result.session_data)
                    logger.info(f"Session data updated for method: {method.value}")
                
                logger.info(f"Authentication successful with method: {method.value}")
            else:
                logger.warning(f"Authentication failed with method: {method.value}: {result.message}")
            
            return result
        except Exception as e:
            error_msg = f"Error during authentication with {method.value}: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)

    async def try_multiple_methods(
        self,
        methods: List[AuthMethod],
        **kwargs
    ) -> AuthResult:
        """
        Try multiple authentication methods in order.

        Args:
            methods: List of authentication methods to try
            **kwargs: Authentication parameters

        Returns:
            Authentication result from the first successful method
        """
        last_error = None

        for method in methods:
            logger.info(f"Trying authentication method: {method.value}")
            
            # Check if method is available
            if not await self.check_availability(method, **kwargs):
                logger.info(f"Authentication method not available: {method.value}")
                continue
            
            # Try to authenticate
            result = await self.authenticate(method, **kwargs)
            
            if result.success:
                return result
            else:
                last_error = result.message
        
        # All methods failed
        error_msg = f"All authentication methods failed. Last error: {last_error}"
        logger.error(error_msg)
        return AuthResult(False, error_msg)

    def get_session_data(self, key: str, default: Any = None) -> Any:
        """
        Get session data by key.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Session data value or default
        """
        return self.session_data.get(key, default)

    def set_session_data(self, key: str, value: Any) -> None:
        """
        Set session data.

        Args:
            key: Data key
            value: Data value
        """
        self.session_data[key] = value
        logger.debug(f"Session data set: {key} = {value}")

    def clear_session_data(self) -> None:
        """Clear all session data."""
        self.session_data.clear()
        logger.info("Session data cleared")

    def save_session_data(self, path: str) -> None:
        """
        Save session data to a file.

        Args:
            path: Path to save the session data
        """
        import json
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.session_data, f, indent=2, default=str)
            
            logger.info(f"Session data saved to: {path}")
        except Exception as e:
            logger.error(f"Failed to save session data: {e}")

    def load_session_data(self, path: str) -> None:
        """
        Load session data from a file.

        Args:
            path: Path to load the session data from
        """
        import json
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.session_data = json.load(f)
            
            logger.info(f"Session data loaded from: {path}")
        except Exception as e:
            logger.error(f"Failed to load session data: {e}")


class WebAuthenticator:
    """Base class for web-based authentication."""

    def __init__(self, engine):
        """
        Initialize the web authenticator.

        Args:
            engine: Automation engine instance
        """
        self.engine = engine

    async def navigate_to_login(self, url: str) -> None:
        """
        Navigate to the login page.

        Args:
            url: Login page URL
        """
        logger.info(f"Navigating to login page: {url}")
        await self.engine.navigate_to(url)

    async def fill_login_form(
        self,
        username_selector: str,
        username: str,
        password_selector: str,
        password: str,
        submit_selector: Optional[str] = None
    ) -> None:
        """
        Fill and submit a login form.

        Args:
            username_selector: Selector for username field
            username: Username value
            password_selector: Selector for password field
            password: Password value
            submit_selector: Selector for submit button (optional)
        """
        logger.info("Filling login form")
        
        # Fill username
        await self.engine.fill(username_selector, username)
        
        # Fill password
        await self.engine.fill(password_selector, password)
        
        # Submit form
        if submit_selector:
            await self.engine.click(submit_selector)
        else:
            # Try to submit by pressing Enter in the password field
            await self.engine.press_key(password_selector, "Enter")
        
        logger.info("Login form submitted")

    async def wait_for_login_completion(
        self,
        success_selector: Optional[str] = None,
        error_selector: Optional[str] = None,
        timeout: int = 30000
    ) -> bool:
        """
        Wait for login to complete.

        Args:
            success_selector: Selector that indicates successful login
            error_selector: Selector that indicates login error
            timeout: Timeout in milliseconds

        Returns:
            True if login was successful, False otherwise
        """
        logger.info("Waiting for login completion")
        
        # Wait for either success or error indicator
        start_time = asyncio.get_event_loop().time()
        remaining_timeout = timeout / 1000
        
        while remaining_timeout > 0:
            # Check for success
            if success_selector:
                if await self.engine.wait_for_element(success_selector, timeout=1000):
                    logger.info("Login successful (success indicator found)")
                    return True
            
            # Check for error
            if error_selector:
                if await self.engine.wait_for_element(error_selector, timeout=1000):
                    logger.warning("Login failed (error indicator found)")
                    return False
            
            # Wait a bit before checking again
            await asyncio.sleep(0.5)
            elapsed = asyncio.get_event_loop().time() - start_time
            remaining_timeout = timeout / 1000 - elapsed
        
        # Timeout reached
        logger.warning("Login completion check timed out")
        return False

    async def check_login_status(self, logged_in_selector: str) -> bool:
        """
        Check if currently logged in.

        Args:
            logged_in_selector: Selector that indicates logged in state

        Returns:
            True if logged in, False otherwise
        """
        logger.info("Checking login status")
        
        try:
            return await self.engine.wait_for_element(logged_in_selector, timeout=5000)
        except Exception:
            return False

    async def logout(self, logout_selector: str) -> None:
        """
        Log out of the current session.

        Args:
            logout_selector: Selector for logout button/link
        """
        logger.info("Logging out")
        
        try:
            await self.engine.click(logout_selector)
            logger.info("Logout successful")
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            raise
