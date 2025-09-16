# MCP Bridge Extension Testing Guide

## Overview
This guide provides instructions for testing the MCP Bridge extension connectivity in Automata.

## Prerequisites
Before running the tests, ensure you have the following:

- Python 3.11 or higher
- Automata installed
- (Optional) Access to an MCP server running on ws://localhost:8080
- (Optional) A compatible browser with the MCP extension installed and running on port 9222

## Test Setup

### 1. Install Dependencies
```bash
# Install Automata and its dependencies
pip install -e .
```

### 2. Start MCP Server (Optional)
If you want to test with a real MCP server:
```bash
# Start a typical MCP server
mcp-server --port 8080
```

### 3. Start Browser with Extension (Optional)
If you want to test with a real browser extension:
1. Install the MCP browser extension in your browser
2. Start the browser with the extension enabled
3. Ensure the extension is listening on port 9222

## Running the Tests

### 1. Basic Test
Run the test script to verify MCP Bridge extension connectivity:
```bash
python3.11 test_mcp_bridge_extension.py
```

### 2. Verbose Test
Run the test script with verbose logging:
```bash
python3.11 test_mcp_bridge_extension.py --verbose
```

### 3. Test with Custom Configuration
Create a custom configuration file (e.g., `custom_config.json`):
```json
{
  "server_url": "ws://localhost:8080",
  "timeout": 30000,
  "retry_attempts": 3,
  "retry_delay": 1000,
  "bridge_extension_mode": true,
  "bridge_extension_port": 9222
}
```

Then run the test with the custom configuration:
```bash
python3.11 test_mcp_bridge_extension.py --config custom_config.json
```

## Understanding Test Results

### Expected Results Without Server or Extension
If you run the tests without a running MCP server or browser extension, you should see:
```
Extension Connectivity: FAIL
Extension Endpoints: FAIL
Overall Result: FAIL
```

This is expected behavior and indicates that the test script is correctly identifying connection issues.

### Expected Results With Server and Extension
If you run the tests with a running MCP server and browser extension, you should see:
```
Extension Connectivity: PASS
Extension Endpoints: PASS
Overall Result: PASS
```

### Error Messages
The test script provides detailed error messages to help identify connection issues:

1. **MCP Server Connection Errors**:
   ```
   Failed to connect to MCP Bridge: Failed to connect to MCP server: Failed to connect to WebSocket: [Errno 111] Connect call failed ('127.0.0.1', 8080)
   ```
   This indicates that the MCP server is not running or is not accessible at the specified URL.

2. **Browser Extension Connection Errors**:
   ```
   Error testing extension endpoints: Cannot connect to host localhost:9222 ssl:default [Connect call failed ('127.0.0.1', 9222)]
   ```
   This indicates that the browser extension is not running or is not accessible at the specified port.

## Troubleshooting

### 1. MCP Server Not Running
If you see MCP server connection errors:
1. Verify that the MCP server is running
2. Check the server URL and port in your configuration
3. Ensure network connectivity between the test script and the MCP server

### 2. Browser Extension Not Running
If you see browser extension connection errors:
1. Verify that the browser extension is installed and enabled
2. Check the extension port configuration
3. Ensure the browser is running with the extension
4. Try accessing the extension's JSON endpoint directly:
   ```bash
   curl http://localhost:9222/json
   ```

### 3. Unclosed Client Session Warning
If you see an unclosed client session warning:
```
asyncio - ERROR - Unclosed client session
client_session: <aiohttp.client.ClientSession object at 0x...>
```
This is a minor issue that doesn't affect the test results but should be addressed in future versions of the test script.

## Test Script Details

### Test Functions
The test script includes the following test functions:

1. **test_extension_connectivity()**
   - Tests the connection to the MCP Bridge in extension mode
   - Verifies that the bridge can connect to the MCP server
   - Tests basic communication with the extension

2. **test_extension_endpoints()**
   - Tests the various endpoints provided by the browser extension
   - Verifies that the extension's JSON endpoint is accessible
   - Checks that the extension returns valid tab information

### Configuration
The test script uses the following configuration parameters:

- `server_url`: URL of the MCP server (default: ws://localhost:8080)
- `timeout`: Connection timeout in milliseconds (default: 10000)
- `bridge_extension_mode`: Whether to use extension mode (default: true)
- `bridge_extension_port`: Port for extension mode communication (default: 9222)

## Customizing the Tests

### Adding New Test Cases
To add new test cases:
1. Create a new test function in the test script
2. Add the test function to the main() function
3. Update the test results reporting

### Modifying Test Parameters
To modify test parameters:
1. Edit the configuration values in the test script
2. Or create a custom configuration file and use the --config option

### Extending Test Coverage
To extend test coverage:
1. Add tests for additional MCP server capabilities
2. Add tests for additional browser extension endpoints
3. Add tests for error conditions and edge cases

## Best Practices

### 1. Test Environment
- Run tests in a clean environment without unnecessary services
- Ensure consistent network conditions for each test run
- Use virtual environments to manage dependencies

### 2. Test Data
- Use mock data when real data is not available
- Ensure test data is consistent and repeatable
- Clean up test data after each test run

### 3. Test Reporting
- Document test results thoroughly
- Include detailed error messages and logs
- Track test results over time to identify trends

## Conclusion
This guide provides comprehensive instructions for testing the MCP Bridge extension connectivity in Automata. By following these guidelines, you can ensure that your MCP Bridge implementation is working correctly and identify any connection issues quickly.
