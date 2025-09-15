# Playwright MCP WebSocket Handler Parameter Mismatch Issue - Comprehensive Resolution Guide

## Executive Summary

This document provides a comprehensive analysis of the WebSocket handler parameter mismatch issue affecting the Playwright MCP (Model Context Protocol) server implementation. The issue prevents successful WebSocket connections between the MCP client and server, causing the MCP Bridge extension to fail during browser automation tasks.

## Problem Description

### Primary Issue

The core issue is a **WebSocket handler parameter mismatch** in the MCP server implementation. The error occurs when the websockets library attempts to call the WebSocket handler with an incorrect number of parameters.

**Error Message:**
```
TypeError: MCPServer.handle_websocket() missing 1 required positional argument: 'path'
```

**Error Trace:**
```
ERROR:websockets.server:connection handler failed
Traceback (most recent call last):
  File "/home/olereon/.local/lib/python3.11/site-packages/websockets/asyncio/server.py", line 376, in conn_handler
    await self.handler(connection)
          ^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: MCPServer.handle_websocket() missing 1 required positional argument: 'path'
```

### Technical Details

1. **Environment:**
   - Python Version: 3.11
   - Websockets Library: websockets 15.0.1 (actual installed version)
   - Requirements specify: websockets>=10.0
   - Operating System: Linux

2. **Affected Components:**
   - MCP Server: `src/automata/mcp_server/server.py`
   - MCP Client: `src/automata/core/mcp_client.py`
   - MCP Bridge: `src/automata/core/mcp_bridge.py`

## Root Cause Analysis

### WebSocket Handler Signature Mismatch

The issue stems from a version compatibility problem between the websockets library version (15.0.1) and the expected handler signature in the MCP server implementation.

**Current Implementation (Lines 458-467 in server.py):**
```python
# Create a wrapper function for the WebSocket handler
async def websocket_handler(websocket, path):
    await self._handle_websocket_connection(websocket, path)

# Start WebSocket server
ws_server = await websockets.serve(
    websocket_handler,
    self.host,
    self.port
)
```

**Actual Handler Method (Line 178 in server.py):**
```python
async def _handle_websocket_connection(self, websocket, path=None):
    """Handle WebSocket connection."""
```

### Version Compatibility Issue

The websockets library version 15.0.1 has changed how it calls WebSocket handlers:
- **Expected by library:** `handler(websocket)` - single parameter
- **Implemented in code:** `handler(websocket, path)` - two parameters

This change in the library's API is not reflected in the current implementation, causing the parameter mismatch error.

## Troubleshooting Approaches Attempted

### 1. Direct Handler Implementation
- **Approach:** Implemented `handle_websocket(self, websocket, path)` directly
- **Result:** Failed with the same parameter mismatch error
- **Status:** ❌ Not Successful

### 2. Wrapper Function Approach
- **Approach:** Created a wrapper function `websocket_handler(websocket, path)`
- **Result:** Still failed with the same parameter mismatch error
- **Status:** ❌ Not Successful

### 3. Optional Path Parameter
- **Approach:** Made the path parameter optional with `path=None`
- **Result:** Still failed with the same parameter mismatch error
- **Status:** ❌ Not Successful

## Recommended Solution

### Solution Overview

The most effective solution is to **update the WebSocket handler signature** to match the websockets library version 15.0.1 API requirements. This involves modifying the handler to accept only the websocket parameter and removing the path parameter entirely.

### Implementation Steps

#### Step 1: Update WebSocket Handler in server.py

**File:** `src/automata/mcp_server/server.py`
**Lines:** 458-467

**Current Code:**
```python
# Create a wrapper function for the WebSocket handler
async def websocket_handler(websocket, path):
    await self._handle_websocket_connection(websocket, path)

# Start WebSocket server
ws_server = await websockets.serve(
    websocket_handler,
    self.host,
    self.port
)
```

**Updated Code:**
```python
# Create a wrapper function for the WebSocket handler
async def websocket_handler(websocket):
    await self._handle_websocket_connection(websocket)

# Start WebSocket server
ws_server = await websockets.serve(
    websocket_handler,
    self.host,
    self.port
)
```

#### Step 2: Update Handler Method Signature

**File:** `src/automata/mcp_server/server.py`
**Line:** 178

**Current Code:**
```python
async def _handle_websocket_connection(self, websocket, path=None):
    """Handle WebSocket connection."""
```

**Updated Code:**
```python
async def _handle_websocket_connection(self, websocket):
    """Handle WebSocket connection."""
```

#### Step 3: Verify All References

Ensure that all calls to `_handle_websocket_connection` are updated to remove the path parameter:

**File:** `src/automata/mcp_server/server.py`
**Line:** 460

**Current Code:**
```python
await self._handle_websocket_connection(websocket, path)
```

**Updated Code:**
```python
await self._handle_websocket_connection(websocket)
```

### Alternative Solutions

#### Option A: Downgrade Websockets Library

If the above solution doesn't work, consider downgrading the websockets library to a version that supports the two-parameter handler signature:

**Update requirements.txt:**
```
websockets>=10.0,<14.0
```

Then reinstall dependencies:
```bash
pip install -r requirements.txt
```

#### Option B: Use aiohttp WebSocket Implementation

As a more robust solution, consider replacing the websockets library with aiohttp's WebSocket implementation:

**File:** `src/automata/mcp_server/server.py`

