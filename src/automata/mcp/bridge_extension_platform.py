"""
Platform compatibility module for MCP Bridge Extension.

This module provides cross-platform compatibility for the MCP Bridge extension,
ensuring that the client works correctly on Linux, Windows, and macOS.
"""

import os
import platform
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

from ..core.logger import get_logger

logger = get_logger(__name__)


class PlatformCompatibilityError(Exception):
    """Base exception for platform compatibility errors."""
    pass


class UnsupportedPlatformError(PlatformCompatibilityError):
    """Exception raised when the platform is not supported."""
    pass


class PlatformConfigurationError(PlatformCompatibilityError):
    """Exception raised when platform configuration is invalid."""
    pass


class PlatformManager:
    """
    Manages platform-specific settings and behaviors for the MCP Bridge extension.
    """

    def __init__(self):
        """Initialize the platform manager."""
        self.system = platform.system()
        self.version = platform.version()
        self.architecture = platform.machine()
        self.python_version = platform.python_version()
        
        # Platform-specific settings
        self._settings = self._get_platform_settings()
        
        # Log platform information
        logger.info(f"Platform: {self.system} {self.version} ({self.architecture})")
        logger.info(f"Python: {self.python_version}")

    def _get_platform_settings(self) -> Dict[str, Any]:
        """
        Get platform-specific settings.
        
        Returns:
            Platform settings dictionary
        """
        settings = {
            "system": self.system,
            "version": self.version,
            "architecture": self.architecture,
            "python_version": self.python_version,
            "paths": {},
            "websocket": {},
            "security": {},
            "browser": {},
            "extension": {}  # Add the missing extension key
        }
        
        # Common paths
        home_dir = Path.home()
        settings["paths"]["home"] = str(home_dir)
        settings["paths"]["config"] = str(home_dir / ".automata")
        settings["paths"]["temp"] = str(Path.home() / ".automata" / "temp")
        
        # Create directories if they don't exist
        for path_key in ["config", "temp"]:
            path = Path(settings["paths"][path_key])
            path.mkdir(parents=True, exist_ok=True)
        
        # Platform-specific settings
        if self.system == "Windows":
            self._configure_windows(settings)
        elif self.system == "Linux":
            self._configure_linux(settings)
        elif self.system == "Darwin":  # macOS
            self._configure_macos(settings)
        else:
            logger.warning(f"Unsupported platform: {self.system}")
        
        return settings

    def _configure_windows(self, settings: Dict[str, Any]) -> None:
        """
        Configure Windows-specific settings.
        
        Args:
            settings: Settings dictionary to update
        """
        logger.debug("Configuring Windows-specific settings")
        
        # Windows paths
        app_data = os.environ.get("APPDATA", "")
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        
        if app_data:
            settings["paths"]["app_data"] = app_data
            settings["paths"]["config"] = str(Path(app_data) / "automata")
        
        if local_app_data:
            settings["paths"]["local_app_data"] = local_app_data
            settings["paths"]["temp"] = str(Path(local_app_data) / "automata" / "temp")
        
        # Create directories if they don't exist
        for path_key in ["config", "temp"]:
            path = Path(settings["paths"][path_key])
            path.mkdir(parents=True, exist_ok=True)
        
        # Windows WebSocket settings
        settings["websocket"]["library"] = "websockets"
        settings["websocket"]["ssl_context"] = "default"
        
        # Windows security settings
        settings["security"]["cert_store"] = "system"
        settings["security"]["cert_file"] = None
        
        # Windows browser settings
        settings["browser"]["default_paths"] = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
            "C:\\Program Files\\Microsoft Edge\\Application\\msedge.exe"
        ]
        
        # Windows extension settings
        settings["extension"]["profile_dir"] = str(Path(local_app_data) / "automata" / "extension_profile") if local_app_data else None

    def _configure_linux(self, settings: Dict[str, Any]) -> None:
        """
        Configure Linux-specific settings.
        
        Args:
            settings: Settings dictionary to update
        """
        logger.debug("Configuring Linux-specific settings")
        
        # Linux paths
        config_home = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        cache_home = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
        
        settings["paths"]["config"] = str(Path(config_home) / "automata")
        settings["paths"]["cache"] = str(Path(cache_home) / "automata")
        settings["paths"]["temp"] = str(Path(cache_home) / "automata" / "temp")
        
        # Create directories if they don't exist
        for path_key in ["config", "cache", "temp"]:
            path = Path(settings["paths"][path_key])
            path.mkdir(parents=True, exist_ok=True)
        
        # Linux WebSocket settings
        settings["websocket"]["library"] = "websockets"
        settings["websocket"]["ssl_context"] = "default"
        
        # Linux security settings
        settings["security"]["cert_store"] = "file"
        
        # Common Linux certificate locations
        cert_locations = [
            "/etc/ssl/certs/ca-certificates.crt",
            "/etc/pki/tls/certs/ca-bundle.crt",
            "/etc/ssl/ca-bundle.pem",
            "/usr/local/share/ca-certificates"
        ]
        
        for cert_file in cert_locations:
            if os.path.exists(cert_file):
                settings["security"]["cert_file"] = cert_file
                break
        else:
            settings["security"]["cert_file"] = None
        
        # Linux browser settings
        settings["browser"]["default_paths"] = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium",
            "/usr/bin/firefox",
            "/usr/bin/microsoft-edge"
        ]
        
        # Linux extension settings
        settings["extension"]["profile_dir"] = str(Path(config_home) / "automata" / "extension_profile")

    def _configure_macos(self, settings: Dict[str, Any]) -> None:
        """
        Configure macOS-specific settings.
        
        Args:
            settings: Settings dictionary to update
        """
        logger.debug("Configuring macOS-specific settings")
        
        # macOS paths
        home_dir = Path.home()
        settings["paths"]["config"] = str(home_dir / "Library" / "Application Support" / "automata")
        settings["paths"]["cache"] = str(home_dir / "Library" / "Caches" / "automata")
        settings["paths"]["temp"] = str(home_dir / "Library" / "Caches" / "automata" / "temp")
        
        # Create directories if they don't exist
        for path_key in ["config", "cache", "temp"]:
            path = Path(settings["paths"][path_key])
            path.mkdir(parents=True, exist_ok=True)
        
        # macOS WebSocket settings
        settings["websocket"]["library"] = "websockets"
        settings["websocket"]["ssl_context"] = "default"
        
        # macOS security settings
        settings["security"]["cert_store"] = "keychain"
        settings["security"]["cert_file"] = None
        
        # macOS browser settings
        settings["browser"]["default_paths"] = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Firefox.app/Contents/MacOS/firefox",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        ]
        
        # macOS extension settings
        settings["extension"]["profile_dir"] = str(home_dir / "Library" / "Application Support" / "automata" / "extension_profile")

    def get_settings(self) -> Dict[str, Any]:
        """
        Get platform-specific settings.
        
        Returns:
            Platform settings dictionary
        """
        return self._settings.copy()

    def get_path(self, path_type: str) -> str:
        """
        Get a platform-specific path.
        
        Args:
            path_type: Type of path (config, temp, etc.)
            
        Returns:
            Path string
            
        Raises:
            PlatformConfigurationError: If the path type is not found
        """
        if path_type not in self._settings["paths"]:
            raise PlatformConfigurationError(f"Unknown path type: {path_type}")
        
        return self._settings["paths"][path_type]

    def get_browser_path(self, browser_name: str = None) -> Optional[str]:
        """
        Get the path to a browser executable.
        
        Args:
            browser_name: Name of the browser (chrome, firefox, edge, etc.)
            
        Returns:
            Path to the browser executable, or None if not found
        """
        browser_paths = self._settings["browser"]["default_paths"]
        
        if browser_name:
            # Filter paths by browser name
            filtered_paths = []
            for path in browser_paths:
                path_lower = path.lower()
                if browser_name.lower() in path_lower:
                    filtered_paths.append(path)
            browser_paths = filtered_paths
        
        # Check if any of the paths exist
        for path in browser_paths:
            if os.path.exists(path):
                return path
        
        return None

    def get_websocket_config(self) -> Dict[str, Any]:
        """
        Get platform-specific WebSocket configuration.
        
        Returns:
            WebSocket configuration dictionary
        """
        return self._settings["websocket"].copy()

    def get_security_config(self) -> Dict[str, Any]:
        """
        Get platform-specific security configuration.
        
        Returns:
            Security configuration dictionary
        """
        return self._settings["security"].copy()

    def get_extension_config(self) -> Dict[str, Any]:
        """
        Get platform-specific extension configuration.
        
        Returns:
            Extension configuration dictionary
        """
        return self._settings["extension"].copy()

    def check_compatibility(self) -> Tuple[bool, List[str]]:
        """
        Check if the current platform is compatible with the MCP Bridge extension.
        
        Returns:
            Tuple of (is_compatible, list of issues)
        """
        is_compatible = True
        issues = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            is_compatible = False
            issues.append(f"Python version {python_version.major}.{python_version.minor} is not supported. Please use Python 3.8 or later.")
        
        # Check platform
        if self.system not in ["Windows", "Linux", "Darwin"]:
            is_compatible = False
            issues.append(f"Platform {self.system} is not supported.")
        
        # Check architecture
        if self.architecture not in ["x86_64", "AMD64", "arm64", "aarch64"]:
            issues.append(f"Architecture {self.architecture} may not be fully supported.")
        
        # Check for required dependencies
        try:
            import websockets
        except ImportError:
            is_compatible = False
            issues.append("websockets library is not installed.")
        
        try:
            import aiohttp
        except ImportError:
            is_compatible = False
            issues.append("aiohttp library is not installed.")
        
        return is_compatible, issues

    def get_platform_specific_help(self) -> str:
        """
        Get platform-specific help information.
        
        Returns:
            Help string
        """
        help_text = f"Platform: {self.system} {self.version}\n\n"
        
        if self.system == "Windows":
            help_text += (
                "Windows-specific help:\n"
                "- Make sure the browser extension is installed in Chrome, Firefox, or Edge.\n"
                "- Check that Windows Firewall allows connections on the WebSocket port.\n"
                "- If using Chrome, make sure remote debugging is enabled.\n"
            )
        elif self.system == "Linux":
            help_text += (
                "Linux-specific help:\n"
                "- Make sure the browser extension is installed in Chrome, Firefox, or Edge.\n"
                "- Check that your firewall allows connections on the WebSocket port.\n"
                "- If using Chrome, make sure remote debugging is enabled with --remote-debugging-port=9222.\n"
            )
        elif self.system == "Darwin":  # macOS
            help_text += (
                "macOS-specific help:\n"
                "- Make sure the browser extension is installed in Chrome, Firefox, or Edge.\n"
                "- Check that your firewall allows connections on the WebSocket port.\n"
                "- If using Chrome, make sure remote debugging is enabled with --remote-debugging-port=9222.\n"
            )
        
        return help_text


def get_platform_manager() -> PlatformManager:
    """
    Get a platform manager instance.
    
    Returns:
        PlatformManager instance
    """
    return PlatformManager()


def check_platform_compatibility() -> Tuple[bool, List[str]]:
    """
    Check if the current platform is compatible with the MCP Bridge extension.
    
    Returns:
        Tuple of (is_compatible, list of issues)
    """
    platform_manager = get_platform_manager()
    return platform_manager.check_compatibility()
