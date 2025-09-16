"""
Security module for MCP Bridge Extension connection.

This module provides authentication and security functionality for connecting
to the Playwright MCP Bridge extension, including token management,
secure communication, and cross-platform compatibility.
"""

import asyncio
import base64
import hashlib
import hmac
import json
import os
import platform
import secrets
import ssl
from typing import Dict, Any, Optional, Union, Tuple
from pathlib import Path

import aiohttp
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from ..core.logger import get_logger

logger = get_logger(__name__)


class MCPBridgeExtensionSecurityError(Exception):
    """Base exception for MCP Bridge extension security errors."""
    pass


class AuthenticationError(MCPBridgeExtensionSecurityError):
    """Exception raised when authentication fails."""
    pass


class SecurityConfigurationError(MCPBridgeExtensionSecurityError):
    """Exception raised when security configuration is invalid."""
    pass


class TokenManager:
    """
    Manages authentication tokens for the MCP Bridge extension.
    """

    def __init__(self, token_file: str = None):
        """
        Initialize the token manager.
        
        Args:
            token_file: Path to the token file
        """
        if token_file is None:
            # Default token file location
            home_dir = Path.home()
            token_file = home_dir / ".automata" / "mcp_bridge_tokens.json"
        
        self.token_file = Path(token_file)
        self.tokens = {}
        
        # Create directory if it doesn't exist
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing tokens
        self._load_tokens()

    def _load_tokens(self) -> None:
        """Load tokens from the token file."""
        if self.token_file.exists():
            try:
                with open(self.token_file, "r", encoding="utf-8") as f:
                    self.tokens = json.load(f)
                logger.debug(f"Loaded tokens from {self.token_file}")
            except Exception as e:
                logger.error(f"Failed to load tokens: {e}")
                self.tokens = {}

    def _save_tokens(self) -> None:
        """Save tokens to the token file."""
        try:
            with open(self.token_file, "w", encoding="utf-8") as f:
                json.dump(self.tokens, f, indent=2)
            logger.debug(f"Saved tokens to {self.token_file}")
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")

    def get_token(self, extension_id: str) -> Optional[str]:
        """
        Get the authentication token for an extension.
        
        Args:
            extension_id: ID of the extension
            
        Returns:
            Authentication token, or None if not found
        """
        return self.tokens.get(extension_id)

    def set_token(self, extension_id: str, token: str) -> None:
        """
        Set the authentication token for an extension.
        
        Args:
            extension_id: ID of the extension
            token: Authentication token
        """
        self.tokens[extension_id] = token
        self._save_tokens()

    def remove_token(self, extension_id: str) -> bool:
        """
        Remove the authentication token for an extension.
        
        Args:
            extension_id: ID of the extension
            
        Returns:
            True if the token was removed, False if it didn't exist
        """
        if extension_id in self.tokens:
            del self.tokens[extension_id]
            self._save_tokens()
            return True
        return False

    def generate_token(self, extension_id: str) -> str:
        """
        Generate a new authentication token for an extension.
        
        Args:
            extension_id: ID of the extension
            
        Returns:
            New authentication token
        """
        # Generate a secure random token
        token = secrets.token_urlsafe(32)
        self.set_token(extension_id, token)
        return token

    def verify_token(self, extension_id: str, token: str) -> bool:
        """
        Verify an authentication token for an extension.
        
        Args:
            extension_id: ID of the extension
            token: Token to verify
            
        Returns:
            True if the token is valid, False otherwise
        """
        stored_token = self.get_token(extension_id)
        if stored_token is None:
            return False
        
        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(stored_token, token)


