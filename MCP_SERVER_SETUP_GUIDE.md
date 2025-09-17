# MCP Server Setup Guide for Windows

This guide provides detailed instructions for setting up and starting the MCP server for Automata on Windows, including extension mode configuration.

## Table of Contents
- [MCP Server Configuration](#mcp-server-configuration)
- [Starting the MCP Server](#starting-the-mcp-server)
- [Extension Mode Configuration](#extension-mode-configuration)
- [AI Assistant Configuration](#ai-assistant-configuration)
- [Troubleshooting](#troubleshooting)

## MCP Server Configuration

The MCP server configuration is stored in a JSON file. Here's a comprehensive example:

```json
{
  "server": {
    "host": "localhost",
    "port": 8080,
    "log_level": "INFO"
  },
  "browser": {
    "browserName": "chromium",
    "headless": false,
    "launchOptions": {
      "channel": "chrome"
    },
    "contextOptions": {
      "viewport": {
        "width": 1920,
        "height": 1080
      }
    }
  },
  "capabilities": [
    "tabs",
    "pdf"
  ],
  "outputDir": "./output",
  "extension_mode": true,
  "extension_port": 9222
}
```

### Configuration Options

- **server**: Server configuration
  - **host**: Host to bind to (default: "localhost")
  - **port**: Port to bind to (default: 8080)
  - **log_level**: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

- **browser**: Browser configuration
  - **browserName**: Browser type (chromium, firefox, webkit)
  - **headless**: Whether to run in headless mode
  - **launchOptions**: Browser launch options
  - **contextOptions**: Browser context options

- **capabilities**: List of capabilities to enable
  - **tabs**: Tab management capability
  - **pdf**: PDF generation capability

- **outputDir**: Directory for output files

- **extension_mode**: Enable extension mode (true/false)
- **extension_port**: Port for extension communication (default: 9222)

## Starting the MCP Server

There are two ways to start the MCP server:

### 1. Using Command Line Options

```bash
python3.11 -m automata mcp-server start --host localhost --port 8080 --log-level INFO
```

### 2. Using a Configuration File

```bash
python3.11 -m automata mcp-server start --config path/to/config.json
```

## Extension Mode Configuration

The MCP server supports an extension mode that allows it to connect to existing browser tabs through a browser extension.

### Configuring Extension Mode

To configure extension mode, you have two options:

#### Option 1: Using the Configure Command

```bash
python3.11 -m automata mcp-server configure --extension-mode --host localhost --port 8080
```

This will create a configuration file at `~/.automata/mcp_server_config.json` with extension mode enabled.

#### Option 2: Manual Configuration

Add the following to your configuration file:

```json
{
  "extension_mode": true,
  "extension_port": 9222
}
```

### Starting the Server in Extension Mode

Currently, the `--extension-mode` flag is only available in the `configure` command, not the `start` command. To start the server in extension mode:

1. First, configure the server with extension mode enabled:
   ```bash
   python3.11 -m automata mcp-server configure --extension-mode
   ```

2. Then, start the server using the configuration file:
   ```bash
   python3.11 -m automata mcp-server start --config ~/.automata/mcp_server_config.json
   ```

## AI Assistant Configuration

To use the MCP server with an AI assistant like Claude Desktop, you need to configure the assistant to connect to the MCP server.

### Claude Desktop Configuration

1. Locate your Claude Desktop configuration file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the MCP server configuration:

```json
{
  "mcpServers": {
    "automata": {
      "command": "python3.11",
      "args": [
        "-m",
        "automata",
        "mcp-server",
        "start",
        "--config",
        "path/to/your/config.json"
      ]
    }
  }
}
```

### Extension Mode Configuration for AI Assistants

If you're using extension mode, the configuration should include the extension settings:

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
        "--config",
        "path/to/your/extension_config.json"
      ]
    }
  }
}
```

## Troubleshooting

### Server Won't Start

1. **Check if Python 3.11 is installed**:
   ```bash
   python3.11 --version
   ```

2. **Check if Automata is installed**:
   ```bash
   python3.11 -m automata --version
   ```

3. **Check the configuration file**:
   ```bash
   python3.11 -m json.tool path/to/config.json
   ```

4. **Check if the port is available**:
   ```bash
   netstat -an | grep 8080
   ```

### Extension Mode Issues

1. **Check if extension mode is enabled in the configuration**:
   ```json
   {
     "extension_mode": true
   }
   ```

2. **Check if the extension is installed in Chrome**:
   - Open Chrome and navigate to `chrome://extensions/`
   - Look for the Automata extension
   - Make sure it's enabled

3. **Check if the extension can connect to the server**:
   - Start the server
   - Click the extension icon in Chrome
   - Select "Connect to MCP Server"
   - Check the server logs for connection messages

### AI Assistant Can't Connect

1. **Check if the server is running**:
   ```bash
   python3.11 -m automata mcp-server status
   ```

2. **Check the AI assistant configuration**:
   - Verify the command and arguments are correct
   - Make sure the configuration file path is correct

3. **Check the server logs**:
   - Start the server with verbose logging:
     ```bash
     python3.11 -m automata mcp-server start --config path/to/config.json --log-level DEBUG
     ```
   - Look for error messages

## Additional Resources

- [Automata Documentation](https://github.com/olereon/automata)
- [MCP Bridge Setup and Troubleshooting Guide](docs/mcp_bridge_setup_and_troubleshooting.md)
- [Extension Integration Guide](docs/bridge_extension_integration.md)
