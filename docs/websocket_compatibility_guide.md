# WebSocket Library Compatibility Guide

## Overview

This document provides guidance on WebSocket library compatibility issues that have been encountered in the Automata project, specifically related to the `websockets` Python library and its integration with the MCP (Model Context Protocol) server.

## The Issue

In September 2025, we encountered a breaking change in the `websockets` library version 15.0.1 that affected our MCP server implementation. The issue was related to a change in the WebSocket handler signature.

### Breaking Change Details

**Before websockets v15.0.1:**
```python
async def websocket_handler(websocket, path):
    # Handler implementation
```

**After websockets v15.0.1:**
```python
async def websocket_handler(websocket):
    # Handler implementation (path parameter removed)
```

This change caused a `TypeError` when trying to start the MCP server:
```
TypeError: websocket_handler() takes 2 positional arguments but 3 were given
```

## Impact on MCP Server Integration

The WebSocket compatibility issue had significant implications for the MCP server integration in Automata:

1. **Connection Failures**: AI assistants were unable to establish connections with the MCP server
2. **Tool Execution Failures**: Even when connections were established, tool execution often failed
3. **Extension Mode Issues**: The Bridge extension for connecting to existing browser tabs was particularly affected
4. **User Experience Degradation**: Users experienced inconsistent behavior and frequent disconnections

## Solutions Implemented

### 1. Dependency Version Pinning

We updated `requirements.txt` to pin the websockets library version to a compatible range:

```
websockets>=10.0,<15.0
```

This prevents automatic updates to the incompatible version while still allowing updates within the compatible range.

### 2. Code Updates

We updated the WebSocket handler code in `src/automata/mcp_server/server.py`:

1. **Removed the path parameter** from both the wrapper function and the handler method
2. **Added comprehensive comments** explaining the compatibility issue
3. **Added detailed logging** for better debugging of connection issues
4. **Implemented version detection** to provide appropriate error messages

### 3. Enhanced Error Handling

We implemented improved error handling that:

- Detects WebSocket API compatibility errors
- Provides clear, actionable error messages
- Suggests specific solutions to users
- Includes MCP-specific error context

### 4. Version Detection Mechanism

We added a version detection function that:

- Checks the installed websockets library version at startup
- Logs warnings if an incompatible version is detected
- Provides information about compatible version ranges
- Offers automatic configuration adjustments when possible

### 5. MCP Server Integration Fixes

We implemented specific fixes for the MCP server integration:

1. **WebSocket Handler Compatibility**:
   ```python
   async def handle_websocket(self, websocket, path=None):
       """
       Handle WebSocket connections with compatibility for different websockets library versions.
       
       Args:
           websocket: The WebSocket connection
           path: The request path (required for websockets < 15.0, ignored for >= 15.0)
       """
       try:
           # Implementation that works with both old and new API
           pass
       except Exception as e:
           # Enhanced error handling with MCP-specific context
           pass
   ```

2. **Connection Management**:
   - Added retry logic for failed connections
   - Implemented connection state tracking
   - Added heartbeat mechanism to detect stale connections

3. **Message Handling**:
   - Added message validation and error recovery
   - Implemented message batching for improved performance
   - Added support for both JSON and binary message formats

### 6. Documentation Updates

We updated the documentation to include:

- A new section on WebSocket handler parameter mismatch errors
- Step-by-step solutions for resolving compatibility issues
- References to the code comments for additional context
- MCP-specific troubleshooting guidance
- Integration examples for different AI assistants

## Detection and Resolution

### How to Detect the Issue

1. **Check for the specific error message:**
   ```
   TypeError: websocket_handler() takes 2 positional arguments but 3 were given
   ```

2. **Check your websockets library version:**
   ```bash
   python3.11 -m pip show websockets
   ```

3. **Look for version 15.0.1 or higher**

4. **Check MCP server logs for connection errors:**
   ```bash
   python3.11 -m automata mcp-server start --verbose
   ```

### How to Resolve the Issue

#### Option 1: Use the Fixed Implementation (Recommended)

The Automata MCP server now includes built-in compatibility fixes. To use them:

1. **Update to the latest version of Automata:**
   ```bash
   python3.11 -m pip install --upgrade automata
   ```

2. **Start the MCP server:**
   ```bash
   python3.11 -m automata mcp-server start
   ```

3. **Verify the server is running correctly:**
   ```bash
   python3.11 -m automata mcp-server status
   ```

#### Option 2: Downgrade to Compatible Version

If you need to use an older version of Automata or encounter issues with the fixed implementation:

```bash
python3.11 -m pip install "websockets>=10.0,<15.0"
```

