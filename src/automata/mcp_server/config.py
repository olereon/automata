"""
MCP Server configuration module.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class MCPServerConfig:
    """Configuration class for MCP Server."""
    
    def __init__(self):
        """Initialize MCP Server configuration with default values."""
        self.config = {
            "server": {
                "host": "localhost",
                "port": 8080,
                "log_level": "INFO"
            },
            "browser": {
                "type": "chromium",
                "headless": True,
                "timeout": 30000
            },
            "server_settings": {
                "max_connections": 10,
                "extension_mode": False
            }
        }
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            file_path: Path to the configuration file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # Update configuration with file contents
            self._update_config(file_config)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            file_path: Path to save the configuration file
        """
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def get_server_host(self) -> str:
        """Get the server host."""
        return self.config["server"]["host"]
    
    def set_server_host(self, host: str) -> None:
        """
        Set the server host.
        
        Args:
            host: Server host
        """
        self.config["server"]["host"] = host
    
    def get_server_port(self) -> int:
        """Get the server port."""
        return self.config["server"]["port"]
    
    def set_server_port(self, port: int) -> None:
        """
        Set the server port.
        
        Args:
            port: Server port
        """
        self.config["server"]["port"] = port
    
    def get_log_level(self) -> str:
        """Get the log level."""
        return self.config["server"]["log_level"]
    
    def set_log_level(self, level: str) -> None:
        """
        Set the log level.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.config["server"]["log_level"] = level
    
    def get_browser_type(self) -> str:
        """Get the browser type."""
        return self.config["browser"]["type"]
    
    def set_browser_type(self, browser_type: str) -> None:
        """
        Set the browser type.
        
        Args:
            browser_type: Browser type (chromium, firefox, webkit)
        """
        self.config["browser"]["type"] = browser_type
    
    def is_headless(self) -> bool:
        """Check if browser should run in headless mode."""
        return self.config["browser"]["headless"]
    
    def set_headless(self, headless: bool) -> None:
        """
        Set headless mode.
        
        Args:
            headless: Whether to run in headless mode
        """
        self.config["browser"]["headless"] = headless
    
    def get_timeout(self) -> int:
        """Get the timeout in milliseconds."""
        return self.config["browser"]["timeout"]
    
    def set_timeout(self, timeout: int) -> None:
        """
        Set the timeout.
        
        Args:
            timeout: Timeout in milliseconds
        """
        self.config["browser"]["timeout"] = timeout
    
    def get_max_connections(self) -> int:
        """Get the maximum number of connections."""
        return self.config["server_settings"]["max_connections"]
    
    def set_max_connections(self, max_connections: int) -> None:
        """
        Set the maximum number of connections.
        
        Args:
            max_connections: Maximum number of connections
        """
        self.config["server_settings"]["max_connections"] = max_connections
    
    def is_extension_mode(self) -> bool:
        """Check if extension mode is enabled."""
        return self.config["server_settings"]["extension_mode"]
    
    def set_extension_mode(self, extension_mode: bool) -> None:
        """
        Set extension mode.
        
        Args:
            extension_mode: Whether to enable extension mode
        """
        self.config["server_settings"]["extension_mode"] = extension_mode
    
    def _update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update configuration with new values.
        
        Args:
            new_config: New configuration dictionary
        """
        def update_dict_recursive(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
            for key, value in update_dict.items():
                if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                    update_dict_recursive(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        update_dict_recursive(self.config, new_config)
    
    @classmethod
    def load_default(cls) -> 'MCPServerConfig':
        """
        Load default configuration.
        
        Returns:
            Default configuration instance
        """
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
        """
        self._update_config(config_dict)