```python
from aiohttp import web, WSMsgType

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    self._connected_clients.add(ws)
    logger.info(f"New WebSocket connection from {request.remote}")
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    response = await self._handle_message(data)
                    await ws.send_str(json.dumps(response))
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                    await ws.send_str(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await ws.send_str(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
            elif msg.type == WSMsgType.ERROR:
                logger.error(f"WebSocket connection closed with exception {ws.exception()}")
    finally:
        self._connected_clients.discard(ws)
        logger.info("WebSocket connection closed")
    
    return ws

# Add to routes
self.app.add_routes([
    web.get('/', self.handle_http),
    web.get('/health', self.handle_health),
    web.get('/ws', websocket_handler),
])
```

## Implementation Plan

### Phase 1: Immediate Fix (Recommended)

1. **Update WebSocket Handler Signature**
   - Modify `src/automata/mcp_server/server.py` lines 458-467
   - Remove path parameter from handler function
   - Update method call on line 460

2. **Update Handler Method**
   - Modify `src/automata/mcp_server/server.py` line 178
   - Remove path parameter from `_handle_websocket_connection` method

3. **Test the Fix**
   - Run the test script: `python3.11 scripts/test_mcp_bridge.py`
   - Verify WebSocket connection establishment
   - Confirm message handling works correctly

### Phase 2: Validation and Testing

1. **Unit Testing**
   - Test WebSocket connection establishment
   - Test message sending and receiving
   - Test error handling scenarios

2. **Integration Testing**
   - Test MCP Bridge connector functionality
   - Test all browser automation tools
   - Test connection/disconnection cycles

3. **Performance Testing**
   - Test with multiple concurrent connections
   - Test with large message payloads
   - Test long-running connections

### Phase 3: Long-term Stability

1. **Version Pinning**
   - Consider pinning the websockets library version
   - Add compatibility checks for future updates

2. **Documentation Update**
   - Update API documentation
   - Add version compatibility notes
   - Update troubleshooting guide

## Prevention Strategies

### 1. Dependency Management

- **Pin Critical Versions:** Pin the websockets library version in requirements.txt
- **Regular Updates:** Schedule regular dependency updates with compatibility testing
- **Version Monitoring:** Monitor library updates for breaking changes

### 2. Code Quality Practices

- **Type Hints:** Add type hints to all handler functions
- **Unit Tests:** Implement comprehensive unit tests for WebSocket handlers
- **Integration Tests:** Add end-to-end tests for MCP client-server communication

### 3. Error Handling Improvements

- **Graceful Degradation:** Implement fallback mechanisms for connection failures
- **Detailed Logging:** Add more detailed logging for connection establishment
- **Health Checks:** Implement robust health check endpoints

## Testing Strategy

### Test Cases

1. **Connection Establishment**
   - Test successful WebSocket connection
   - Test connection with invalid URLs
   - Test connection timeout scenarios

2. **Message Handling**
   - Test valid JSON message processing
   - Test invalid JSON message handling
   - Test large message payloads

3. **Tool Execution**
   - Test all browser automation tools
   - Test tool error handling
   - Test concurrent tool execution

### Test Script

```python
#!/usr/bin/env python3.11
"""
Test script for WebSocket handler fix validation.
"""

import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_connection():
    """Test WebSocket connection to MCP server."""
    uri = "ws://localhost:8081"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("WebSocket connection established")
            
            # Test initialize message
            init_message = {
                "type": "initialize",
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                }
            }
            
            await websocket.send(json.dumps(init_message))
            logger.info("Sent initialize message")
            
            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)
            logger.info(f"Received response: {response_data}")
            
            # Test tools list
            tools_message = {
                "type": "tools/list",
                "id": "test-1"
            }
            
            await websocket.send(json.dumps(tools_message))
            logger.info("Sent tools/list message")
            
            # Wait for tools response
            tools_response = await websocket.recv()
            tools_data = json.loads(tools_response)
            logger.info(f"Received tools response: {tools_data}")
            
            # Test tool call
            tool_call_message = {
                "type": "tool/call",
                "toolName": "browser_snapshot",
                "arguments": {},
                "id": "test-2"
            }
            
            await websocket.send(json.dumps(tool_call_message))
            logger.info("Sent tool/call message")
            
            # Wait for tool response
            tool_response = await websocket.recv()
            tool_data = json.loads(tool_response)
            logger.info(f"Received tool response: {tool_data}")
            
            logger.info("All tests passed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket_connection())
    exit(0 if success else 1)
```

## Conclusion

The WebSocket handler parameter mismatch issue is a critical problem that prevents the Playwright MCP server from functioning correctly. The root cause is a version compatibility issue with the websockets library, which changed its API in version 15.0.1.

The recommended solution is to update the WebSocket handler signature to match the current library API by removing the path parameter. This fix is minimal, targeted, and maintains backward compatibility while resolving the immediate issue.

By implementing this solution and following the recommended prevention strategies, the MCP Bridge extension will be able to establish successful WebSocket connections and provide reliable browser automation capabilities.

## Files to Modify

1. **Primary Fix:**
   - `src/automata/mcp_server/server.py` - Lines 178, 458-467

2. **Testing:**
   - `scripts/test_mcp_bridge.py` - Verify the fix works
   - Create new test script for WebSocket validation

3. **Documentation:**
   - Update troubleshooting documentation
   - Add version compatibility notes

## Additional Resources

- [Websockets Library Documentation](https://websockets.readthedocs.io/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Aiohttp WebSocket Documentation](https://docs.aiohttp.org/en/stable/websockets.html)

---

**Document Version:** 1.0  
**Last Updated:** 2025-09-15  
**Author:** Playwright MCP Development Team