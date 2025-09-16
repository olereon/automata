# MCP Bridge Setup and Troubleshooting Guide

This guide provides instructions for setting up and troubleshooting the MCP (Model Context Protocol) Bridge in Automata.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Operating Modes](#operating-modes)
   - [Server Mode](#server-mode)
   - [Extension Mode](#extension-mode)
6. [Setup Instructions](#setup-instructions)
   - [Server Mode Setup](#server-mode-setup)
   - [Extension Mode Setup](#extension-mode-setup)
7. [Troubleshooting](#troubleshooting)
   - [Common Issues](#common-issues)
   - [Error Messages](#error-messages)
   - [Debugging Steps](#debugging-steps)
8. [Testing](#testing)
9. [API Reference](#api-reference)

## Overview

The MCP Bridge is a component in Automata that enables communication with browser automation services through the Model Context Protocol. It supports two operating modes:

1. **Server Mode**: Connects to an external MCP server for browser automation.
2. **Extension Mode**: Communicates directly with a browser extension for automation.

## Prerequisites

Before setting up the MCP Bridge, ensure you have the following:

- Python 3.11 or higher
- Automata installed
- (For Server Mode) Access to an MCP server
- (For Extension Mode) A compatible browser with the MCP extension installed

## Installation

The MCP Bridge is included with Automata. No additional installation is required beyond the standard Automata installation.

```bash
# Install Automata
pip install automata
```

## Configuration

The MCP Bridge can be configured through:

1. **Command-line arguments**
2. **Configuration files**
3. **Environment variables**

### Command-line Arguments

```bash
# Enable MCP Bridge
automata --mcp-bridge

# Disable MCP Bridge (default)
automata --no-mcp-bridge

# Specify MCP configuration file
automata --mcp-config /path/to/mcp_config.json
```

### Configuration File

Create a JSON configuration file (e.g., `mcp_config.json`):

```json
{
  "server_url": "ws://localhost:8080",
  "timeout": 30000,
  "retry_attempts": 3,
  "retry_delay": 1000,
  "bridge_extension_mode": false,
  "bridge_extension_port": 9222
}
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `server_url` | String | "ws://localhost:8080" | URL of the MCP server |
| `timeout` | Integer | 30000 | Connection timeout in milliseconds |
| `retry_attempts` | Integer | 3 | Number of connection retry attempts |
| `retry_delay` | Integer | 1000 | Delay between retry attempts in milliseconds |
| `bridge_extension_mode` | Boolean | false | Enable extension mode |
| `bridge_extension_port` | Integer | 9222 | Port for extension mode communication |

## Operating Modes

### Server Mode

In Server Mode, the MCP Bridge connects to an external MCP server that handles browser automation. This mode is suitable for:

- Distributed systems
- Centralized browser automation
- Environments where browser extensions are not feasible

#### Server Mode Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Automata  │────▶│  MCP Bridge │────▶│ MCP Server  │
└─────────────┘     └─────────────┘     └─────────────┘
                                          │
                                          ▼
                                    ┌─────────────┐
                                    │   Browser   │
                                    └─────────────┘
```

### Extension Mode

In Extension Mode, the MCP Bridge communicates directly with a browser extension. This mode is suitable for:

- Local development
- Direct browser control
- Environments where running a separate server is not desired

#### Extension Mode Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Automata  │────▶│  MCP Bridge │────▶│   Browser   │
└─────────────┘     └─────────────┘     │  Extension  │
                                         └─────────────┘
```

## Setup Instructions

### Server Mode Setup

1. **Start the MCP Server**

   Ensure your MCP server is running and accessible at the configured URL.

   ```bash
   # Example: Start a typical MCP server
   mcp-server --port 8080
   ```

2. **Configure Automata**

   Create a configuration file or use command-line arguments:

   ```bash
   # Using command-line arguments
   automata --mcp-bridge --mcp-config mcp_server_config.json
   ```

   Example `mcp_server_config.json`:
   ```json
   {
     "server_url": "ws://localhost:8080",
     "timeout": 30000,
     "retry_attempts": 3,
     "retry_delay": 1000,
     "bridge_extension_mode": false
   }
   ```

3. **Verify Connection**

   Run Automata and check the logs for successful connection:

   ```bash
   automata --mcp-bridge --verbose
   ```

   Look for messages like:
   ```
   INFO: Connecting to MCP Bridge
   INFO: Connecting to MCP server at ws://localhost:8080
   INFO: MCP server health check passed
   INFO: WebSocket connection established
   INFO: Connected to MCP Bridge
   ```

### Extension Mode Setup

1. **Install the Browser Extension**

   Install the MCP browser extension in your browser. The extension should be compatible with Automata.

2. **Enable Extension Mode**

   Configure Automata to use extension mode:

   ```bash
   # Using command-line arguments
   automata --mcp-bridge --mcp-config mcp_extension_config.json
   ```

   Example `mcp_extension_config.json`:
   ```json
   {
     "bridge_extension_mode": true,
     "bridge_extension_port": 9222,
     "timeout": 30000,
     "retry_attempts": 3,
     "retry_delay": 1000
   }
   ```

3. **Start the Browser with Extension**

   Launch your browser with the MCP extension enabled. The extension should start listening on the configured port.

4. **Verify Connection**

   Run Automata and check the logs for successful connection:

   ```bash
   automata --mcp-bridge --verbose
   ```

   Look for messages like:
   ```
   INFO: Connecting to MCP Bridge
   INFO: Checking browser extension availability on port 9222
   INFO: Browser extension is available
   INFO: Connected to MCP Bridge
   ```

## Troubleshooting

### Common Issues

#### Connection Failures

**Symptoms**: Error messages indicating connection failures, timeouts, or unreachable servers.

**Possible Causes**:
- MCP server is not running
- Incorrect server URL or port
- Network connectivity issues
- Firewall blocking the connection

**Solutions**:
1. Verify the MCP server is running and accessible
2. Check the server URL and port in your configuration
3. Ensure network connectivity between Automata and the MCP server
4. Check firewall settings

#### Extension Not Detected

**Symptoms**: Error messages indicating the browser extension is not available.

**Possible Causes**:
- Browser extension is not installed or enabled
- Incorrect extension port configuration
- Browser is not running with the extension

**Solutions**:
1. Verify the browser extension is installed and enabled
2. Check the extension port configuration
3. Ensure the browser is running with the extension
4. Try accessing the extension's JSON endpoint directly:
   ```bash
   curl http://localhost:9222/json
   ```

#### Timeouts

**Symptoms**: Operations take too long and eventually time out.

**Possible Causes**:
- Network latency
- Server or browser under heavy load
- Timeout value too low for your environment

**Solutions**:
1. Increase the timeout value in your configuration
2. Check the performance of your MCP server or browser
3. Investigate network latency issues

### Error Messages

#### "Failed to connect to MCP Bridge"

This error indicates a general connection failure. Check the specific error message that follows for more details.

#### "Browser extension returned status XXX"

This error indicates that the browser extension is accessible but returned an unexpected HTTP status code. Check the extension logs for more information.

#### "All WebSocket connection attempts failed"

This error indicates that the MCP Bridge could not establish a WebSocket connection to the MCP server. Check the server logs and ensure the server is running and accessible.

#### "MCP server health check returned status XXX"

This error indicates that the MCP server's health check endpoint returned an unexpected HTTP status code. Check the server logs for more information.

### Debugging Steps

1. **Enable Verbose Logging**

   Run Automata with verbose logging to get detailed information:

   ```bash
   automata --mcp-bridge --verbose
   ```

2. **Check Server Health**

   Verify that the MCP server is running and responding to health checks:

   ```bash
   # For Server Mode
   curl http://localhost:8081/health

   # For Extension Mode
   curl http://localhost:9222/json
   ```

3. **Test Network Connectivity**

   Verify network connectivity between Automata and the MCP server or browser extension:

   ```bash
   # Test TCP connection
   telnet localhost 8080  # For Server Mode
   telnet localhost 9222  # For Extension Mode
   ```

4. **Check Configuration**

   Verify your configuration file or command-line arguments:

   ```bash
   # Display configuration
   automata --help
   ```

5. **Review Logs**

   Check the logs for both Automata and the MCP server or browser extension for error messages and warnings.

## Testing

### Running Tests

Automata includes tests for the MCP Bridge functionality. Run the tests to verify your setup:

```bash
# Run all MCP Bridge tests
python3.11 -m pytest tests/mcp/

# Run specific test file
python3.11 -m pytest tests/mcp/test_bridge_extension.py

# Run with verbose output
python3.11 -m pytest tests/mcp/ -v
```

### Test Coverage

To check test coverage:

```bash
# Run tests with coverage report
python3.11 -m pytest tests/mcp/ --cov=src/automata/mcp --cov-report=term-missing
```

## API Reference

### MCPConfiguration

The `MCPConfiguration` class manages configuration settings for the MCP Bridge.

#### Methods

- `set_server_url(url: str)`: Set the MCP server URL
- `set_timeout(timeout_ms: int)`: Set the connection timeout in milliseconds
- `set_retry_attempts(attempts: int)`: Set the number of retry attempts
- `set_retry_delay(delay_ms: int)`: Set the delay between retry attempts in milliseconds
- `set_bridge_extension_mode(enabled: bool)`: Enable or disable extension mode
- `set_bridge_extension_port(port: int)`: Set the port for extension mode communication

### MCPBridgeConnector

The `MCPBridgeConnector` class handles communication with the MCP server or browser extension.

#### Methods

- `connect(test_mode: bool = False) -> bool`: Connect to the MCP server or browser extension
- `disconnect()`: Disconnect from the MCP server or browser extension
- `send_request(method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`: Send a request to the MCP server or browser extension
- `get_next_message(timeout: Optional[float] = None) -> Dict[str, Any]`: Get the next message from the MCP server or browser extension

### Exceptions

- `MCPBridgeConnectionError`: Raised when a connection to the MCP server or browser extension fails

## Additional Resources

- [Automata Documentation](../../README.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Server Implementation Guide](../server/README.md)
- [Browser Extension Development Guide](../extension/README.md)
