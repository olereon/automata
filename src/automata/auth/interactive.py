"""
Interactive login authentication provider.
"""

import asyncio
import getpass
from typing import Dict, Any, Optional, List
import logging

from .base import AuthenticationProvider, AuthResult, AuthMethod, WebAuthenticator
from ..core.logger import get_logger

logger = get_logger(__name__)


class InteractiveAuthProvider(AuthenticationProvider):
    """Authentication provider using interactive prompts."""

    def __init__(self):
        """Initialize the interactive authentication provider."""
        super().__init__("Interactive Login")

    async def is_available(self, **kwargs) -> bool:
        """
        Check if interactive authentication is available.

        Args:
            **kwargs: Check parameters

        Returns:
            True if available, False otherwise
        """
        # Interactive authentication is always available in a terminal environment
        return True

    async def authenticate(self, **kwargs) -> AuthResult:
        """
        Authenticate using interactive prompts.

        Args:
            **kwargs: Authentication parameters:
                - username: Pre-filled username (optional)
                - prompt_username: Whether to prompt for username (default: True)
                - prompt_password: Whether to prompt for password (default: True)
                - username_prompt: Custom username prompt
                - password_prompt: Custom password prompt

        Returns:
            Authentication result
        """
        username = kwargs.get("username", "")
        prompt_username = kwargs.get("prompt_username", True)
        prompt_password = kwargs.get("prompt_password", True)
        username_prompt = kwargs.get("username_prompt", "Username: ")
        password_prompt = kwargs.get("password_prompt", "Password: ")
        
        logger.info("Attempting interactive authentication")
        
        try:
            # Prompt for username if needed
            if prompt_username:
                if username:
                    print(f"{username_prompt}[{username}] ", end="")
                    input_username = input().strip()
                    if input_username:
                        username = input_username
                else:
                    username = input(username_prompt).strip()
            
            # Prompt for password if needed
            if prompt_password:
                password = getpass.getpass(password_prompt)
            else:
                password = kwargs.get("password", "")
            
            if not username:
                error_msg = "Username is required"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            if not password:
                error_msg = "Password is required"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Create session data
            session_data = {
                "username": username,
                "auth_method": AuthMethod.INTERACTIVE.value
            }
            
            # Create result data
            data = {
                "username": username
            }
            
            logger.info(f"Interactive authentication successful for user: {username}")
            
            return AuthResult(
                success=True,
                message=f"Authenticated as {username} using interactive login",
                data=data,
                session_data=session_data
            )
        
        except KeyboardInterrupt:
            error_msg = "Interactive authentication cancelled by user"
            logger.warning(error_msg)
            return AuthResult(False, error_msg)
        except Exception as e:
            error_msg = f"Error during interactive authentication: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)


