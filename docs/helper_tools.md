# Helper Tools Documentation

## Table of Contents
- [Introduction](#introduction)
- [HTML Parser](#html-parser)
- [Selector Generator](#selector-generator)
- [Action Builder](#action-builder)
- [File I/O Utilities](#file-io-utilities)
- [Credential Handling](#credential-handling)
- [Examples and Use Cases](#examples-and-use-cases)

## Introduction

Automata provides a set of helper tools to assist you in creating and debugging workflows. These tools can be used standalone or as part of the CLI to help you parse HTML, generate selectors, build actions, and manage file I/O operations.

This guide will walk you through each helper tool, explaining how to use it and providing examples of common use cases.

## HTML Parser

The HTML Parser tool allows you to parse HTML files and extract element information. This is useful for understanding the structure of a web page and identifying the elements you want to interact with in your workflows.

### Features

- Parse HTML files and extract element information
- Display element hierarchy and relationships
- Identify element attributes and properties
- Export element information to JSON format

### CLI Usage

To parse an HTML file using the CLI:

```bash
automata helper parse-html path/to/file.html
```

You can also specify an output file to save the parsed data:

```bash
automata helper parse-html path/to/file.html --output parsed_data.json
```

### Programmatic Usage

You can also use the HTML Parser programmatically:

```python
from src.automata.helper import HtmlParser

# Create a parser instance
parser = HtmlParser()

# Parse an HTML file
parsed_data = parser.parse_file("path/to/file.html")

# Print the parsed data
print(parsed_data)
```

### Output Format

The HTML Parser outputs a JSON structure that represents the parsed HTML:

```json
{
  "title": "Page Title",
  "elements": [
    {
      "tag": "div",
      "id": "container",
      "class": "main-container",
      "attributes": {
        "data-id": "12345"
      },
      "text": "Container content",
      "children": [
        {
          "tag": "h1",
          "id": "title",
          "class": "page-title",
          "text": "Page Title",
          "children": []
        }
      ]
    }
  ]
}
```

### Use Cases

#### Understanding Page Structure

Use the HTML Parser to understand the structure of a web page before creating a workflow:

```bash
automata helper parse-html page.html
```

This will display the element hierarchy, making it easier to identify the elements you want to interact with.

#### Identifying Element Attributes

Use the HTML Parser to identify the attributes of elements that you want to interact with:

```bash
automata helper parse-html page.html | grep "attributes"
```

This will display the attributes of all elements, helping you find unique identifiers for your selectors.

#### Exporting Element Information

Use the HTML Parser to export element information to a JSON file for further processing:

```bash
automata helper parse-html page.html --output elements.json
```

This will save the parsed data to a JSON file that you can use in your scripts or other tools.

## Selector Generator

The Selector Generator tool allows you to generate robust CSS selectors from HTML elements. This is useful for creating selectors that are less likely to break when the web page structure changes.

### Features

- Generate CSS selectors from HTML elements
- Optimize selectors for robustness and reliability
- Provide multiple selector options with different specificity levels
- Export selectors to JSON format
- **NEW:** HTML Fragment Support - Accepts outerHTML fragments directly and automatically wraps them in a basic HTML structure
- **NEW:** Multiple Input Methods - Supports direct HTML input, fragment files, and stdin
- **NEW:** Three Targeting Modes - "all", "selector", and "auto" for flexible element selection

### CLI Usage

#### Basic Usage

To generate selectors from an HTML file using the CLI:

```bash
automata helper generate-selectors path/to/file.html
```

You can also specify an output file to save the generated selectors:

```bash
automata helper generate-selectors path/to/file.html --output selectors.json
```

You can also specify a target element to generate a selector for:

```bash
automata helper generate-selectors path/to/file.html --target "#submit-button"
```

#### New HTML Fragment Support

The tool now supports HTML fragments directly, which are automatically wrapped in a basic HTML structure:

```bash
# Using direct HTML fragment
automata helper generate-selectors --html-fragment "<div class='container'><button id='submit'>Submit</button></div>"

# Using a fragment file
automata helper generate-selectors --fragment-file path/to/fragment.html

# Using stdin (piping)
echo "<div class='container'><button id='submit'>Submit</button></div>" | automata helper generate-selectors --stdin
```

#### New Targeting Modes

The tool now supports three targeting modes:

1. **"all"** (default): Generate selectors for all elements in the fragment
2. **"selector"**: Generate selectors for elements matching a specific selector
3. **"auto"**: Automatically detect important elements

```bash
# Generate selectors for all elements (default)
automata helper generate-selectors --html-fragment "<div><button>Click</button></div>" --targeting-mode all

# Generate selectors for elements matching a specific selector
automata helper generate-selectors --html-fragment "<div><button>Click</button></div>" --targeting-mode selector --custom-selector "button"

# Auto-detect important elements
automata helper generate-selectors --html-fragment "<div><button>Click</button></div>" --targeting-mode auto
```

#### New Selector Type Support

You can now specify the type of selectors to generate:

```bash
# Generate CSS selectors (default)
automata helper generate-selectors --html-fragment "<div><button>Click</button></div>" --selector-type css

# Generate XPath selectors
automata helper generate-selectors --html-fragment "<div><button>Click</button></div>" --selector-type xpath
```

#### Combined Examples

Here are some examples combining the new features:

```bash
# Generate XPath selectors for all elements in a fragment
automata helper generate-selectors --html-fragment "<div class='container'><button id='submit'>Submit</button></div>" --selector-type xpath --targeting-mode all

# Generate CSS selectors for specific elements in a fragment file
automata helper generate-selectors --fragment-file path/to/fragment.html --selector-type css --targeting-mode selector --custom-selector "button"

# Auto-detect important elements from piped HTML and save to file
echo "<div class='container'><button id='submit'>Submit</button></div>" | automata helper generate-selectors --stdin --targeting-mode auto --output selectors.json
```

### Programmatic Usage

You can also use the Selector Generator programmatically:

```python
from src.automata.helper import SelectorGenerator

# Create a generator instance
generator = SelectorGenerator()

# Generate selectors from an HTML file
selectors = generator.generate_from_file("path/to/file.html")

# Print the generated selectors
print(selectors)
```

### Output Format

The Selector Generator outputs a JSON structure that contains the generated selectors:

```json
{
  "selectors": [
    {
      "element": "div#container.main-container",
      "selector": "#container",
      "specificity": "high",
      "robustness": "high"
    },
    {
      "element": "h1#title.page-title",
      "selector": "#title",
      "specificity": "high",
      "robustness": "high"
    },
    {
      "element": "button.submit-button",
      "selector": ".submit-button",
      "specificity": "medium",
      "robustness": "medium"
    }
  ]
}
```

### Use Cases

#### Creating Robust Selectors

Use the Selector Generator to create robust selectors for your workflows:

```bash
automata helper generate-selectors page.html
```

This will generate selectors for all elements in the page, with different specificity levels.

#### Finding Selectors for Specific Elements

Use the Selector Generator to find selectors for specific elements:

```bash
automata helper generate-selectors page.html --target "#submit-button"
```

This will generate selectors specifically for the element with the ID "submit-button".

#### Exporting Selectors for Reuse

Use the Selector Generator to export selectors to a JSON file for reuse in your workflows:

```bash
automata helper generate-selectors page.html --output selectors.json
```

This will save the generated selectors to a JSON file that you can reference in your workflows.

## Action Builder

The Action Builder tool allows you to build action definitions interactively. This is useful for creating complex actions with multiple parameters and ensuring that they are correctly formatted.

### Features

- Build action definitions interactively
- Validate action parameters and formats
- Provide suggestions for common action types
- Export action definitions to JSON format

### CLI Usage

To build an action interactively using the CLI:

```bash
automata helper build-action
```

This will start an interactive session where you can specify the action type, selector, value, and other parameters.

You can also specify an output file to save the built action:

```bash
automata helper build-action --output action.json
```

### Programmatic Usage

You can also use the Action Builder programmatically:

```python
from src.automata.helper import ActionBuilder

# Create a builder instance
builder = ActionBuilder()

# Build an action
action = builder.build_action(
    action_type="click",
    selector="#submit-button",
    value=None,
    timeout=10
)

# Print the built action
print(action)
```

### Output Format

The Action Builder outputs a JSON structure that represents the built action:

```json
{
  "name": "Click submit button",
  "action": "click",
  "selector": "#submit-button",
  "value": null,
  "timeout": 10,
  "on_error": "stop"
}
```

### Use Cases

#### Building Simple Actions

Use the Action Builder to build simple actions like clicking a button:

```bash
automata helper build-action
```

Follow the prompts to specify the action type as "click", the selector as "#submit-button", and other parameters.

#### Building Complex Actions

Use the Action Builder to build complex actions with multiple parameters:

```bash
automata helper build-action
```

Follow the prompts to specify the action type as "extract", the selector as ".result-item", and the value as a JSON object with the fields to extract.

#### Exporting Actions for Reuse

Use the Action Builder to export actions to a JSON file for reuse in your workflows:

```bash
automata helper build-action --output action.json
```

This will save the built action to a JSON file that you can include in your workflows.

## File I/O Utilities

The File I/O Utilities tool allows you to read and write files in various formats. This is useful for loading data into your workflows and saving the results of your workflows.

### Features

- Read and write files in various formats (JSON, CSV, XML, etc.)
- Handle file paths and directories
- Validate file formats and contents
- Provide error handling for file operations

### CLI Usage

To read a file using the CLI:

```bash
automata helper read-file path/to/file.json
```

To write to a file using the CLI:

```bash
automata helper write-file path/to/file.json --data '{"key": "value"}'
```

You can also specify the format of the file:

```bash
automata helper write-file path/to/file.csv --format csv --data "name,age\nJohn,30"
```

### Programmatic Usage

You can also use the File I/O Utilities programmatically:

```python
from src.automata.helper import FileIO

# Create a FileIO instance
file_io = FileIO()

# Read a file
data = file_io.read_file("path/to/file.json")

# Write to a file
file_io.write_file("path/to/file.json", {"key": "value"})
```

### Output Format

The File I/O Utilities handle various file formats and return the data in a consistent format:

```json
{
  "status": "success",
  "data": {
    "key": "value"
  },
  "message": "File read successfully"
}
```

### Use Cases

#### Loading Configuration Data

Use the File I/O Utilities to load configuration data into your workflows:

```bash
automata helper read-file config.json
```

This will read the configuration data from the JSON file, which you can then use in your workflows.

#### Saving Workflow Results

Use the File I/O Utilities to save the results of your workflows:

```bash
automata helper write-file results.json --data '{"results": [{"title": "Result 1"}, {"title": "Result 2"}]}'
```

This will save the results to a JSON file, which you can then process further or share with others.

#### Converting File Formats

Use the File I/O Utilities to convert between file formats:

```bash
automata helper read-file data.csv --format csv
automata helper write-file data.json --data '{"results": [...]}' --format json
```

This will read data from a CSV file and write it to a JSON file, effectively converting the format.

## Credential Handling

The Credential Handling feature allows you to securely manage and use credentials in your workflows. This is particularly useful for workflows that require authentication, such as logging into websites or accessing APIs.

### Features

- Load credentials from JSON files
- Support for multiple credential formats
- Secure credential storage and handling
- Integration with workflow execution
- Comprehensive error handling and validation

### CLI Usage

#### Using Credentials with Workflow Execution

To use credentials when executing a workflow, use the `--credentials` parameter:

```bash
automata workflow execute my_workflow.json --credentials path/to/credentials.json
```

This will load the credentials from the specified JSON file and make them available to your workflow.

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

### Error Handling

The credential handling feature includes comprehensive error handling:

- **File Not Found**: If the specified credentials file doesn't exist, the workflow will fail with a clear error message.
- **Invalid JSON**: If the credentials file contains invalid JSON, the workflow will fail with a parsing error.
- **Missing Required Fields**: If required fields are missing from the credentials file, the workflow will fail with a validation error.
- **Invalid Configuration**: If the configuration section is invalid or missing, the workflow will fail with a configuration error.

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

### Best Practices

1. **Use Separate Credentials Files**: Use different credentials files for different environments (development, staging, production).
2. **Template Variables**: Combine credentials with template variables for flexible workflow configuration.
3. **Validation**: Always validate that credentials are loaded correctly before using them in your workflow.
4. **Error Handling**: Implement proper error handling in your workflows to gracefully handle authentication failures.
5. **Security**: Never commit credentials files to version control. Use environment variables or secret management tools for sensitive data.

## Examples and Use Cases

### Example 1: Web Scraping Workflow

In this example, we'll create a workflow that scrapes data from a web page. We'll use the helper tools to understand the page structure, generate selectors, and build actions.

#### Step 1: Parse the HTML

First, let's parse the HTML to understand the page structure:

```bash
automata helper parse-html page.html --output parsed_data.json
```

This will give us a JSON file with the parsed HTML structure.

#### Step 2: Generate Selectors

Next, let's generate selectors for the elements we want to interact with:

```bash
automata helper generate-selectors page.html --target ".result-item" --output selectors.json
```

This will give us a JSON file with selectors for the result items.

#### Step 3: Build Actions

Now, let's build the actions for our workflow:

```bash
automata helper build-action --output navigate_action.json
```

Follow the prompts to create a navigate action.

```bash
automata helper build-action --output extract_action.json
```

Follow the prompts to create an extract action.

#### Step 4: Create the Workflow

Finally, let's create the workflow using the actions we built:

```json
{
  "name": "Web Scraping Workflow",
  "version": "1.0.0",
  "description": "Scrape data from a web page",
  "steps": [
    {
      "name": "Navigate to page",
      "action": "navigate",
      "value": "https://example.com"
    },
    {
      "name": "Wait for results",
      "action": "wait_for",
      "selector": ".result-item",
      "timeout": 10
    },
    {
      "name": "Extract data",
      "action": "extract",
      "selector": ".result-item",
      "value": {
        "title": ".title",
        "description": ".description"
      }
    },
    {
      "name": "Save results",
      "action": "save",
      "value": "results.json"
    }
  ]
}
```

### Example 2: Form Submission Workflow

In this example, we'll create a workflow that fills out and submits a form. We'll use the helper tools to understand the form structure, generate selectors, and build actions.

#### Step 1: Parse the HTML

First, let's parse the HTML to understand the form structure:

```bash
automata helper parse-html form.html --output parsed_data.json
```

This will give us a JSON file with the parsed HTML structure.

#### Step 2: Generate Selectors

Next, let's generate selectors for the form elements:

```bash
automata helper generate-selectors form.html --target "#username" --output username_selector.json
automata helper generate-selectors form.html --target "#password" --output password_selector.json
automata helper generate-selectors form.html --target "#submit-button" --output submit_selector.json
```

This will give us JSON files with selectors for the form elements.

#### Step 3: Build Actions

Now, let's build the actions for our workflow:

```bash
automata helper build-action --output navigate_action.json
```

Follow the prompts to create a navigate action.

```bash
automata helper build-action --output type_username_action.json
```

Follow the prompts to create a type action for the username field.

```bash
automata helper build-action --output type_password_action.json
```

Follow the prompts to create a type action for the password field.

```bash
automata helper build-action --output click_submit_action.json
```

Follow the prompts to create a click action for the submit button.

#### Step 4: Create the Workflow

Finally, let's create the workflow using the actions we built:

```json
{
  "name": "Form Submission Workflow",
  "version": "1.0.0",
  "description": "Fill out and submit a form",
  "variables": {
    "username": "myuser",
    "password": "mypass"
  },
  "steps": [
    {
      "name": "Navigate to form",
      "action": "navigate",
      "value": "https://example.com/form"
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
      "name": "Click submit button",
      "action": "click",
      "selector": "#submit-button"
    },
    {
      "name": "Wait for confirmation",
      "action": "wait_for",
      "selector": ".confirmation-message",
      "timeout": 10
    }
  ]
}
```

### Example 3: Data Processing Workflow

In this example, we'll create a workflow that processes data from a file and saves the results. We'll use the File I/O Utilities to read and write files.

#### Step 1: Read the Input File

First, let's read the input file:

```bash
automata helper read-file input.json --output input_data.json
```

This will give us a JSON file with the input data.

#### Step 2: Process the Data

Next, let's process the data. In this example, we'll filter the data to only include items with a specific property:

```python
import json

# Read the input data
with open("input_data.json", "r") as f:
    input_data = json.load(f)

# Filter the data
filtered_data = [item for item in input_data if item.get("active", False)]

# Save the filtered data
with open("filtered_data.json", "w") as f:
    json.dump(filtered_data, f, indent=2)
```

#### Step 3: Save the Results

Finally, let's save the results:

```bash
automata helper write-file output.json --data "$(cat filtered_data.json)"
```

This will save the filtered data to a JSON file.

#### Step 4: Create the Workflow

Now, let's create a workflow that automates this process:

```json
{
  "name": "Data Processing Workflow",
  "version": "1.0.0",
  "description": "Process data from a file and save the results",
  "steps": [
    {
      "name": "Load input data",
      "action": "load",
      "value": "input.json"
    },
    {
      "name": "Filter data",
      "action": "execute_script",
      "value": "filtered_data = [item for item in input_data if item.get('active', false)]; set_variable('filtered_data', filtered_data);"
    },
    {
      "name": "Save results",
      "action": "save",
      "value": "output.json",
      "data": "{{filtered_data}}"
    }
  ]
}
```

### Best Practices

#### Use Descriptive Names

When building actions and creating workflows, use descriptive names that clearly indicate what the action or workflow does. This will make your workflows easier to understand and maintain.

#### Validate Your Workflows

Before executing your workflows, validate them using the workflow validator:

```bash
automata workflow validate my_workflow.json
```

This will help you identify and fix any issues before running the workflow.

#### Use Variables for Reusable Values

Use variables for values that you might want to change later, such as URLs, file paths, and configuration settings. This will make your workflows more flexible and easier to maintain.

#### Handle Errors Gracefully

Add error handling to your workflows to ensure that they can recover from unexpected situations. Use the `on_error` parameter to specify what should happen if an action fails.

#### Test Your Workflows

Test your workflows thoroughly before using them in production. Start with small, simple workflows and gradually add complexity as you become more comfortable with the tool.

#### Document Your Workflows

Add comments and documentation to your workflows to explain what they do and how they work. This will make it easier for others (and your future self) to understand and maintain your workflows.

#### Use Version Control

Use version control to track changes to your workflows. This will allow you to revert to previous versions if needed and collaborate with others on your workflows.

#### Keep Your Workflows Modular

Break down complex workflows into smaller, modular workflows that can be reused and combined in different ways. This will make your workflows more flexible and easier to maintain.

#### Use Templates for Common Tasks

Create templates for common tasks that you perform frequently. This will save you time and ensure consistency across your workflows.

#### Monitor Your Workflows

Monitor your workflows to ensure that they are running correctly and efficiently. Use logging and debugging tools to identify and fix any issues.

#### Optimize Your Workflows

Optimize your workflows for performance and efficiency. Use parallel execution, caching, and other optimization techniques to speed up your workflows.

#### Secure Your Workflows

Secure your workflows to protect sensitive data and prevent unauthorized access. Use encryption, authentication, and other security measures as needed.