#### Option 3: Update Your Code

If you need to use websockets v15.0.1 or higher with a custom implementation:

1. Remove the `path` parameter from your handler functions
2. Update any calls to these handlers to remove the path argument
3. Add version detection logic to handle both APIs
4. Test thoroughly to ensure functionality is preserved

## MCP Server Integration Specifics

### Configuration for WebSocket Compatibility

The MCP server configuration now includes WebSocket compatibility settings:

```json
{
  "server": {
    "host": "localhost",
    "port": 8080,
    "websocket": {
      "compatibility_mode": "auto",
      "heartbeat_interval": 30,
      "connection_timeout": 60,
      "max_retries": 3
    }
  },
  "browser": {
    "browserName": "chromium",
    "headless": false
  }
}
```

### Compatibility Modes

The MCP server supports three compatibility modes:

1. **Auto (Recommended)**: Automatically detects the websockets library version and adjusts behavior accordingly
2. **Legacy**: Forces the use of the old API (with path parameter)
3. **Modern**: Forces the use of the new API (without path parameter)

### Extension Mode Considerations

The Bridge extension for connecting to existing browser tabs has specific WebSocket compatibility requirements:

1. **Extension Installation**: Ensure the Bridge extension is correctly installed in Chrome
2. **Connection Verification**: Use the extension's built-in connection verification tool
3. **Error Logging**: Enable verbose logging to diagnose connection issues

### AI Assistant Configuration

Different AI assistants may require specific configuration adjustments:

1. **Claude Desktop**:
   ```json
   {
     "mcpServers": {
       "automata": {
         "command": "python3.11",
         "args": ["-m", "automata", "mcp-server", "start"],
         "env": {
           "WEBSOCKETS_COMPATIBILITY": "auto"
         }
       }
     }
   }
   ```

2. **VS Code with Copilot**:
   ```json
   {
     "mcpServers": {
       "automata": {
         "command": "python3.11",
         "args": ["-m", "automata", "mcp-server", "start"],
         "env": {
           "WEBSOCKETS_COMPATIBILITY": "auto"
         }
       }
     }
   }
   ```

## Best Practices for Future Development

### 1. Dependency Management

- Pin dependency versions to prevent unexpected breaking changes
- Use version ranges rather than exact versions when possible
- Regularly review and update dependency constraints
- Implement automated testing for dependency updates

### 2. Code Design

- Design WebSocket handlers to be resilient to API changes
- Add comprehensive error handling for connection issues
- Include detailed logging for debugging purposes
- Implement version detection and compatibility layers

### 3. Testing

- Test with multiple versions of critical dependencies
- Include compatibility tests in your CI/CD pipeline
- Have a rollback plan for dependency updates
- Test MCP server integration with various AI assistants

### 4. Documentation

- Document known compatibility issues and their solutions
- Keep troubleshooting guides updated with common issues
- Include version compatibility information in API documentation
- Provide MCP-specific integration examples

## Long-term Considerations

### Monitoring Future Changes

- Subscribe to release notifications for critical dependencies
- Monitor breaking changes in library release notes
- Participate in library communities when possible
- Track WebSocket API evolution across different implementations

### Alternative Implementations

Consider evaluating alternative WebSocket libraries for future-proofing:

- **aiohttp WebSocket implementation**: More stable API, part of a larger ecosystem
- **Custom WebSocket handling**: Full control over the implementation
- **WebRTC-based communication**: Alternative real-time communication protocol

### Migration Strategy

If a future migration becomes necessary:

1. Create a feature branch for the migration
2. Implement compatibility checks for both old and new APIs
3. Provide clear migration documentation
4. Offer a transition period with support for both versions
5. Update MCP server integration guides and examples

## Conclusion

The WebSocket library compatibility issue was a significant challenge that required multiple approaches to resolve effectively. By implementing version pinning, code updates, enhanced error handling, version detection, comprehensive documentation, and MCP-specific integration fixes, we've created a robust solution that prevents similar issues in the future.

This experience highlights the importance of:

- Proactive dependency management
- Resilient code design
- Comprehensive error handling
- Clear documentation and communication
- MCP-specific integration considerations

These practices will help ensure the long-term stability and maintainability of the Automata project and its MCP server integration.

## Additional Resources

- [websockets Library Documentation](https://websockets.readthedocs.io/)
- [Python Packaging Best Practices](https://packaging.python.org/en/latest/guides/)
- [Semantic Versioning](https://semver.org/)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Automata MCP Server Integration Guide](docs/Playwright_MCP.md)
- [MCP Bridge Setup and Troubleshooting Guide](docs/mcp_bridge_setup_and_troubleshooting.md)
