# Automata User Guide

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [CLI Commands](#cli-commands)
  - [Workflow Commands](#workflow-commands)
  - [Template Commands](#template-commands)
  - [Helper Commands](#helper-commands)
  - [Configuration Commands](#configuration-commands)
- [Workflow Definition](#workflow-definition)
  - [Workflow Structure](#workflow-structure)
  - [Step Actions](#step-actions)
  - [Variables and Conditions](#variables-and-conditions)
- [Credential Management](#credential-management)
- [Examples](#examples)
  - [Simple Web Scraping](#simple-web-scraping)
  - [Form Submission](#form-submission)
  - [Data Extraction](#data-extraction)
- [Troubleshooting](#troubleshooting)
- [Advanced Features](#advanced-features)

## Introduction

Automata is a powerful web automation tool that allows you to create, manage, and execute automation workflows using a simple JSON-based configuration. With Automata, you can automate repetitive web tasks, extract data from websites, fill out forms, and much more.

This guide will walk you through the installation process, explain the CLI commands, show you how to define workflows, and provide examples to help you get started quickly.

## Installation

### Prerequisites

Before installing Automata, make sure you have the following prerequisites:

- Python 3.11 or higher
- pip (Python package installer)

### Install from PyPI

You can install Automata directly from PyPI using pip:

```bash
pip install automata
```

### Install from Source

If you prefer to install from source, you can clone the repository and install it:

```bash
git clone https://github.com/olereon/0_GLM-RooCode/automata.git
cd automata
pip install -e .
```

### Verify Installation

To verify that Automata has been installed correctly, run:

```bash
automata --help
```

You should see the help message for the Automata CLI.

## Getting Started

Once you have Automata installed, you can start creating and executing workflows. Here's a quick overview of the basic workflow:

1. Create a workflow definition in JSON format
2. Execute the workflow using the Automata CLI
3. View the results of the execution

Let's create a simple workflow that navigates to a website and takes a screenshot:

```json
{
  "name": "Screenshot Example",
  "version": "1.0.0",
  "description": "Navigate to a website and take a screenshot",
  "variables": {
    "url": "https://example.com"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Take screenshot",
      "action": "screenshot",
      "value": "screenshot.png"
    }
  ]
}
```

Save this workflow to a file named `screenshot_workflow.json`, then execute it:

```bash
automata workflow execute screenshot_workflow.json
```

This will navigate to `https://example.com` and save a screenshot as `screenshot.png` in the current directory.

## CLI Commands

Automata provides a set of CLI commands to help you create, manage, and execute workflows. The main command groups are:

- `workflow`: Commands for managing workflows
- `template`: Commands for managing workflow templates
- `helper`: Commands for helper tools
- `config`: Commands for managing configuration

### Workflow Commands

#### Create a Workflow

You can create a new workflow interactively using the `workflow create` command:

```bash
automata workflow create
```

This will prompt you for the workflow name, description, and steps, and then save the workflow to a JSON file.

You can also specify an output file path:

```bash
automata workflow create --output my_workflow.json
```

#### Execute a Workflow

To execute a workflow, use the `workflow execute` command:

```bash
automata workflow execute my_workflow.json
```

This will execute the workflow and display the results.

#### Execute a Workflow with Credentials

To execute a workflow with credentials from a JSON file, use the `--credentials` parameter:

```bash
automata workflow execute my_workflow.json --credentials path/to/credentials.json
```

This will load the credentials from the specified JSON file and make them available to your workflow. For more information on the credentials JSON format, see the [Credential Management](#credential-management) section.

#### Validate a Workflow

Before executing a workflow, you can validate it using the `workflow validate` command:

```bash
automata workflow validate my_workflow.json
```

This will check if the workflow is valid and display any errors or warnings.

You can use the `--strict` flag to enable strict validation:

```bash
automata workflow validate my_workflow.json --strict
```

#### Edit a Workflow

You can edit a workflow interactively using the `workflow edit` command:

```bash
automata workflow edit my_workflow.json
```

This will prompt you for the workflow name and description, and allow you to edit them.

### Template Commands

Templates are reusable workflow definitions that can be customized with variables. You can create, use, list, search, and delete templates.

#### Create a Template

To create a template from an existing workflow, use the `template create` command:

```bash
automata template create my_template my_workflow.json --description "My template"
```

You can also add tags to the template:

```bash
automata template create my_template my_workflow.json --description "My template" --tag web --tag scraping
```

#### Use a Template

To create a workflow from a template, use the `template use` command:

```bash
automata template use my_template my_workflow --variable url=https://example.com
```

You can also specify an output file path:

```bash
automata template use my_template my_workflow --variable url=https://example.com --output my_workflow.json
```

#### List Templates

To list all available templates, use the `template list` command:

```bash
automata template list
```

#### Search Templates

To search for templates, use the `template search` command:

```bash
automata template search web scraping
```

You can also filter by tags:

```bash
automata template search --tag web --tag scraping
```

#### Delete a Template

To delete a template, use the `template delete` command:

```bash
automata template delete my_template
```

### Helper Commands

Helper commands provide tools to help you create and debug workflows.

#### Parse HTML

To parse an HTML file and extract element information, use the `helper parse-html` command:

```bash
automata helper parse-html page.html
```

#### Generate Selectors

To generate selectors from an HTML file, use the `helper generate-selectors` command:

```bash
automata helper generate-selectors page.html --output selectors.json
```

**NEW:** The generate-selectors tool now supports HTML fragments directly, with multiple input methods and targeting modes:

```bash
# Using direct HTML fragment
automata helper generate-selectors --html-fragment "<div class='container'><button id='submit'>Submit</button></div>"

# Using a fragment file
automata helper generate-selectors --fragment-file path/to/fragment.html

# Using stdin (piping)
echo "<div class='container'><button id='submit'>Submit</button></div>" | automata helper generate-selectors --stdin

# Generate selectors with specific targeting mode
automata helper generate-selectors --html-fragment "<div><button>Click</button></div>" --targeting-mode selector --custom-selector "button"

# Generate XPath selectors instead of CSS
automata helper generate-selectors --html-fragment "<div><button>Click</button></div>" --selector-type xpath
```

The tool supports three targeting modes:
- "all" (default): Generate selectors for all elements
- "selector": Generate selectors for elements matching a specific selector
- "auto": Automatically detect important elements

#### Build Action

To build an action interactively, use the `helper build-action` command:

```bash
automata helper build-action
```

This will prompt you for the action type, selector, value, and other parameters, and then display the resulting action definition.

### Configuration Commands

Configuration commands allow you to manage the Automata configuration.

#### Show Configuration

To show the current configuration, use the `config show` command:

```bash
automata config show
```

#### Initialize Configuration

To initialize the configuration file, use the `config init` command:

```bash
automata config init
```

This will create a default configuration file at `~/.automata/config.json`.

## Workflow Definition

Workflows are defined in JSON format and consist of a name, version, description, variables, and steps.

### Workflow Structure

Here's the basic structure of a workflow:

```json
{
  "name": "Workflow Name",
  "version": "1.0.0",
  "description": "Workflow description",
  "variables": {
    "variable_name": "variable_value"
  },
  "steps": [
    {
      "name": "Step Name",
      "action": "action_type",
      "selector": "css_selector",
      "value": "action_value"
    }
  ]
}
```

#### Required Fields

- `name`: The name of the workflow
- `version`: The version of the workflow
- `steps`: An array of steps to execute

#### Optional Fields

- `description`: A description of the workflow
- `variables`: A dictionary of variables that can be used in the workflow

### Step Actions

Each step in a workflow has an `action` field that specifies what action to perform. Here are the available actions:

#### navigate

Navigate to a URL.

```json
{
  "name": "Navigate to page",
  "action": "navigate",
  "value": "https://example.com"
}
```

#### click

Click on an element.

```json
{
  "name": "Click button",
  "action": "click",
  "selector": "#button"
}
```

#### type

Type text into an input field.

```json
{
  "name": "Enter search term",
  "action": "type",
  "selector": "#search",
  "value": "search term"
}
```

#### hover

Hover over an element.

```json
{
  "name": "Hover over menu",
  "action": "hover",
  "selector": "#menu"
}
```

#### wait_for

Wait for an element to be visible.

```json
{
  "name": "Wait for results",
  "action": "wait_for",
  "selector": ".results",
  "timeout": 10
}
```

#### wait

Wait for a specified amount of time.

```json
{
  "name": "Wait for page to load",
  "action": "wait",
  "value": 3
}
```

#### get_text

Get the text content of an element.

```json
{
  "name": "Get title",
  "action": "get_text",
  "selector": "h1"
}
```

#### get_attribute

Get the value of an attribute of an element.

```json
{
  "name": "Get link URL",
  "action": "get_attribute",
  "selector": "#link",
  "value": "href"
}
```

#### screenshot

Take a screenshot of the current page.

```json
{
  "name": "Take screenshot",
  "action": "screenshot",
  "value": "screenshot.png"
}
```

#### execute_script

Execute JavaScript code.

```json
{
  "name": "Execute script",
  "action": "execute_script",
  "value": "document.title = 'New Title';"
}
```

#### evaluate

Evaluate a JavaScript expression and return the result.

```json
{
  "name": "Get page title",
  "action": "evaluate",
  "value": "document.title"
}
```

#### extract

Extract data from elements matching a selector.

```json
{
  "name": "Extract results",
  "action": "extract",
  "selector": ".result-item",
  "value": {
    "title": ".title",
    "description": ".description"
  }
}
```

#### save

Save data to a file.

```json
{
  "name": "Save results",
  "action": "save",
  "value": "results.json"
}
```

#### load

Load data from a file.

```json
{
  "name": "Load data",
  "action": "load",
  "value": "data.json"
}
```

#### set_variable

Set a variable.

```json
{
  "name": "Set variable",
  "action": "set_variable",
  "selector": "variable_name",
  "value": "variable_value"
}
```

#### if

Execute a step conditionally.

```json
{
  "name": "Check condition",
  "action": "if",
  "value": {
    "operator": "equals",
    "left": "{{variable_name}}",
    "right": "expected_value"
  }
}
```

#### loop

Execute a step in a loop.

```json
{
  "name": "Loop through items",
  "action": "loop",
  "value": {
    "type": "for_each",
    "items": ["item1", "item2", "item3"],
    "variable": "item",
    "steps": [
      {
        "name": "Process item",
        "action": "type",
        "selector": "#input",
        "value": "{{item}}"
      }
    ]
  }
}
```

#### goto

Jump to a specific step by name.

```json
{
  "name": "Go to step",
  "action": "goto",
  "value": "Step Name"
}
```

#### stop

Stop the workflow execution.

```json
{
  "name": "Stop workflow",
  "action": "stop"
}
```

#### pause

Pause the workflow execution.

```json
{
  "name": "Pause workflow",
  "action": "pause"
}
```

#### resume

Resume the workflow execution.

```json
{
  "name": "Resume workflow",
  "action": "resume"
}
```

### Variables and Conditions

#### Variables

Variables are defined in the `variables` section of a workflow and can be used in step values using the `{{variable_name}}` syntax.

```json
{
  "name": "Variable Example",
  "version": "1.0.0",
  "variables": {
    "url": "https://example.com",
    "search_term": "test"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Enter search term",
      "action": "type",
      "selector": "#search",
      "value": "{{search_term}}"
    }
  ]
}
```

#### Conditions

Conditions are used in `if` actions and step conditions to control the flow of the workflow.

```json
{
  "name": "Condition Example",
  "version": "1.0.0",
  "variables": {
    "should_click": true
  },
  "steps": [
    {
      "name": "Check if should click",
      "action": "if",
      "value": {
        "operator": "equals",
        "left": "{{should_click}}",
        "right": true
      }
    },
    {
      "name": "Click button",
      "action": "click",
      "selector": "#button",
      "condition": {
        "operator": "equals",
        "left": "{{should_click}}",
        "right": true
      }
    }
  ]
}
```

## Credential Management

Automata provides a secure way to manage and use credentials in your workflows. This feature allows you to store authentication information in JSON files and use them in your workflows without hardcoding sensitive data.

### Credentials JSON Format

The credentials JSON file should follow this format:

```json
{
  "config": {
    "auth_type": "credentials_json"
  },
  "credentials": {
    "username": "your_username",
    "password": "your_password",
    "api_key": "your_api_key",
    "custom_field": "custom_value"
  }
}
```

#### Required Fields

- `config`: Configuration section
  - `auth_type`: Must be set to "credentials_json"
- `credentials`: Credentials section containing your authentication data

#### Optional Fields

The `credentials` section can contain any number of key-value pairs depending on what your workflow requires. Common fields include:

- `username`: Username for authentication
- `password`: Password for authentication
- `api_key`: API key for API access
- `token`: Authentication token
- Any custom fields required by your workflow

### Using Credentials in Workflows

Once loaded, credentials can be accessed in your workflows using variable substitution:

```json
{
  "name": "Login Workflow",
  "version": "1.0.0",
  "steps": [
    {
      "name": "Navigate to login page",
      "action": "navigate",
      "value": "https://example.com/login"
    },
    {
      "name": "Enter username",
      "action": "type",
      "selector": "#username",
      "value": "{{credentials.username}}"
    },
    {
      "name": "Enter password",
      "action": "type",
      "selector": "#password",
      "value": "{{credentials.password}}"
    },
    {
      "name": "Click login button",
      "action": "click",
      "selector": "#login-button"
    }
  ]
}
```

### Security Considerations

- **File Permissions**: Ensure your credentials files have appropriate file permissions to prevent unauthorized access.
- **Environment Variables**: For sensitive credentials, consider using environment variables instead of storing them in files.
- **Encryption**: For additional security, you can encrypt your credentials files and decrypt them at runtime.
- **Git Ignore**: Add credentials files to your `.gitignore` to prevent accidentally committing them to version control.

### Examples

#### Basic Authentication

```json
{
  "config": {
    "auth_type": "credentials_json"
  },
  "credentials": {
    "username": "john.doe",
    "password": "securepassword123"
  }
}
```

#### API Authentication

```json
{
  "config": {
    "auth_type": "credentials_json"
  },
  "credentials": {
    "api_key": "abcdef123456",
    "api_secret": "secretkey789",
    "environment": "production"
  }
}
```

#### Multi-Service Authentication

```json
{
  "config": {
    "auth_type": "credentials_json"
  },
  "credentials": {
    "database": {
      "host": "db.example.com",
      "username": "dbuser",
      "password": "dbpass"
    },
    "api": {
      "key": "api_key_123",
      "secret": "api_secret_456"
    },
    "email": {
      "smtp_server": "smtp.example.com",
      "username": "email@example.com",
      "password": "emailpass"
    }
  }
}
```

### Error Handling

The credential handling feature includes comprehensive error handling:

- **File Not Found**: If the specified credentials file doesn't exist, the workflow will fail with a clear error message.
- **Invalid JSON**: If the credentials file contains invalid JSON, the workflow will fail with a parsing error.
- **Missing Required Fields**: If required fields are missing from the credentials file, the workflow will fail with a validation error.
- **Invalid Configuration**: If the configuration section is invalid or missing, the workflow will fail with a configuration error.

### Best Practices

1. **Use Separate Credentials Files**: Use different credentials files for different environments (development, staging, production).
2. **Template Variables**: Combine credentials with template variables for flexible workflow configuration.
3. **Validation**: Always validate that credentials are loaded correctly before using them in your workflow.
4. **Error Handling**: Implement proper error handling in your workflows to gracefully handle authentication failures.
5. **Security**: Never commit credentials files to version control. Use environment variables or secret management tools for sensitive data.

## Examples

### Simple Web Scraping

This example navigates to a website, waits for the content to load, and extracts the titles of all articles.

```json
{
  "name": "Article Titles Scraper",
  "version": "1.0.0",
  "description": "Extract article titles from a news website",
  "variables": {
    "url": "https://example-news.com"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Wait for articles",
      "action": "wait_for",
      "selector": ".article",
      "timeout": 10
    },
    {
      "name": "Extract article titles",
      "action": "extract",
      "selector": ".article",
      "value": {
        "title": ".title"
      }
    },
    {
      "name": "Save results",
      "action": "save",
      "value": "article_titles.json"
    }
  ]
}
```

### Form Submission

This example fills out a search form and submits it.

```json
{
  "name": "Form Submission",
  "version": "1.0.0",
  "description": "Fill out and submit a search form",
  "variables": {
    "url": "https://example-search.com",
    "search_term": "web automation"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Enter search term",
      "action": "type",
      "selector": "#search-input",
      "value": "{{search_term}}"
    },
    {
      "name": "Submit form",
      "action": "click",
      "selector": "#search-button"
    },
    {
      "name": "Wait for results",
      "action": "wait_for",
      "selector": ".search-results",
      "timeout": 10
    },
    {
      "name": "Take screenshot",
      "action": "screenshot",
      "value": "search_results.png"
    }
  ]
}
```

### Data Extraction

This example logs into a website, navigates to a dashboard, and extracts data from a table.

```json
{
  "name": "Data Extraction",
  "version": "1.0.0",
  "description": "Log in and extract data from a dashboard",
  "variables": {
    "login_url": "https://example.com/login",
    "dashboard_url": "https://example.com/dashboard",
    "username": "user@example.com",
    "password": "password123"
  },
  "steps": [
    {
      "name": "Navigate to login page",
      "action": "navigate",
      "value": "{{login_url}}"
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
      "name": "Click login button",
      "action": "click",
      "selector": "#login-button"
    },
    {
      "name": "Wait for dashboard",
      "action": "wait_for",
      "selector": ".dashboard",
      "timeout": 10
    },
    {
      "name": "Navigate to data page",
      "action": "navigate",
      "value": "{{dashboard_url}}/data"
    },
    {
      "name": "Wait for table",
      "action": "wait_for",
      "selector": ".data-table",
      "timeout": 10
    },
    {
      "name": "Extract table data",
      "action": "extract",
      "selector": ".data-table tr",
      "value": {
        "name": "td:nth-child(1)",
        "value": "td:nth-child(2)",
        "date": "td:nth-child(3)"
      }
    },
    {
      "name": "Save results",
      "action": "save",
      "value": "table_data.json"
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### Workflow Execution Fails

If your workflow execution fails, check the following:

1. Validate your workflow using `automata workflow validate my_workflow.json`
2. Check if all selectors in your workflow are correct
3. Make sure the website structure hasn't changed
4. Check if there are any network issues

#### Elements Not Found

If elements are not found during execution, try the following:

1. Increase the timeout for `wait_for` actions
2. Add explicit `wait` actions before interacting with elements
3. Use more robust selectors (e.g., CSS selectors instead of XPath)
4. Check if the elements are inside iframes (you'll need to switch to the iframe first)

#### Authentication Issues

If you're having trouble with authentication, try the following:

1. Make sure you're using the correct login credentials
2. Check if there are any CAPTCHAs or two-factor authentication
3. Try adding explicit waits after login actions
4. Check if the website uses JavaScript to handle login

### Debugging Tips

1. Use the `--verbose` flag to get detailed logs:
   ```bash
   automata --verbose workflow execute my_workflow.json
   ```

2. Add screenshot actions at key points to see what's happening:
   ```json
   {
     "name": "Debug screenshot",
     "action": "screenshot",
     "value": "debug.png"
   }
   ```

3. Use the `get_text` action to verify that you're on the right page:
   ```json
   {
     "name": "Get page title",
     "action": "get_text",
     "selector": "h1"
   }
   ```

4. Break down complex workflows into smaller parts and test each part separately.

## Advanced Features

### Error Handling

You can specify how to handle errors for each step using the `on_error` field:

```json
{
  "name": "Click button",
  "action": "click",
  "selector": "#button",
  "on_error": "continue"
}
```

The possible values for `on_error` are:

- `stop`: Stop the workflow execution (default)
- `continue`: Continue to the next step
- `retry`: Retry the step (you can specify retry parameters)

#### Retry Configuration

If you set `on_error` to `retry`, you can specify retry parameters using the `retry` field:

```json
{
  "name": "Click button",
  "action": "click",
  "selector": "#button",
  "on_error": "retry",
  "retry": {
    "max_attempts": 3,
    "delay": 2
  }
}
```

### Step Conditions

You can add conditions to steps to control whether they should be executed:

```json
{
  "name": "Click button",
  "action": "click",
  "selector": "#button",
  "condition": {
    "operator": "equals",
    "left": "{{should_click}}",
    "right": true
  }
}
```

### Loops

You can use loops to repeat actions:

#### For Each Loop

```json
{
  "name": "Process items",
  "action": "loop",
  "value": {
    "type": "for_each",
    "items": ["item1", "item2", "item3"],
    "variable": "item",
    "steps": [
      {
        "name": "Process item",
        "action": "type",
        "selector": "#input",
        "value": "{{item}}"
      }
    ]
  }
}
```

#### For Loop

```json
{
  "name": "Count to 5",
  "action": "loop",
  "value": {
    "type": "for",
    "start": 1,
    "end": 5,
    "variable": "i",
    "steps": [
      {
        "name": "Print number",
        "action": "execute_script",
        "value": "console.log({{i}});"
      }
    ]
  }
}
```

#### While Loop

```json
{
  "name": "While condition is true",
  "action": "loop",
  "value": {
    "type": "while",
    "condition": {
      "operator": "less_than",
      "left": "{{counter}}",
      "right": 5
    },
    "steps": [
      {
        "name": "Increment counter",
        "action": "set_variable",
        "selector": "counter",
        "value": "{{counter + 1}}"
      }
    ]
  }
}
```

### Custom Selectors

If the default CSS selectors don't work for your use case, you can use XPath selectors:

```json
{
  "name": "Click element",
  "action": "click",
  "selector": "xpath=//div[@class='button']"

}
```
When using the generate-selectors tool to create XPath selectors, they will automatically be generated with the "xpath=" prefix, making them ready for direct use in your workflows without requiring manual conversion.

For example, a generated XPath selector might look like: `"xpath": "xpath=//div[@class='button']"`

### JavaScript Execution

You can execute custom JavaScript code using the `execute_script` action:

```json
{
  "name": "Execute custom script",
  "action": "execute_script",
  "value": "document.querySelector('#button').click();"
}
```

You can also evaluate JavaScript expressions and use the result:

```json
{
  "name": "Get page title",
  "action": "evaluate",
  "value": "document.title"
}
```

### File Operations

You can save data to files and load data from files:

#### Save Data

```json
{
  "name": "Save results",
  "action": "save",
  "value": "results.json",
  "data": "{{results}}"
}
```

#### Load Data

```json
{
  "name": "Load data",
  "action": "load",
  "value": "data.json"
}
```

### Session Management

Automata automatically manages browser sessions, but you can also save and restore sessions manually:

#### Save Session

```json
{
  "name": "Save session",
  "action": "execute_script",
  "value": "localStorage.setItem('session_data', JSON.stringify({{session_data}}));"
}
```

#### Restore Session

```json
{
  "name": "Restore session",
  "action": "evaluate",
  "value": "JSON.parse(localStorage.getItem('session_data'))"
}
```

### Parallel Execution

You can run multiple workflows in parallel by executing them in separate terminal windows or using a process manager like GNU Parallel or PM2.

### Workflow Templates

Templates are a powerful way to reuse workflow definitions. You can create templates for common tasks and then customize them with variables:

#### Create a Template

```bash
automata template create login_template login_workflow.json --description "Login workflow template" --tag auth --tag common
```

#### Use a Template

```bash
automata template use login_template my_login --variable url=https://example.com/login --variable username=myuser --variable password=mypass
```

This will create a new workflow named `my_login` with the specified variables.

### Configuration

You can customize Automata's behavior by editing the configuration file at `~/.automata/config.json`:

```json
{
  "browser": {
    "headless": true,
    "viewport": {
      "width": 1280,
      "height": 720
    }
  },
  "logging": {
    "level": "INFO",
    "file": null
  },
  "templates": {
    "directory": "~/.automata/templates"
  }
}
```

#### Browser Configuration

You can configure the browser settings:

- `headless`: Whether to run the browser in headless mode (default: true)
- `viewport`: The default viewport size (default: 1280x720)

#### Logging Configuration

You can configure the logging settings:

- `level`: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `file`: The path to the log file (null for console logging)

#### Templates Configuration

You can configure the templates directory:

- `directory`: The path to the templates directory (default: ~/.automata/templates)

### Environment Variables

You can use environment variables in your workflows:

```json
{
  "name": "Environment Variable Example",
  "version": "1.0.0",
  "variables": {
    "api_key": "${API_KEY}"
  },
  "steps": [
    {
      "name": "Use API key",
      "action": "type",
      "selector": "#api-key",
      "value": "{{api_key}}"
    }
  ]
}
```

You can set environment variables in your shell before running Automata:

```bash
export API_KEY="your_api_key_here"
automata workflow execute my_workflow.json
```

### Command Line Variables

You can also pass variables as command line arguments when executing a workflow:

```bash
automata workflow execute my_workflow.json --variable url=https://example.com --variable search_term=test
```

This will override the variables defined in the workflow file.

### Workflow Hooks

You can define hooks that run at specific points during workflow execution:

```json
{
  "name": "Workflow with Hooks",
  "version": "1.0.0",
  "hooks": {
    "before_start": [
      {
        "name": "Log start",
        "action": "execute_script",
        "value": "console.log('Workflow starting');"
      }
    ],
    "after_end": [
      {
        "name": "Log end",
        "action": "execute_script",
        "value": "console.log('Workflow ended');"
      }
    ]
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "https://example.com"
    }
  ]
}
```

The available hooks are:

- `before_start`: Runs before the workflow starts
- `after_end`: Runs after the workflow ends
- `before_step`: Runs before each step
- `after_step`: Runs after each step
- `on_error`: Runs when an error occurs

### Step Timeouts

You can specify a timeout for each step:

```json
{
  "name": "Click button",
  "action": "click",
  "selector": "#button",
  "timeout": 10
}
```

If the step doesn't complete within the specified timeout (in seconds), it will fail.

### Step Dependencies

You can specify dependencies between steps:

```json
{
  "name": "Step with dependency",
  "action": "click",
  "selector": "#button",
  "depends_on": ["previous_step_name"]
}
```

The step will only execute after all its dependencies have completed successfully.

### Workflow Variables Scope

Variables have different scopes:

- Global variables: Defined in the `variables` section of the workflow
- Local variables: Defined within a step or loop
- Environment variables: Defined in the shell environment

You can access variables from different scopes using the following syntax:

- `{{variable_name}}`: Access a global or local variable
- `${ENV_VAR}`: Access an environment variable

### Workflow Comments

You can add comments to your workflows:

```json
{
  "name": "Workflow with Comments",
  "version": "1.0.0",
  "_comment": "This is a workflow comment",
  "variables": {
    "url": "https://example.com",
    "_comment": "This is a variable comment"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}",
      "_comment": "This is a step comment"
    }
  ]
}
```

Comments are ignored during workflow execution.

### Workflow Versioning

You can specify a version for your workflow:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "https://example.com"
    }
  ]
}
```

The version should follow semantic versioning (SemVer) format (MAJOR.MINOR.PATCH).

### Workflow Metadata

You can add metadata to your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "metadata": {
    "author": "John Doe",
    "created": "2023-01-01",
    "tags": ["web", "scraping"],
    "category": "data extraction"
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "https://example.com"
    }
  ]
}
```

Metadata is ignored during workflow execution but can be useful for organizing and documenting your workflows.

### Workflow Parameters

You can define parameters for your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "parameters": {
    "url": {
      "type": "string",
      "description": "The URL to navigate to",
      "required": true,
      "default": "https://example.com"
    },
    "search_term": {
      "type": "string",
      "description": "The search term to use",
      "required": false
    }
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Enter search term",
      "action": "type",
      "selector": "#search",
      "value": "{{search_term}}",
      "condition": {
        "operator": "not_equals",
        "left": "{{search_term}}",
        "right": null
      }
    }
  ]
}
```

Parameters are similar to variables but have additional metadata like type, description, and whether they are required.

### Workflow Outputs

You can define outputs for your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "outputs": {
    "results": {
      "type": "array",
      "description": "The extracted results"
    },
    "status": {
      "type": "string",
      "description": "The status of the workflow"
    }
  },
  "steps": [
    {
      "name": "Extract data",
      "action": "extract",
      "selector": ".result",
      "value": {
        "title": ".title",
        "description": ".description"
      }
    },
    {
      "name": "Set output",
      "action": "set_variable",
      "selector": "results",
      "value": "{{extract_data}}"
    },
    {
      "name": "Set status",
      "action": "set_variable",
      "selector": "status",
      "value": "completed"
    }
  ]
}
```

Outputs are similar to variables but are intended to be the final results of the workflow.

### Workflow Imports

You can import other workflows into your workflow:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "imports": {
    "login": "login_workflow.json",
    "scrape": "scrape_workflow.json"
  },
  "steps": [
    {
      "name": "Execute login workflow",
      "action": "execute_workflow",
      "value": "login"
    },
    {
      "name": "Execute scrape workflow",
      "action": "execute_workflow",
      "value": "scrape"
    }
  ]
}
```

This allows you to create modular workflows that can be reused across different projects.

### Workflow Functions

You can define functions in your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "functions": {
    "login": {
      "parameters": {
        "username": {
          "type": "string",
          "required": true
        },
        "password": {
          "type": "string",
          "required": true
        }
      },
      "steps": [
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
          "name": "Click login button",
          "action": "click",
          "selector": "#login-button"
        }
      ]
    }
  },
  "steps": [
    {
      "name": "Call login function",
      "action": "call_function",
      "value": {
        "function": "login",
        "parameters": {
          "username": "myuser",
          "password": "mypass"
        }
      }
    }
  ]
}
```

Functions are reusable blocks of steps that can be called with different parameters.

### Workflow Conditions

You can define complex conditions in your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "steps": [
    {
      "name": "Check condition",
      "action": "if",
      "value": {
        "operator": "and",
        "operands": [
          {
            "operator": "equals",
            "left": "{{variable1}}",
            "right": "value1"
          },
          {
            "operator": "or",
            "operands": [
              {
                "operator": "equals",
                "left": "{{variable2}}",
                "right": "value2"
              },
              {
                "operator": "equals",
                "left": "{{variable3}}",
                "right": "value3"
              }
            ]
          }
        ]
      }
    }
  ]
}
```

Conditions support logical operators (and, or, not) and comparison operators (equals, not_equals, greater_than, less_than, etc.).

### Workflow Loops

You can define complex loops in your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "steps": [
    {
      "name": "Loop through pages",
      "action": "loop",
      "value": {
        "type": "for",
        "start": 1,
        "end": 10,
        "step": 1,
        "variable": "page",
        "steps": [
          {
            "name": "Navigate to page",
            "action": "navigate",
            "value": "https://example.com?page={{page}}"
          },
          {
            "name": "Extract data",
            "action": "extract",
            "selector": ".result",
            "value": {
              "title": ".title",
              "description": ".description"
            }
          }
        ]
      }
    }
  ]
}
```

Loops support different types (for, while, for_each) and can be nested.

### Workflow Error Handling

You can define advanced error handling in your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "steps": [
    {
      "name": "Try to click button",
      "action": "click",
      "selector": "#button",
      "on_error": {
        "action": "catch",
        "steps": [
          {
            "name": "Log error",
            "action": "execute_script",
            "value": "console.log('Button not found');"
          },
          {
            "name": "Click alternative button",
            "action": "click",
            "selector": "#alternative-button"
          }
        ]
      }
    }
  ]
}
```

Error handling supports try-catch blocks and custom error recovery steps.

### Workflow Performance

You can optimize the performance of your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "settings": {
    "parallel": true,
    "max_parallel_steps": 5,
    "cache": true,
    "cache_ttl": 3600
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "https://example.com"
    },
    {
      "name": "Extract data",
      "action": "extract",
      "selector": ".result",
      "value": {
        "title": ".title",
        "description": ".description"
      }
    }
  ]
}
```

Performance settings allow you to enable parallel execution, caching, and other optimizations.

### Workflow Security

You can enhance the security of your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "settings": {
    "secure": true,
    "encrypt_sensitive_data": true,
    "mask_sensitive_data": true
  },
  "steps": [
    {
      "name": "Enter password",
      "action": "type",
      "selector": "#password",
      "value": "{{password}}",
      "sensitive": true
    }
  ]
}
```

Security settings allow you to encrypt sensitive data, mask it in logs, and enable other security features.

### Workflow Debugging

You can debug your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "settings": {
    "debug": true,
    "log_level": "DEBUG",
    "trace": true
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "https://example.com"
    },
    {
      "name": "Debug breakpoint",
      "action": "debug",
      "value": "Check page title"
    }
  ]
}
```

Debug settings allow you to enable detailed logging, tracing, and breakpoints.

### Workflow Testing

You can test your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "tests": [
    {
      "name": "Test navigation",
      "steps": [
        {
          "name": "Navigate to page",
          "action": "navigate",
          "value": "https://example.com"
        },
        {
          "name": "Check title",
          "action": "assert",
          "value": {
            "operator": "equals",
            "left": "{{page_title}}",
            "right": "Example Domain"
          }
        }
      ]
    }
  ],
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "https://example.com"
    }
  ]
}
```

Tests allow you to verify that your workflows are working correctly.

### Workflow Documentation

You can document your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "documentation": {
    "purpose": "This workflow extracts data from a website",
    "usage": "Run this workflow with the URL of the website to extract data from",
    "examples": [
      {
        "description": "Extract data from example.com",
        "command": "automata workflow execute my_workflow.json --variable url=https://example.com"
      }
    ],
    "dependencies": [
      {
        "name": "login_workflow",
        "description": "This workflow requires the user to be logged in"
      }
    ],
    "outputs": [
      {
        "name": "results",
        "description": "The extracted data"
      }
    ]
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    }
  ]
}
```

Documentation helps others understand how to use your workflows.

### Workflow Deployment

You can deploy your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "deployment": {
    "schedule": "0 9 * * *",  # Run at 9 AM every day
    "environment": "production",
    "notifications": {
      "on_success": "admin@example.com",
      "on_failure": "admin@example.com"
    }
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    }
  ]
}
```

Deployment settings allow you to schedule workflows, specify the environment, and configure notifications.

### Workflow Monitoring

You can monitor your workflows:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "monitoring": {
    "metrics": [
      "execution_time",
      "success_rate",
      "error_rate"
    ],
    "alerts": {
      "execution_time_threshold": 300,
      "error_rate_threshold": 0.1
    }
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    }
  ]
}
```

Monitoring settings allow you to track metrics and configure alerts.

### Workflow Integrations

You can integrate your workflows with other systems:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "integrations": {
    "webhooks": {
      "on_start": "https://example.com/webhook/start",
      "on_success": "https://example.com/webhook/success",
      "on_failure": "https://example.com/webhook/failure"
    },
    "apis": {
      "slack": {
        "url": "https://slack.com/api/chat.postMessage",
        "token": "${SLACK_TOKEN}"
      }
    }
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    }
  ]
}
```

