"""
JSON credentials file authentication provider.

This provider loads credentials from a JSON file with a specific format
that supports multiple credentials, configuration, and custom fields.
"""

import os
import json
import stat
from pathlib import Path
from typing import Dict, Any, Optional

from .base import AuthenticationProvider, AuthResult, AuthMethod, WebAuthenticator
from ..core.logger import get_logger

logger = get_logger(__name__)


class CredentialsJsonAuthProvider(AuthenticationProvider):
    """Authentication provider using JSON credentials files."""

    def __init__(self):
        """Initialize the JSON credentials authentication provider."""
        super().__init__("JSON Credentials")
        self.required_sections = ["credentials", "config"]
        self.supported_formats = ["json"]

    async def is_available(self, **kwargs) -> bool:
        """
        Check if JSON credentials file authentication is available.

        Args:
            **kwargs: Check parameters:
                - path: Path to the JSON credentials file

        Returns:
            True if available, False otherwise
        """
        path = kwargs.get("path")
        
        if not path:
            logger.debug("No JSON credentials file path provided")
            return False
        
        # Check if file exists
        credential_path = Path(path).expanduser()
        if not credential_path.exists():
            logger.debug(f"JSON credentials file not found: {path}")
            return False
        
        # Check if file is readable
        if not os.access(credential_path, os.R_OK):
            logger.debug(f"JSON credentials file not readable: {path}")
            return False
        
        # Check file permissions for security
        if not self._check_file_permissions(credential_path):
            logger.debug(f"JSON credentials file has insecure permissions: {path}")
            return False
        
        # Check if file is in a version control directory
        if self._is_in_version_control(credential_path):
            logger.debug(f"JSON credentials file is in a version control directory: {path}")
            return False
        
        logger.debug(f"JSON credentials file found and readable: {path}")
        return True

    async def authenticate(self, **kwargs) -> AuthResult:
        """
        Authenticate using a JSON credentials file.

        Args:
            **kwargs: Authentication parameters:
                - path: Path to the JSON credentials file

        Returns:
            Authentication result
        """
        path = kwargs.get("path")
        
        logger.info(f"Attempting JSON credentials file authentication with {path}")
        
        if not path:
            error_msg = "No JSON credentials file path provided"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Load credentials from file
        try:
            credential_path = Path(path).expanduser()
            
            # Check file permissions for security
            if not self._check_file_permissions(credential_path):
                error_msg = f"JSON credentials file has insecure permissions: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Check if file is in a version control directory
            if self._is_in_version_control(credential_path):
                error_msg = f"JSON credentials file is in a version control directory: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Load and validate JSON credentials
            credentials_data = self._load_json_credentials(credential_path)
            
            if not credentials_data:
                error_msg = f"Failed to load credentials from JSON file: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Validate required sections
            validation_error = self._validate_credentials_format(credentials_data)
            if validation_error:
                error_msg = f"Invalid credentials format: {validation_error}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Extract credentials and config
            credentials = credentials_data.get("credentials", {})
            config = credentials_data.get("config", {})
            custom_fields = credentials_data.get("custom_fields", {})
            
            # Check for sensitive data and log warnings
            self._check_for_sensitive_data(credentials_data)
            
            # Create session data
            session_data = {
                "auth_method": AuthMethod.CREDENTIALS_JSON.value,
                "credentials_file": path,
                "credentials": credentials,
                "config": config,
                "custom_fields": custom_fields
            }
            
            # Create result data
            data = {
                "credentials_file": path,
                "credentials": {k: "***" for k in credentials.keys()},  # Mask sensitive data
                "config": config,
                "custom_fields": custom_fields
            }
            
            logger.info(f"JSON credentials file authentication successful")
            
            return AuthResult(
                success=True,
                message="Authenticated using JSON credentials file",
                data=data,
                session_data=session_data
            )
        
        except Exception as e:
            error_msg = f"Error loading credentials from JSON file {path}: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)

    def _check_file_permissions(self, path: Path) -> bool:
        """
        Check if the credentials file has secure permissions.

        Args:
            path: Path to the credentials file

        Returns:
            True if permissions are secure, False otherwise
        """
        try:
            # Get file status
            file_stat = path.stat()
            
            # Check if file is readable by others
            if file_stat.st_mode & stat.S_IROTH:
                logger.warning(f"Credentials file is readable by others: {path}")
                return False
            
            # Check if file is writable by others
            if file_stat.st_mode & stat.S_IWOTH:
                logger.warning(f"Credentials file is writable by others: {path}")
                return False
            
            # Check if file is owned by current user
            if file_stat.st_uid != os.getuid():
                logger.warning(f"Credentials file is not owned by current user: {path}")
                return False
            
            # Check if file is readable by group
            if file_stat.st_mode & stat.S_IRGRP:
                logger.warning(f"Credentials file is readable by group: {path}")
                return False
            
            # Check if file is writable by group
            if file_stat.st_mode & stat.S_IWGRP:
                logger.warning(f"Credentials file is writable by group: {path}")
                return False
            
            # Check if file is executable by others
            if file_stat.st_mode & stat.S_IXOTH:
                logger.warning(f"Credentials file is executable by others: {path}")
                return False
            
            # Check if file is executable by group
            if file_stat.st_mode & stat.S_IXGRP:
                logger.warning(f"Credentials file is executable by group: {path}")
                return False
            
            # Check if file is executable by owner
            if file_stat.st_mode & stat.S_IXUSR:
                logger.warning(f"Credentials file is executable by owner: {path}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking file permissions for {path}: {e}")
            return False

    def _is_in_version_control(self, path: Path) -> bool:
        """
        Check if the credentials file is in a version control directory.

        Args:
            path: Path to the credentials file

        Returns:
            True if in version control directory, False otherwise
        """
        try:
            # Check if file is in a .git directory
            current_path = path.parent
            while current_path != current_path.parent:
                if (current_path / ".git").exists():
                    return True
                current_path = current_path.parent
            
            # Check for other version control directories
            current_path = path.parent
            while current_path != current_path.parent:
                for vcs_dir in [".svn", ".hg", ".bzr"]:
                    if (current_path / vcs_dir).exists():
                        return True
                current_path = current_path.parent
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking version control for {path}: {e}")
            return False

    def _check_for_sensitive_data(self, credentials_data: Dict[str, Any]) -> None:
        """
        Check for sensitive data in the credentials file and log warnings.

        Args:
            credentials_data: Credentials data to check
        """
        try:
            # Check for common sensitive keys
            sensitive_keys = [
                "password", "passwd", "pwd", "secret", "token", "key", "api_key",
                "private_key", "access_token", "refresh_token", "auth_token",
                "credit_card", "ssn", "social_security", "bank_account"
            ]
            
            # Check credentials section
            credentials = credentials_data.get("credentials", {})
            for key, value in credentials.items():
                if key.lower() in sensitive_keys:
                    logger.warning(f"Sensitive data found in credentials section: {key}")
            
            # Check custom fields section
            custom_fields = credentials_data.get("custom_fields", {})
            for key, value in custom_fields.items():
                if key.lower() in sensitive_keys:
                    logger.warning(f"Sensitive data found in custom fields section: {key}")
            
            # Check for potential plaintext passwords
            for key, value in credentials.items():
                if isinstance(value, str) and len(value) > 0:
                    # Check if value looks like a password (no spaces, contains mix of letters, numbers, symbols)
                    if " " not in value and any(c.isalpha() for c in value) and any(c.isdigit() for c in value) and any(not c.isalnum() for c in value):
                        logger.warning(f"Potential plaintext password found in credentials: {key}")
        
        except Exception as e:
            logger.error(f"Error checking for sensitive data: {e}")

    def _load_json_credentials(self, path: Path) -> Optional[Dict[str, Any]]:
        """
        Load credentials from a JSON file.

        Args:
            path: Path to the JSON file

        Returns:
            Dictionary with credentials data or None if failed
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in credentials file {path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading JSON credentials from {path}: {e}")
            return None

    def _validate_credentials_format(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Validate the format of the credentials data.

        Args:
            data: Credentials data to validate

        Returns:
            Error message if invalid, None if valid
        """
        # Check if data is a dictionary
        if not isinstance(data, dict):
            return "Credentials data must be a dictionary"
        
        # Check required sections
        for section in self.required_sections:
            if section not in data:
                return f"Missing required section: {section}"
        
        # Validate credentials section
        credentials = data.get("credentials", {})
        if not isinstance(credentials, dict):
            return "Credentials section must be a dictionary"
        
        # Validate config section
        config = data.get("config", {})
        if not isinstance(config, dict):
            return "Config section must be a dictionary"
        
        # Validate custom_fields section if present
        custom_fields = data.get("custom_fields", {})
        if custom_fields and not isinstance(custom_fields, dict):
            return "Custom fields section must be a dictionary"
        
        return None

    def get_credentials(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract credentials from session data.

        Args:
            session_data: Session data containing credentials

        Returns:
            Dictionary with credentials
        """
        return session_data.get("credentials", {})

    def get_config(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract config from session data.

        Args:
            session_data: Session data containing config

        Returns:
            Dictionary with config
        """
        return session_data.get("config", {})

    def get_custom_fields(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract custom fields from session data.

        Args:
            session_data: Session data containing custom fields

        Returns:
            Dictionary with custom fields
        """
        return session_data.get("custom_fields", {})


class CredentialsJsonWebAuthenticator(WebAuthenticator):
    """Web authenticator using JSON credentials files."""

    def __init__(self, engine):
        """
        Initialize the JSON credentials web authenticator.

        Args:
            engine: Automation engine instance
        """
        super().__init__(engine)
        self.auth_provider = CredentialsJsonAuthProvider()

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
        Authenticate using a JSON credentials file on a web page.

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
        # Check if JSON credentials file authentication is available
        if not await self.auth_provider.is_available(**kwargs):
            error_msg = "JSON credentials file authentication is not available"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Get credentials from file
        path = kwargs.get("path")
        
        if not path:
            error_msg = "No JSON credentials file path provided"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
        
        # Load credentials from file
        try:
            credential_path = Path(path).expanduser()
            
            # Check file permissions for security
            if not self.auth_provider._check_file_permissions(credential_path):
                error_msg = f"JSON credentials file has insecure permissions: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Check if file is in a version control directory
            if self.auth_provider._is_in_version_control(credential_path):
                error_msg = f"JSON credentials file is in a version control directory: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Load and validate JSON credentials
            credentials_data = self.auth_provider._load_json_credentials(credential_path)
            
            if not credentials_data:
                error_msg = f"Failed to load credentials from JSON file: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Validate required sections
            validation_error = self.auth_provider._validate_credentials_format(credentials_data)
            if validation_error:
                error_msg = f"Invalid credentials format: {validation_error}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            # Extract credentials
            credentials = credentials_data.get("credentials", {})
            config = credentials_data.get("config", {})
            
            # Get username and password from credentials
            username = credentials.get("username")
            password = credentials.get("password")
            
            if not username:
                error_msg = f"Username not found in JSON credentials file: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            if not password:
                error_msg = f"Password not found in JSON credentials file: {path}"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
            
            logger.info(f"Attempting web authentication using JSON credentials for user: {username}")
            
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
                    "auth_method": AuthMethod.CREDENTIALS_JSON.value,
                    "credentials_file": path,
                    "credentials": credentials,
                    "config": config,
                    "login_url": login_url
                }
                
                # Create result data
                data = {
                    "credentials_file": path,
                    "credentials": {k: "***" for k in credentials.keys()},  # Mask sensitive data
                    "config": config,
                    "login_url": login_url
                }
                
                logger.info(f"Web authentication successful using JSON credentials for user: {username}")
                
                return AuthResult(
                    success=True,
                    message=f"Web authentication successful for user: {username}",
                    data=data,
                    session_data=session_data
                )
            else:
                error_msg = "Web authentication failed using JSON credentials"
                logger.error(error_msg)
                return AuthResult(False, error_msg)
        
        except Exception as e:
            error_msg = f"Error during web authentication using JSON credentials: {e}"
            logger.error(error_msg)
            return AuthResult(False, error_msg)
