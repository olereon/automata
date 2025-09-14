"""
Authentication module for web automation.

This module provides a flexible authentication framework supporting multiple methods:
- Environment variables
- Credential files
- Interactive login
- Session persistence
"""

from .base import (
    AuthMethod,
    AuthResult,
    AuthenticationProvider,
    AuthenticationManager,
    WebAuthenticator
)

from .environment import (
    EnvironmentAuthProvider,
    EnvironmentWebAuthenticator
)

from .credential_file import (
    CredentialFileAuthProvider,
    CredentialFileWebAuthenticator
)

from .interactive import (
    InteractiveAuthProvider,
    InteractiveWebAuthenticator
)

from .session import (
    SessionAuthProvider,
    CookieManager
)

from .config import (
    AuthenticationConfig,
    AuthenticationFactory
)

__all__ = [
    # Base classes
    "AuthMethod",
    "AuthResult",
    "AuthenticationProvider",
    "AuthenticationManager",
    "WebAuthenticator",
    
    # Environment authentication
    "EnvironmentAuthProvider",
    "EnvironmentWebAuthenticator",
    
    # Credential file authentication
    "CredentialFileAuthProvider",
    "CredentialFileWebAuthenticator",
    
    # Interactive authentication
    "InteractiveAuthProvider",
    "InteractiveWebAuthenticator",
    
    # Session authentication
    "SessionAuthProvider",
    "CookieManager",
    
    # Configuration
    "AuthenticationConfig",
    "AuthenticationFactory"
]