Integrations allow you to connect your workflows with webhooks, APIs, and other systems.

### Workflow Extensions

You can extend your workflows with custom actions:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "extensions": {
    "custom_actions": {
      "custom_action": {
        "module": "custom_actions",
        "function": "custom_action_function",
        "parameters": {
          "param1": {
            "type": "string",
            "required": true
          },
          "param2": {
            "type": "number",
            "required": false,
            "default": 10
          }
        }
      }
    }
  },
  "steps": [
    {
      "name": "Execute custom action",
      "action": "custom_action",
      "value": {
        "param1": "value1",
        "param2": 20
      }
    }
  ]
}
```

Extensions allow you to add custom actions to your workflows.

### Workflow Plugins

You can use plugins to extend the functionality of Automata:

```json
{
  "name": "My Workflow",
  "version": "1.0.0",
  "description": "My workflow description",
  "plugins": {
    "screenshot": {
      "enabled": true,
      "format": "png",
      "quality": 90
    },
    "pdf": {
      "enabled": true,
      "format": "A4",
      "orientation": "portrait"
    }
  },
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "{{url}}"
    },
    {
      "name": "Take screenshot",
      "action": "screenshot",
      "value": "screenshot.png"
    },
    {
      "name": "Generate PDF",
      "action": "pdf",
      "value": "document.pdf"
    }
  ]
}
```

Plugins allow you to add new actions and features to Automata.

### Workflow Templates

You can create templates for common workflows:

```json
{
  "name": "Login Template",
  "version": "1.0.0",
  "description": "A template for logging into websites",
  "type": "template",
  "parameters": {
    "url": {
      "type": "string",
      "description": "The URL of the login page",
      "required": true
    },
    "username": {
      "type": "string",
      "description": "The username to use for login",
      "required": true
    },
    "password": {
      "type": "string",
      "description": "The password to use for login",
      "required": true
    }
  },
  "steps": [
    {
      "name": "Navigate to login page",
      "action": "navigate",
      "value": "{{url}}"
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
      "name": "Click login button",
      "action": "click",
      "selector": "#login-button"
    },
    {
      "name": "Wait for login to complete",
      "action": "wait_for",
      "selector": ".dashboard",
      "timeout": 10
    }
  ]
}
```

### Workflow The End

This is the end of the user guide. We hope you found it helpful and that you enjoy using Automata for all your web automation needs!

If you have any questions or need further assistance, please don't hesitate to reach out to our support team at support@automata.dev.

Happy automating!
