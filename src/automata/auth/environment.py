"""
Environment variable-based authentication provider.
"""

import os
from typing import Dict, Any, Optional
import logging

from .base import AuthenticationProvider, AuthResult, AuthMethod, WebAuthenticator
from ..core.logger import get_logger

logger = get_logger(__name__)


class EnvironmentAuthProvider(AuthenticationProvider):
    """Authentication provider using environment variables."""

    def __init__(self):
        """Initialize the environment authentication provider."""
        super().__init__("Environment Variables")
        self.prefix = "AUTOMATA_AUTH_"

    async def is_available(self, **kwargs) -> bool:
        """
        Check if environment variable authentication is available.

        Args:
            **kwargs: Check parameters (prefix: custom prefix for env vars)

        Returns:
            True if available, False otherwise
        """
        prefix = kwargs.get("prefix", self.prefix)
        
        # Check for username and password environment variables
        username_var = f"{prefix}USERNAME"
        password_var = f"{prefix}PASSWORD"
        
        has_username = os.environ.get(username_var) is not None
        has_password = os.environ.get(password_var) is not None
        
        logger.debug(f"Environment auth availability - {username_var}: {has_username}, {password_var}: {has_password}")
        
        return has_username and has_password

    async def authenticate(self, **kwargs) -> AuthResult:
        """
        Authenticate using environment variables.

        Args:
            **kwargs: Authentication parameters:
                - prefix: Custom prefix for environment variables
                - username_var: Custom username environment variable name
                - password_var: Custom password environment variable name

        Returns:
            Authentication result
        """
        prefix = kwargs.get("prefix", self.prefix)
        username_var = kwargs.get("username_var", f"{prefix}USERNAME")
        password_var = kwargs.get("password_var", f"{prefix}PASSWORD")
        
        logger.info(f"Attempting environment variable authentication with {username_var} and {password_var}")
        
        # Get credentials from environment variables
        username = os.environ.get(username_var)
        password = os.environ.get(password_var)
        
        if not username:
            error_msg = f"Username environment variable not found: {username_var}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        if not password:
            error_msg = f"Password environment variable not found: {password_var}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Create session data
        session_data = {
            "username": username,
            "auth_method": AuthMethod.ENVIRONMENT.value
        }
        
        # Create result data
        data = {
            "username": username,
            "username_var": username_var,
            "password_var": password_var
        }
        
        logger.info(f"Environment variable authentication successful for user: {username}")
        
        return AuthResult(
            success=True,
            message=f"Authenticated as {username} using environment variables",
            data=data,
            session_data=session_data
        )


class EnvironmentWebAuthenticator(WebAuthenticator):
    """Web authenticator using environment variables."""

    def __init__(self, engine):
        """
        Initialize the environment web authenticator.

        Args:
            engine: Automation engine instance
        """
        super().__init__(engine)
        self.auth_provider = EnvironmentAuthProvider()

    async def authenticate(
        self,
        login_url: str,
        username_selector: str,
        password_selector: str,
        submit_selector: Optional[str] = None,
        success_selector: Optional[str] = None,
        error_selector: Optional[str] = None,
        **kwargs
    ) -> AuthResult:
        """
        Authenticate using environment variables on a web page.

        Args:
            login_url: URL of the login page
            username_selector: Selector for the username field
            password_selector: Selector for the password field
            submit_selector: Selector for the submit button (optional)
            success_selector: Selector that indicates successful login (optional)
            error_selector: Selector that indicates login error (optional)
            **kwargs: Additional authentication parameters

        Returns:
            Authentication result
        """
        # Check if environment authentication is available
        if not await self.auth_provider.is_available(**kwargs):
            error_msg = "Environment variable authentication is not available"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Get credentials from environment
        prefix = kwargs.get("prefix", self.auth_provider.prefix)
        username_var = kwargs.get("username_var", f"{prefix}USERNAME")
        password_var = kwargs.get("password_var", f"{prefix}PASSWORD")
        
        username = os.environ.get(username_var)
        password = os.environ.get(password_var)
        
        logger.info(f"Attempting web authentication using environment variables for user: {username}")
        
        try:
            # Navigate to login page
            await self.navigate_to_login(login_url)
            
            # Fill and submit login form
            await self.fill_login_form(
                username_selector=username_selector,
                username=username,
                password_selector=password_selector,
                password=password,
                submit_selector=submit_selector
            )
            
            # Wait for login completion
            login_success = await self.wait_for_login_completion(
                success_selector=success_selector,
                error_selector=error_selector
            )
            
            if login_success:
                # Create session data
                session_data = {
                    "username": username,
                    "auth_method": AuthMethod.ENVIRONMENT.value,
                    "login_url": login_url
                }
                
                # Create result data
                data = {
                    "username": username,
                    "username_var": username_var,
                    "password_var": password_var,
                    "login_url": login_url
                }
                
                logger.info(f"Web authentication successful using environment variables for user: {username}")
                
                return AuthResult(
                    success=True,
                    message=f"Web authentication successful for user: {username}",
                    data=data,
                    session_data=session_data
                )
            else:
                error_msg = "Web authentication failed using environment variables"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
        
        except Exception as e:
            error_msg = f"Error during web authentication using environment variables: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
