"""
Exception classes for the MCP Server.
"""

from typing import Optional, Dict, Any


class MCPServerError(Exception):
    """Base exception for MCP Server errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize MCP Server error.
        
        Args:
            message: Error message
            details: Optional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class CommandValidationError(MCPServerError):
    """Exception raised when command validation fails."""
    
    def __init__(self, message: str, command: Optional[Dict[str, Any]] = None):
        """
        Initialize command validation error.
        
        Args:
            message: Error message
            command: Command that failed validation
        """
        super().__init__(message, {"command": command})
        self.command = command


class BrowserAutomationError(MCPServerError):
    """Exception raised when browser automation fails."""
    
    def __init__(self, message: str, command: Optional[Dict[str, Any]] = None):
        """
        Initialize browser automation error.
        
        Args:
            message: Error message
            command: Command that failed execution
        """
        super().__init__(message, {"command": command})
        self.command = command


class ConfigurationError(MCPServerError):
    """Exception raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
        """
        super().__init__(message, {"config_key": config_key})
        self.config_key = config_key
