"""
MCP configuration module for managing MCP Bridge settings.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from ..core.logger import get_logger

logger = get_logger(__name__)


class MCPConfiguration:
    """Configuration class for MCP Bridge settings."""

    def __init__(self):
        """Initialize MCP configuration with default values."""
        self._config = {
            "server": {
                "url": "ws://localhost:8080",
                "timeout": 30000,
                "retry_attempts": 3,
                "retry_delay": 1000
            },
            "bridge": {
                "extension_mode": False,
                "extension_port": 9222
            }
        }

    def get_server_url(self) -> str:
        """Get the MCP server URL."""
        return self._config["server"]["url"]

    def set_server_url(self, url: str) -> None:
        """Set the MCP server URL."""
        self._config["server"]["url"] = url

    def get_timeout(self) -> int:
        """Get the timeout in milliseconds."""
        return self._config["server"]["timeout"]

    def set_timeout(self, timeout: int) -> None:
        """Set the timeout in milliseconds."""
        self._config["server"]["timeout"] = timeout

    def get_retry_attempts(self) -> int:
        """Get the number of retry attempts."""
        return self._config["server"]["retry_attempts"]

    def set_retry_attempts(self, attempts: int) -> None:
        """Set the number of retry attempts."""
        self._config["server"]["retry_attempts"] = attempts

    def get_retry_delay(self) -> int:
        """Get the retry delay in milliseconds."""
        return self._config["server"]["retry_delay"]

    def set_retry_delay(self, delay: int) -> None:
        """Set the retry delay in milliseconds."""
        self._config["server"]["retry_delay"] = delay

    def is_bridge_extension_enabled(self) -> bool:
        """Check if bridge extension mode is enabled."""
        return self._config["bridge"]["extension_mode"]

    def set_bridge_extension_enabled(self, enabled: bool) -> None:
        """Enable or disable bridge extension mode."""
        self._config["bridge"]["extension_mode"] = enabled

    def get_bridge_extension_port(self) -> int:
        """Get the bridge extension port."""
        return self._config["bridge"]["extension_port"]

    def set_bridge_extension_port(self, port: int) -> None:
        """Set the bridge extension port."""
        self._config["bridge"]["extension_port"] = port

    def load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a file.

        Args:
            file_path: Path to the configuration file
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            # Update configuration with loaded data
            if "server" in config_data:
                self._config["server"].update(config_data["server"])
            
            if "bridge" in config_data:
                self._config["bridge"].update(config_data["bridge"])
            
            logger.info(f"Loaded MCP configuration from: {file_path}")
        
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
            raise

    def save_to_file(self, file_path: str) -> None:
        """
        Save configuration to a file.

        Args:
            file_path: Path to save the configuration file
        """
        try:
            # Create directory if it doesn't exist
            directory = Path(file_path).parent
            directory.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
            
            logger.info(f"Saved MCP configuration to: {file_path}")
        
        except Exception as e:
            logger.error(f"Error saving configuration to {file_path}: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as a dictionary."""
        return self._config.copy()

    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from a dictionary.

        Args:
            config_dict: Configuration dictionary
        """
        if "server" in config_dict:
            self._config["server"].update(config_dict["server"])
        
        if "bridge" in config_dict:
            self._config["bridge"].update(config_dict["bridge"])

    @classmethod
    def load_default(cls) -> 'MCPConfiguration':
        """
        Load configuration from default location.

        Returns:
            MCPConfiguration instance with loaded configuration
        """
        config = cls()
        default_path = os.path.expanduser("~/.automata/mcp_config.json")
        
        if os.path.exists(default_path):
            config.load_from_file(default_path)
        
        return config