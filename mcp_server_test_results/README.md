# Playwright MCP Server Testing Framework

This directory contains a comprehensive testing framework for the Playwright MCP Server implementation. The tests are designed to verify the server's functionality, reliability, and cross-platform compatibility.

## Test Structure

The testing framework is organized into the following components:

### 1. Test Plan
- **File**: `test_plan.md`
- **Description**: Comprehensive test plan outlining all test scenarios, potential issues, and testing strategies.

### 2. Test Scripts
- **File**: `test_basic_functionality.py`
- **Description**: Tests for basic server functionality including startup, shutdown, health checks, and WebSocket connections.

- **File**: `test_json_command_parsing.py`
- **Description**: Tests for JSON command parsing and validation, including valid commands, invalid commands, and edge cases.

- **File**: `test_cross_platform_compatibility.py`
- **Description**: Tests for cross-platform compatibility, including platform detection, browser executable paths, file path handling, and platform-specific configurations.

### 3. Test Report Template
- **File**: `test_report_template.md`
- **Description**: Template for documenting test results, issues found, and recommendations.

### 4. Test Results
- **Directory**: Various `.log` and `.json` files
- **Description**: Raw test results and logs generated during test execution.

## Running the Tests

### Prerequisites

1. Python 3.11 or higher
2. Required Python packages:
   - aiohttp
   - websockets
   - playwright
   - jsonschema

3. Playwright browsers installed:
   ```bash
   python3.11 -m playwright install
   ```

### Running Individual Tests

To run a specific test script:

```bash
# Basic functionality tests
python3.11 mcp_server_test_results/test_basic_functionality.py

# JSON command parsing tests
python3.11 mcp_server_test_results/test_json_command_parsing.py

# Cross-platform compatibility tests
python3.11 mcp_server_test_results/test_cross_platform_compatibility.py
```

### Running All Tests

To run all tests sequentially:

```bash
# Run basic functionality tests
python3.11 mcp_server_test_results/test_basic_functionality.py

# Run JSON command parsing tests
python3.11 mcp_server_test_results/test_json_command_parsing.py

# Run cross-platform compatibility tests
python3.11 mcp_server_test_results/test_cross_platform_compatibility.py
```

### Test Output

Each test script generates:
1. Console output with real-time test progress
2. Log files in the `mcp_server_test_results/` directory
3. JSON files with detailed test results

## Interpreting Test Results

### Test Summary

Each test script prints a summary at the end with:
- Total number of tests
- Number of passed tests
- Number of failed tests
- Success rate percentage
- List of failed tests with details

### Detailed Results

Detailed test results are saved in JSON files:
- `basic_functionality_results.json`
- `json_command_parsing_results.json`
- `cross_platform_compatibility_results.json`

Each result entry includes:
- Test name
- Pass/fail status
- Detailed information
- Timestamp
- Platform information

### Log Files

Log files provide detailed information during test execution:
- `basic_functionality.log`
- `json_command_parsing.log`
- `cross_platform_compatibility.log`

## Test Categories

### 1. Basic Functionality Tests
These tests verify the fundamental server operations:
- Server startup and shutdown
- Health check endpoint
- WebSocket connections
- Server info endpoint
- Commands list endpoint
- Command schema endpoint

### 2. JSON Command Parsing Tests
These tests verify the command parsing and validation:
- Valid command parsing for all supported command types
- Invalid JSON command handling
- Missing required fields
- Invalid field values
- Commands with additional properties
- Edge case values
- Command schema validation

### 3. Cross-Platform Compatibility Tests
These tests verify cross-platform compatibility:
- Platform detection
- Browser executable path detection
- File path handling
- Temporary directory configuration
- Cross-browser compatibility
- Platform-specific commands
- Error screenshot path handling
- Configuration file paths

## Potential Issues Identified

Based on analysis of the codebase, the following potential issues have been identified:

### 1. Cross-Platform Browser Path Issues
The code includes platform-specific browser executable paths that may not be correctly configured on Windows vs Linux.

### 2. WebSocket Connection Handling
The MCP server relies on WebSocket connections that may behave differently across platforms.

### 3. Async/Await Pattern Inconsistencies
The code uses extensive async/await patterns that may have platform-specific timing issues.

### 4. Browser Context and Page Management
Multiple browser contexts and pages may not be properly cleaned up on all platforms.

### 5. JSON Command Parsing and Validation
The command parser uses JSON schema validation that may have platform-specific quirks.

### 6. Error Handling and Logging
Error handling mechanisms may not work consistently across platforms.

### 7. Memory and Resource Management
Browser automation may leak resources differently on Windows vs Linux.

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Error: `OSError: [Errno 98] Address already in use`
   - Solution: Change the port number in the test script or kill the process using the port.

2. **Browser Not Found**
   - Error: `BrowserTypeNotFound: Browser type not found`
   - Solution: Install Playwright browsers with `python3.11 -m playwright install`.

3. **Missing Dependencies**
   - Error: `ModuleNotFoundError: No module named 'xxx'`
   - Solution: Install the required dependencies with `pip install`.

4. **Permission Denied**
   - Error: `PermissionError: [Errno 13] Permission denied`
   - Solution: Check file permissions and run with appropriate privileges.

### Debug Mode

To enable debug logging, set the log level to DEBUG in the test scripts:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Generating Test Reports

To generate a comprehensive test report:

1. Run all test scripts
2. Collect the results from the JSON files
3. Fill in the `test_report_template.md` with the collected data
4. Add any issues found and recommendations

## Continuous Integration

These tests can be integrated into a CI/CD pipeline to ensure ongoing compatibility and functionality:

```yaml
# Example GitHub Actions workflow
name: MCP Server Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: [3.11]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install aiohttp websockets playwright jsonschema
        python -m playwright install
    - name: Run tests
      run: |
        python mcp_server_test_results/test_basic_functionality.py
        python mcp_server_test_results/test_json_command_parsing.py
        python mcp_server_test_results/test_cross_platform_compatibility.py
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: test-results-${{ matrix.os }}
        path: mcp_server_test_results/
```

## Contributing

When adding new tests:

1. Follow the existing test structure and naming conventions
2. Add appropriate logging and error handling
3. Update the test plan and documentation
4. Ensure tests work on all supported platforms

## License

This testing framework is part of the Automata project and is subject to the same license terms.
