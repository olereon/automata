# MCP Bridge Setup and Troubleshooting Guide

This guide provides detailed instructions for setting up and troubleshooting the MCP Bridge extension for Automata, which enables AI assistants to interact with existing browser tabs through the Playwright MCP server.

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Automata Installation](#automata-installation)
  - [Bridge Extension Installation](#bridge-extension-installation)
- [Configuration](#configuration)
  - [MCP Server Configuration](#mcp-server-configuration)
  - [AI Assistant Configuration](#ai-assistant-configuration)
- [Usage](#usage)
  - [Starting the MCP Server](#starting-the-mcp-server)
  - [Connecting to Existing Tabs](#connecting-to-existing-tabs)
  - [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)
  - [WebSocket Compatibility Issues](#websocket-compatibility-issues)
  - [Extension Connection Issues](#extension-connection-issues)
  - [Server Connection Issues](#server-connection-issues)
  - [Browser Compatibility Issues](#browser-compatibility-issues)
- [Advanced Configuration](#advanced-configuration)
  - [Custom Browser Profiles](#custom-browser-profiles)
  - [Network Settings](#network-settings)
  - [Security Considerations](#security-considerations)
- [FAQ](#faq)

## Introduction

The MCP Bridge extension for Automata enables AI assistants to interact with existing browser tabs through the Playwright MCP server. This allows AI assistants to leverage existing browser sessions, cookies, and authentication states to perform web automation tasks.

### Key Features

- **Seamless Integration**: Connect to existing browser tabs without disrupting your workflow
- **Session Persistence**: Leverage existing browser sessions, cookies, and authentication states
- **Cross-Platform Support**: Works with Chrome, Edge, and other Chromium-based browsers
- **WebSocket Compatible**: Fully compatible with the latest websockets library versions
- **Secure Communication**: Encrypted communication between the browser and MCP server

## Prerequisites

Before setting up the MCP Bridge extension, ensure you have the following:

- **Python 3.11 or newer**: Required for Automata
- **Node.js 18 or newer**: Required for the Playwright MCP server
- **Chrome or Edge**: Required for the Bridge extension
- **AI Assistant**: Such as Claude Desktop, VS Code with Copilot, or other MCP-compatible assistants

## Installation

### Automata Installation

1. **Install Automata**:
   ```bash
   python3.11 -m pip install automata
   ```

2. **Verify installation**:
   ```bash
   python3.11 -m automata --version
   ```

### Bridge Extension Installation

1. **Download the Bridge extension**:
   - Download the latest Chrome extension from: https://github.com/microsoft/playwright-mcp/releases
   - Or build from source:
     ```bash
     git clone https://github.com/microsoft/playwright-mcp.git
     cd playwright-mcp/extension
     npm install
     npm run build
     ```

2. **Install the extension in Chrome**:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked"
   - Select the extension directory (either the downloaded release or the built source)

3. **Verify the extension is installed**:
   - The extension should appear in the Chrome extensions list
   - Make sure the "Enabled" toggle is on
   - You should see the extension icon in the Chrome toolbar

## Configuration

### MCP Server Configuration

1. **Create a configuration file** (e.g., `mcp_config.json`):
   ```json
   {
     "server": {
       "host": "localhost",
       "port": 8080
     },
     "browser": {
       "browserName": "chromium",
       "headless": false,
       "launchOptions": {
         "channel": "chrome"
       },
       "contextOptions": {
         "viewport": {
           "width": 1280,
           "height": 720
         }
       }
     },
     "capabilities": [
       "tabs",
       "pdf"
     ],
     "outputDir": "./output"
   }
   ```

2. **Customize the configuration** as needed:
   - Adjust the `host` and `port` if needed
   - Change the `browserName` to `firefox` or `webkit` if preferred
   - Enable or disable `headless` mode
   - Add or remove capabilities as needed

### AI Assistant Configuration

1. **Configure your AI assistant** to use the MCP server:
   ```json
   {
     "mcpServers": {
       "automata-extension": {
         "command": "python3.11",
         "args": [
           "-m",
           "automata",
           "mcp-server",
           "start",
           "--extension",
           "--config",
           "mcp_config.json"
         ]
       }
     }
   }
   ```

2. **Restart your AI assistant** to apply the configuration changes.

## Usage

### Starting the MCP Server

1. **Start the MCP server in extension mode**:
   ```bash
   python3.11 -m automata mcp-server start --extension --config mcp_config.json
   ```

2. **Verify the server is running**:
   ```bash
   python3.11 -m automata mcp-server status
   ```

### Connecting to Existing Tabs

1. **Open Chrome** with the tabs you want to automate
2. **Click the Bridge extension icon** in the Chrome toolbar
3. **Select "Connect to MCP Server"** from the extension menu
4. **Verify the connection**:
   - The extension icon should change to indicate a successful connection
   - The MCP server logs should show a connection from the extension

### Common Use Cases

1. **Form Filling**:
   - Navigate to a form in an existing tab
   - Use your AI assistant to fill in the form fields
   - Submit the form

2. **Data Extraction**:
   - Navigate to a page with data you want to extract
   - Use your AI assistant to extract the data
   - Save the data to a file or database

3. **Session Management**:
   - Log in to a website in an existing tab
   - Use your AI assistant to perform actions on the website
   - Log out when done

## Troubleshooting

### WebSocket Compatibility Issues

The Automata MCP server implementation includes comprehensive fixes for WebSocket handler parameter compatibility issues with the websockets library version 15.0.1 and higher.

**Error Symptoms**:
```
TypeError: websocket_handler() takes 2 positional arguments but 3 were given
TypeError: MCPServer.handle_websocket() missing 1 required positional argument: 'path'
ERROR:websockets.server:connection handler failed
```

**Solutions**:
1. **Check your websockets library version**:
   ```bash
   python3.11 -m pip show websockets
   ```

2. **If using version 15.0.1 or higher**, the code has been updated to work correctly.

3. **If you need to downgrade** (not recommended as the fix is already implemented):
   ```bash
   python3.11 -m pip install "websockets>=10.0,<15.0"
   ```

**Verification**:
1. **Start the MCP server**:
   ```bash
   python3.11 scripts/start_mcp_server.py
   ```

2. **Run the test script**:
   ```bash
   python3.11 scripts/test_websocket_fix.py
   ```

3. **Check for successful connection establishment** and message handling.

### Extension Connection Issues

If you encounter issues with the extension mode:

1. **Ensure the Bridge extension is installed correctly**:
   - Download the latest Chrome extension from: https://github.com/microsoft/playwright-mcp/releases
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the extension directory

2. **Check if the extension is enabled**:
   - The extension should appear in the Chrome extensions list
   - Make sure the "Enabled" toggle is on

3. **Verify the extension is connected**:
   - Start the MCP server in extension mode
   - Check the server logs for connection messages
   - Click the extension icon and verify it shows a connected state

4. **Restart Chrome** if the extension doesn't appear to be working

### Server Connection Issues

If you encounter issues connecting to the MCP server:

1. **Check if the server is running**:
   ```bash
   python3.11 -m automata mcp-server status
   ```

2. **Verify the server configuration**:
   ```bash
   python3.11 -m automata mcp-server config --show
   ```

3. **Check network connectivity**:
   ```bash
   curl http://localhost:8080/health
   ```

4. **Enable verbose logging**:
   ```bash
   python3.11 -m automata mcp-server start --verbose
   ```

5. **Check for port conflicts**:
   - Ensure the port specified in the configuration is not already in use
   - Try using a different port if needed

### Browser Compatibility Issues

If you encounter issues with browser compatibility:

1. **Ensure you're using a supported browser**:
   - Chrome (recommended)
   - Edge
   - Other Chromium-based browsers

2. **Check browser version**:
   - Ensure you're using the latest version of your browser
   - Update your browser if needed

3. **Try a different browser** if issues persist

## Advanced Configuration

### Custom Browser Profiles

1. **Create a custom browser profile**:
   ```json
   {
     "browser": {
       "browserName": "chromium",
       "userDataDir": "/path/to/custom/profile"
     }
   }
   ```

2. **Start the MCP server with the custom profile**:
   ```bash
   python3.11 -m automata mcp-server start --config custom_profile_config.json
   ```

### Network Settings

1. **Configure proxy settings**:
   ```json
   {
     "browser": {
       "browserName": "chromium",
       "launchOptions": {
         "proxy": {
           "server": "http://proxy.example.com:8080"
         }
       }
     }
   }
   ```

2. **Configure network restrictions**:
   ```json
   {
     "network": {
       "allowedOrigins": ["https://example.com", "https://trusted-site.com"],
       "blockedOrigins": ["https://malicious-site.com"]
     }
   }
   ```

### Security Considerations

1. **Use HTTPS** for sensitive operations:
   ```json
   {
     "server": {
       "ssl": {
         "cert": "/path/to/cert.pem",
         "key": "/path/to/key.pem"
       }
     }
   }
   ```

2. **Restrict access to trusted origins**:
   ```json
   {
     "network": {
       "allowedOrigins": ["https://trusted-site.com"]
     }
   }
   ```

3. **Use authentication** if needed:
   ```json
   {
     "server": {
       "auth": {
         "type": "basic",
         "username": "user",
         "password": "pass"
       }
     }
   }
   ```

## FAQ

### Q: Can I use the MCP Bridge extension with multiple browsers simultaneously?
A: No, the MCP Bridge extension can only connect to one browser instance at a time. If you need to work with multiple browsers, you'll need to start separate MCP server instances for each browser.

### Q: Is the MCP Bridge extension compatible with Firefox or Safari?
A: Currently, the MCP Bridge extension is only compatible with Chromium-based browsers like Chrome and Edge. Support for Firefox and Safari may be added in future releases.

### Q: Can I use the MCP Bridge extension with headless browsers?
A: No, the MCP Bridge extension is designed to work with existing browser tabs in headed browsers. For headless automation, use the standard MCP server mode without the extension.

### Q: How do I update the MCP Bridge extension?
A: To update the MCP Bridge extension, download the latest version from the releases page and reinstall it using the Chrome extensions manager. Your settings and configurations should be preserved.

### Q: Can I use the MCP Bridge extension with custom browser profiles?
A: Yes, you can configure the MCP server to use custom browser profiles. See the "Custom Browser Profiles" section in the Advanced Configuration chapter for more details.

### Q: Is the communication between the browser and MCP server encrypted?
A: Yes, all communication between the browser and MCP server is encrypted using WebSocket Secure (WSS) when HTTPS is enabled. For additional security, you can configure custom SSL certificates.

### Q: Can I use the MCP Bridge extension with mobile browsers?
A: Currently, the MCP Bridge extension is only compatible with desktop browsers. Mobile browser support may be added in future releases.

### Q: How do I troubleshoot WebSocket compatibility issues?
A: See the "WebSocket Compatibility Issues" section in the Troubleshooting chapter for detailed instructions on resolving WebSocket compatibility issues.

### Q: Can I use the MCP Bridge extension with multiple AI assistants simultaneously?
A: Yes, you can configure multiple AI assistants to use the same MCP server instance. However, be aware that this may lead to conflicts if both assistants try to interact with the same browser tab simultaneously.

### Q: How do I report bugs or request features for the MCP Bridge extension?
A: You can report bugs or request features by creating an issue in the Automata GitHub repository: https://github.com/olereon/automata/issues
