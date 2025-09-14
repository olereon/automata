"""
Credential file-based authentication provider.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

from .base import AuthenticationProvider, AuthResult, AuthMethod, WebAuthenticator
from ..core.logger import get_logger

logger = get_logger(__name__)


class CredentialFileAuthProvider(AuthenticationProvider):
    """Authentication provider using credential files."""

    def __init__(self):
        """Initialize the credential file authentication provider."""
        super().__init__("Credential File")
        self.default_paths = [
            "~/.automata/credentials.json",
            "~/.automata/credentials",
            "./credentials.json",
            "./credentials"
        ]
        self.supported_formats = ["json", "env", "ini"]

    async def is_available(self, **kwargs) -> bool:
        """
        Check if credential file authentication is available.

        Args:
            **kwargs: Check parameters:
                - path: Path to the credential file
                - format: Format of the credential file

        Returns:
            True if available, False otherwise
        """
        path = kwargs.get("path")
        
        if not path:
            # Try default paths
            for default_path in self.default_paths:
                expanded_path = Path(default_path).expanduser()
                if expanded_path.exists():
                    path = str(expanded_path)
                    break
        
        if not path:
            logger.debug("No credential file found in default paths")
            return False
        
        # Check if file exists
        credential_path = Path(path).expanduser()
        if not credential_path.exists():
            logger.debug(f"Credential file not found: {path}")
            return False
        
        # Check if file is readable
        if not os.access(credential_path, os.R_OK):
            logger.debug(f"Credential file not readable: {path}")
            return False
        
        logger.debug(f"Credential file found and readable: {path}")
        return True

    async def authenticate(self, **kwargs) -> AuthResult:
        """
        Authenticate using a credential file.

        Args:
            **kwargs: Authentication parameters:
                - path: Path to the credential file
                - format: Format of the credential file (json, env, ini)
                - username_key: Key for username in the credential file
                - password_key: Key for password in the credential file

        Returns:
            Authentication result
        """
        path = kwargs.get("path")
        format_type = kwargs.get("format", "json")
        username_key = kwargs.get("username_key", "username")
        password_key = kwargs.get("password_key", "password")
        
        logger.info(f"Attempting credential file authentication with {path}")
        
        # Find credential file
        if not path:
            for default_path in self.default_paths:
                expanded_path = Path(default_path).expanduser()
                if expanded_path.exists():
                    path = str(expanded_path)
                    break
        
        if not path:
            error_msg = "No credential file found"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Load credentials from file
        try:
            credential_path = Path(path).expanduser()
            
            if format_type.lower() == "json":
                credentials = self._load_json_credentials(credential_path, username_key, password_key)
            elif format_type.lower() == "env":
                credentials = self._load_env_credentials(credential_path, username_key, password_key)
            elif format_type.lower() == "ini":
                credentials = self._load_ini_credentials(credential_path, username_key, password_key)
            else:
                error_msg = f"Unsupported credential file format: {format_type}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            username = credentials.get("username")
            password = credentials.get("password")
            
            if not username:
                error_msg = f"Username not found in credential file: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            if not password:
                error_msg = f"Password not found in credential file: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Create session data
            session_data = {
                "username": username,
                "auth_method": AuthMethod.CREDENTIAL_FILE.value,
                "credential_file": path
            }
            
            # Create result data
            data = {
                "username": username,
                "credential_file": path,
                "format": format_type
            }
            
            logger.info(f"Credential file authentication successful for user: {username}")
            
            return AuthResult(
                success=True,
                message=f"Authenticated as {username} using credential file",
                data=data,
                session_data=session_data
            )
        
        except Exception as e:
            error_msg = f"Error loading credentials from file {path}: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)

    def _load_json_credentials(
        self,
        path: Path,
        username_key: str,
        password_key: str
    ) -> Dict[str, str]:
        """
        Load credentials from a JSON file.

        Args:
            path: Path to the JSON file
            username_key: Key for username
            password_key: Key for password

        Returns:
            Dictionary with username and password
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return {
            "username": data.get(username_key),
            "password": data.get(password_key)
        }

    def _load_env_credentials(
        self,
        path: Path,
        username_key: str,
        password_key: str
    ) -> Dict[str, str]:
        """
        Load credentials from an environment file.

        Args:
            path: Path to the environment file
            username_key: Key for username
            password_key: Key for password

        Returns:
            Dictionary with username and password
        """
        credentials = {}
        
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    if key == username_key:
                        credentials["username"] = value
                    elif key == password_key:
                        credentials["password"] = value
        
        return credentials

    def _load_ini_credentials(
        self,
        path: Path,
        username_key: str,
        password_key: str
    ) -> Dict[str, str]:
        """
        Load credentials from an INI file.

        Args:
            path: Path to the INI file
            username_key: Key for username
            password_key: Key for password

        Returns:
            Dictionary with username and password
        """
        import configparser
        
        config = configparser.ConfigParser()
        config.read(path)
        
        # Try to find credentials in any section
        for section in config.sections():
            if config.has_option(section, username_key) and config.has_option(section, password_key):
                return {
                    "username": config.get(section, username_key),
                    "password": config.get(section, password_key)
                }
        
        # Try default section
        if config.has_option("DEFAULT", username_key) and config.has_option("DEFAULT", password_key):
            return {
                "username": config.get("DEFAULT", username_key),
                "password": config.get("DEFAULT", password_key)
            }
        
        return {"username": None, "password": None}


