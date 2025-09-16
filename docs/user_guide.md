# Web Automation Tool - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [MCP Server Integration](#mcp-server-integration)
   - [Overview](#overview)
   - [Setup](#setup)
   - [Configuration](#configuration)
   - [Usage](#usage)
5. [Workflows](#workflows)
   - [Creating Workflows](#creating-workflows)
   - [Executing Workflows](#executing-workflows)
   - [Validating Workflows](#validating-workflows)
   - [Editing Workflows](#editing-workflows)
6. [Templates](#templates)
   - [Creating Templates](#creating-templates)
   - [Using Templates](#using-templates)
   - [Managing Templates](#managing-templates)
7. [Session Management](#session-management)
   - [Saving Sessions](#saving-sessions)
   - [Restoring Sessions](#restoring-sessions)
   - [Listing Sessions](#listing-sessions)
   - [Deleting Sessions](#deleting-sessions)
   - [Session Encryption](#session-encryption)
8. [Helper Tools](#helper-tools)
   - [HTML Parsing](#html-parsing)
   - [Selector Generation](#selector-generation)
   - [Action Building](#action-building)
9. [Browser Exploration](#browser-exploration)
10. [Configuration](#configuration)
11. [Authentication](#authentication)
12. [Examples](#examples)
    - [Simple Login Workflow](#simple-login-workflow)
    - [Session Management Example](#session-management-example)
    - [MCP Server Example](#mcp-server-example)

## Introduction

The Web Automation Tool is a powerful CLI-based application for automating web interactions, including form filling, data extraction, and web scraping. It provides a comprehensive set of features for creating, managing, and executing web automation workflows. With the new MCP (Model Context Protocol) server integration, AI assistants can now interact with web pages through structured accessibility snapshots, providing a powerful bridge between AI capabilities and browser automation.

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Node.js 18 or newer (for MCP server)

### Install from Source

```bash
git clone https://github.com/yourusername/web-automation-tool.git
cd web-automation-tool
make setup
```

### Verify Installation

```bash
make check
```

## Getting Started

### Basic CLI Usage

The tool provides a command-line interface with various subcommands:

```bash
# Show help
python3.11 -m automata --help

# Show help for a specific command
python3.11 -m automata workflow --help
```

### Configuration

Initialize the configuration file:

```bash
python3.11 -m automata config init
```

This creates a configuration file at `~/.automata/config.json` with default settings.

## MCP Server Integration

### Overview

The MCP (Model Context Protocol) server integration enables AI assistants to interact with web pages through structured accessibility snapshots. This integration provides a powerful bridge between AI capabilities and browser automation, allowing AI assistants to perform web automation tasks with precision and reliability.

### Key Features

- **Fast and lightweight**: Uses Playwright's accessibility tree, not pixel-based input
- **LLM-friendly**: No vision models needed, operates purely on structured data
- **Deterministic tool application**: Avoids ambiguity common with screenshot-based approaches
- **WebSocket Compatible**: Fully compatible with the latest websockets library versions
- **Extension Support**: Connect to existing browser tabs with the Bridge extension

### Setup

#### 1. Install the Playwright MCP Server

Install the Playwright MCP server with your preferred MCP client:

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

#### 2. Extension Mode Setup (Optional)

To connect to existing browser tabs:

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

#### 3. Install the Bridge Extension (for Extension Mode)

1. Download the latest Chrome extension from: https://github.com/microsoft/playwright-mcp/releases
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked" and select the extension directory

### Configuration

#### Command Line Configuration

```bash
# Start MCP server with default settings
python3.11 -m automata mcp-server start

# Start MCP server with custom configuration
python3.11 -m automata mcp-server start --config path/to/config.json

# Start MCP server in extension mode
python3.11 -m automata mcp-server start --extension
```

#### Configuration File

Create a JSON configuration file for the MCP server:

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

#### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `server.host` | String | "localhost" | Host to bind the server to |
| `server.port` | Integer | 8080 | Port to listen on |
| `browser.browserName` | String | "chromium" | Browser to use (chromium, firefox, webkit) |
| `browser.headless` | Boolean | false | Run in headless mode |
| `browser.launchOptions` | Object | {} | Browser launch options |
| `browser.contextOptions` | Object | {} | Browser context options |
| `capabilities` | Array | [] | Additional capabilities to enable |
| `outputDir` | String | "./output" | Directory for output files |

### Usage

#### Starting the MCP Server

```bash
# Start with default configuration
python3.11 -m automata mcp-server start

# Start with custom configuration file
python3.11 -m automata mcp-server start --config my_config.json

# Start in extension mode
python3.11 -m automata mcp-server start --extension

# Start in headless mode
python3.11 -m automata mcp-server start --headless

# Start with custom port
python3.11 -m automata mcp-server start --port 9000
```

#### MCP Server Tools

The MCP server provides a comprehensive set of tools for browser automation:

1. **Core Automation Tools**
   - `browser_click`: Perform click on a web page
   - `browser_navigate`: Navigate to a URL
   - `browser_type`: Type text into editable element
   - `browser_snapshot`: Capture accessibility snapshot of the current page
   - `browser_wait_for`: Wait for text to appear or disappear or a specified time to pass

2. **Tab Management**
   - `browser_tabs`: List, create, close, or select a browser tab

3. **Form Interaction**
   - `browser_fill_form`: Fill multiple form fields
   - `browser_select_option`: Select an option in a dropdown
   - `browser_file_upload`: Upload one or multiple files

4. **Data Extraction**
   - `browser_extract`: Extract data from web pages
   - `browser_console_messages`: Returns all console messages
   - `browser_network_requests`: List network requests

5. **Verification Tools**
   - `browser_verify_element_visible`: Verify element is visible on the page
   - `browser_verify_text_visible`: Verify text is visible on the page
   - `browser_verify_value`: Verify element value

6. **Advanced Features**
   - `browser_pdf_save`: Save page as PDF
   - `browser_take_screenshot`: Take a screenshot of the current page
   - `browser_evaluate`: Evaluate JavaScript expression on page or element

#### Using MCP Server with AI Assistants

1. **Configure your AI assistant** to use the MCP server:
   - Add the server configuration to your AI assistant's MCP settings
   - Use the standard configuration provided in the Setup section

2. **Interact with web pages** through your AI assistant:
   - Your AI assistant can now use the MCP server tools to interact with web pages
   - The assistant will automatically take snapshots, understand the page structure, and perform actions

3. **Example interactions**:
   - "Navigate to https://example.com and fill out the login form"
   - "Extract all product information from this e-commerce page"
   - "Take a screenshot of the current page and save it as a PDF"

#### MCP Server and Workflows Integration

The MCP server can be integrated with Automata workflows:

```json
{
  "name": "Workflow with MCP Server",
  "version": "1.0.0",
  "steps": [
    {
      "name": "Start MCP server",
      "action": "execute_script",
      "value": "python3.11 -m automata mcp-server start --port 8080 &"
    },
    {
      "name": "Wait for server to start",
      "action": "wait",
      "value": 5
    },
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "https://example.com"
    },
    {
      "name": "Extract data using MCP",
      "action": "execute_script",
      "value": "fetch('http://localhost:8080/api/snapshot').then(response => response.json()).then(data => console.log(data));"
    },
    {
      "name": "Stop MCP server",
      "action": "execute_script",
      "value": "fetch('http://localhost:8080/api/stop').then(() => console.log('Server stopped'));"
    }
  ]
}
```

#### Troubleshooting MCP Server

1. **Server not starting**:
   - Check if the port is already in use
   - Verify the configuration file syntax
   - Ensure all dependencies are installed

2. **WebSocket connection issues**:
   - Verify the websockets library version (15.0.1 or higher)
   - Check firewall settings
   - Ensure the server is running and accessible

3. **Browser automation failures**:
   - Check if the browser is installed and accessible
   - Verify browser launch options
   - Ensure the page is fully loaded before interacting with elements

For detailed troubleshooting information, see the [MCP Bridge Setup and Troubleshooting Guide](mcp/bridge_setup_and_troubleshooting.md).

## Workflows

Workflows are JSON files that define a sequence of actions to be performed on web pages.

### Creating Workflows

Create a new workflow interactively:

```bash
python3.11 -m automata workflow create --output my_workflow.json
```

### Executing Workflows

Execute a workflow from a file:

```bash
python3.11 -m automata workflow execute my_workflow.json
```

#### Session Options

You can use saved sessions with workflows:

```bash
# Execute with a saved session
python3.11 -m automata workflow execute my_workflow.json --session my_session_id

# Save session after execution
python3.11 -m automata workflow execute my_workflow.json --save-session my_session_id
```

#### Browser Options

Control browser visibility:

```bash
# Run in headless mode (default)
python3.11 -m automata workflow execute my_workflow.json --headless

# Run in visible mode
python3.11 -m automata workflow execute my_workflow.json --visible
```

### Validating Workflows

Validate a workflow file:

```bash
python3.11 -m automata workflow validate my_workflow.json
```

### Editing Workflows

Edit a workflow interactively:

```bash
python3.11 -m automata workflow edit my_workflow.json
```

## Templates

Templates are reusable workflow definitions that can be customized with variables.

### Creating Templates

Create a template from a workflow:

```bash
python3.11 -m automata template create my_template my_workflow.json --description "My template"
```

### Using Templates

Create a workflow from a template:

```bash
python3.11 -m automata template use my_template my_workflow --variable name=value
```

### Managing Templates

List all templates:

```bash
python3.11 -m automata template list
```

Search for templates:

```bash
python3.11 -m automata template search "login" --tag authentication
```

Delete a template:

```bash
python3.11 -m automata template delete my_template
```

## Session Management

Session management allows you to save browser sessions (cookies, localStorage, sessionStorage) and restore them later, enabling persistent login states across workflow executions. This feature is particularly useful for maintaining authentication without repeatedly entering credentials.

### CLI Session Management Commands

The tool provides comprehensive CLI commands for session management that can be used independently or integrated with workflows.

#### Saving Sessions

Save a browser session with various options:

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

#### Restoring Sessions

Restore a saved browser session:

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

#### Listing Sessions

List all saved sessions with detailed information:

```bash
# List active sessions
python3.11 -m automata session list

# Include expired sessions
python3.11 -m automata session list --include-expired

# List encrypted sessions
python3.11 -m automata session list --encryption-key "my_secret_key"
```

#### Getting Session Information

Get detailed information about a session:

```bash
python3.11 -m automata session info my_session_id

# Get info for encrypted session
python3.11 -m automata session info my_session_id --encryption-key "my_secret_key"
```

#### Deleting Sessions

Delete a saved session:

```bash
python3.11 -m automata session delete my_session_id
```

#### Cleaning Up Expired Sessions

Delete all expired sessions:

```bash
python3.11 -m automata session cleanup

# Clean up encrypted sessions
python3.11 -m automata session cleanup --encryption-key "my_secret_key"
```

### Session Management in Workflows

Session management can be integrated directly into workflow execution using CLI options.

#### Using --save-session and --session Options

When executing workflows, you can save or restore sessions using command-line options:

```bash
# Execute a workflow and save the session
python3.11 -m automata workflow execute login_workflow.json --save-session login_session

# Execute a workflow using a saved session
python3.11 -m automata workflow execute dashboard_workflow.json --session login_session

# Execute a workflow, save session with encryption
python3.11 -m automata workflow execute login_workflow.json --save-session secure_login --encryption-key "my_secret_key"

# Execute a workflow using encrypted session
python3.11 -m automata workflow execute dashboard_workflow.json --session secure_login --encryption-key "my_secret_key"
```

### Session Management Examples

#### Example 1: Basic Login and Session Save

```bash
# Execute login workflow and save session
python3.11 -m automata workflow execute login_workflow.json --save-session my_login

# Use the saved session for subsequent workflows
python3.11 -m automata workflow execute dashboard_workflow.json --session my_login
```

#### Example 2: Session Management with Custom Expiry

```bash
# Save a session with 7-day expiry
python3.11 -m automata workflow execute login_workflow.json --save-session temp_login --expiry 7

# Use the session for data extraction
python3.11 -m automata workflow execute extract_data_workflow.json --session temp_login
```

#### Example 3: Encrypted Session Management

```bash
# Save an encrypted session for sensitive operations
python3.11 -m automata workflow execute banking_login.json --save-session banking_session --encryption-key "my_secure_key"

# Use the encrypted session for financial operations
python3.11 -m automata workflow execute transfer_funds.json --session banking_session --encryption-key "my_secure_key"
```

### Session Management Best Practices

1. **Use Descriptive Session IDs**: Choose meaningful names for your sessions to easily identify their purpose.

   ```bash
   # Good
   python3.11 -m automata workflow execute login.json --save-session admin_dashboard_login
   
   # Avoid
   python3.11 -m automata workflow execute login.json --save-session session1
   ```

2. **Set Appropriate Expiry Times**: Match session expiry to your security requirements.

   ```bash
   # Short-term sessions for testing
   python3.11 -m automata workflow execute login.json --save-session test_session --expiry 1
   
   # Long-term sessions for regular operations
   python3.11 -m automata workflow execute login.json --save-session regular_session --expiry 30
   ```

3. **Use Encryption for Sensitive Data**: Always encrypt sessions that contain sensitive information.

   ```bash
   python3.11 -m automata workflow execute login.json --save-session secure_session --encryption-key "your_secure_key"
   ```

4. **Regular Session Cleanup**: Periodically clean up expired sessions to free up storage space.

   ```bash
   python3.11 -m automata session cleanup
   ```

5. **Test Sessions Before Production**: Always test saved sessions in a non-production environment first.

   ```bash
   # Test session restoration
   python3.11 -m automata session restore test_session --visible
   ```

### localStorage-based vs CLI Session Management

The tool supports two types of session management:

#### localStorage-based Session Management
- Stored within the workflow JSON structure
- Managed through workflow actions
- Suitable for simple, short-term storage needs
- Example:
  ```json
  {
    "name": "localStorage Session Example",
    "steps": [
      {
        "name": "Save session data",
        "action": "execute_script",
        "value": "localStorage.setItem('session_data', JSON.stringify({user: 'test'}));"
      }
    ]
  }
  ```

#### CLI Session Management
- Stored as separate files in the session directory
- Managed through CLI commands and options
- Supports encryption, expiry, and metadata
- More secure and flexible for complex workflows
- Example:
  ```bash
  python3.11 -m automata workflow execute workflow.json --save-session my_session
  ```

### Session Expiry Handling

Sessions automatically expire after a specified period to enhance security:

#### Default Expiry
- Sessions expire after 30 days by default
- Custom expiry can be set when saving a session
- Expired sessions are automatically skipped during restoration

#### Managing Expiry
```bash
# Save with custom expiry (7 days)
python3.11 -m automata session save my_session --expiry 7

# Check session status
python3.11 -m automata session info my_session

# Clean up expired sessions
python3.11 -m automata session cleanup
```

### Error Handling for Session Operations

The tool provides comprehensive error handling for session operations:

#### Common Errors and Solutions

1. **Session Not Found**
   ```
   Error: Session file not found
   ```
   - Verify the session ID is correct
   - Check if the session has expired
   - Use `python3.11 -m automata session list` to view available sessions

2. **Encryption Key Mismatch**
   ```
   Error: Error decrypting session data
   ```
   - Verify the encryption key is correct
   - Ensure the same key was used for saving and restoring

3. **Session Expired**
   ```
   Error: Session has expired
   ```
   - Save a new session
   - Adjust expiry time when saving

4. **Permission Issues**
   ```
   Error: Permission denied
   ```
   - Check file permissions in the session directory
   - Ensure the session directory is writable

#### Debugging Session Issues

Enable verbose logging to troubleshoot session issues:

```bash
python3.11 -m automata --verbose session save my_session_id
python3.11 -m automata --verbose session restore my_session_id
```

### Session Encryption

For sensitive sessions, you can encrypt the session data:

```bash
# Save with encryption
python3.11 -m automata session save my_session_id --encryption-key "my_secret_key"

# Restore with encryption
python3.11 -m automata session restore my_session_id --encryption-key "my_secret_key"

# List encrypted sessions
python3.11 -m automata session list --encryption-key "my_secret_key"

# Get info for encrypted session
python3.11 -m automata session info my_session_id --encryption-key "my_secret_key"
```

The encryption key is used to encrypt and decrypt the session data. Without the correct key, the session cannot be restored. Keys are derived using SHA-256 hashing and encrypted using Fernet symmetric encryption.

### Session Storage Location

Sessions are stored in the following directory by default:
- `~/.automata/sessions/`

You can customize this location by setting the `AUTOMATA_SESSION_DIR` environment variable or by configuring it in the settings file.

### Session Actions in Workflow JSON Files

While CLI session management is handled through command-line options, you can also incorporate session-related actions directly within your workflow JSON files for more complex scenarios.

#### Where to Place Session Actions

Session actions should be strategically placed within your workflow steps to ensure proper timing and execution:

```json
{
  "name": "Workflow with Session Actions",
  "version": "1.0.0",
  "steps": [
    {
      "name": "Navigate to login page",
      "action": "navigate",
      "value": "https://example.com/login"
    },
    {
      "name": "Enter credentials",
      "action": "type",
      "selector": "#username",
      "value": "${username}"
    },
    {
      "name": "Enter password",
      "action": "type",
      "selector": "#password",
      "value": "${password}"
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
      "name": "Save session data to localStorage",
      "action": "execute_script",
      "value": "localStorage.setItem('session_data', JSON.stringify({loggedIn: true, timestamp: Date.now()}));"
    },
    {
      "name": "Perform authenticated actions",
      "action": "click",
      "selector": ".protected-content"
    },
    {
      "name": "Retrieve session data",
      "action": "execute_script",
      "value": "const sessionData = JSON.parse(localStorage.getItem('session_data') || '{}'); return sessionData;"
    }
  ]
}
```

#### Session Action Types

1. **Saving Session Data**
   ```json
   {
     "name": "Save session data",
     "action": "execute_script",
     "value": "localStorage.setItem('session_key', JSON.stringify(session_data));"
   }
   ```

2. **Retrieving Session Data**
   ```json
   {
     "name": "Get session data",
     "action": "execute_script",
     "value": "return JSON.parse(localStorage.getItem('session_key') || '{}');"
   }
   ```

3. **Clearing Session Data**
   ```json
   {
     "name": "Clear session data",
     "action": "execute_script",
     "value": "localStorage.removeItem('session_key');"
   }
   ```

#### Best Practices for Session Actions in Workflows

1. **Place session actions after authentication**:
   ```json
   {
     "name": "Save session after login",
     "action": "execute_script",
     "value": "localStorage.setItem('auth_token', document.querySelector('#token').value);"
   }
   ```

2. **Verify session data before use**:
   ```json
   {
     "name": "Check if session exists",
     "action": "execute_script",
     "value": "if (!localStorage.getItem('session_data')) { throw new Error('No session data found'); }"
   }
   ```

3. **Handle session expiry gracefully**:
   ```json
   {
     "name": "Check session expiry",
     "action": "execute_script",
     "value": "const session = JSON.parse(localStorage.getItem('session_data') || '{}'); if (session.expiry && Date.now() > session.expiry) { localStorage.removeItem('session_data'); throw new Error('Session expired'); }"
   }
   ```

4. **Use conditional logic based on session state**:
   ```json
   {
     "name": "Check login status",
     "action": "evaluate",
     "value": "localStorage.getItem('isLoggedIn') === 'true'"
   },
   {
     "name": "Handle based on login status",
     "action": "if",
     "value": {
       "operator": "equals",
       "left": "{{evaluate}}",
       "right": true
     },
     "steps": [
       {
         "name": "Access protected content",
         "action": "click",
         "selector": ".protected-content"
       }
     ],
     "else_steps": [
       {
         "name": "Redirect to login",
         "action": "navigate",
         "value": "/login"
       }
     ]
   }
   ```

#### Combining CLI Session Management with Workflow Session Actions

For maximum flexibility, you can combine CLI session management with workflow session actions:

```bash
# Execute workflow with CLI session management
python3.11 -m automata workflow execute complex_workflow.json --session my_session --save-session updated_session
```

```json
{
  "name": "Complex Workflow with Session Management",
  "version": "1.0.0",
  "steps": [
    {
      "name": "Check if CLI session is active",
      "action": "evaluate",
      "value": "document.cookie.includes('session_token')"
    },
    {
      "name": "Handle based on CLI session",
      "action": "if",
      "value": {
        "operator": "equals",
        "left": "{{evaluate}}",
        "right": true
      },
      "steps": [
        {
          "name": "Use existing session",
          "action": "execute_script",
          "value": "console.log('Using CLI-provided session');"
        }
      ],
      "else_steps": [
        {
          "name": "Perform login",
          "action": "navigate",
          "value": "/login"
        },
        {
          "name": "Save session to localStorage",
          "action": "execute_script",
          "value": "localStorage.setItem('workflow_session', JSON.stringify({loggedIn: true}));"
        }
      ]
    }
  ]
}
```

This approach allows you to leverage the security and encryption features of CLI session management while maintaining the flexibility of workflow-based session actions for complex scenarios.

## Helper Tools

### HTML Parsing

Parse an HTML file to extract element information:

```bash
python3.11 -m automata helper parse-html page.html
```

### Selector Generation

Generate selectors from HTML:

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

### Action Building

Build an action interactively:

```bash
python3.11 -m automata helper build-action
```

## Browser Exploration

Start an interactive browser exploration session:

```bash
# Run in visible mode (default)
python3.11 -m automata browser explore

# Run in headless mode
python3.11 -m automata browser explore --headless
```

## Configuration

### Show Configuration

Display the current configuration:

```bash
python3.11 -m automata config show
```

### Initialize Configuration

Create a new configuration file:

```bash
python3.11 -m automata config init
```

## Authentication

### Using Credentials

Execute a workflow with credentials:

```bash
python3.11 -m automata workflow execute my_workflow.json --credentials credentials.json
```

The credentials file should be in JSON format with the required authentication information.

### Session Authentication

Use saved sessions for authentication:

```bash
# Save a session after login
python3.11 -m automata workflow execute login_workflow.json --save-session login_session

# Use the saved session for subsequent workflows
python3.11 -m automata workflow execute dashboard_workflow.json --session login_session
```

## Examples

### Simple Login Workflow

1. Create a login workflow:

```bash
python3.11 -m automata workflow create --output login_workflow.json
```

2. Execute the workflow and save the session:

```bash
python3.11 -m automata workflow execute login_workflow.json --save-session login_session
```

3. Use the saved session for other workflows:

```bash
python3.11 -m automata workflow execute dashboard_workflow.json --session login_session
```

### Session Management Example

1. Save a session with encryption:

```bash
python3.11 -m automata session save secure_session --encryption-key "my_secret_key" --url https://example.com/dashboard
```

2. List sessions:

```bash
python3.11 -m automata session list --encryption-key "my_secret_key"
```

3. Get session information:

```bash
python3.11 -m automata session info secure_session --encryption-key "my_secret_key"
```

4. Restore the session:

```bash
python3.11 -m automata session restore secure_session --encryption-key "my_secret_key"
```

5. Clean up expired sessions:

```bash
python3.11 -m automata session cleanup --encryption-key "my_secret_key"
```

### MCP Server Example

1. Start the MCP server:

```bash
python3.11 -m automata mcp-server start --config mcp_config.json
```

2. Create a workflow that uses the MCP server:

```json
{
  "name": "MCP Server Example",
  "version": "1.0.0",
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "https://example.com"
    },
    {
      "name": "Take snapshot using MCP",
      "action": "execute_script",
      "value": "fetch('http://localhost:8080/api/snapshot').then(response => response.json()).then(data => setVariable('page_snapshot', data));"
    },
    {
      "name": "Extract data from snapshot",
      "action": "execute_script",
      "value": "const elements = page_snapshot.elements; const data = elements.map(el => ({ text: el.text, selector: el.selector })); setVariable('extracted_data', data);"
    },
    {
      "name": "Save extracted data",
      "action": "save",
      "value": "extracted_data.json",
      "data": "{{extracted_data}}"
    }
  ]
}
```

3. Execute the workflow:

```bash
python3.11 -m automata workflow execute mcp_example.json
```

## Troubleshooting

### Common Issues

1. **Session not loading**: Ensure you're using the correct session ID and encryption key (if applicable).

2. **Browser not starting**: Check if the browser is installed and accessible in your system PATH.

3. **Workflow execution fails**: Validate the workflow file using the `workflow validate` command.

4. **Selectors not working**: Use the `helper generate-selectors` tool to verify selectors for your target elements.

5. **WebSocket compatibility errors**: If you encounter errors related to WebSocket handler parameters, see the [WebSocket Library Compatibility Guide](docs/websocket_compatibility_guide.md) for detailed information and solutions.

6. **MCP Server connection issues**: Ensure the server is running and accessible, check firewall settings, and verify the configuration.

### WebSocket Compatibility Requirements

This project includes a comprehensive fix for WebSocket handler parameter compatibility issues with the websockets library version 15.0.1 and higher.

#### Understanding the Issue

The MCP server implementation was affected by a breaking change in the websockets library that changed the handler signature from `handler(websocket, path)` to `handler(websocket)`. This caused a `TypeError` when trying to establish WebSocket connections.

#### Error Symptoms

If you encounter any of the following errors, it may be related to WebSocket compatibility issues:

```
TypeError: websocket_handler() takes 2 positional arguments but 3 were given
TypeError: MCPServer.handle_websocket() missing 1 required positional argument: 'path'
ERROR:websockets.server:connection handler failed
```

#### Solutions

The project has been updated to handle these compatibility issues automatically. However, if you need to manually address the issue:

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

To verify that the WebSocket fix is working correctly:

1. **Start the MCP server**:
   ```bash
   python3.11 scripts/start_mcp_server.py
   ```

2. **Run the test script**:
   ```bash
   python3.11 scripts/test_websocket_fix.py
   ```

3. **Check for successful connection establishment** and message handling.

#### Additional Resources

For more detailed information about the WebSocket compatibility issue and its resolution, see:

- [WebSocket Issue Resolution](../playwright_mcp_websocket_issue_resolution.md)
- [WebSocket Compatibility Guide](docs/websocket_compatibility_guide.md)
- [WebSocket Fix Summary](../websocket_fix_summary.md)

### Debug Mode

Enable verbose logging to troubleshoot issues:

```bash
python3.11 -m automata --verbose workflow execute my_workflow.json
```

### MCP Server Debugging

To troubleshoot MCP server issues:

1. **Enable verbose logging**:
   ```bash
   python3.11 -m automata mcp-server start --verbose
   ```

2. **Check server status**:
   ```bash
   curl http://localhost:8080/health
   ```

3. **Test WebSocket connection**:
   ```bash
   python3.11 scripts/test_websocket_fix.py
   ```

4. **Check browser compatibility**:
   - Ensure the browser is supported (Chrome, Firefox, WebKit)
   - Verify the browser is installed and accessible

## Advanced Usage

### Custom Session Directory

You can specify a custom directory for storing sessions by setting the `session_dir` parameter in the configuration file or by using the `AUTOMATA_SESSION_DIR` environment variable.

### Session Expiry

Sessions automatically expire after a default period (30 days). You can customize this when saving a session:

```bash
python3.11 -m automata session save my_session_id --expiry 7  # Expires in 7 days
```

### Session Metadata

Sessions include metadata such as creation time, expiry date, and version information. You can view this metadata using the `session info` command.

### MCP Server Advanced Configuration

The MCP server supports advanced configuration options:

1. **Browser Selection**:
   ```json
   {
     "browser": {
       "browserName": "firefox"
     }
   }
   ```

2. **Custom Capabilities**:
   ```json
   {
     "capabilities": ["tabs", "pdf", "vision"]
   }
   ```

3. **Network Configuration**:
   ```json
   {
     "network": {
       "allowedOrigins": ["https://example.com"],
       "blockedOrigins": ["https://ads.example.com"]
     }
   }
   ```

4. **Security Settings**:
   ```json
   {
     "security": {
       "ignoreHTTPSErrors": true,
       "blockServiceWorkers": true
     }
   }
   ```

For detailed information about MCP server configuration, see [docs/Playwright_MCP.md](Playwright_MCP.md) and [docs/Playwright_MCP_Bridge_Extension_Guide.md](Playwright_MCP_Bridge_Extension_Guide.md).
