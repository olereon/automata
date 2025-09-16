# Playwright MCP and Bridge Extension Guide for Automata CLI

## Table of Contents
1. [Introduction](#introduction)
2. [Overview](#overview)
3. [Installation and Setup](#installation-and-setup)
   - [Prerequisites](#prerequisites)
   - [Installing Playwright MCP](#installing-playwright-mcp)
   - [Installing the Bridge Extension](#installing-the-bridge-extension)
   - [Configuring Automata CLI](#configuring-automata-cli)
4. [Getting Started](#getting-started)
   - [Basic Configuration](#basic-configuration)
   - [Connecting to Existing Browser Tabs](#connecting-to-existing-browser-tabs)
   - [First Automation Example](#first-automation-example)
5. [Advanced Configuration](#advanced-configuration)
   - [Configuration File Options](#configuration-file-options)
   - [Command Line Arguments](#command-line-arguments)
   - [User Profile Management](#user-profile-management)
6. [Workflows and Automation](#workflows-and-automation)
   - [Creating Workflows](#creating-workflows)
   - [Executing Workflows](#executing-workflows)
   - [Session Management](#session-management)
   - [Template Usage](#template-usage)
7. [Playwright MCP Tools and Capabilities](#playwright-mcp-tools-and-capabilities)
   - [Core Automation Tools](#core-automation-tools)
   - [Tab Management](#tab-management)
   - [Browser Installation](#browser-installation)
   - [Coordinate-based Interactions](#coordinate-based-interactions)
   - [PDF Generation](#pdf-generation)
   - [Verification Tools](#verification-tools)
   - [Tracing](#tracing)
8. [Integration with Automata CLI](#integration-with-automata-cli)
   - [CLI Commands](#cli-commands)
   - [Helper Tools](#helper-tools)
   - [Browser Exploration](#browser-exploration)
9. [Troubleshooting](#troubleshooting)
   - [Common Issues](#common-issues)
   - [WebSocket Compatibility](#websocket-compatibility)
   - [Debugging Tips](#debugging-tips)
10. [Best Practices](#best-practices)
    - [Security Considerations](#security-considerations)
    - [Performance Optimization](#performance-optimization)
    - [Error Handling](#error-handling)
11. [Examples and Use Cases](#examples-and-use-cases)
    - [Web Scraping](#web-scraping)
    - [Form Interaction](#form-interaction)
    - [Data Extraction](#data-extraction)
    - [Authentication Workflows](#authentication-workflows)
    - [Testing Scenarios](#testing-scenarios)
12. [Conclusion](#conclusion)

## Introduction

This guide provides a comprehensive overview of using Playwright MCP and the Bridge extension with Automata CLI to automate workflows using existing tabs in your daily browser. This powerful combination allows you to leverage the state of your default user profile, enabling AI assistants to interact with websites where you're already logged in, using your existing cookies, sessions, and browser state.

## Overview

### What is Playwright MCP?

Playwright MCP is a Model Context Protocol (MCP) server that provides browser automation capabilities using Playwright. It enables LLMs to interact with web pages through structured accessibility snapshots, bypassing the need for screenshots or visually-tuned models.

Key features:
- **Fast and lightweight**: Uses Playwright's accessibility tree, not pixel-based input
- **LLM-friendly**: No vision models needed, operates purely on structured data
- **Deterministic tool application**: Avoids ambiguity common with screenshot-based approaches

### What is the Bridge Extension?

The Playwright MCP Chrome Extension (Bridge Extension) allows you to connect to pages in your existing browser and leverage the state of your default user profile. This means the AI assistant can interact with websites where you're already logged in, using your existing cookies, sessions, and browser state, providing a seamless experience without requiring separate authentication or setup.

### What is Automata CLI?

Automata CLI is a powerful command-line interface for web automation that provides a comprehensive set of features for creating, managing, and executing web automation workflows. It integrates with Playwright MCP and the Bridge Extension to provide a complete automation solution.

## Installation and Setup

### Prerequisites

Before you begin, ensure you have the following:

- Python 3.11 or higher
- Chrome/Edge/Chromium browser
- Node.js 18 or newer (for Playwright MCP)
- pip (Python package manager)

### Installing Playwright MCP

1. **Standard Installation**:

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

2. **For Extension Mode**:

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

### Installing the Bridge Extension

1. **Download the Extension**:
   - Download the latest Chrome extension from GitHub: https://github.com/microsoft/playwright-mcp/releases

2. **Load Chrome Extension**:
   1. Open Chrome and navigate to `chrome://extensions/`
   2. Enable "Developer mode" (toggle in the top right corner)
   3. Click "Load unpacked" and select the extension directory

### Configuring Automata CLI

1. **Install from Source**:

```bash
git clone https://github.com/yourusername/web-automation-tool.git
cd web-automation-tool
make setup
```

2. **Verify Installation**:

```bash
make check
```

3. **Initialize Configuration**:

```bash
python3.11 -m automata config init
```

This creates a configuration file at `~/.automata/config.json` with default settings.

## Getting Started

### Basic Configuration

1. **Show Configuration**:

```bash
python3.11 -m automata config show
```

2. **Basic CLI Usage**:

```bash
# Show help
python3.11 -m automata --help

# Show help for a specific command
python3.11 -m automata workflow --help
```

### Connecting to Existing Browser Tabs

When the LLM interacts with the browser for the first time with the Bridge extension, it will load a page where you can select which browser tab the LLM will connect to. This allows you to control which specific page the AI assistant will interact with during the session.

### First Automation Example

1. **Start an interactive browser exploration session**:

```bash
# Run in visible mode (default)
python3.11 -m automata browser explore

# Run in headless mode
python3.11 -m automata browser explore --headless
```

2. **Create a simple workflow**:

```bash
python3.11 -m automata workflow create --output my_workflow.json
```

3. **Execute the workflow**:

```bash
python3.11 -m automata workflow execute my_workflow.json
```

## Advanced Configuration

### Configuration File Options

The Playwright MCP server can be configured using a JSON configuration file. You can specify the configuration file using the `--config` command line option:

```bash
npx @playwright/mcp@latest --config path/to/config.json
```

#### Configuration File Schema

```typescript
{
  // Browser configuration
  browser?: {
    // Browser type to use (chromium, firefox, or webkit)
    browserName?: 'chromium' | 'firefox' | 'webkit';

    // Keep the browser profile in memory, do not save it to disk.
    isolated?: boolean;

    // Path to user data directory for browser profile persistence
    userDataDir?: string;

    // Browser launch options (see Playwright docs)
    launchOptions?: {
      channel?: string;        // Browser channel (e.g. 'chrome')
      headless?: boolean;      // Run in headless mode
      executablePath?: string; // Path to browser executable
      // ... other Playwright launch options
    };

    // Browser context options
    contextOptions?: {
      viewport?: { width: number, height: number };
      // ... other Playwright context options
    };

    // CDP endpoint for connecting to existing browser
    cdpEndpoint?: string;

    // Remote Playwright server endpoint
    remoteEndpoint?: string;
  },

  // Server configuration
  server?: {
    port?: number;  // Port to listen on
    host?: string;  // Host to bind to (default: localhost)
  },

  // List of additional capabilities
  capabilities?: Array<
    'tabs' |    // Tab management
    'install' | // Browser installation
    'pdf' |     // PDF generation
    'vision' |  // Coordinate-based interactions
  >;

  // Directory for output files
  outputDir?: string;

  // Network configuration
  network?: {
    // List of origins to allow the browser to request. Default is to allow all.
    allowedOrigins?: string[];

    // List of origins to block the browser to request.
    blockedOrigins?: string[];
  },
 
  /**
   * Whether to send image responses to the client. Can be "allow" or "omit". 
   * Defaults to "allow".
   */
  imageResponses?: 'allow' | 'omit';
}
```

### Command Line Arguments

Playwright MCP server supports the following arguments:

```
> npx @playwright/mcp@latest --help
  --allowed-origins <origins>     semicolon-separated list of origins to allow
                                  the browser to request. Default is to allow
                                  all.
  --blocked-origins <origins>     semicolon-separated list of origins to block
                                  the browser from requesting. Blocklist is
                                  evaluated before allowlist.
  --block-service-workers         block service workers
  --browser <browser>             browser or chrome channel to use, possible
                                  values: chrome, firefox, webkit, msedge.
  --caps <caps>                   comma-separated list of additional
                                  capabilities to enable, possible values:
                                  vision, pdf.
  --cdp-endpoint <endpoint>       CDP endpoint to connect to.
  --cdp-header <headers...>       CDP headers to send with the connect request,
                                  multiple can be specified.
  --config <path>                 path to the configuration file.
  --device <device>               device to emulate, for example: "iPhone 15"
  --executable-path <path>        path to the browser executable.
  --extension                     Connect to a running browser instance
                                  (Edge/Chrome only). Requires the "Playwright
                                  MCP Bridge" browser extension to be installed.
  --headless                      run browser in headless mode, headed by
                                  default
  --host <host>                   host to bind server to. Default is localhost.
                                  Use 0.0.0.0 to bind to all interfaces.
  --ignore-https-errors           ignore https errors
  --isolated                      keep the browser profile in memory, do not
                                  save it to disk.
  --image-responses <mode>        whether to send image responses to the client.
                                  Can be "allow" or "omit", Defaults to "allow".
  --no-sandbox                    disable the sandbox for all process types that
                                  are normally sandboxed.
  --output-dir <path>             path to the directory for output files.
  --port <port>                   port to listen on for SSE transport.
  --proxy-bypass <bypass>         comma-separated domains to bypass proxy, for
                                  example ".com,chromium.org,.domain.com"
  --proxy-server <proxy>          specify proxy server, for example
                                  "http://myproxy:3128" or
                                  "socks5://myproxy:8080"
  --save-session                  Whether to save the Playwright MCP session
                                  into the output directory.
  --save-trace                    Whether to save the Playwright Trace of the
                                  session into the output directory.
  --secrets <path>                path to a file containing secrets in the
                                  dotenv format
  --storage-state <path>          path to the storage state file for isolated
                                  sessions.
  --timeout-action <timeout>      specify action timeout in milliseconds,
                                  defaults to 5000ms
  --timeout-navigation <timeout>  specify navigation timeout in milliseconds,
                                  defaults to 60000ms
  --user-agent <ua string>        specify user agent string
  --user-data-dir <path>          path to the user data directory. If not
                                  specified, a temporary directory will be
                                  created.
  --viewport-size <size>          specify browser viewport size in pixels, for
                                  example "1280, 720"
```

### User Profile Management

You can run Playwright MCP with persistent profile like a regular browser (default), in isolated contexts for testing sessions, or connect to your existing browser using the browser extension.

#### Persistent Profile

All the logged in information will be stored in the persistent profile, you can delete it between sessions if you'd like to clear the offline state.
Persistent profile is located at the following locations and you can override it with the `--user-data-dir` argument.

```bash
# Windows
%USERPROFILE%\AppData\Local\ms-playwright\mcp-{channel}-profile

# macOS
- ~/Library/Caches/ms-playwright/mcp-{channel}-profile

# Linux
- ~/.cache/ms-playwright/mcp-{channel}-profile
```

#### Isolated

In the isolated mode, each session is started in the isolated profile. Every time you ask MCP to close the browser, the session is closed and all the storage state for this session is lost. You can provide initial storage state to the browser via the config's `contextOptions` or via the `--storage-state` argument.

```js
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--isolated",
        "--storage-state={path/to/storage.json}"
      ]
    }
  }
}
```

#### Browser Extension

The Playwright MCP Chrome Extension allows you to connect to existing browser tabs and leverage your logged-in sessions and browser state.

## Workflows and Automation

### Creating Workflows

Workflows are JSON files that define a sequence of actions to be performed on web pages.

1. **Create a new workflow interactively**:

```bash
python3.11 -m automata workflow create --output my_workflow.json
```

2. **Example Workflow Structure**:

```json
{
  "name": "Simple Web Scraping",
  "version": "1.0.0",
  "description": "Scrape article titles and descriptions from a news website",
  "variables": {
    "url": "https://example-news.com",
    "output_file": "articles.json"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for articles to load",
      "action": "wait_for",
      "selector": ".article",
      "timeout": 10
    },
    {
      "name": "Extract article data",
      "action": "extract",
      "selector": ".article",
      "value": {
        "title": ".title",
        "description": ".description",
        "url": {
          "attribute": "href",
          "selector": "a"
        }
      }
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}"
    }
  ]
}
```

### Executing Workflows

1. **Execute a workflow from a file**:

```bash
python3.11 -m automata workflow execute my_workflow.json
```

2. **Session Options**:

```bash
# Execute with a saved session
python3.11 -m automata workflow execute my_workflow.json --session my_session_id

# Save session after execution
python3.11 -m automata workflow execute my_workflow.json --save-session my_session_id
```

3. **Browser Options**:

```bash
# Run in headless mode (default)
python3.11 -m automata workflow execute my_workflow.json --headless

# Run in visible mode
python3.11 -m automata workflow execute my_workflow.json --visible
```

### Session Management

Session management allows you to save browser sessions (cookies, localStorage, sessionStorage) and restore them later, enabling persistent login states across workflow executions.

#### CLI Session Management Commands

1. **Saving Sessions**:

```bash
# Basic session save
python3.11 -m automata session save my_session_id

# Save with custom expiry (in days)
python3.11 -m automata session save my_session_id --expiry 7

# Save with encryption for sensitive data
python3.11 -m automata session save my_session_id --encryption-key "my_secret_key"

# Navigate to a URL before saving
python3.11 -m automata session save my_session_id --url https://example.com/login

# Save in visible mode for debugging
python3.11 -m automata session save my_session_id --visible
```

2. **Restoring Sessions**:

```bash
# Basic session restore
python3.11 -m automata session restore my_session_id

# Restore with encryption
python3.11 -m automata session restore my_session_id --encryption-key "my_secret_key"

# Navigate to a URL after restoring
python3.11 -m automata session restore my_session_id --url https://example.com/dashboard

# Restore in visible mode for debugging
python3.11 -m automata session restore my_session_id --visible
```

3. **Listing Sessions**:

```bash
# List active sessions
python3.11 -m automata session list

# Include expired sessions
python3.11 -m automata session list --include-expired

# List encrypted sessions
python3.11 -m automata session list --encryption-key "my_secret_key"
```

### Template Usage

Templates are reusable workflow definitions that can be customized with variables.

1. **Create a template from a workflow**:

```bash
python3.11 -m automata template create my_template my_workflow.json --description "My template"
```

2. **Create a workflow from a template**:

```bash
python3.11 -m automata template use my_template my_workflow --variable name=value
```

3. **Managing Templates**:

```bash
# List all templates
python3.11 -m automata template list

# Search for templates
python3.11 -m automata template search "login" --tag authentication

# Delete a template
python3.11 -m automata template delete my_template
```

## Playwright MCP Tools and Capabilities

### Core Automation Tools

- **browser_click**: Perform click on a web page
- **browser_close**: Close the page
- **browser_console_messages**: Returns all console messages
- **browser_drag**: Perform drag and drop between two elements
- **browser_evaluate**: Evaluate JavaScript expression on page or element
- **browser_file_upload**: Upload one or multiple files
- **browser_fill_form**: Fill multiple form fields
- **browser_handle_dialog**: Handle a dialog
- **browser_hover**: Hover over element on page
- **browser_navigate**: Navigate to a URL
- **browser_navigate_back**: Go back to the previous page
- **browser_network_requests**: List network requests
- **browser_press_key**: Press a key on the keyboard
- **browser_resize**: Resize the browser window
- **browser_select_option**: Select an option in a dropdown
- **browser_snapshot**: Capture accessibility snapshot of the current page
- **browser_take_screenshot**: Take a screenshot of the current page
- **browser_type**: Type text into editable element
- **browser_wait_for**: Wait for text to appear or disappear or a specified time to pass

### Tab Management

- **browser_tabs**: List, create, close, or select a browser tab

### Browser Installation

- **browser_install**: Install the browser specified in the config

### Coordinate-based Interactions (opt-in via --caps=vision)

- **browser_mouse_click_xy**: Click left mouse button at a given position
- **browser_mouse_drag_xy**: Drag left mouse button to a given position
- **browser_mouse_move_xy**: Move mouse to a given position

### PDF Generation (opt-in via --caps=pdf)

- **browser_pdf_save**: Save page as PDF

### Verification Tools (opt-in via --caps=verify)

- **browser_verify_element_visible**: Verify element is visible on the page
- **browser_verify_list_visible**: Verify list is visible on the page
- **browser_verify_text_visible**: Verify text is visible on the page
- **browser_verify_value**: Verify element value

### Tracing (opt-in via --caps=tracing)

- **browser_start_tracing**: Start trace recording
- **browser_stop_tracing**: Stop trace recording

## Integration with Automata CLI

### CLI Commands

Automata CLI provides comprehensive commands for web automation:

```bash
# Workflow commands
python3.11 -m automata workflow create --output my_workflow.json
python3.11 -m automata workflow execute my_workflow.json
python3.11 -m automata workflow validate my_workflow.json
python3.11 -m automata workflow edit my_workflow.json

# Session commands
python3.11 -m automata session save my_session_id
python3.11 -m automata session restore my_session_id
python3.11 -m automata session list
python3.11 -m automata session delete my_session_id

# Template commands
python3.11 -m automata template create my_template my_workflow.json
python3.11 -m automata template use my_template my_workflow --variable name=value
python3.11 -m automata template list
python3.11 -m automata template delete my_template

# Configuration commands
python3.11 -m automata config show
python3.11 -m automata config init
```

### Helper Tools

1. **HTML Parsing**:

```bash
python3.11 -m automata helper parse-html page.html
```

2. **Selector Generation**:

```bash
# From an HTML file
python3.11 -m automata helper generate-selectors --file page.html

# From an HTML fragment
python3.11 -m automata helper generate-selectors --html-fragment "<div id='test'>Content</div>"

# From stdin
echo "<div id='test'>Content</div>" | python3.11 -m automata helper generate-selectors --stdin

# With custom targeting
python3.11 -m automata helper generate-selectors --file page.html --targeting-mode selector --custom-selector "#test"
```

3. **Action Building**:

```bash
python3.11 -m automata helper build-action
```

### Browser Exploration

Start an interactive browser exploration session:

```bash
# Run in visible mode (default)
python3.11 -m automata browser explore

# Run in headless mode
python3.11 -m automata browser explore --headless
```

## Troubleshooting

### Common Issues

#### Installation and Setup Issues

1. **Python version not compatible**:
   - Automata requires Python 3.11
   - Check your Python version: `python3.11 --version`
   - Install Python 3.11 if needed

2. **Dependencies not installing correctly**:
   - Update pip: `python3.11 -m pip install --upgrade pip`
   - Install manually: `python3.11 -m pip install -r requirements.txt`
   - Try a new virtual environment

3. **Playwright browsers not installing**:
   - Check disk space
   - Install manually: `python3.11 -m playwright install chromium`
   - Configure proxy if needed

#### Browser Issues

1. **Browser not starting**:
   - Install Playwright browsers: `python3.11 -m playwright install`
   - Check for conflicting browser processes
   - Use debug logging: `automata --log-level debug workflow execute my_workflow.json`

2. **Elements not found**:
   - Ensure page is fully loaded
   - Use explicit waits: `wait_for_element_visible`
   - Check for iframes
   - Try different selectors
   - Use helper tools: `automata helper generate-selectors page.html`

3. **Timeouts**:
   - Increase timeout values
   - Check internet connection
   - Ensure page is not waiting for additional resources
   - Use explicit waits instead of fixed timeouts

#### Workflow Issues

1. **Workflow validation fails**:
   - Check error messages
   - Ensure required fields are present
   - Use validator: `automata workflow validate my_workflow.json`
   - Refer to workflow schema

2. **Workflow execution stops unexpectedly**:
   - Use debug logging: `automata --log-level debug workflow execute my_workflow.json`
   - Check for unhandled exceptions
   - Ensure proper error handling
   - Execute step by step

3. **Variables not working correctly**:
   - Ensure variables are defined
   - Check spelling
   - Use correct syntax: `{{variable_name}}`
   - Verify variable types

### WebSocket Compatibility

The project includes a comprehensive fix for WebSocket handler parameter compatibility issues with the websockets library version 15.0.1 and higher.

#### Understanding the Issue

The MCP server implementation was affected by a breaking change in the websockets library that changed the handler signature from `handler(websocket, path)` to `handler(websocket)`.

#### Error Symptoms

```
TypeError: websocket_handler() takes 2 positional arguments but 3 were given
TypeError: MCPServer.handle_websocket() missing 1 required positional argument: 'path'
ERROR:websockets.server:connection handler failed
```

#### Solutions

1. **Check your websockets library version**:
   ```bash
   python3.11 -m pip show websockets
   ```

2. **If using version 15.0.1 or higher**, the code has been updated to work correctly.

3. **If you need to downgrade** (not recommended as the fix is already implemented):
   ```bash
   python3.11 -m pip install "websockets>=10.0,<15.0"
   ```

#### Verification

1. **Start the MCP server**:
   ```bash
   python3.11 scripts/start_mcp_server.py
   ```

2. **Run the test script**:
   ```bash
   python3.11 scripts/test_websocket_fix.py
   ```

3. **Check for successful connection establishment** and message handling.

### Debugging Tips

1. **Enable Debug Logging**:
   ```bash
   automata --log-level debug workflow execute my_workflow.json
   ```

2. **Take Screenshots**:
   ```json
   {
     "name": "Take screenshot",
     "action": "screenshot",
     "value": "debug_screenshot.png"
   }
   ```

3. **Save Page Source**:
   ```json
   {
     "name": "Save page source",
     "action": "save_page_source",
     "value": "debug_page.html"
   }
   ```

4. **Use the Helper Tools**:
   ```bash
   automata helper parse-html page.html
   automata helper generate-selectors page.html
   ```

5. **Step Through Your Workflow**:
   ```json
   {
     "name": "Pause for debugging",
     "action": "pause"
   }
   ```

6. **Check Element Visibility**:
   ```json
   {
     "name": "Check if button is visible",
     "action": "wait_for_element_visible",
     "selector": "#submit-button",
     "timeout": 10
   }
   ```

7. **Handle Errors Gracefully**:
   ```json
   {
     "name": "Click button with error handling",
     "action": "click",
     "selector": "#submit-button",
     "on_error": "continue"
   }
   ```

8. **Test Selectors Manually**:
   - Use browser developer tools to test selectors before using them in workflows

9. **Use Explicit Waits**:
   ```json
   {
     "name": "Wait for content to load",
     "action": "wait_for",
     "selector": ".content",
     "timeout": 10
   }
   ```

## Best Practices

### Security Considerations

1. **Use Encryption for Sensitive Data**:
   - Always encrypt sessions that contain sensitive information
   ```bash
   python3.11 -m automata workflow execute login.json --save-session secure_session --encryption-key "your_secure_key"
   ```

2. **Use Descriptive Session IDs**:
   - Choose meaningful names for sessions to easily identify their purpose
   ```bash
   # Good
   python3.11 -m automata workflow execute login.json --save-session admin_dashboard_login
   
   # Avoid
   python3.11 -m automata workflow execute login.json --save-session session1
   ```

3. **Set Appropriate Expiry Times**:
   - Match session expiry to security requirements
   ```bash
   # Short-term sessions for testing
   python3.11 -m automata workflow execute login.json --save-session test_session --expiry 1
   
   # Long-term sessions for regular operations
   python3.11 -m automata workflow execute login.json --save-session regular_session --expiry 30
   ```

4. **Regular Session Cleanup**:
   - Periodically clean up expired sessions
   ```bash
   python3.11 -m automata session cleanup
   ```

5. **Test Sessions Before Production**:
   - Always test saved sessions in a non-production environment first
   ```bash
   # Test session restoration
   python3.11 -m automata session restore test_session --visible
   ```

### Performance Optimization

1. **Reduce Unnecessary Waits and Delays**:
   - Use explicit waits instead of fixed delays where possible
   - Minimize the number of actions in workflows

2. **Use More Specific Selectors**:
   - Specific selectors speed up element selection
   - Use ID selectors when available: `#element-id`
   - Use class selectors: `.element-class`
   - Avoid complex XPath selectors when possible

3. **Minimize Browser Resource Usage**:
   - Disable unnecessary browser features (images, JavaScript) if not needed
   - Properly close pages and tabs when no longer needed
   - Avoid storing large amounts of data in variables

4. **Break Long Workflows**:
   - Consider breaking long workflows into smaller, separate workflows
   - Use session management to maintain state between workflows

### Error Handling

1. **Add Error Handling to Actions**:
   ```json
   {
     "name": "Click button with error handling",
     "action": "click",
     "selector": "#submit-button",
     "on_error": "continue"
   }
   ```

2. **Use Retry Logic for Unreliable Actions**:
   ```json
   {
     "name": "Try to click a button that might not exist",
     "action": "click",
     "selector": "#non-existent-button",
     "on_error": "retry",
     "retry": {
       "max_attempts": 3,
       "delay": 2
     }
   }
   ```

3. **Handle Conditional Logic**:
   ```json
   {
     "name": "Check if element exists",
     "action": "evaluate",
     "value": "document.querySelector('.element') !== null"
   },
   {
     "name": "Handle based on element existence",
     "action": "if",
     "value": {
       "operator": "equals",
       "left": "{{evaluate}}",
       "right": true
     },
     "steps": [
       {
         "name": "Element exists action",
         "action": "click",
         "selector": ".element"
       }
     ],
     "else_steps": [
       {
         "name": "Element doesn't exist action",
         "action": "navigate",
         "value": "/alternative-page"
       }
     ]
   }
   ```

## Examples and Use Cases

### Web Scraping

#### Simple Web Scraping

```json
{
  "name": "Simple Web Scraping",
  "version": "1.0.0",
  "description": "Scrape article titles and descriptions from a news website",
  "variables": {
    "url": "https://example-news.com",
    "output_file": "articles.json"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for articles to load",
      "action": "wait_for",
      "selector": ".article",
      "timeout": 10
    },
    {
      "name": "Extract article data",
      "action": "extract",
      "selector": ".article",
      "value": {
        "title": ".title",
        "description": ".description",
        "url": {
          "attribute": "href",
          "selector": "a"
        }
      }
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}"
    }
  ]
}
```

#### Pagination Handling

```json
{
  "name": "Pagination Handling",
  "version": "1.0.0",
  "description": "Scrape data from multiple pages with pagination",
  "variables": {
    "base_url": "https://example-news.com",
    "output_file": "articles.json",
    "max_pages": 10,
    "current_page": 1,
    "all_articles": []
  },
  "steps": [
    {
      "name": "Initialize articles array",
      "action": "set_variable",
      "selector": "all_articles",
      "value": []
    },
    {
      "name": "Loop through pages",
      "action": "loop",
      "value": {
        "type": "while",
        "condition": {
          "operator": "less_than_or_equals",
          "left": "{{current_page}}",
          "right": "{{max_pages}}"
        },
        "steps": [
          {
            "name": "Navigate to page",
            "action": "navigate",
            "value": "{{base_url}}?page={{current_page}}"
          },
          {
            "name": "Wait for articles to load",
            "action": "wait_for",
            "selector": ".article",
            "timeout": 10
          },
          {
            "name": "Extract article data",
            "action": "extract",
            "selector": ".article",
            "value": {
              "title": ".title",
              "description": ".description",
              "url": {
                "attribute": "href",
                "selector": "a"
              }
            }
          },
          {
            "name": "Add articles to collection",
            "action": "execute_script",
            "value": "all_articles = all_articles + extract_article_data; set_variable('all_articles', all_articles);"
          },
          {
            "name": "Check if next button exists",
            "action": "evaluate",
            "value": "document.querySelector('.next-button') !== null"
          },
          {
            "name": "Increment page counter",
            "action": "set_variable",
            "selector": "current_page",
            "value": "{{current_page + 1}}"
          },
          {
            "name": "Click next button if exists",
            "action": "if",
            "value": {
              "operator": "equals",
              "left": "{{evaluate}}",
              "right": true
            },
            "steps": [
              {
                "name": "Click next button",
                "action": "click",
                "selector": ".next-button"
              }
            ]
          }
        ]
      }
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}",
      "data": "{{all_articles}}"
    }
  ]
}
```

### Form Interaction

#### Simple Form Submission

```json
{
  "name": "Simple Form Submission",
  "version": "1.0.0",
  "description": "Fill out and submit a simple form",
  "variables": {
    "url": "https://example.com/contact",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "message": "This is a test message."
  },
  "steps": [
    {
      "name": "Navigate to form page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for form to load",
      "action": "wait_for",
      "selector": "#contact-form",
      "timeout": 10
    },
    {
      "name": "Enter name",
      "action": "type",
      "selector": "#name",
      "value": "{{name}}"
    },
    {
      "name": "Enter email",
      "action": "type",
      "selector": "#email",
      "value": "{{email}}"
    },
    {
      "name": "Enter message",
      "action": "type",
      "selector": "#message",
      "value": "{{message}}"
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Wait for confirmation",
      "action": "wait_for",
      "selector": ".success-message",
      "timeout": 10
    }
  ]
}
```

#### Multi-Step Form

```json
{
  "name": "Multi-Step Form",
  "version": "1.0.0",
  "description": "Fill out a multi-step form",
  "variables": {
    "url": "https://example.com/register",
    "username": "johndoe",
    "password": "securepassword",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip": "12345"
  },
  "steps": [
    {
      "name": "Navigate to registration page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for form to load",
      "action": "wait_for",
      "selector": "#registration-form",
      "timeout": 10
    },
    {
      "name": "Step 1: Account Information",
      "action": "execute_script",
      "value": "console.log('Filling out Step 1: Account Information');"
    },
    {
      "name": "Enter username",
      "action": "type",
      "selector": "#username",
      "value": "{{username}}"
    },
    {
      "name": "Enter password",
      "action": "type",
      "selector": "#password",
      "value": "{{password}}"
    },
    {
      "name": "Enter email",
      "action": "type",
      "selector": "#email",
      "value": "{{email}}"
    },
    {
      "name": "Click next button",
      "action": "click",
      "selector": "#step1-next"
    },
    {
      "name": "Wait for step 2 to load",
      "action": "wait_for",
      "selector": "#step2",
      "timeout": 10
    },
    {
      "name": "Step 2: Personal Information",
      "action": "execute_script",
      "value": "console.log('Filling out Step 2: Personal Information');"
    },
    {
      "name": "Enter first name",
      "action": "type",
      "selector": "#first-name",
      "value": "{{first_name}}"
    },
    {
      "name": "Enter last name",
      "action": "type",
      "selector": "#last-name",
      "value": "{{last_name}}"
    },
    {
      "name": "Click next button",
      "action": "click",
      "selector": "#step2-next"
    },
    {
      "name": "Wait for step 3 to load",
      "action": "wait_for",
      "selector": "#step3",
      "timeout": 10
    },
    {
      "name": "Step 3: Address Information",
      "action": "execute_script",
      "value": "console.log('Filling out Step 3: Address Information');"
    },
    {
      "name": "Enter address",
      "action": "type",
      "selector": "#address",
      "value": "{{address}}"
    },
    {
      "name": "Enter city",
      "action": "type",
      "selector": "#city",
      "value": "{{city}}"
    },
    {
      "name": "Enter state",
      "action": "type",
      "selector": "#state",
      "value": "{{state}}"
    },
    {
      "name": "Enter zip code",
      "action": "type",
      "selector": "#zip",
      "value": "{{zip}}"
    },
    {
      "name": "Click submit button",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Wait for confirmation",
      "action": "wait_for",
      "selector": ".success-message",
      "timeout": 10
    }
  ]
}
```

### Data Extraction

#### Table Data Extraction

```json
{
  "name": "Table Data Extraction",
  "version": "1.0.0",
  "description": "Extract data from an HTML table",
  "variables": {
    "url": "https://example.com/data-table",
    "output_file": "table_data.json"
  },
  "steps": [
    {
      "name": "Navigate to page with table",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for table to load",
      "action": "wait_for",
      "selector": "#data-table",
      "timeout": 10
    },
    {
      "name": "Extract table headers",
      "action": "extract",
      "selector": "#data-table th",
      "value": {
        "header": "text"
      }
    },
    {
      "name": "Extract table rows",
      "action": "extract",
      "selector": "#data-table tbody tr",
      "value": {
        "cells": "td"
      }
    },
    {
      "name": "Process table data",
      "action": "execute_script",
      "value": "headers = extract_table_headers.map(h => h.header); rows = extract_table_rows.map(r => r.cells); table_data = rows.map(row => { obj = {}; headers.forEach((header, i) => { obj[header] = row[i] }); return obj; }); set_variable('processed_data', table_data);"
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}",
      "data": "{{processed_data}}"
    }
  ]
}
```

#### Product Information Extraction

```json
{
  "name": "Product Information Extraction",
  "version": "1.0.0",
  "description": "Extract product information from an e-commerce website",
  "variables": {
    "url": "https://example-store.com/products",
    "output_file": "products.json"
  },
  "steps": [
    {
      "name": "Navigate to product listing page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for products to load",
      "action": "wait_for",
      "selector": ".product",
      "timeout": 10
    },
    {
      "name": "Extract product information",
      "action": "extract",
      "selector": ".product",
      "value": {
        "name": ".product-name",
        "price": ".product-price",
        "url": {
          "attribute": "href",
          "selector": ".product-link"
        },
        "image": {
          "attribute": "src",
          "selector": ".product-image img"
        }
      }
    },
    {
      "name": "Save results to file",
      "action": "save",
      "value": "{{output_file}}"
    }
  ]
}
```

### Authentication Workflows

#### Form-Based Login

```json
{
  "name": "Form-Based Login",
  "version": "1.0.0",
  "description": "Log in to a website using a form-based login",
  "variables": {
    "login_url": "https://example.com/login",
    "username": "myuser",
    "password": "mypass"
  },
  "steps": [
    {
      "name": "Navigate to login page",
      "action": "navigate",
      "value": "{{login_url}}"
    },
    {
      "name": "Wait for login form to load",
      "action": "wait_for",
      "selector": "#login-form",
      "timeout": 10
    },
    {
      "name": "Enter username",
      "action": "type",
      "selector": "#username",
      "value": "{{username}}"
    },
    {
      "name": "Enter password",
      "action": "type",
      "selector": "#password",
      "value": "{{password}}"
    },
    {
      "name": "Submit login form",
      "action": "click",
      "selector": "#login-button"
    },
    {
      "name": "Wait for login to complete",
      "action": "wait_for",
      "selector": ".user-dashboard",
      "timeout": 10
    }
  ]
}
```

#### Session Management

```json
{
  "name": "Session Management",
  "version": "1.0.0",
  "description": "Save and restore a browser session",
  "variables": {
    "login_url": "https://example.com/login",
    "username": "myuser",
    "password": "mypass",
    "session_file": "session.json"
  },
  "steps": [
    {
      "name": "Navigate to login page",
      "action": "navigate",
      "value": "{{login_url}}"
    },
    {
      "name": "Wait for login form to load",
      "action": "wait_for",
      "selector": "#login-form",
      "timeout": 10
    },
    {
      "name": "Enter username",
      "action": "type",
      "selector": "#username",
      "value": "{{username}}"
    },
    {
      "name": "Enter password",
      "action": "type",
      "selector": "#password",
      "value": "{{password}}"
    },
    {
      "name": "Submit login form",
      "action": "click",
      "selector": "#login-button"
    },
    {
      "name": "Wait for login to complete",
      "action": "wait_for",
      "selector": ".user-dashboard",
      "timeout": 10
    },
    {
      "name": "Save session cookies",
      "action": "execute_script",
      "value": "cookies = document.cookie.split(';').reduce((cookies, cookie) => { const [name, value] = cookie.trim().split('='); cookies[name] = value; return cookies; }, {}); set_variable('session_cookies', cookies);"
    },
    {
      "name": "Save session to file",
      "action": "save",
      "value": "{{session_file}}",
      "data": "{{session_cookies}}"
    },
    {
      "name": "Log out",
      "action": "click",
      "selector": "#logout-button"
    },
    {
      "name": "Wait for logout to complete",
      "action": "wait_for",
      "selector": "#login-form",
      "timeout": 10
    },
    {
      "name": "Load session from file",
      "action": "load",
      "value": "{{session_file}}"
    },
    {
      "name": "Restore session cookies",
      "action": "execute_script",
      "value": "Object.keys(load_session).forEach(name => { document.cookie = `${name}=${load_session[name]}`; });"
    },
    {
      "name": "Refresh page",
      "action": "navigate",
      "value": "{{login_url}}"
    },
    {
      "name": "Wait for login to complete",
      "action": "wait_for",
      "selector": ".user-dashboard",
      "timeout": 10
    }
  ]
}
```

### Testing Scenarios

#### Form Validation Testing

```json
{
  "name": "Form Validation Testing",
  "version": "1.0.0",
  "description": "Test form validation by submitting invalid data",
  "variables": {
    "url": "https://example.com/contact",
    "test_results": []
  },
  "steps": [
    {
      "name": "Initialize test results",
      "action": "set_variable",
      "selector": "test_results",
      "value": []
    },
    {
      "name": "Navigate to form page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for form to load",
      "action": "wait_for",
      "selector": "#contact-form",
      "timeout": 10
    },
    {
      "name": "Test 1: Empty name field",
      "action": "execute_script",
      "value": "console.log('Running Test 1: Empty name field');"
    },
    {
      "name": "Clear name field",
      "action": "type",
      "selector": "#name",
      "value": ""
    },
    {
      "name": "Enter email",
      "action": "type",
      "selector": "#email",
      "value": "test@example.com"
    },
    {
      "name": "Enter message",
      "action": "type",
      "selector": "#message",
      "value": "This is a test message."
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Check for name error message",
      "action": "wait_for",
      "selector": "#name-error",
      "timeout": 5
    },
    {
      "name": "Get name error message",
      "action": "get_text",
      "selector": "#name-error"
    },
    {
      "name": "Add test result",
      "action": "execute_script",
      "value": "test_results.push({ test: 'Empty name field', expected: 'Name is required', actual: get_text_name_error, passed: get_text_name_error.includes('required') }); set_variable('test_results', test_results);"
    },
    {
      "name": "Test 2: Invalid email format",
      "action": "execute_script",
      "value": "console.log('Running Test 2: Invalid email format');"
    },
    {
      "name": "Enter name",
      "action": "type",
      "selector": "#name",
      "value": "John Doe"
    },
    {
      "name": "Enter invalid email",
      "action": "type",
      "selector": "#email",
      "value": "invalid-email"
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Check for email error message",
      "action": "wait_for",
      "selector": "#email-error",
      "timeout": 5
    },
    {
      "name": "Get email error message",
      "action": "get_text",
      "selector": "#email-error"
    },
    {
      "name": "Add test result",
      "action": "execute_script",
      "value": "test_results.push({ test: 'Invalid email format', expected: 'Valid email is required', actual: get_text_email_error, passed: get_text_email_error.includes('valid') }); set_variable('test_results', test_results);"
    },
    {
      "name": "Save test results",
      "action": "save",
      "value": "form_validation_test_results.json",
      "data": "{{test_results}}"
    }
  ]
}
```

#### Link Checking

```json
{
  "name": "Link Checking",
  "version": "1.0.0",
  "description": "Check for broken links on a web page",
  "variables": {
    "url": "https://example.com",
    "output_file": "link_check_results.json",
    "links": [],
    "results": []
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for page to load",
      "action": "wait_for",
      "selector": "body",
      "timeout": 10
    },
    {
      "name": "Extract all links",
      "action": "extract",
      "selector": "a[href]",
      "value": {
        "url": {
          "attribute": "href"
        },
        "text": "text"
      }
    },
    {
      "name": "Filter and process links",
      "action": "execute_script",
      "value": "links = extract_all_links.filter(link => link.url && !link.url.startsWith('#') && !link.url.startsWith('javascript:')).map(link => ({ url: new URL(link.url, window.location.href).href, text: link.text })); set_variable('processed_links', links);"
    },
    {
      "name": "Initialize results",
      "action": "set_variable",
      "selector": "results",
      "value": []
    },
    {
      "name": "Check each link",
      "action": "loop",
      "value": {
        "type": "for_each",
        "items": "{{processed_links}}",
        "variable": "link",
        "steps": [
          {
            "name": "Check link status",
            "action": "execute_script",
            "value": "fetch('{{link.url}}', { method: 'HEAD' }).then(response => { results.push({ url: '{{link.url}}', text: '{{link.text}}', status: response.status, ok: response.ok }); set_variable('results', results); }).catch(error => { results.push({ url: '{{link.url}}', text: '{{link.text}}', status: 'Error', ok: false, error: error.message }); set_variable('results', results); });"
          }
        ]
      }
    },
    {
      "name": "Wait for all link checks to complete",
      "action": "wait",
      "value": 5
    },
    {
      "name": "Save results",
      "action": "save",
      "value": "{{output_file}}",
      "data": "{{results}}"
    }
  ]
}
```

## Conclusion

This comprehensive guide has provided you with all the information needed to effectively use Playwright MCP and the Bridge extension with Automata CLI to automate workflows using existing tabs in your daily browser. By leveraging these powerful tools together, you can create sophisticated automation workflows that interact with websites where you're already logged in, using your existing cookies, sessions, and browser state.

Key takeaways:
1. The Bridge Extension allows you to connect to existing browser tabs and leverage your logged-in sessions
2. Playwright MCP provides fast, lightweight browser automation capabilities
3. Automata CLI offers a comprehensive set of tools for creating, managing, and executing workflows
4. Session management enables persistent login states across workflow executions
5. The combination of these tools provides a seamless automation experience

Remember to follow best practices for security, performance, and error handling when creating your automation workflows. Always test your workflows thoroughly before using them in production, and keep your sessions secure with encryption and appropriate expiry times.

With these tools and techniques, you can automate a wide range of web tasks, from simple form filling to complex data extraction and testing scenarios, all while leveraging your existing browser state and logged-in sessions.