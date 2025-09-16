"""
Utility functions for working with the MCP Server.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Union

import aiohttp

from .config import AutomataConfig
from .logger import get_logger

logger = get_logger(__name__)


class MCPServerConnectionError(Exception):
    """Exception raised when MCP Server connection fails."""
    pass


class MCPServerCommandError(Exception):
    """Exception raised when MCP Server command execution fails."""
    pass


async def check_mcp_server_status(host: str = "localhost", port: int = 8080, 
                                 timeout: int = 5000) -> Dict[str, Any]:
    """
    Check the status of the MCP Server.
    
    Args:
        host: Server host
        port: Server port
        timeout: Request timeout in milliseconds
        
    Returns:
        Server status information
        
    Raises:
        MCPServerConnectionError: If connection fails
    """
    url = f"http://{host}:{port}/health"
    
    try:
        timeout_sec = timeout / 1000
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_sec)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise MCPServerConnectionError(f"Server returned HTTP {response.status}")
    except aiohttp.ClientError as e:
        raise MCPServerConnectionError(f"Connection error: {e}")
    except asyncio.TimeoutError:
        raise MCPServerConnectionError("Request timed out")


async def execute_mcp_server_command(command: Dict[str, Any], host: str = "localhost", 
                                    port: int = 8080, timeout: int = 30000) -> Dict[str, Any]:
    """
    Execute a command on the MCP Server.
    
    Args:
        command: Command to execute
        host: Server host
        port: Server port
        timeout: Request timeout in milliseconds
        
    Returns:
        Command execution result
        
    Raises:
        MCPServerConnectionError: If connection fails
        MCPServerCommandError: If command execution fails
    """
    url = f"http://{host}:{port}/command"
    
    try:
        timeout_sec = timeout / 1000
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_sec)) as session:
            async with session.post(url, json=command) as response:
                if response.status == 200:
                    result = await response.json()
                    if not result.get("success", False):
                        raise MCPServerCommandError(result.get("error", "Unknown error"))
                    return result.get("result", {})
                else:
                    error_text = await response.text()
                    raise MCPServerCommandError(f"Server returned HTTP {response.status}: {error_text}")
    except aiohttp.ClientError as e:
        raise MCPServerConnectionError(f"Connection error: {e}")
    except asyncio.TimeoutError:
        raise MCPServerConnectionError("Request timed out")
    except json.JSONDecodeError as e:
        raise MCPServerCommandError(f"Invalid JSON response: {e}")


async def execute_mcp_server_commands(commands: List[Dict[str, Any]], host: str = "localhost", 
                                     port: int = 8080, timeout: int = 30000) -> List[Dict[str, Any]]:
    """
    Execute multiple commands on the MCP Server.
    
    Args:
        commands: Commands to execute
        host: Server host
        port: Server port
        timeout: Request timeout in milliseconds
        
    Returns:
        List of command execution results
        
    Raises:
        MCPServerConnectionError: If connection fails
    """
    url = f"http://{host}:{port}/commands"
    
    try:
        timeout_sec = timeout / 1000
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_sec)) as session:
            async with session.post(url, json={"commands": commands}) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("results", [])
                else:
                    error_text = await response.text()
                    raise MCPServerConnectionError(f"Server returned HTTP {response.status}: {error_text}")
    except aiohttp.ClientError as e:
        raise MCPServerConnectionError(f"Connection error: {e}")
    except asyncio.TimeoutError:
        raise MCPServerConnectionError("Request timed out")
    except json.JSONDecodeError as e:
        raise MCPServerCommandError(f"Invalid JSON response: {e}")


async def get_mcp_server_commands(host: str = "localhost", port: int = 8080, 
                                 timeout: int = 5000) -> List[str]:
    """
    Get the list of supported commands from the MCP Server.
    
    Args:
        host: Server host
        port: Server port
        timeout: Request timeout in milliseconds
        
    Returns:
        List of supported commands
        
    Raises:
        MCPServerConnectionError: If connection fails
    """
    url = f"http://{host}:{port}/commands"
    
    try:
        timeout_sec = timeout / 1000
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_sec)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("commands", [])
                else:
                    error_text = await response.text()
                    raise MCPServerConnectionError(f"Server returned HTTP {response.status}: {error_text}")
    except aiohttp.ClientError as e:
        raise MCPServerConnectionError(f"Connection error: {e}")
    except asyncio.TimeoutError:
        raise MCPServerConnectionError("Request timed out")
    except json.JSONDecodeError as e:
        raise MCPServerCommandError(f"Invalid JSON response: {e}")


async def get_mcp_server_command_schema(command_type: str, host: str = "localhost", 
                                       port: int = 8080, timeout: int = 5000) -> Dict[str, Any]:
    """
    Get the schema for a specific command from the MCP Server.
    
    Args:
        command_type: Type of command
        host: Server host
        port: Server port
        timeout: Request timeout in milliseconds
        
    Returns:
        Command schema
        
    Raises:
        MCPServerConnectionError: If connection fails
    """
    url = f"http://{host}:{port}/commands/{command_type}"
    
    try:
        timeout_sec = timeout / 1000
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_sec)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("schema", {})
                else:
                    error_text = await response.text()
                    raise MCPServerConnectionError(f"Server returned HTTP {response.status}: {error_text}")
    except aiohttp.ClientError as e:
        raise MCPServerConnectionError(f"Connection error: {e}")
    except asyncio.TimeoutError:
        raise MCPServerConnectionError("Request timed out")
    except json.JSONDecodeError as e:
        raise MCPServerCommandError(f"Invalid JSON response: {e}")


async def stop_mcp_server(host: str = "localhost", port: int = 8080, 
                         timeout: int = 5000) -> bool:
    """
    Stop the MCP Server.
    
    Args:
        host: Server host
        port: Server port
        timeout: Request timeout in milliseconds
        
    Returns:
        True if server was stopped successfully, False otherwise
        
    Raises:
        MCPServerConnectionError: If connection fails
    """
    url = f"http://{host}:{port}/stop"
    
    try:
        timeout_sec = timeout / 1000
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout_sec)) as session:
            async with session.post(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("success", False)
                else:
                    return False
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return False


def create_navigate_command(url: str) -> Dict[str, Any]:
    """
    Create a navigate command.
    
    Args:
        url: URL to navigate to
        
    Returns:
        Navigate command
    """
    return {
        "type": "navigate",
        "url": url
    }


def create_click_command(selector: str) -> Dict[str, Any]:
    """
    Create a click command.
    
    Args:
        selector: CSS selector
        
    Returns:
        Click command
    """
    return {
        "type": "click",
        "selector": selector
    }


def create_fill_command(selector: str, value: str) -> Dict[str, Any]:
    """
    Create a fill command.
    
    Args:
        selector: CSS selector
        value: Value to fill
        
    Returns:
        Fill command
    """
    return {
        "type": "fill",
        "selector": selector,
        "value": value
    }


def create_screenshot_command(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a screenshot command.
    
    Args:
        path: Path to save screenshot
        
    Returns:
        Screenshot command
    """
    command = {
        "type": "screenshot"
    }
    
    if path:
        command["path"] = path
    
    return command