class InteractiveWebAuthenticator(WebAuthenticator):
    """Web authenticator using interactive prompts."""

    def __init__(self, engine):
        """
        Initialize the interactive web authenticator.

        Args:
            engine: Automation engine instance
        """
        super().__init__(engine)
        self.auth_provider = InteractiveAuthProvider()

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
        Authenticate using interactive prompts on a web page.

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
        # Check if interactive authentication is available
        if not await self.auth_provider.is_available(**kwargs):
            error_msg = "Interactive authentication is not available"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Get credentials interactively
        username = kwargs.get("username", "")
        prompt_username = kwargs.get("prompt_username", True)
        prompt_password = kwargs.get("prompt_password", True)
        username_prompt = kwargs.get("username_prompt", "Username: ")
        password_prompt = kwargs.get("password_prompt", "Password: ")
        
        logger.info("Attempting interactive web authentication")
        
        try:
            # Prompt for username if needed
            if prompt_username:
                if username:
                    print(f"{username_prompt}[{username}] ", end="")
                    input_username = input().strip()
                    if input_username:
                        username = input_username
                else:
                    username = input(username_prompt).strip()
            
            # Prompt for password if needed
            if prompt_password:
                password = getpass.getpass(password_prompt)
            else:
                password = kwargs.get("password", "")
            
            if not username or not password:
                error_msg = "Username and password are required"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            logger.info(f"Attempting web authentication using interactive login for user: {username}")
            
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
                    "auth_method": AuthMethod.INTERACTIVE.value,
                    "login_url": login_url
                }
                
                # Create result data
                data = {
                    "username": username,
                    "login_url": login_url
                }
                
                logger.info(f"Interactive web authentication successful for user: {username}")
                
                return AuthResult(
                    success=True,
                    message=f"Web authentication successful for user: {username}",
                    data=data,
                    session_data=session_data
                )
            else:
                error_msg = "Interactive web authentication failed"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
        
        except KeyboardInterrupt:
            error_msg = "Interactive web authentication cancelled by user"
            logger.warning(error_msg)
            return AuthResult(False, error_msg)
        except Exception as e:
            error_msg = f"Error during interactive web authentication: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)

    async def authenticate_with_captcha(
        self,
        login_url: str,
        username_selector: str,
        password_selector: str,
        submit_selector: Optional[str] = None,
        success_selector: Optional[str] = None,
        error_selector: Optional[str] = None,
        captcha_selector: Optional[str] = None,
        **kwargs
    ) -> AuthResult:
        """
        Authenticate using interactive prompts with CAPTCHA handling.

        Args:
            login_url: URL of the login page
            username_selector: Selector for the username field
            password_selector: Selector for the password field
            submit_selector: Selector for the submit button (optional)
            success_selector: Selector that indicates successful login (optional)
            error_selector: Selector that indicates login error (optional)
            captcha_selector: Selector for CAPTCHA field (optional)
            **kwargs: Additional authentication parameters

        Returns:
            Authentication result
        """
        # Get credentials interactively
        username = kwargs.get("username", "")
        prompt_username = kwargs.get("prompt_username", True)
        prompt_password = kwargs.get("prompt_password", True)
        username_prompt = kwargs.get("username_prompt", "Username: ")
        password_prompt = kwargs.get("password_prompt", "Password: ")
        
        logger.info("Attempting interactive web authentication with CAPTCHA handling")
        
        try:
            # Prompt for username if needed
            if prompt_username:
                if username:
                    print(f"{username_prompt}[{username}] ", end="")
                    input_username = input().strip()
                    if input_username:
                        username = input_username
                else:
                    username = input(username_prompt).strip()
            
            # Prompt for password if needed
            if prompt_password:
                password = getpass.getpass(password_prompt)
            else:
                password = kwargs.get("password", "")
            
            if not username or not password:
                error_msg = "Username and password are required"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            logger.info(f"Attempting web authentication with CAPTCHA for user: {username}")
            
            # Navigate to login page
            await self.navigate_to_login(login_url)
            
            # Fill username and password
            await self.engine.fill(username_selector, username)
            await self.engine.fill(password_selector, password)
            
            # If CAPTCHA selector is provided, pause for manual solving
            if captcha_selector:
                print("\nCAPTCHA detected! Please solve the CAPTCHA in the browser.")
                print("Press Enter when you have solved the CAPTCHA and are ready to continue...")
                input()
            
            # Submit the form
            if submit_selector:
                await self.engine.click(submit_selector)
            else:
                # Try to submit by pressing Enter in the password field
                await self.engine.press_key(password_selector, "Enter")
            
            # Wait for login completion
            login_success = await self.wait_for_login_completion(
                success_selector=success_selector,
                error_selector=error_selector
            )
            
            if login_success:
                # Create session data
                session_data = {
                    "username": username,
                    "auth_method": AuthMethod.INTERACTIVE.value,
                    "login_url": login_url,
                    "captcha_handled": captcha_selector is not None
                }
                
                # Create result data
                data = {
                    "username": username,
                    "login_url": login_url,
                    "captcha_handled": captcha_selector is not None
                }
                
                logger.info(f"Interactive web authentication with CAPTCHA successful for user: {username}")
                
                return AuthResult(
                    success=True,
                    message=f"Web authentication with CAPTCHA successful for user: {username}",
                    data=data,
                    session_data=session_data
                )
            else:
                error_msg = "Interactive web authentication with CAPTCHA failed"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
        
        except KeyboardInterrupt:
            error_msg = "Interactive web authentication with CAPTCHA cancelled by user"
            logger.warning(error_msg)
            return AuthResult(False, error_msg)
        except Exception as e:
            error_msg = f"Error during interactive web authentication with CAPTCHA: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)

    async def authenticate_with_2fa(
        self,
        login_url: str,
        username_selector: str,
        password_selector: str,
        submit_selector: Optional[str] = None,
        success_selector: Optional[str] = None,
        error_selector: Optional[str] = None,
        two_fa_selector: Optional[str] = None,
        two_fa_submit_selector: Optional[str] = None,
        **kwargs
    ) -> AuthResult:
        """
        Authenticate using interactive prompts with 2FA handling.

        Args:
            login_url: URL of the login page
            username_selector: Selector for the username field
            password_selector: Selector for the password field
            submit_selector: Selector for the submit button (optional)
            success_selector: Selector that indicates successful login (optional)
            error_selector: Selector that indicates login error (optional)
            two_fa_selector: Selector for 2FA code field (optional)
            two_fa_submit_selector: Selector for 2FA submit button (optional)
            **kwargs: Additional authentication parameters

        Returns:
            Authentication result
        """
        # Get credentials interactively
        username = kwargs.get("username", "")
        prompt_username = kwargs.get("prompt_username", True)
        prompt_password = kwargs.get("prompt_password", True)
        username_prompt = kwargs.get("username_prompt", "Username: ")
        password_prompt = kwargs.get("password_prompt", "Password: ")
        
        logger.info("Attempting interactive web authentication with 2FA handling")
        
        try:
            # Prompt for username if needed
            if prompt_username:
                if username:
                    print(f"{username_prompt}[{username}] ", end="")
                    input_username = input().strip()
                    if input_username:
                        username = input_username
                else:
                    username = input(username_prompt).strip()
            
            # Prompt for password if needed
            if prompt_password:
                password = getpass.getpass(password_prompt)
            else:
                password = kwargs.get("password", "")
            
            if not username or not password:
                error_msg = "Username and password are required"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            logger.info(f"Attempting web authentication with 2FA for user: {username}")
            
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
            
            # If 2FA selector is provided, handle 2FA
            if two_fa_selector:
                print("\nTwo-factor authentication required!")
                two_fa_code = input("Please enter your 2FA code: ")
                
                # Fill 2FA code
                await self.engine.fill(two_fa_selector, two_fa_code)
                
                # Submit 2FA form
                if two_fa_submit_selector:
                    await self.engine.click(two_fa_submit_selector)
                else:
                    # Try to submit by pressing Enter in the 2FA field
                    await self.engine.press_key(two_fa_selector, "Enter")
            
            # Wait for login completion
            login_success = await self.wait_for_login_completion(
                success_selector=success_selector,
                error_selector=error_selector
            )
            
            if login_success:
                # Create session data
                session_data = {
                    "username": username,
                    "auth_method": AuthMethod.INTERACTIVE.value,
                    "login_url": login_url,
                    "two_fa_used": two_fa_selector is not None
                }
                
                # Create result data
                data = {
                    "username": username,
                    "login_url": login_url,
                    "two_fa_used": two_fa_selector is not None
                }
                
                logger.info(f"Interactive web authentication with 2FA successful for user: {username}")
                
                return AuthResult(
                    success=True,
                    message=f"Web authentication with 2FA successful for user: {username}",
                    data=data,
                    session_data=session_data
                )
            else:
                error_msg = "Interactive web authentication with 2FA failed"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
        
        except KeyboardInterrupt:
            error_msg = "Interactive web authentication with 2FA cancelled by user"
            logger.warning(error_msg)
            return AuthResult(False, error_msg)
        except Exception as e:
            error_msg = f"Error during interactive web authentication with 2FA: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
