#!/usr/bin/env python3.11
"""
Example script demonstrating how to use the MCP Server integration.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from automata.core.config import AutomataConfig
from automata.core.mcp_server_utils import (
    check_mcp_server_status,
    execute_mcp_server_command,
    execute_mcp_server_commands,
    get_mcp_server_commands,
    load_commands_from_file,
    create_navigate_command,
    create_get_title_command,
    create_screenshot_command
)


async def main():
    """Main function demonstrating MCP Server usage."""
    
    # Load configuration
    config = AutomataConfig.load_default()
    
    # Check if MCP Server is enabled
    if not config.is_mcp_server_enabled():
        print("MCP Server is not enabled in the configuration.")
        return
    
    # Get MCP Server configuration
    mcp_server_config = config.get_mcp_server_config()
    host = mcp_server_config["server"]["host"]
    port = mcp_server_config["server"]["port"]
    
    print(f"Connecting to MCP Server at {host}:{port}...")
    
    try:
        # Check server status
        status = await check_mcp_server_status(host, port)
        print(f"Server status: {status}")
        
        # Get available commands
        commands = await get_mcp_server_commands(host, port)
        print(f"Available commands: {commands}")
        
        # Execute a single command
        navigate_cmd = create_navigate_command("https://example.com")
        result = await execute_mcp_server_command(navigate_cmd, host, port)
        print(f"Navigate result: {result}")
        
        # Execute a get title command
        title_cmd = create_get_title_command()
        result = await execute_mcp_server_command(title_cmd, host, port)
        print(f"Title: {result}")
        
        # Execute a screenshot command
        screenshot_cmd = create_screenshot_command("/tmp/example_screenshot.png")
        result = await execute_mcp_server_command(screenshot_cmd, host, port)
        print(f"Screenshot result: {result}")
        
        # Load commands from file
        commands_file = os.path.join(os.path.dirname(__file__), "mcp_server_commands.json")
        commands = load_commands_from_file(commands_file)
        print(f"Loaded {len(commands)} commands from file")
        
        # Execute multiple commands
        results = await execute_mcp_server_commands(commands, host, port)
        print(f"Executed {len(results)} commands")
        for i, result in enumerate(results):
            print(f"Command {i+1} result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    print("MCP Server usage example completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
