"""
Authentication method selection and configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import logging

from .base import AuthenticationManager, AuthMethod
from .environment import EnvironmentAuthProvider, EnvironmentWebAuthenticator
from .credential_file import CredentialFileAuthProvider, CredentialFileWebAuthenticator
from .credentials_json import CredentialsJsonAuthProvider, CredentialsJsonWebAuthenticator
from .interactive import InteractiveAuthProvider, InteractiveWebAuthenticator
from .session import SessionAuthProvider, CookieManager
from ..core.errors import AutomationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class AuthenticationConfig:
    """Configuration for authentication methods."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the authentication configuration.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        self.auth_manager = AuthenticationManager()
        self.cookie_manager = CookieManager()
        
        # Register authentication providers
        self._register_providers()

    def _get_default_config_path(self) -> str:
        """
        Get the default configuration file path.

        Returns:
            Default configuration file path
        """
        config_dir = Path.home() / ".automata"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "auth_config.json")

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.

        Returns:
            Configuration dictionary
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Create default configuration
                default_config = self._get_default_config()
                self._save_config(default_config)
                return default_config
        except Exception as e:
            logger.error(f"Error loading authentication config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get the default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "default_method": "environment",
            "methods": {
                "environment": {
                    "enabled": True,
                    "priority": 1,
                    "prefix": "AUTOMATA_AUTH_",
                    "username_var": "USERNAME",
                    "password_var": "PASSWORD"
                },
                "credential_file": {
                    "enabled": True,
                    "priority": 2,
                    "path": None,
                    "format": "json",
                    "username_key": "username",
                    "password_key": "password"
                },
                "credentials_json": {
                    "enabled": True,
                    "priority": 2,
                    "path": None
                },
                "interactive": {
                    "enabled": True,
                    "priority": 3,
                    "prompt_username": True,
                    "prompt_password": True,
                    "username_prompt": "Username: ",
                    "password_prompt": "Password: "
                },
                "session": {
                    "enabled": True,
                    "priority": 0,
                    "session_id": None,
                    "auto_save": True,
                    "auto_load": True,
                    "expiry_days": 7
                }
            },
            "web": {
                "default_method": "environment",
                "methods": {
                    "environment": {
                        "enabled": True,
                        "priority": 1,
                        "prefix": "AUTOMATA_AUTH_",
                        "username_var": "USERNAME",
                        "password_var": "PASSWORD"
                    },
                    "credential_file": {
                        "enabled": True,
                        "priority": 2,
                        "path": None,
                        "format": "json",
                        "username_key": "username",
                        "password_key": "password"
                    },
                    "credentials_json": {
                        "enabled": True,
                        "priority": 2,
                        "path": None
                    },
                    "interactive": {
                        "enabled": True,
                        "priority": 3,
                        "prompt_username": True,
                        "prompt_password": True,
                        "username_prompt": "Username: ",
                        "password_prompt": "Password: "
                    },
                    "session": {
                        "enabled": True,
                        "priority": 0,
                        "session_id": None,
                        "auto_save": True,
                        "auto_load": True,
                        "expiry_days": 7
                    }
                }
            }
        }

    def _save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary to save
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Authentication config saved to: {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving authentication config: {e}")

    def _register_providers(self) -> None:
        """Register authentication providers with the manager."""
        # Register environment provider
        self.auth_manager.register_provider(
            AuthMethod.ENVIRONMENT,
            EnvironmentAuthProvider()
        )
        
        # Register credential file provider
        self.auth_manager.register_provider(
            AuthMethod.CREDENTIAL_FILE,
            CredentialFileAuthProvider()
        )
        
        # Register JSON credentials provider
        self.auth_manager.register_provider(
            AuthMethod.CREDENTIALS_JSON,
            CredentialsJsonAuthProvider()
        )
        
        # Register interactive provider
        self.auth_manager.register_provider(
            AuthMethod.INTERACTIVE,
            InteractiveAuthProvider()
        )
        
        # Register session provider
        self.auth_manager.register_provider(
            AuthMethod.SESSION,
            SessionAuthProvider()
        )

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save the updated configuration
        self._save_config(self.config)

    def get_method_config(self, method: AuthMethod, is_web: bool = False) -> Dict[str, Any]:
        """
        Get configuration for a specific authentication method.

        Args:
            method: Authentication method
            is_web: Whether to get web-specific configuration

        Returns:
            Method configuration dictionary
        """
        section = "web" if is_web else "methods"
        method_name = method.value
        
        return self.get_config(f"{section}.{method_name}", {})

    def set_method_config(self, method: AuthMethod, config: Dict[str, Any], is_web: bool = False) -> None:
        """
        Set configuration for a specific authentication method.

        Args:
            method: Authentication method
            config: Method configuration dictionary
            is_web: Whether to set web-specific configuration
        """
        section = "web" if is_web else "methods"
        method_name = method.value
        
        self.set_config(f"{section}.{method_name}", config)

    def get_enabled_methods(self, is_web: bool = False) -> List[AuthMethod]:
        """
        Get list of enabled authentication methods.

        Args:
            is_web: Whether to get web-specific methods

        Returns:
            List of enabled authentication methods
        """
        section = "web" if is_web else "methods"
        methods = []
        
        for method in AuthMethod:
            method_config = self.get_config(f"{section}.{method.value}", {})
            if method_config.get("enabled", True):
                methods.append(method)
        
        # Sort by priority
        methods.sort(key=lambda m: self.get_config(f"{section}.{m.value}.priority", 999))
        
        return methods

    def get_default_method(self, is_web: bool = False) -> AuthMethod:
        """
        Get the default authentication method.

        Args:
            is_web: Whether to get web-specific default method

        Returns:
            Default authentication method
        """
        section = "web" if is_web else ""
        default_key = f"{section}.default_method" if section else "default_method"
        
        default_method_name = self.get_config(default_key, "environment")
        
        try:
            return AuthMethod(default_method_name)
        except ValueError:
            logger.warning(f"Invalid default method: {default_method_name}, using environment")
            return AuthMethod.ENVIRONMENT

    def set_default_method(self, method: AuthMethod, is_web: bool = False) -> None:
        """
        Set the default authentication method.

        Args:
            method: Authentication method to set as default
            is_web: Whether to set web-specific default method
        """
        section = "web" if is_web else ""
        default_key = f"{section}.default_method" if section else "default_method"
        
        self.set_config(default_key, method.value)

    def enable_method(self, method: AuthMethod, is_web: bool = False) -> None:
        """
        Enable an authentication method.

        Args:
            method: Authentication method to enable
            is_web: Whether to enable web-specific method
        """
        self.set_config(f"{'web.' if is_web else ''}methods.{method.value}.enabled", True)

    def disable_method(self, method: AuthMethod, is_web: bool = False) -> None:
        """
        Disable an authentication method.

        Args:
            method: Authentication method to disable
            is_web: Whether to disable web-specific method
        """
        self.set_config(f"{'web.' if is_web else ''}methods.{method.value}.enabled", False)

    def set_method_priority(self, method: AuthMethod, priority: int, is_web: bool = False) -> None:
        """
        Set the priority of an authentication method.

        Args:
            method: Authentication method
            priority: Priority value (lower = higher priority)
            is_web: Whether to set web-specific priority
        """
        self.set_config(f"{'web.' if is_web else ''}methods.{method.value}.priority", priority)

    def save(self) -> None:
        """Save the current configuration to file."""
        self._save_config(self.config)

    def reload(self) -> None:
        """Reload configuration from file."""
        self.config = self._load_config()

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self._get_default_config()
        self._save_config(self.config)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration dictionary
        """
        return self.config.copy()

    def from_dict(self, config: Dict[str, Any]) -> None:
        """
        Load configuration from dictionary.

        Args:
            config: Configuration dictionary
        """
        self.config = config.copy()
        self._save_config(self.config)


class AuthenticationFactory:
    """Factory for creating authentication instances."""

    def __init__(self, config: AuthenticationConfig):
        """
        Initialize the authentication factory.

        Args:
            config: Authentication configuration
        """
        self.config = config
        self.auth_manager = config.auth_manager
        self.cookie_manager = config.cookie_manager

    async def authenticate(self, is_web: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Authenticate using the configured methods.

        Args:
            is_web: Whether to use web-specific authentication
            **kwargs: Authentication parameters

        Returns:
            Authentication result dictionary
        """
        # Get enabled methods
        methods = self.config.get_enabled_methods(is_web)
        
        if not methods:
            error_msg = "No authentication methods are enabled"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Try each method in order of priority
        for method in methods:
            logger.info(f"Trying authentication method: {method.value}")
            
            # Get method configuration
            method_config = self.config.get_method_config(method, is_web)
            
            # Check if method is available
            if not await self.auth_manager.check_availability(method, **method_config):
                logger.info(f"Authentication method not available: {method.value}")
                continue
            
            # Try to authenticate
            result = await self.auth_manager.authenticate(method, **method_config, **kwargs)
            
            if result.success:
                logger.info(f"Authentication successful with method: {method.value}")
                return result.to_dict()
        
        # All methods failed
        error_msg = "All authentication methods failed"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    def create_web_authenticator(self, method: AuthMethod, engine):
        """
        Create a web authenticator for the specified method.

        Args:
            method: Authentication method
            engine: Automation engine instance

        Returns:
            Web authenticator instance
        """
        method_config = self.config.get_method_config(method, is_web=True)
        
        if method == AuthMethod.ENVIRONMENT:
            return EnvironmentWebAuthenticator(engine)
        elif method == AuthMethod.CREDENTIAL_FILE:
            return CredentialFileWebAuthenticator(engine)
        elif method == AuthMethod.CREDENTIALS_JSON:
            return CredentialsJsonWebAuthenticator(engine)
        elif method == AuthMethod.INTERACTIVE:
            return InteractiveWebAuthenticator(engine)
        elif method == AuthMethod.SESSION:
            # Session authentication doesn't need a web authenticator
            return None
        else:
            raise AutomationError(f"Unsupported authentication method: {method.value}")

    async def save_session(self, session_id: str, context, username: Optional[str] = None) -> str:
        """
        Save a session.

        Args:
            session_id: Session ID
            context: Browser context with cookies
            username: Username associated with the session

        Returns:
            Path to the saved session file
        """
        session_provider = self.auth_manager.get_provider(AuthMethod.SESSION)
        if not session_provider:
            raise AutomationError("Session authentication provider not found")
        
        return await session_provider.save_session(session_id, context, username)

    async def load_session(self, session_id: str, context) -> bool:
        """
        Load a session.

        Args:
            session_id: Session ID
            context: Browser context to load cookies into

        Returns:
            True if successful, False otherwise
        """
        method_config = self.config.get_method_config(AuthMethod.SESSION, is_web=True)
        method_config["session_id"] = session_id
        method_config["context"] = context
        
        result = await self.auth_manager.authenticate(AuthMethod.SESSION, **method_config)
        return result.success

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if successful, False otherwise
        """
        session_provider = self.auth_manager.get_provider(AuthMethod.SESSION)
        if not session_provider:
            raise AutomationError("Session authentication provider not found")
        
        return await session_provider.delete_session(session_id)

    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions.

        Returns:
            List of session information
        """
        session_provider = self.auth_manager.get_provider(AuthMethod.SESSION)
        if not session_provider:
            raise AutomationError("Session authentication provider not found")
        
        return await session_provider.list_sessions()

    async def cleanup_expired_sessions(self) -> int:
        """
        Delete all expired sessions.

        Returns:
            Number of deleted sessions
        """
        session_provider = self.auth_manager.get_provider(AuthMethod.SESSION)
        if not session_provider:
            raise AutomationError("Session authentication provider not found")
        
        return await session_provider.cleanup_expired_sessions()
