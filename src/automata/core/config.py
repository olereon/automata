"""
Configuration module for managing Automata settings.
"""

import json
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path

from .logger import get_logger

logger = get_logger(__name__)


class AutomataConfig:
    """Configuration class for Automata settings."""

    def __init__(self):
        """Initialize Automata configuration with default values."""
        self._config = {
            "general": {
                "version": "1.0.0",
                "debug": False,
                "log_level": "INFO"
            },
            "browser": {
                "headless": True,
                "browser_type": "chromium",
                "viewport": {
                    "width": 1280,
                    "height": 720
                },
                "default_timeout": 30000,
                "screenshot_on_error": True,
                "retry_attempts": 3,
                "retry_delay": 1000
            },
            "mcp_bridge": {
                "enabled": False,
                "server": {
                    "url": "ws://localhost:8080",
                    "timeout": 30000,
                    "retry_attempts": 3,
                    "retry_delay": 1000
                },
                "bridge": {
                    "extension_mode": False,
                    "extension_port": 9222
                },
                "bridge_extension": {
                    "extension_id": None,
                    "websocket_url": "ws://localhost:9222",
                    "connection_timeout": 30000,
                    "retry_attempts": 3,
                    "retry_delay": 1000,
                    "auth_token": None
                }
            },
            "mcp_server": {
                "enabled": False,
                "server": {
                    "host": "localhost",
                    "port": 8080,
                    "path": "/mcp",
                    "timeout": 30000,
                    "max_connections": 10
                },
                "browser": {
                    "headless": True,
                    "browser_type": "chromium",
                    "viewport": {
                        "width": 1280,
                        "height": 720
                    },
                    "default_timeout": 30000,
                    "screenshot_on_error": True,
                    "retry_attempts": 3,
                    "retry_delay": 1000
                },
                "security": {
                    "enable_cors": True,
                    "allowed_origins": ["*"],
                    "enable_authentication": False,
                    "api_key": None
                },
                "logging": {
                    "level": "INFO",
                    "log_dir": None,
                    "enable_console": True,
                    "enable_file": True,
                    "enable_screenshots": True,
                    "enable_html": True
                },
                "platform": {
                    "auto_detect": True,
                    "windows_specific": {
                        "executable_path": None,
                        "temp_dir": None
                    },
                    "linux_specific": {
                        "executable_path": None,
                        "temp_dir": None
                    }
                }
            },
            "session": {
                "default_expiry_days": 30,
                "encryption_enabled": False,
                "session_dir": None
            }
        }

    def get_debug(self) -> bool:
        """Get whether debug mode is enabled."""
        return self._config["general"]["debug"]

    def set_debug(self, debug: bool) -> None:
        """Set whether debug mode is enabled."""
        self._config["general"]["debug"] = debug

    def get_log_level(self) -> str:
        """Get the log level."""
        return self._config["general"]["log_level"]

    def set_log_level(self, level: str) -> None:
        """Set the log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level not in valid_levels:
            raise ValueError(f"Invalid log level: {level}")
        self._config["general"]["log_level"] = level

    def is_mcp_bridge_enabled(self) -> bool:
        """Get whether MCP Bridge is enabled."""
        return self._config["mcp_bridge"]["enabled"]

    def set_mcp_bridge_enabled(self, enabled: bool) -> None:
        """Set whether MCP Bridge is enabled."""
        self._config["mcp_bridge"]["enabled"] = enabled

    def get_mcp_bridge_config(self) -> Dict[str, Any]:
        """Get MCP Bridge configuration."""
        return self._config["mcp_bridge"].copy()

    def set_mcp_bridge_config(self, config: Dict[str, Any]) -> None:
        """Set MCP Bridge configuration."""
        if "mcp_bridge" in config:
            self._config["mcp_bridge"].update(config["mcp_bridge"])

    def is_mcp_server_enabled(self) -> bool:
        """Get whether MCP Server is enabled."""
        return self._config["mcp_server"]["enabled"]

    def set_mcp_server_enabled(self, enabled: bool) -> None:
        """Set whether MCP Server is enabled."""
        self._config["mcp_server"]["enabled"] = enabled

    def get_mcp_server_config(self) -> Dict[str, Any]:
        """Get MCP Server configuration."""
        return self._config["mcp_server"].copy()

    def set_mcp_server_config(self, config: Dict[str, Any]) -> None:
        """Set MCP Server configuration."""
        if "mcp_server" in config:
            self._config["mcp_server"].update(config["mcp_server"])

    def get_session_expiry_days(self) -> int:
        """Get the default session expiry days."""
        return self._config["session"]["default_expiry_days"]

    def set_session_expiry_days(self, days: int) -> None:
        """Set the default session expiry days."""
        if days < 1:
            raise ValueError(f"Invalid session expiry days: {days}")
        self._config["session"]["default_expiry_days"] = days

    def is_session_encryption_enabled(self) -> bool:
        """Get whether session encryption is enabled."""
        return self._config["session"]["encryption_enabled"]

    def set_session_encryption_enabled(self, enabled: bool) -> None:
        """Set whether session encryption is enabled."""
        self._config["session"]["encryption_enabled"] = enabled

    def get_session_dir(self) -> Optional[str]:
        """Get the session directory."""
        return self._config["session"]["session_dir"]

    def set_session_dir(self, session_dir: Optional[str]) -> None:
        """Set the session directory."""
        self._config["session"]["session_dir"] = session_dir

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
            self._update_from_dict(config_data)
            
            logger.info(f"Loaded Automata configuration from: {file_path}")
        
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file {file_path}: {e}")
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            logger.error(f"Error loading configuration from {file_path}: {e}")
            raise ValueError(f"Error loading configuration: {e}")

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
            
            logger.info(f"Saved Automata configuration to: {file_path}")
        
        except Exception as e:
            logger.error(f"Error saving configuration to {file_path}: {e}")
            raise ValueError(f"Error saving configuration: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as a dictionary."""
        return self._config.copy()

    def _update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from a dictionary.

        Args:
            config_dict: Configuration dictionary
        """
        for section, values in config_dict.items():
            if section in self._config:
                if isinstance(values, dict) and isinstance(self._config[section], dict):
                    self._config[section].update(values)
                else:
                    self._config[section] = values

    @classmethod
    def load_default(cls) -> 'AutomataConfig':
        """
        Load configuration from default location.

        Returns:
            AutomataConfig instance with loaded configuration
        """
        config = cls()
        
        # Load from environment variables
        config._load_from_env()
        
        # Load from default file path
        default_path = os.path.expanduser("~/.automata/config.json")
        if os.path.exists(default_path):
            config.load_from_file(default_path)
        
        return config

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # General settings
        if "AUTOMATA_DEBUG" in os.environ:
            self.set_debug(os.environ["AUTOMATA_DEBUG"].lower() in ("true", "1", "yes"))
        
        if "AUTOMATA_LOG_LEVEL" in os.environ:
            self.set_log_level(os.environ["AUTOMATA_LOG_LEVEL"])
        
        # MCP Bridge settings
        if "AUTOMATA_MCP_BRIDGE_ENABLED" in os.environ:
            self.set_mcp_bridge_enabled(os.environ["AUTOMATA_MCP_BRIDGE_ENABLED"].lower() in ("true", "1", "yes"))
        
        if "AUTOMATA_MCP_BRIDGE_URL" in os.environ:
            self._config["mcp_bridge"]["server"]["url"] = os.environ["AUTOMATA_MCP_BRIDGE_URL"]
        
        # MCP Server settings
        if "AUTOMATA_MCP_SERVER_ENABLED" in os.environ:
            self.set_mcp_server_enabled(os.environ["AUTOMATA_MCP_SERVER_ENABLED"].lower() in ("true", "1", "yes"))
        
        if "AUTOMATA_MCP_SERVER_HOST" in os.environ:
            self._config["mcp_server"]["server"]["host"] = os.environ["AUTOMATA_MCP_SERVER_HOST"]
        
        if "AUTOMATA_MCP_SERVER_PORT" in os.environ:
            try:
                port = int(os.environ["AUTOMATA_MCP_SERVER_PORT"])
                self._config["mcp_server"]["server"]["port"] = port
            except ValueError:
                logger.warning(f"Invalid AUTOMATA_MCP_SERVER_PORT value: {os.environ['AUTOMATA_MCP_SERVER_PORT']}")
        
        # Session settings
        if "AUTOMATA_SESSION_ENCRYPTION_ENABLED" in os.environ:
            self.set_session_encryption_enabled(os.environ["AUTOMATA_SESSION_ENCRYPTION_ENABLED"].lower() in ("true", "1", "yes"))
        
        if "AUTOMATA_SESSION_DIR" in os.environ:
            self.set_session_dir(os.environ["AUTOMATA_SESSION_DIR"])
