# Automata

A lightweight and fast web automation app for personal use, focusing on CLI-based automation with helper tools for creating and executing workflows.

## Features

- CLI-based web automation using Playwright
- Helper tools for element selection and action building
- **NEW:** HTML Fragment Support - Generate selectors directly from HTML fragments
- **NEW:** Multiple Input Methods - Support for direct HTML input, fragment files, and stdin
- **NEW:** Flexible Targeting Modes - "all", "selector", and "auto" modes for element selection
- **NEW:** CSS and XPath Selector Generation - Choose your preferred selector type
- **NEW:** Credential Management - Securely manage and use credentials in workflows
- **NEW:** MCP Server Integration - Connect with AI assistants through Model Context Protocol
- **FIXED:** WebSocket Compatibility - Resolved MCP server WebSocket handler parameter mismatch issue
- Support for multiple authentication methods
- Workflow-based automation with JSON configuration
- Robust element selection with fallback mechanisms
- Conditional logic and looping capabilities
- Session persistence and cookie management

## Installation

### Prerequisites

- Python 3.11 or higher
- Chromium browser (installed automatically by Playwright)
- Node.js 18 or newer (for MCP server)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/automata.git
   cd automata
   ```

2. Set up the virtual environment and install dependencies:
   ```bash
   make setup
   ```

3. Install Playwright browsers:
   ```bash
   venv/bin/python3.11 -m playwright install chromium
   ```

## MCP Server Integration

Automata now includes an MCP (Model Context Protocol) server that enables AI assistants to interact with web pages through structured accessibility snapshots. This integration provides a powerful bridge between AI assistants and browser automation capabilities.

### Key Features

- **Fast and lightweight**: Uses Playwright's accessibility tree, not pixel-based input
- **LLM-friendly**: No vision models needed, operates purely on structured data
- **Deterministic tool application**: Avoids ambiguity common with screenshot-based approaches
- **WebSocket Compatible**: Fully compatible with the latest websockets library versions

### Getting Started with MCP Server

1. **Install the Playwright MCP server** with your preferred MCP client:

   ```json
   {
     "mcpServers": {
       "playwright": {
         "command": "npx",
         "args": [
           "@playwright/mcp@latest"
         ]
       }
     }
   }
   ```

2. **For Extension Mode** (to connect to existing browser tabs):

   ```json
   {
     "mcpServers": {
       "playwright-extension": {
         "command": "npx",
         "args": [
           "@playwright/mcp@latest",
           "--extension"
         ]
       }
     }
   }
   ```

3. **Install the Bridge Extension**:
   - Download the latest Chrome extension from: https://github.com/microsoft/playwright-mcp/releases
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked" and select the extension directory

### MCP Server Tools

The MCP server provides a comprehensive set of tools for browser automation:

- **Core Automation**: browser_click, browser_navigate, browser_type, browser_snapshot, etc.
- **Tab Management**: Create, close, and switch between browser tabs
- **Form Interaction**: Fill forms, select options, handle dialogs
- **Data Extraction**: Extract text, attributes, and structured data
- **Verification**: Verify element visibility, text content, and values
- **Advanced Features**: PDF generation, coordinate-based interactions, tracing

### Configuration Options

The MCP server supports extensive configuration options:

- Browser selection (Chrome, Firefox, WebKit)
- Headless/visible mode
- Viewport size and user agent customization
- Proxy settings and network controls
- Session persistence and storage management
- Security features (allowed/blocked origins)

For detailed configuration information, see [docs/Playwright_MCP.md](docs/Playwright_MCP.md) and [docs/Playwright_MCP_Bridge_Extension_Guide.md](docs/Playwright_MCP_Bridge_Extension_Guide.md).

## Usage

### Basic Commands

- Run automation workflow:
  ```bash
  automata run workflow.json
  ```

- Run automation workflow with credentials:
  ```bash
  automata run workflow.json --credentials credentials.json
  ```

- Build a workflow:
  ```bash
  automata build
  ```

- Start MCP server:
  ```bash
  python3.11 -m automata.mcp_server
  ```

- Get help:
  ```bash
  automata --help
  ```

### Development

- Run tests:
  ```bash
  make test
  ```

- Run tests with coverage:
  ```bash
  make test-cov
  ```

- Format code:
  ```bash
  make format
  ```

- Lint code:
  ```bash
  make lint
  ```

## Project Structure

```
automata/
├── src/
│   └── automata/
│       ├── __init__.py
│       ├── cli.py           # CLI interface
│       ├── core/            # Core automation engine
│       ├── auth/            # Authentication modules
│       ├── helpers/         # Helper tools
│       ├── workflows/       # Workflow management
│       └── mcp_server/      # MCP server implementation
├── tests/                   # Test files
├── docs/                    # Documentation
├── venv/                    # Virtual environment
├── Makefile                 # Build commands
└── setup.py                 # Package configuration
```

## WebSocket Compatibility

This project includes a comprehensive fix for WebSocket handler parameter compatibility issues with the websockets library version 15.0.1 and higher.

### Issue Summary
The MCP server implementation was affected by a breaking change in the websockets library that changed the handler signature from `handler(websocket, path)` to `handler(websocket)`. This caused a `TypeError` when trying to establish WebSocket connections.

### Resolution
- Fixed WebSocket handler parameter signature in `src/automata/mcp_server/server.py`
- Updated dependency version constraints in `requirements.txt` to prevent incompatible versions
- Enhanced error handling and logging for better debugging
- Created comprehensive documentation for the fix

### Documentation
For detailed information about the WebSocket compatibility issue and its resolution, see:
- [WebSocket Issue Resolution](playwright_mcp_websocket_issue_resolution.md)
- [WebSocket Compatibility Guide](docs/websocket_compatibility_guide.md)
- [WebSocket Fix Summary](websocket_fix_summary.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
