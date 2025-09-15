# WebSocket Library Compatibility Guide

## Overview

This document provides guidance on WebSocket library compatibility issues that have been encountered in the Automata project, specifically related to the `websockets` Python library.

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

### 3. Enhanced Error Handling

We implemented improved error handling that:

- Detects WebSocket API compatibility errors
- Provides clear, actionable error messages
- Suggests specific solutions to users

### 4. Version Detection Mechanism

We added a version detection function that:

- Checks the installed websockets library version at startup
- Logs warnings if an incompatible version is detected
- Provides information about compatible version ranges

### 5. Documentation Updates

We updated the troubleshooting guide to include:

- A new section on WebSocket handler parameter mismatch errors
- Step-by-step solutions for resolving compatibility issues
- References to the code comments for additional context

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

### How to Resolve the Issue

#### Option 1: Downgrade to Compatible Version (Recommended)

```bash
python3.11 -m pip install "websockets>=10.0,<15.0"
```

#### Option 2: Update Your Code

If you need to use websockets v15.0.1 or higher, update your WebSocket handler functions:

1. Remove the `path` parameter from your handler functions
2. Update any calls to these handlers to remove the path argument
3. Test thoroughly to ensure functionality is preserved

## Best Practices for Future Development

### 1. Dependency Management

- Pin dependency versions to prevent unexpected breaking changes
- Use version ranges rather than exact versions when possible
- Regularly review and update dependency constraints

### 2. Code Design

- Design WebSocket handlers to be resilient to API changes
- Add comprehensive error handling for connection issues
- Include detailed logging for debugging purposes

### 3. Testing

- Test with multiple versions of critical dependencies
- Include compatibility tests in your CI/CD pipeline
- Have a rollback plan for dependency updates

### 4. Documentation

- Document known compatibility issues and their solutions
- Keep troubleshooting guides updated with common issues
- Include version compatibility information in API documentation

## Long-term Considerations

### Monitoring Future Changes

- Subscribe to release notifications for critical dependencies
- Monitor breaking changes in library release notes
- Participate in library communities when possible

### Alternative Implementations

Consider evaluating alternative WebSocket libraries for future-proofing:

- **aiohttp WebSocket implementation**: More stable API, part of a larger ecosystem
- **Custom WebSocket handling**: Full control over the implementation

### Migration Strategy

If a future migration becomes necessary:

1. Create a feature branch for the migration
2. Implement compatibility checks for both old and new APIs
3. Provide clear migration documentation
4. Offer a transition period with support for both versions

## Conclusion

The WebSocket library compatibility issue was a significant challenge that required multiple approaches to resolve effectively. By implementing version pinning, code updates, enhanced error handling, version detection, and comprehensive documentation, we've created a robust solution that prevents similar issues in the future.

This experience highlights the importance of:

- Proactive dependency management
- Resilient code design
- Comprehensive error handling
- Clear documentation and communication

These practices will help ensure the long-term stability and maintainability of the Automata project.

## Additional Resources

- [websockets Library Documentation](https://websockets.readthedocs.io/)
- [Python Packaging Best Practices](https://packaging.python.org/en/latest/guides/)
- [Semantic Versioning](https://semver.org/)
