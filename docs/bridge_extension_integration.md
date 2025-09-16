# MCP Bridge Extension Integration Guide

This guide provides information on integrating with the Playwright MCP Bridge extension, including setup, configuration, and usage examples.

## Overview

The MCP Bridge Extension integration allows you to control a web browser through a browser extension, providing capabilities such as:

- Tab management (create, close, select, reload)
- Navigation (go to URL, navigate back/forward)
- Cookie management (get, set, clear)
- LocalStorage management (get, set, clear)
- Screenshot capture
- Secure communication with authentication

## Prerequisites

- Python 3.8 or later
- A supported web browser (Chrome, Firefox, Edge)
- The Playwright MCP Bridge browser extension installed

## Installation

1. Install the automata package:

```bash
pip install automata
```

2. Install the Playwright MCP Bridge browser extension in your browser:
   - Chrome: [Chrome Web Store](https://chrome.google.com/webstore/detail/playwright-mcp-bridge/)
   - Firefox: [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/playwright-mcp-bridge/)
   - Edge: [Microsoft Edge Add-ons](https://microsoftedge.microsoft.com/addons/detail/playwright-mcp-bridge/)

## Quick Start

### Basic Usage

```python
import asyncio
from automata.mcp.bridge_extension_client import MCPBridgeExtensionClient

async def main():
    # Create a client
    client = MCPBridgeExtensionClient()
    
    try:
        # Connect to the extension
        await client.connect()
        
        # List available tabs
        tabs = await client.list_tabs()
        print(f"Available tabs: {tabs}")
        
        # Create a new tab
        result = await client.create_tab("https://example.com")
        print(f"Created tab: {result}")
        
        # List tabs again
        tabs = await client.list_tabs()
        print(f"Available tabs after creating new tab: {tabs}")
        
        # Take a screenshot
        screenshot = await client.take_screenshot()
        with open("screenshot.png", "wb") as f:
            f.write(screenshot)
        print("Screenshot saved")
        
    finally:
        # Disconnect from the extension
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### With Authentication

```python
import asyncio
from automata.mcp.bridge_extension_client import MCPBridgeExtensionClient

async def main():
    # Create a client with authentication enabled
    client = MCPBridgeExtensionClient(
        extension_id="your-extension-id",
        enable_security=True
    )
    
    try:
        # Connect to the extension
        await client.connect()
        
        # The client will automatically authenticate with the extension
        
        # List available tabs
        tabs = await client.list_tabs()
        print(f"Available tabs: {tabs}")
        
    finally:
        # Disconnect from the extension
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Client Configuration

The `MCPBridgeExtensionClient` can be configured with the following parameters:

- `extension_id`: ID of the browser extension
- `websocket_url`: WebSocket URL for the extension (default: "ws://localhost:9222")
- `timeout`: Connection timeout in milliseconds (default: 30000)
- `retry_attempts`: Number of retry attempts (default: 3)
- `retry_delay`: Delay between retries in milliseconds (default: 1000)
- `auth_token`: Authentication token for secure connection
- `enable_security`: Whether to enable security features (default: True)
- `token_file`: Path to the token file

### Configuration File

You can also configure the client using a configuration file:

```json
{
  "bridge_extension": {
    "extension_id": "your-extension-id",
    "websocket_url": "ws://localhost:9222",
    "connection_timeout": 30000,
    "retry_attempts": 3,
    "retry_delay": 1000,
    "auth_token": "your-auth-token"
  }
}
```

Load the configuration file:

```python
from automata.mcp.config import MCPConfiguration

config = MCPConfiguration()
config.load_from_file("path/to/config.json")

# Create a client with configuration
client = MCPBridgeExtensionClient(
    extension_id=config.get_bridge_extension_id(),
    websocket_url=config.get_bridge_extension_websocket_url(),
    timeout=config.get_bridge_extension_connection_timeout(),
    retry_attempts=config.get_bridge_extension_retry_attempts(),
    retry_delay=config.get_bridge_extension_retry_delay(),
    auth_token=config.get_bridge_extension_auth_token()
)
```

## API Reference

### MCPBridgeExtensionClient

#### Constructor

```python
MCPBridgeExtensionClient(
    extension_id: str = None,
    websocket_url: str = "ws://localhost:9222",
    timeout: int = 30000,
    retry_attempts: int = 3,
    retry_delay: int = 1000,
    auth_token: str = None,
    enable_security: bool = True,
    token_file: str = None
)
```

#### Methods

##### Connection Management

- `async connect() -> None`: Connect to the extension
- `async disconnect() -> None`: Disconnect from the extension
- `async is_connected() -> bool`: Check if connected to the extension

##### Tab Management

- `async list_tabs() -> List[Dict[str, Any]]`: List available browser tabs
- `async select_tab(tab_id: str) -> Dict[str, Any]`: Select a browser tab
- `async get_current_tab() -> Optional[str]`: Get the currently selected tab ID
- `async create_tab(url: str = None) -> Dict[str, Any]`: Create a new browser tab
- `async close_tab(tab_id: str) -> Dict[str, Any]`: Close a browser tab
- `async reload_tab(tab_id: str) -> Dict[str, Any]`: Reload a browser tab

##### Navigation

- `async navigate_to(url: str) -> Dict[str, Any]`: Navigate to a URL in the current tab
- `async navigate_back() -> Dict[str, Any]`: Navigate back in the current tab's history
- `async navigate_forward() -> Dict[str, Any]`: Navigate forward in the current tab's history

##### Cookie Management

- `async get_cookies(urls: List[str] = None) -> List[Dict[str, Any]]`: Get cookies from the current tab
- `async set_cookies(cookies: List[Dict[str, Any]]) -> Dict[str, Any]`: Set cookies in the current tab
- `async clear_cookies(urls: List[str] = None) -> Dict[str, Any]`: Clear cookies from the current tab

##### LocalStorage Management

- `async get_local_storage() -> Dict[str, Any]`: Get LocalStorage data from the current tab
- `async set_local_storage(data: Dict[str, str]) -> Dict[str, Any]`: Set LocalStorage data in the current tab
- `async clear_local_storage() -> Dict[str, Any]`: Clear LocalStorage data from the current tab

##### Screenshot

- `async take_screenshot(format: str = "png", quality: int = 80, full_page: bool = False, clip: Dict[str, int] = None) -> bytes`: Take a screenshot of the current tab

##### Event Handling

- `register_event_handler(event_name: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None`: Register an event handler
- `unregister_event_handler(event_name: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None`: Unregister an event handler

##### Message Handling

- `async get_next_message(timeout: Optional[float] = None) -> Dict[str, Any]`: Get the next message from the message queue

## Security

The MCP Bridge Extension integration supports secure communication with authentication:

### Authentication

The client can authenticate with the extension using a token. The token can be provided:

1. Directly in the constructor:
   ```python
   client = MCPBridgeExtensionClient(auth_token="your-token")
   ```

2. Through a token file:
   ```python
   client = MCPBridgeExtensionClient(token_file="path/to/tokens.json")
   ```

3. Generated automatically:
   ```python
   client = MCPBridgeExtensionClient(extension_id="your-extension-id")
   await client.connect()  # Token will be generated and stored
   ```

### Secure Communication

The client supports secure WebSocket connections (wss://) and uses SSL/TLS for encrypted communication.

## Platform Compatibility

The MCP Bridge Extension integration is compatible with:

- Windows 10 and later
- Linux (Ubuntu, Fedora, Debian, etc.)
- macOS 10.14 and later

### Platform-Specific Notes

#### Windows

- The extension works with Chrome, Firefox, and Edge
- Configuration files are stored in `%APPDATA%\automata\`
- Token files are stored in `%LOCALAPPDATA%\automata\`

#### Linux

- The extension works with Chrome, Firefox, and Edge
- Configuration files are stored in `~/.config/automata/`
- Token files are stored in `~/.config/automata/`

#### macOS

- The extension works with Chrome, Firefox, and Edge
- Configuration files are stored in `~/Library/Application Support/automata/`
- Token files are stored in `~/Library/Application Support/automata/`

## Troubleshooting

### Connection Issues

1. Make sure the browser extension is installed and enabled
2. Check that the browser is running with remote debugging enabled:
   - Chrome: Start with `--remote-debugging-port=9222`
   - Firefox: Set `remote-debugging-port` to `9222` in `about:config`
   - Edge: Start with `--remote-debugging-port=9222`
3. Verify the WebSocket URL is correct
4. Check for firewall or antivirus software blocking the connection

### Authentication Issues

1. Make sure the extension ID is correct
2. Verify the authentication token is valid
3. Check that the token file exists and is readable

### Platform-Specific Issues

#### Windows

- Make sure the browser is not running as administrator if the client is not
- Check Windows Firewall settings

#### Linux

- Make sure the browser has permission to access the WebSocket port
- Check SELinux or AppArmor settings

#### macOS

- Make sure the browser has permission to access the WebSocket port
- Check macOS Firewall settings

## Examples

### Example 1: Basic Tab Management

```python
import asyncio
from automata.mcp.bridge_extension_client import MCPBridgeExtensionClient

async def main():
    client = MCPBridgeExtensionClient()
    
    try:
        await client.connect()
        
        # List tabs
        tabs = await client.list_tabs()
        print(f"Tabs: {tabs}")
        
        # Create a new tab
        await client.create_tab("https://example.com")
        
        # List tabs again
        tabs = await client.list_tabs()
        print(f"Tabs after creating new one: {tabs}")
        
        # Close the first tab
        if tabs:
            await client.close_tab(tabs[0]["id"])
        
        # List tabs again
        tabs = await client.list_tabs()
        print(f"Tabs after closing: {tabs}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Navigation and Screenshot

```python
import asyncio
from automata.mcp.bridge_extension_client import MCPBridgeExtensionClient

async def main():
    client = MCPBridgeExtensionClient()
    
    try:
        await client.connect()
        
        # Create a new tab
        result = await client.create_tab()
        tab_id = result["tabId"]
        
        # Select the tab
        await client.select_tab(tab_id)
        
        # Navigate to a URL
        await client.navigate_to("https://example.com")
        
        # Take a screenshot
        screenshot = await client.take_screenshot()
        with open("example.png", "wb") as f:
            f.write(screenshot)
        print("Screenshot saved to example.png")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 3: Cookie and LocalStorage Management

```python
import asyncio
from automata.mcp.bridge_extension_client import MCPBridgeExtensionClient

async def main():
    client = MCPBridgeExtensionClient()
    
    try:
        await client.connect()
        
        # Create a new tab
        result = await client.create_tab("https://example.com")
        tab_id = result["tabId"]
        
        # Select the tab
        await client.select_tab(tab_id)
        
        # Get cookies
        cookies = await client.get_cookies()
        print(f"Cookies: {cookies}")
        
        # Set a cookie
        await client.set_cookies([{
            "name": "test_cookie",
            "value": "test_value",
            "domain": "example.com",
            "path": "/"
        }])
        
        # Get cookies again
        cookies = await client.get_cookies()
        print(f"Cookies after setting: {cookies}")
        
        # Get LocalStorage
        storage = await client.get_local_storage()
        print(f"LocalStorage: {storage}")
        
        # Set LocalStorage
        await client.set_local_storage({"test_key": "test_value"})
        
        # Get LocalStorage again
        storage = await client.get_local_storage()
        print(f"LocalStorage after setting: {storage}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

### Event Handling

```python
import asyncio
from automata.mcp.bridge_extension_client import MCPBridgeExtensionClient

async def on_tab_created(message):
    print(f"Tab created: {message}")

async def on_tab_closed(message):
    print(f"Tab closed: {message}")

async def main():
    client = MCPBridgeExtensionClient()
    
    try:
        await client.connect()
        
        # Register event handlers
        client.register_event_handler("tabCreated", on_tab_created)
        client.register_event_handler("tabClosed", on_tab_closed)
        
        # Create a tab (will trigger the event)
        result = await client.create_tab()
        tab_id = result["tabId"]
        
        # Close the tab (will trigger the event)
        await client.close_tab(tab_id)
        
        # Wait for events to be processed
        await asyncio.sleep(1)
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Configuration

```python
import asyncio
import json
from pathlib import Path
from automata.mcp.bridge_extension_client import MCPBridgeExtensionClient
from automata.mcp.config import MCPConfiguration

async def main():
    # Create a custom configuration
    config = MCPConfiguration()
    config.set_bridge_extension_id("my-extension-id")
    config.set_bridge_extension_websocket_url("ws://localhost:9222")
    config.set_bridge_extension_connection_timeout(60000)
    config.set_bridge_extension_retry_attempts(5)
    config.set_bridge_extension_retry_delay(2000)
    config.set_bridge_extension_auth_token("my-auth-token")
    
    # Save the configuration
    config_dir = Path.home() / ".automata"
    config_dir.mkdir(exist_ok=True)
    config.save_to_file(str(config_dir / "mcp_config.json"))
    
    # Load the configuration
    config = MCPConfiguration()
    config.load_from_file(str(config_dir / "mcp_config.json"))
    
    # Create a client with the loaded configuration
    client = MCPBridgeExtensionClient(
        extension_id=config.get_bridge_extension_id(),
        websocket_url=config.get_bridge_extension_websocket_url(),
        timeout=config.get_bridge_extension_connection_timeout(),
        retry_attempts=config.get_bridge_extension_retry_attempts(),
        retry_delay=config.get_bridge_extension_retry_delay(),
        auth_token=config.get_bridge_extension_auth_token()
    )
    
    try:
        await client.connect()
        
        # Use the client
        tabs = await client.list_tabs()
        print(f"Tabs: {tabs}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())