# Web Automation Tool - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Workflows](#workflows)
   - [Creating Workflows](#creating-workflows)
   - [Executing Workflows](#executing-workflows)
   - [Validating Workflows](#validating-workflows)
   - [Editing Workflows](#editing-workflows)
5. [Templates](#templates)
   - [Creating Templates](#creating-templates)
   - [Using Templates](#using-templates)
   - [Managing Templates](#managing-templates)
6. [Session Management](#session-management)
   - [Saving Sessions](#saving-sessions)
   - [Restoring Sessions](#restoring-sessions)
   - [Listing Sessions](#listing-sessions)
   - [Deleting Sessions](#deleting-sessions)
   - [Session Encryption](#session-encryption)
7. [Helper Tools](#helper-tools)
   - [HTML Parsing](#html-parsing)
   - [Selector Generation](#selector-generation)
   - [Action Building](#action-building)
8. [Browser Exploration](#browser-exploration)
9. [Configuration](#configuration)
10. [Authentication](#authentication)
11. [Examples](#examples)
    - [Simple Login Workflow](#simple-login-workflow)
    - [Session Management Example](#session-management-example)

## Introduction

The Web Automation Tool is a powerful CLI-based application for automating web interactions, including form filling, data extraction, and web scraping. It provides a comprehensive set of features for creating, managing, and executing web automation workflows.

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

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

## Troubleshooting

### Common Issues

1. **Session not loading**: Ensure you're using the correct session ID and encryption key (if applicable).

2. **Browser not starting**: Check if the browser is installed and accessible in your system PATH.

3. **Workflow execution fails**: Validate the workflow file using the `workflow validate` command.

4. **Selectors not working**: Use the `helper generate-selectors` tool to verify selectors for your target elements.

### Debug Mode

Enable verbose logging to troubleshoot issues:

```bash
python3.11 -m automata --verbose workflow execute my_workflow.json
```

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