class SecureCommunicator:
    """
    Handles secure communication with the MCP Bridge extension.
    """

    def __init__(self, token_manager: TokenManager):
        """
        Initialize the secure communicator.
        
        Args:
            token_manager: Token manager instance
        """
        self.token_manager = token_manager
        self.session = None
        self.ssl_context = None

    async def initialize(self) -> None:
        """Initialize the secure communicator."""
        # Create SSL context for secure connections
        self.ssl_context = ssl.create_default_context()
        
        # Configure SSL context based on platform
        system = platform.system()
        if system == "Windows":
            # Windows-specific SSL configuration
            self.ssl_context.load_default_certs()
        elif system == "Linux":
            # Linux-specific SSL configuration
            self.ssl_context.load_default_certs()
        elif system == "Darwin":  # macOS
            # macOS-specific SSL configuration
            self.ssl_context.load_default_certs()
        
        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)

    async def close(self) -> None:
        """Close the secure communicator."""
        if self.session:
            await self.session.close()
            self.session = None

    async def send_authenticated_request(
        self,
        url: str,
        method: str = "GET",
        data: Dict[str, Any] = None,
        extension_id: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """
        Send an authenticated request to the extension.
        
        Args:
            url: URL to send the request to
            method: HTTP method
            data: Request data
            extension_id: Extension ID
            token: Authentication token
            
        Returns:
            Response data
            
        Raises:
            AuthenticationError: If authentication fails
            MCPBridgeExtensionSecurityError: If the request fails
        """
        if not self.session:
            await self.initialize()
        
        # Get token if not provided
        if token is None:
            if extension_id is None:
                raise SecurityConfigurationError("Either extension_id or token must be provided")
            
            token = self.token_manager.get_token(extension_id)
            if token is None:
                raise AuthenticationError(f"No authentication token found for extension {extension_id}")
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Add platform-specific headers
        system = platform.system()
        headers["X-Platform"] = system
        headers["X-Platform-Version"] = platform.version()
        
        try:
            # Send request
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers, ssl=self.ssl_context) as response:
                    response_data = await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers, ssl=self.ssl_context) as response:
                    response_data = await response.json()
            else:
                raise SecurityConfigurationError(f"Unsupported HTTP method: {method}")
            
            # Check response status
            if response.status == 401:
                raise AuthenticationError("Authentication failed: Invalid token")
            elif response.status == 403:
                raise AuthenticationError("Authentication failed: Access denied")
            elif response.status >= 400:
                raise MCPBridgeExtensionSecurityError(
                    f"Request failed with status {response.status}: {response_data.get('message', 'Unknown error')}"
                )
            
            return response_data
        
        except aiohttp.ClientError as e:
            raise MCPBridgeExtensionSecurityError(f"Request failed: {e}")

    async def establish_secure_websocket(
        self,
        websocket_url: str,
        extension_id: str = None,
        token: str = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Establish a secure WebSocket connection.
        
        Args:
            websocket_url: WebSocket URL
            extension_id: Extension ID
            token: Authentication token
            
        Returns:
            Tuple of (WebSocket connection, response data)
            
        Raises:
            AuthenticationError: If authentication fails
            MCPBridgeExtensionSecurityError: If the connection fails
        """
        # Get token if not provided
        if token is None:
            if extension_id is None:
                raise SecurityConfigurationError("Either extension_id or token must be provided")
            
            token = self.token_manager.get_token(extension_id)
            if token is None:
                raise AuthenticationError(f"No authentication token found for extension {extension_id}")
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Add platform-specific headers
        system = platform.system()
        headers["X-Platform"] = system
        headers["X-Platform-Version"] = platform.version()
        
        try:
            # Import websockets here to avoid issues if it's not available
            import websockets
            
            # Establish WebSocket connection
            websocket = await websockets.connect(
                websocket_url,
                extra_headers=headers,
                ssl=self.ssl_context if websocket_url.startswith("wss://") else None
            )
            
            # Wait for authentication response
            response_str = await websocket.recv()
            response_data = json.loads(response_str)
            
            # Check authentication response
            if response_data.get("type") == "error" and response_data.get("code") == 401:
                await websocket.close()
                raise AuthenticationError("WebSocket authentication failed: Invalid token")
            elif response_data.get("type") == "error" and response_data.get("code") == 403:
                await websocket.close()
                raise AuthenticationError("WebSocket authentication failed: Access denied")
            
            return websocket, response_data
        
        except Exception as e:
            if isinstance(e, (AuthenticationError, MCPBridgeExtensionSecurityError)):
                raise
            raise MCPBridgeExtensionSecurityError(f"WebSocket connection failed: {e}")


class MCPBridgeExtensionSecurity:
    """
    Main security class for MCP Bridge extension connections.
    """

    def __init__(self, token_file: str = None):
        """
        Initialize the security manager.
        
        Args:
            token_file: Path to the token file
        """
        self.token_manager = TokenManager(token_file)
        self.secure_communicator = SecureCommunicator(self.token_manager)
        self.initialized = False

    async def initialize(self) -> None:
        """Initialize the security manager."""
        if not self.initialized:
            await self.secure_communicator.initialize()
            self.initialized = True

    async def close(self) -> None:
        """Close the security manager."""
        if self.initialized:
            await self.secure_communicator.close()
            self.initialized = False

    async def authenticate_extension(self, extension_id: str, token: str = None) -> bool:
        """
        Authenticate with an extension.
        
        Args:
            extension_id: ID of the extension
            token: Authentication token (optional, will generate if not provided)
            
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            await self.initialize()
            
            # Generate token if not provided
            if token is None:
                token = self.token_manager.generate_token(extension_id)
            else:
                # Store the provided token
                self.token_manager.set_token(extension_id, token)
            
            # For now, we'll consider authentication successful if we have a token
            # In a real implementation, we would verify the token with the extension
            return True
        
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    async def send_secure_request(
        self,
        url: str,
        method: str = "GET",
        data: Dict[str, Any] = None,
        extension_id: str = None,
        token: str = None
    ) -> Dict[str, Any]:
        """
        Send a secure request to the extension.
        
        Args:
            url: URL to send the request to
            method: HTTP method
            data: Request data
            extension_id: Extension ID
            token: Authentication token
            
        Returns:
            Response data
        """
        await self.initialize()
        return await self.secure_communicator.send_authenticated_request(
            url, method, data, extension_id, token
        )

    async def establish_secure_websocket(
        self,
        websocket_url: str,
        extension_id: str = None,
        token: str = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Establish a secure WebSocket connection.
        
        Args:
            websocket_url: WebSocket URL
            extension_id: Extension ID
            token: Authentication token
            
        Returns:
            Tuple of (WebSocket connection, response data)
        """
        await self.initialize()
        return await self.secure_communicator.establish_secure_websocket(
            websocket_url, extension_id, token
        )

    def get_platform_config(self) -> Dict[str, Any]:
        """
        Get platform-specific configuration.
        
        Returns:
            Platform configuration dictionary
        """
        system = platform.system()
        config = {
            "platform": system,
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version()
        }
        
        # Add platform-specific settings
        if system == "Windows":
            config["ssl_cert_file"] = None  # Windows uses system certificate store
            config["websocket_library"] = "websockets"
        elif system == "Linux":
            # Common Linux certificate locations
            cert_locations = [
                "/etc/ssl/certs/ca-certificates.crt",
                "/etc/pki/tls/certs/ca-bundle.crt",
                "/etc/ssl/ca-bundle.pem"
            ]
            for cert_file in cert_locations:
                if os.path.exists(cert_file):
                    config["ssl_cert_file"] = cert_file
                    break
            else:
                config["ssl_cert_file"] = None
            config["websocket_library"] = "websockets"
        elif system == "Darwin":  # macOS
            config["ssl_cert_file"] = None  # macOS uses system keychain
            config["websocket_library"] = "websockets"
        
        return config

    def validate_security_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate security configuration.
        
        Args:
            config: Security configuration dictionary
            
        Returns:
            True if the configuration is valid, False otherwise
        """
        required_keys = ["extension_id"]
        for key in required_keys:
            if key not in config:
                logger.error(f"Missing required security configuration key: {key}")
                return False
        
        # Validate token if provided
        if "token" in config:
            extension_id = config["extension_id"]
            token = config["token"]
            if not self.token_manager.verify_token(extension_id, token):
                logger.error("Invalid token in security configuration")
                return False
        
        return True