def create_wait_for_selector_command(selector: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """
    Create a wait for selector command.
    
    Args:
        selector: CSS selector
        timeout: Timeout in milliseconds
        
    Returns:
        Wait for selector command
    """
    command = {
        "type": "wait_for_selector",
        "selector": selector
    }
    
    if timeout:
        command["timeout"] = timeout
    
    return command


def create_wait_for_navigation_command(timeout: Optional[int] = None) -> Dict[str, Any]:
    """
    Create a wait for navigation command.
    
    Args:
        timeout: Timeout in milliseconds
        
    Returns:
        Wait for navigation command
    """
    command = {
        "type": "wait_for_navigation"
    }
    
    if timeout:
        command["timeout"] = timeout
    
    return command


def create_execute_script_command(script: str) -> Dict[str, Any]:
    """
    Create an execute script command.
    
    Args:
        script: JavaScript script to execute
        
    Returns:
        Execute script command
    """
    return {
        "type": "execute_script",
        "script": script
    }


def create_get_title_command() -> Dict[str, Any]:
    """
    Create a get title command.
    
    Returns:
        Get title command
    """
    return {
        "type": "get_title"
    }


def create_get_url_command() -> Dict[str, Any]:
    """
    Create a get URL command.
    
    Returns:
        Get URL command
    """
    return {
        "type": "get_url"
    }


def create_get_content_command() -> Dict[str, Any]:
    """
    Create a get content command.
    
    Returns:
        Get content command
    """
    return {
        "type": "get_content"
    }


def create_snapshot_command() -> Dict[str, Any]:
    """
    Create a snapshot command.
    
    Returns:
        Snapshot command
    """
    return {
        "type": "snapshot"
    }


def validate_command(command: Dict[str, Any]) -> bool:
    """
    Validate a command.
    
    Args:
        command: Command to validate
        
    Returns:
        True if command is valid, False otherwise
    """
    if not isinstance(command, dict):
        return False
    
    if "type" not in command:
        return False
    
    command_type = command["type"]
    
    # Validate based on command type
    if command_type == "navigate":
        return "url" in command and isinstance(command["url"], str)
    elif command_type == "click":
        return "selector" in command and isinstance(command["selector"], str)
    elif command_type == "fill":
        return ("selector" in command and isinstance(command["selector"], str) and
                "value" in command and isinstance(command["value"], str))
    elif command_type == "screenshot":
        return True  # Optional path parameter
    elif command_type == "wait_for_selector":
        return "selector" in command and isinstance(command["selector"], str)
    elif command_type == "wait_for_navigation":
        return True  # Optional timeout parameter
    elif command_type == "execute_script":
        return "script" in command and isinstance(command["script"], str)
    elif command_type in ["get_title", "get_url", "get_content", "snapshot"]:
        return True  # No additional parameters required
    else:
        return False  # Unknown command type


def load_commands_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Load commands from a file.
    
    Args:
        file_path: Path to the commands file
        
    Returns:
        List of commands
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
        ValueError: If file contains invalid commands
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, dict) or "commands" not in data:
            raise ValueError("Invalid commands file format")
        
        commands = data["commands"]
        
        if not isinstance(commands, list):
            raise ValueError("Commands must be a list")
        
        # Validate commands
        for i, command in enumerate(commands):
            if not validate_command(command):
                raise ValueError(f"Invalid command at index {i}: {command}")
        
        return commands
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Commands file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in commands file: {e}", e.doc, e.pos)


def save_commands_to_file(commands: List[Dict[str, Any]], file_path: str) -> None:
    """
    Save commands to a file.
    
    Args:
        commands: List of commands
        file_path: Path to save the commands file
        
    Raises:
        ValueError: If commands are invalid
    """
    # Validate commands
    for i, command in enumerate(commands):
        if not validate_command(command):
            raise ValueError(f"Invalid command at index {i}: {command}")
    
    # Create directory if it doesn't exist
    from pathlib import Path
    directory = Path(file_path).parent
    directory.mkdir(parents=True, exist_ok=True)
    
    # Save commands
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"commands": commands}, f, indent=2)