class CredentialFileWebAuthenticator(WebAuthenticator):
    """Web authenticator using credential files."""

    def __init__(self, engine):
        """
        Initialize the credential file web authenticator.

        Args:
            engine: Automation engine instance
        """
        super().__init__(engine)
        self.auth_provider = CredentialFileAuthProvider()

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
        Authenticate using a credential file on a web page.

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
        # Check if credential file authentication is available
        if not await self.auth_provider.is_available(**kwargs):
            error_msg = "Credential file authentication is not available"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Get credentials from file
        path = kwargs.get("path")
        format_type = kwargs.get("format", "json")
        username_key = kwargs.get("username_key", "username")
        password_key = kwargs.get("password_key", "password")
        
        # Find credential file
        if not path:
            for default_path in self.auth_provider.default_paths:
                expanded_path = Path(default_path).expanduser()
                if expanded_path.exists():
                    path = str(expanded_path)
                    break
        
        if not path:
            error_msg = "No credential file found"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Load credentials from file
        try:
            credential_path = Path(path).expanduser()
            
            if format_type.lower() == "json":
                credentials = self.auth_provider._load_json_credentials(
                    credential_path, username_key, password_key
                )
            elif format_type.lower() == "env":
                credentials = self.auth_provider._load_env_credentials(
                    credential_path, username_key, password_key
                )
            elif format_type.lower() == "ini":
                credentials = self.auth_provider._load_ini_credentials(
                    credential_path, username_key, password_key
                )
            else:
                error_msg = f"Unsupported credential file format: {format_type}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            username = credentials.get("username")
            password = credentials.get("password")
            
            if not username or not password:
                error_msg = f"Username or password not found in credential file: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            logger.info(f"Attempting web authentication using credential file for user: {username}")
            
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
                    "auth_method": AuthMethod.CREDENTIAL_FILE.value,
                    "credential_file": path,
                    "login_url": login_url
                }
                
                # Create result data
                data = {
                    "username": username,
                    "credential_file": path,
                    "format": format_type,
                    "login_url": login_url
                }
                
                logger.info(f"Web authentication successful using credential file for user: {username}")
                
                return AuthResult(
                    success=True,
                    message=f"Web authentication successful for user: {username}",
                    data=data,
                    session_data=session_data
                )
            else:
                error_msg = "Web authentication failed using credential file"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
        
        except Exception as e:
            error_msg = f"Error during web authentication using credential file: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
