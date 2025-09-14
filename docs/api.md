# API Documentation

## Table of Contents
- [Introduction](#introduction)
- [Core Engine](#core-engine)
  - [AutomationEngine](#automationengine)
  - [BrowserManager](#browsermanager)
  - [SessionManager](#sessionmanager)
  - [ElementSelector](#elementselector)
  - [WaitManager](#waitmanager)
  - [ErrorHandler](#errorhandler)
- [Authentication System](#authentication-system)
  - [AuthManager](#authmanager)
  - [AuthProvider](#authprovider)
  - [SessionPersistence](#sessionpersistence)
- [Helper Tools](#helper-tools)
  - [HtmlParser](#htmlparser)
  - [SelectorGenerator](#selectorgenerator)
  - [ActionBuilder](#actionbuilder)
  - [FileIO](#fileio)
- [Workflow System](#workflow-system)
  - [WorkflowBuilder](#workflowbuilder)
  - [WorkflowValidator](#workflowvalidator)
  - [WorkflowExecutor](#workflowexecutor)
  - [WorkflowTemplate](#workflowtemplate)
- [CLI Interface](#cli-interface)
  - [CLI](#cli)
  - [WorkflowCommands](#workflowcommands)
  - [TemplateCommands](#templatecommands)
  - [HelperCommands](#helpercommands)
- [Examples](#examples)

## Introduction

This document provides API documentation for the core components of Automata. Each component is described with its purpose, methods, and usage examples.

The API is organized into several modules:

- Core Engine: Provides the main automation functionality
- Authentication System: Handles authentication and session management
- Helper Tools: Utilities for parsing HTML, generating selectors, and building actions
- Workflow System: Manages workflow creation, validation, and execution
- CLI Interface: Provides command-line interface for interacting with Automata

## Core Engine

### AutomationEngine

The `AutomationEngine` class is the main component of Automata. It orchestrates the automation process by coordinating the other components.

#### Methods

- `__init__(config=None)`: Initialize the automation engine with optional configuration.
- `start()`: Start the automation engine and initialize the browser.
- `stop()`: Stop the automation engine and close the browser.
- `execute_action(action)`: Execute a single action.
- `execute_workflow(workflow)`: Execute a complete workflow.
- `get_page_source()`: Get the HTML source of the current page.
- `take_screenshot(path=None)`: Take a screenshot of the current page.
- `execute_script(script)`: Execute JavaScript code in the browser.
- `evaluate(expression)`: Evaluate a JavaScript expression and return the result.

#### Example

```python
from src.automata.core import AutomationEngine

# Create an automation engine instance
engine = AutomationEngine()

# Start the engine
engine.start()

# Navigate to a page
engine.execute_action({
    "name": "Navigate to page",
    "action": "navigate",
    "value": "https://example.com"
})

# Take a screenshot
engine.take_screenshot("screenshot.png")

# Stop the engine
engine.stop()
```

### BrowserManager

The `BrowserManager` class manages the browser instance and provides methods for controlling the browser.

#### Methods

- `__init__(config=None)`: Initialize the browser manager with optional configuration.
- `start_browser()`: Start the browser instance.
- `stop_browser()`: Stop the browser instance.
- `get_page()`: Get the current page instance.
- `new_page()`: Create a new page/tab.
- `switch_to_page(index)`: Switch to a specific page/tab.
- `close_page(index)`: Close a specific page/tab.
- `set_viewport(width, height)`: Set the viewport size.
- `set_user_agent(user_agent)`: Set the user agent.
- `add_cookie(cookie)`: Add a cookie to the browser.
- `get_cookies()`: Get all cookies from the browser.
- `clear_cookies()`: Clear all cookies from the browser.
- `set_timeout(timeout)`: Set the default timeout for actions.

#### Example

```python
from src.automata.core import BrowserManager

# Create a browser manager instance
manager = BrowserManager()

# Start the browser
manager.start_browser()

# Get the current page
page = manager.get_page()

# Navigate to a page
page.goto("https://example.com")

# Set the viewport size
manager.set_viewport(1280, 720)

# Stop the browser
manager.stop_browser()
```

### SessionManager

The `SessionManager` class manages browser sessions, including cookies, localStorage, and sessionStorage.

#### Methods

- `__init__(browser_manager)`: Initialize the session manager with a browser manager.
- `save_session(path=None)`: Save the current session to a file.
- `load_session(path)`: Load a session from a file.
- `save_cookies(path=None)`: Save cookies to a file.
- `load_cookies(path)`: Load cookies from a file.
- `save_local_storage(path=None)`: Save localStorage to a file.
- `load_local_storage(path)`: Load localStorage from a file.
- `save_session_storage(path=None)`: Save sessionStorage to a file.
- `load_session_storage(path)`: Load sessionStorage from a file.
- `clear_session()`: Clear the current session.
- `get_session_info()`: Get information about the current session.

#### Example

```python
from src.automata.core import BrowserManager, SessionManager

# Create a browser manager instance
browser_manager = BrowserManager()
browser_manager.start_browser()

# Create a session manager instance
session_manager = SessionManager(browser_manager)

# Save the current session
session_manager.save_session("session.json")

# Clear the session
session_manager.clear_session()

# Load the session
session_manager.load_session("session.json")

# Stop the browser
browser_manager.stop_browser()
```

### ElementSelector

The `ElementSelector` class provides methods for selecting elements on a web page.

#### Methods

- `__init__(page)`: Initialize the element selector with a page instance.
- `select_element(selector, timeout=None)`: Select a single element.
- `select_elements(selector, timeout=None)`: Select multiple elements.
- `select_element_by_text(text, timeout=None)`: Select an element by its text content.
- `select_element_by_attribute(attribute, value, timeout=None)`: Select an element by an attribute.
- `select_element_by_partial_text(text, timeout=None)`: Select an element by partial text content.
- `is_element_visible(selector, timeout=None)`: Check if an element is visible.
- `is_element_enabled(selector, timeout=None)`: Check if an element is enabled.
- `is_element_present(selector, timeout=None)`: Check if an element is present.
- `get_element_text(selector, timeout=None)`: Get the text content of an element.
- `get_element_attribute(selector, attribute, timeout=None)`: Get the value of an element attribute.
- `get_element_property(selector, property, timeout=None)`: Get the value of an element property.

#### Example

```python
from src.automata.core import BrowserManager, ElementSelector

# Create a browser manager instance
browser_manager = BrowserManager()
browser_manager.start_browser()

# Get the current page
page = browser_manager.get_page()

# Navigate to a page
page.goto("https://example.com")

# Create an element selector instance
selector = ElementSelector(page)

# Select an element
element = selector.select_element("#submit-button")

# Get the text content of an element
text = selector.get_element_text(".title")

# Check if an element is visible
is_visible = selector.is_element_visible("#submit-button")

# Stop the browser
browser_manager.stop_browser()
```

### WaitManager

The `WaitManager` class provides methods for waiting for certain conditions on a web page.

#### Methods

- `__init__(page)`: Initialize the wait manager with a page instance.
- `wait_for_element(selector, timeout=None)`: Wait for an element to be present.
- `wait_for_element_visible(selector, timeout=None)`: Wait for an element to be visible.
- `wait_for_element_hidden(selector, timeout=None)`: Wait for an element to be hidden.
- `wait_for_element_enabled(selector, timeout=None)`: Wait for an element to be enabled.
- `wait_for_element_disabled(selector, timeout=None)`: Wait for an element to be disabled.
- `wait_for_text(text, selector=None, timeout=None)`: Wait for text to be present.
- `wait_for_function(function, timeout=None)`: Wait for a function to return a truthy value.
- `wait_for_navigation(timeout=None)`: Wait for a navigation to complete.
- `wait_for_load_state(state="domcontentloaded", timeout=None)`: Wait for a specific load state.
- `sleep(seconds)`: Sleep for a specified number of seconds.

#### Example

```python
from src.automata.core import BrowserManager, WaitManager

# Create a browser manager instance
browser_manager = BrowserManager()
browser_manager.start_browser()

# Get the current page
page = browser_manager.get_page()

# Navigate to a page
page.goto("https://example.com")

# Create a wait manager instance
wait_manager = WaitManager(page)

# Wait for an element to be visible
wait_manager.wait_for_element_visible("#submit-button")

# Wait for a specific text to be present
wait_manager.wait_for_text("Welcome to our website")

# Wait for a navigation to complete
wait_manager.wait_for_navigation()

# Stop the browser
browser_manager.stop_browser()
```

### ErrorHandler

The `ErrorHandler` class provides methods for handling errors that occur during automation.

#### Methods

- `__init__(engine)`: Initialize the error handler with an automation engine.
- `handle_error(error, action=None)`: Handle an error that occurred during an action.
- `retry_action(action, max_attempts=3, delay=1)`: Retry an action that failed.
- `take_error_screenshot(path=None)`: Take a screenshot when an error occurs.
- `save_error_page_source(path=None)`: Save the page source when an error occurs.
- `log_error(error, action=None)`: Log an error that occurred during an action.
- `get_error_info(error, action=None)`: Get information about an error.

#### Example

```python
from src.automata.core import AutomationEngine, ErrorHandler

# Create an automation engine instance
engine = AutomationEngine()
engine.start()

# Create an error handler instance
error_handler = ErrorHandler(engine)

try:
    # Execute an action that might fail
    engine.execute_action({
        "name": "Click non-existent button",
        "action": "click",
        "selector": "#non-existent-button"
    })
except Exception as e:
    # Handle the error
    error_handler.handle_error(e)

# Stop the engine
engine.stop()
```

## Authentication System

### AuthManager

The `AuthManager` class manages authentication for websites.

#### Methods

- `__init__(engine)`: Initialize the auth manager with an automation engine.
- `login(credentials, method=None)`: Log in to a website using the specified credentials and method.
- `logout()`: Log out of the current website.
- `is_logged_in()`: Check if the user is currently logged in.
- `get_session_info()`: Get information about the current session.
- `save_session(path=None)`: Save the current session to a file.
- `load_session(path)`: Load a session from a file.
- `register_auth_provider(name, provider)`: Register an authentication provider.
- `get_auth_provider(name)`: Get an authentication provider by name.
- `list_auth_providers()`: List all available authentication providers.

#### Example

```python
from src.automata.core import AutomationEngine
from src.automata.auth import AuthManager

# Create an automation engine instance
engine = AutomationEngine()
engine.start()

# Create an auth manager instance
auth_manager = AuthManager(engine)

# Log in using form-based authentication
auth_manager.login({
    "username": "myuser",
    "password": "mypass"
}, method="form")

# Check if logged in
is_logged_in = auth_manager.is_logged_in()

# Save the session
auth_manager.save_session("session.json")

# Log out
auth_manager.logout()

# Stop the engine
engine.stop()
```

### AuthProvider

The `AuthProvider` class is the base class for authentication providers.

#### Methods

- `__init__(engine)`: Initialize the auth provider with an automation engine.
- `login(credentials)`: Log in using the specified credentials.
- `logout()`: Log out of the current website.
- `is_logged_in()`: Check if the user is currently logged in.
- `get_name()`: Get the name of the auth provider.

#### Example

```python
from src.automata.core import AutomationEngine
from src.automata.auth import AuthProvider

class FormAuthProvider(AuthProvider):
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "form"

    def login(self, credentials):
        # Navigate to login page
        self.engine.execute_action({
            "name": "Navigate to login page",
            "action": "navigate",
            "value": "https://example.com/login"
        })

        # Enter username
        self.engine.execute_action({
            "name": "Enter username",
            "action": "type",
            "selector": "#username",
            "value": credentials["username"]
        })

        # Enter password
        self.engine.execute_action({
            "name": "Enter password",
            "action": "type",
            "selector": "#password",
            "value": credentials["password"]
        })

        # Submit form
        self.engine.execute_action({
            "name": "Submit form",
            "action": "click",
            "selector": "#login-button"
        })

        # Wait for login to complete
        self.engine.execute_action({
            "name": "Wait for login to complete",
            "action": "wait_for",
            "selector": ".user-dashboard",
            "timeout": 10
        })

    def logout(self):
        # Click logout button
        self.engine.execute_action({
            "name": "Click logout button",
            "action": "click",
            "selector": "#logout-button"
        })

        # Wait for logout to complete
        self.engine.execute_action({
            "name": "Wait for logout to complete",
            "action": "wait_for",
            "selector": "#login-form",
            "timeout": 10
        })

    def is_logged_in(self):
        # Check if user dashboard is visible
        return self.engine.execute_action({
            "name": "Check if user dashboard is visible",
            "action": "evaluate",
            "value": "document.querySelector('.user-dashboard') !== null"
        })

    def get_name(self):
        return self.name
```

### SessionPersistence

The `SessionPersistence` class provides methods for persisting and restoring browser sessions.

#### Methods

- `__init__(browser_manager)`: Initialize the session persistence with a browser manager.
- `save_session(path=None)`: Save the current session to a file.
- `load_session(path)`: Load a session from a file.
- `save_cookies(path=None)`: Save cookies to a file.
- `load_cookies(path)`: Load cookies from a file.
- `save_local_storage(path=None)`: Save localStorage to a file.
- `load_local_storage(path)`: Load localStorage from a file.
- `save_session_storage(path=None)`: Save sessionStorage to a file.
- `load_session_storage(path)`: Load sessionStorage from a file.
- `export_session()`: Export the current session as a dictionary.
- `import_session(session_data)`: Import a session from a dictionary.

#### Example

```python
from src.automata.core import BrowserManager, SessionPersistence

# Create a browser manager instance
browser_manager = BrowserManager()
browser_manager.start_browser()

# Create a session persistence instance
session_persistence = SessionPersistence(browser_manager)

# Save the current session
session_data = session_persistence.export_session()

# Clear the session
browser_manager.clear_cookies()

# Import the session
session_persistence.import_session(session_data)

# Stop the browser
browser_manager.stop_browser()
```

## Helper Tools

### HtmlParser

The `HtmlParser` class provides methods for parsing HTML files and extracting element information.

#### Methods

- `__init__()`: Initialize the HTML parser.
- `parse_file(path)`: Parse an HTML file and return the parsed data.
- `parse_string(html)`: Parse an HTML string and return the parsed data.
- `parse_url(url)`: Parse the HTML from a URL and return the parsed data.
- `extract_elements(html, selector=None)`: Extract elements from HTML that match a selector.
- `extract_text(html, selector=None)`: Extract text from HTML elements that match a selector.
- `extract_attributes(html, selector=None, attributes=None)`: Extract attributes from HTML elements that match a selector.
- `get_element_hierarchy(html)`: Get the hierarchy of elements in HTML.
- `find_elements_by_text(html, text)`: Find elements that contain specific text.
- `find_elements_by_attribute(html, attribute, value)`: Find elements with a specific attribute value.

#### Example

```python
from src.automata.helper import HtmlParser

# Create an HTML parser instance
parser = HtmlParser()

# Parse an HTML file
parsed_data = parser.parse_file("page.html")

# Extract elements that match a selector
elements = parser.extract_elements(parsed_data, ".article")

# Extract text from elements
text = parser.extract_text(parsed_data, ".title")

# Find elements that contain specific text
elements = parser.find_elements_by_text(parsed_data, "Welcome")
```

### SelectorGenerator

The `SelectorGenerator` class provides methods for generating CSS selectors from HTML elements.

#### Methods

- `__init__()`: Initialize the selector generator.
- `generate_from_file(path, target=None)`: Generate selectors from an HTML file.
- `generate_from_string(html, target=None)`: Generate selectors from an HTML string.
- `generate_from_element(element)`: Generate a selector for an HTML element.
- `optimize_selector(selector)`: Optimize a selector for robustness.
- `get_selector_specificity(selector)`: Get the specificity of a selector.
- `get_selector_robustness(selector)`: Get the robustness of a selector.
- `generate_fallback_selectors(selector)`: Generate fallback selectors for a selector.
- `validate_selector(selector)`: Validate a selector.

#### Example

```python
from src.automata.helper import SelectorGenerator

# Create a selector generator instance
generator = SelectorGenerator()

# Generate selectors from an HTML file
selectors = generator.generate_from_file("page.html")

# Generate a selector for a specific element
selector = generator.generate_from_element(element)

# Optimize a selector
optimized_selector = generator.optimize_selector(selector)

# Get the specificity of a selector
specificity = generator.get_selector_specificity(selector)
```

### ActionBuilder

The `ActionBuilder` class provides methods for building action definitions.

#### Methods

- `__init__()`: Initialize the action builder.
- `build_action(action_type, selector=None, value=None, **kwargs)`: Build an action definition.
- `build_navigate_action(url)`: Build a navigate action.
- `build_click_action(selector)`: Build a click action.
- `build_type_action(selector, text)`: Build a type action.
- `build_hover_action(selector)`: Build a hover action.
- `build_wait_for_action(selector, timeout=None)`: Build a wait_for action.
- `build_wait_action(seconds)`: Build a wait action.
- `build_get_text_action(selector)`: Build a get_text action.
- `build_get_attribute_action(selector, attribute)`: Build a get_attribute action.
- `build_screenshot_action(path=None)`: Build a screenshot action.
- `build_execute_script_action(script)`: Build an execute_script action.
- `build_evaluate_action(expression)`: Build an evaluate action.
- `build_extract_action(selector, value)`: Build an extract action.
- `build_save_action(path, data=None)`: Build a save action.
- `build_load_action(path)`: Build a load action.
- `build_set_variable_action(name, value)`: Build a set_variable action.
- `build_if_action(condition, steps=None, else_steps=None)`: Build an if action.
- `build_loop_action(type, value, steps=None)`: Build a loop action.
- `build_goto_action(step_name)`: Build a goto action.
- `build_stop_action()`: Build a stop action.
- `build_pause_action()`: Build a pause action.
- `build_resume_action()`: Build a resume action.
- `validate_action(action)`: Validate an action definition.

#### Example

```python
from src.automata.helper import ActionBuilder

# Create an action builder instance
builder = ActionBuilder()

# Build a navigate action
navigate_action = builder.build_navigate_action("https://example.com")

# Build a click action
click_action = builder.build_click_action("#submit-button")

# Build a type action
type_action = builder.build_type_action("#search", "search term")

# Build an extract action
extract_action = builder.build_extract_action(".result", {
    "title": ".title",
    "description": ".description"
})
```

### FileIO

The `FileIO` class provides methods for reading and writing files in various formats.

#### Methods

- `__init__()`: Initialize the file I/O utility.
- `read_file(path, format=None)`: Read a file and return the data.
- `write_file(path, data, format=None)`: Write data to a file.
- `read_json(path)`: Read a JSON file and return the data.
- `write_json(path, data)`: Write data to a JSON file.
- `read_csv(path, **kwargs)`: Read a CSV file and return the data.
- `write_csv(path, data, **kwargs)`: Write data to a CSV file.
- `read_xml(path)`: Read an XML file and return the data.
- `write_xml(path, data)`: Write data to an XML file.
- `read_text(path)`: Read a text file and return the data.
- `write_text(path, data)`: Write data to a text file.
- `read_binary(path)`: Read a binary file and return the data.
- `write_binary(path, data)`: Write data to a binary file.
- `file_exists(path)`: Check if a file exists.
- `create_directory(path)`: Create a directory.
- `delete_file(path)`: Delete a file.
- `copy_file(src, dst)`: Copy a file.
- `move_file(src, dst)`: Move a file.
- `get_file_size(path)`: Get the size of a file.
- `get_file_modified_time(path)`: Get the modified time of a file.

#### Example

```python
from src.automata.helper import FileIO

# Create a file I/O instance
file_io = FileIO()

# Read a JSON file
data = file_io.read_json("data.json")

# Write data to a JSON file
file_io.write_json("output.json", data)

# Read a CSV file
data = file_io.read_csv("data.csv")

# Write data to a CSV file
file_io.write_csv("output.csv", data)

# Check if a file exists
exists = file_io.file_exists("data.json")
```

## Workflow System

### WorkflowBuilder

The `WorkflowBuilder` class provides methods for building workflow definitions.

#### Methods

- `__init__()`: Initialize the workflow builder.
- `build_workflow(name, version, description=None, variables=None, steps=None)`: Build a workflow definition.
- `add_step(workflow, step)`: Add a step to a workflow.
- `remove_step(workflow, step_name)`: Remove a step from a workflow.
- `update_step(workflow, step_name, step)`: Update a step in a workflow.
- `get_step(workflow, step_name)`: Get a step from a workflow.
- `list_steps(workflow)`: List all steps in a workflow.
- `add_variable(workflow, name, value)`: Add a variable to a workflow.
- `remove_variable(workflow, name)`: Remove a variable from a workflow.
- `update_variable(workflow, name, value)`: Update a variable in a workflow.
- `get_variable(workflow, name)`: Get a variable from a workflow.
- `list_variables(workflow)`: List all variables in a workflow.
- `validate_workflow(workflow)`: Validate a workflow definition.
- `export_workflow(workflow, path)`: Export a workflow to a file.
- `import_workflow(path)`: Import a workflow from a file.

#### Example

```python
from src.automata.workflow import WorkflowBuilder

# Create a workflow builder instance
builder = WorkflowBuilder()

# Build a workflow
workflow = builder.build_workflow(
    name="My Workflow",
    version="1.0.0",
    description="My workflow description",
    variables={
        "url": "https://example.com"
    },
    steps=[
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
)

# Export the workflow
builder.export_workflow(workflow, "workflow.json")
```

### WorkflowValidator

The `WorkflowValidator` class provides methods for validating workflow definitions.

#### Methods

- `__init__()`: Initialize the workflow validator.
- `validate_workflow(workflow)`: Validate a workflow definition.
- `validate_step(step)`: Validate a step definition.
- `validate_action(action)`: Validate an action definition.
- `validate_variable(variable)`: Validate a variable definition.
- `validate_condition(condition)`: Validate a condition definition.
- `validate_loop(loop)`: Validate a loop definition.
- `validate_selector(selector)`: Validate a selector definition.
- `validate_value(value, type)`: Validate a value against a type.
- `get_validation_errors(workflow)`: Get all validation errors for a workflow.
- `is_valid_workflow(workflow)`: Check if a workflow is valid.

#### Example

```python
from src.automata.workflow import WorkflowBuilder, WorkflowValidator

# Create a workflow builder instance
builder = WorkflowBuilder()

# Build a workflow
workflow = builder.build_workflow(
    name="My Workflow",
    version="1.0.0",
    steps=[
        {
            "name": "Navigate to page",
            "action": "navigate",
            "value": "https://example.com"
        }
    ]
)

# Create a workflow validator instance
validator = WorkflowValidator()

# Validate the workflow
is_valid = validator.is_valid_workflow(workflow)

# Get validation errors
errors = validator.get_validation_errors(workflow)
```

### WorkflowExecutor

The `WorkflowExecutor` class provides methods for executing workflow definitions.

#### Methods

- `__init__(engine)`: Initialize the workflow executor with an automation engine.
- `execute_workflow(workflow, variables=None)`: Execute a workflow.
- `execute_step(step, variables=None)`: Execute a step.
- `execute_action(action, variables=None)`: Execute an action.
- `pause_workflow()`: Pause the current workflow execution.
- `resume_workflow()`: Resume the current workflow execution.
- `stop_workflow()`: Stop the current workflow execution.
- `get_execution_status()`: Get the status of the current workflow execution.
- `get_execution_results()`: Get the results of the current workflow execution.
- `get_execution_errors()`: Get the errors of the current workflow execution.

#### Example

```python
from src.automata.core import AutomationEngine
from src.automata.workflow import WorkflowBuilder, WorkflowExecutor

# Create an automation engine instance
engine = AutomationEngine()
engine.start()

# Create a workflow builder instance
builder = WorkflowBuilder()

# Build a workflow
workflow = builder.build_workflow(
    name="My Workflow",
    version="1.0.0",
    steps=[
        {
            "name": "Navigate to page",
            "action": "navigate",
            "value": "https://example.com"
        },
        {
            "name": "Take screenshot",
            "action": "screenshot",
            "value": "screenshot.png"
        }
    ]
)

# Create a workflow executor instance
executor = WorkflowExecutor(engine)

# Execute the workflow
results = executor.execute_workflow(workflow)

# Stop the engine
engine.stop()
```

### WorkflowTemplate

The `WorkflowTemplate` class provides methods for managing workflow templates.

#### Methods

- `__init__()`: Initialize the workflow template manager.
- `create_template(name, workflow, description=None, tags=None)`: Create a workflow template.
- `get_template(name)`: Get a workflow template by name.
- `list_templates()`: List all workflow templates.
- `search_templates(query)`: Search for workflow templates.
- `update_template(name, workflow)`: Update a workflow template.
- `delete_template(name)`: Delete a workflow template.
- `use_template(name, variables=None)`: Use a workflow template to create a workflow.
- `export_template(name, path)`: Export a workflow template to a file.
- `import_template(name, path)`: Import a workflow template from a file.

#### Example

```python
from src.automata.workflow import WorkflowBuilder, WorkflowTemplate

# Create a workflow builder instance
builder = WorkflowBuilder()

# Build a workflow
workflow = builder.build_workflow(
    name="Login Template",
    version="1.0.0",
    description="A template for logging into websites",
    variables={
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
    steps=[
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
)

# Create a workflow template instance
template_manager = WorkflowTemplate()

# Create a template
template_manager.create_template(
    name="login",
    workflow=workflow,
    description="A template for logging into websites",
    tags=["auth", "login"]
)

# Use the template
login_workflow = template_manager.use_template(
    name="login",
    variables={
        "url": "https://example.com/login",
        "username": "myuser",
        "password": "mypass"
    }
)
```

## CLI Interface

### CLI

The `CLI` class provides the command-line interface for Automata.

#### Methods

- `__init__()`: Initialize the CLI.
- `run()`: Run the CLI.
- `add_command(command)`: Add a command to the CLI.
- `remove_command(name)`: Remove a command from the CLI.
- `get_command(name)`: Get a command by name.
- `list_commands()`: List all commands.
- `parse_args(args)`: Parse command-line arguments.
- `execute_command(command, args)`: Execute a command with arguments.
- `print_help()`: Print help information.
- `print_version()`: Print version information.

#### Example

```python
from src.automata.cli import CLI

# Create a CLI instance
cli = CLI()

# Add a command
cli.add_command({
    "name": "hello",
    "description": "Say hello",
    "function": lambda args: print(f"Hello, {args.name}!"),
    "arguments": [
        {
            "name": "name",
            "description": "Your name",
            "required": true
        }
    ]
})

# Run the CLI
cli.run()
```

### WorkflowCommands

The `WorkflowCommands` class provides commands for managing workflows.

#### Methods

- `__init__(cli)`: Initialize the workflow commands with a CLI instance.
- `register_commands()`: Register all workflow commands with the CLI.
- `create_workflow(args)`: Create a new workflow.
- `execute_workflow(args)`: Execute a workflow.
- `validate_workflow(args)`: Validate a workflow.
- `edit_workflow(args)`: Edit a workflow.
- `list_workflows(args)`: List all workflows.
- `delete_workflow(args)`: Delete a workflow.

#### Example

```python
from src.automata.cli import CLI
from src.automata.cli.commands import WorkflowCommands

# Create a CLI instance
cli = CLI()

# Create workflow commands
workflow_commands = WorkflowCommands(cli)

# Register the commands
workflow_commands.register_commands()

# Run the CLI
cli.run()
```

### TemplateCommands

The `TemplateCommands` class provides commands for managing workflow templates.

#### Methods

- `__init__(cli)`: Initialize the template commands with a CLI instance.
- `register_commands()`: Register all template commands with the CLI.
- `create_template(args)`: Create a new template.
- `use_template(args)`: Use a template to create a workflow.
- `list_templates(args)`: List all templates.
- `search_templates(args)`: Search for templates.
- `update_template(args)`: Update a template.
- `delete_template(args)`: Delete a template.

#### Example

```python
from src.automata.cli import CLI
from src.automata.cli.commands import TemplateCommands

# Create a CLI instance
cli = CLI()

# Create template commands
template_commands = TemplateCommands(cli)

# Register the commands
template_commands.register_commands()

# Run the CLI
cli.run()
```

### HelperCommands

The `HelperCommands` class provides commands for helper tools.

#### Methods

- `__init__(cli)`: Initialize the helper commands with a CLI instance.
- `register_commands()`: Register all helper commands with the CLI.
- `parse_html(args)`: Parse an HTML file.
- `generate_selectors(args)`: Generate selectors from an HTML file.
- `build_action(args)`: Build an action.
- `read_file(args)`: Read a file.
- `write_file(args)`: Write to a file.

#### Example

```python
from src.automata.cli import CLI
from src.automata.cli.commands import HelperCommands

# Create a CLI instance
cli = CLI()

# Create helper commands
helper_commands = HelperCommands(cli)

# Register the commands
helper_commands.register_commands()

# Run the CLI
cli.run()
```

## Examples

### Example 1: Simple Web Scraping

```python
from src.automata.core import AutomationEngine
from src.automata.workflow import WorkflowBuilder, WorkflowExecutor

# Create an automation engine instance
engine = AutomationEngine()
engine.start()

# Create a workflow builder instance
builder = WorkflowBuilder()

# Build a workflow
workflow = builder.build_workflow(
    name="Web Scraping",
    version="1.0.0",
    description="Scrape data from a web page",
    variables={
        "url": "https://example.com",
        "output_file": "data.json"
    },
    steps=[
        {
            "name": "Navigate to page",
            "action": "navigate",
            "value": "{{url}}"
        },
        {
            "name": "Wait for content to load",
            "action": "wait_for",
            "selector": ".content",
            "timeout": 10
        },
        {
            "name": "Extract data",
            "action": "extract",
            "selector": ".item",
            "value": {
                "title": ".title",
                "description": ".description"
            }
        },
        {
            "name": "Save results",
            "action": "save",
            "value": "{{output_file}}"
        }
    ]
)

# Create a workflow executor instance
executor = WorkflowExecutor(engine)

# Execute the workflow
results = executor.execute_workflow(workflow)

# Stop the engine
engine.stop()
```

### Example 2: Form Submission

```python
from src.automata.core import AutomationEngine
from src.automata.auth import AuthManager
from src.automata.workflow import WorkflowBuilder, WorkflowExecutor

# Create an automation engine instance
engine = AutomationEngine()
engine.start()

# Create an auth manager instance
auth_manager = AuthManager(engine)

# Log in
auth_manager.login({
    "username": "myuser",
    "password": "mypass"
}, method="form")

# Create a workflow builder instance
builder = WorkflowBuilder()

# Build a workflow
workflow = builder.build_workflow(
    name="Form Submission",
    version="1.0.0",
    description="Fill out and submit a form",
    variables={
        "form_url": "https://example.com/form",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "message": "This is a test message."
    },
    steps=[
        {
            "name": "Navigate to form",
            "action": "navigate",
            "value": "{{form_url}}"
        },
        {
            "name": "Wait for form to load",
            "action": "wait_for",
            "selector": "#form",
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
            "selector": ".confirmation",
            "timeout": 10
        }
    ]
)

# Create a workflow executor instance
executor = WorkflowExecutor(engine)

# Execute the workflow
results = executor.execute_workflow(workflow)

# Log out
auth_manager.logout()

# Stop the engine
engine.stop()
```

### Example 3: Custom Authentication Provider

```python
from src.automata.core import AutomationEngine
from src.automata.auth import AuthManager, AuthProvider

class CustomAuthProvider(AuthProvider):
    def __init__(self, engine):
        super().__init__(engine)
        self.name = "custom"

    def login(self, credentials):
        # Navigate to login page
        self.engine.execute_action({
            "name": "Navigate to login page",
            "action": "navigate",
            "value": "https://example.com/login"
        })

        # Enter custom credentials
        self.engine.execute_action({
            "name": "Enter custom ID",
            "action": "type",
            "selector": "#custom-id",
            "value": credentials["custom_id"]
        })

        # Enter password
        self.engine.execute_action({
            "name": "Enter password",
            "action": "type",
            "selector": "#password",
            "value": credentials["password"]
        })

        # Submit form
        self.engine.execute_action({
            "name": "Submit form",
            "action": "click",
            "selector": "#login-button"
        })

        # Wait for login to complete
        self.engine.execute_action({
            "name": "Wait for login to complete",
            "action": "wait_for",
            "selector": ".user-dashboard",
            "timeout": 10
        })

    def logout(self):
        # Click logout button
        self.engine.execute_action({
            "name": "Click logout button",
            "action": "click",
            "selector": "#logout-button"
        })

        # Wait for logout to complete
        self.engine.execute_action({
            "name": "Wait for logout to complete",
            "action": "wait_for",
            "selector": "#login-form",
            "timeout": 10
        })

    def is_logged_in(self):
        # Check if user dashboard is visible
        return self.engine.execute_action({
            "name": "Check if user dashboard is visible",
            "action": "evaluate",
            "value": "document.querySelector('.user-dashboard') !== null"
        })

    def get_name(self):
        return self.name

# Create an automation engine instance
engine = AutomationEngine()
engine.start()

# Create an auth manager instance
auth_manager = AuthManager(engine)

# Register the custom auth provider
auth_manager.register_auth_provider("custom", CustomAuthProvider(engine))

# Log in using the custom auth provider
auth_manager.login({
    "custom_id": "mycustomid",
    "password": "mypass"
}, method="custom")

# Check if logged in
is_logged_in = auth_manager.is_logged_in()

# Log out
auth_manager.logout()

# Stop the engine
engine.stop()
```

### Example 4: Conditional Workflow

```python
from src.automata.core import AutomationEngine
from src.automata.workflow import WorkflowBuilder, WorkflowExecutor

# Create an automation engine instance
engine = AutomationEngine()
engine.start()

# Create a workflow builder instance
builder = WorkflowBuilder()

# Build a workflow
workflow = builder.build_workflow(
    name="Conditional Workflow",
    "version": "1.0.0",
    description="A workflow with conditional logic",
    variables={
        "url": "https://example.com",
        "output_file": "data.json"
    },
    steps=[
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
            "name": "Check if premium content is available",
            "action": "evaluate",
            "value": "document.querySelector('.premium-content') !== null"
        },
        {
            "name": "Process based on content availability",
            "action": "if",
            "value": {
                "operator": "equals",
                "left": "{{evaluate}}",
                "right": true
            },
            "steps": [
                {
                    "name": "Extract premium content",
                    "action": "extract",
                    "selector": ".premium-content",
                    "value": {
                        "title": ".title",
                        "content": ".content"
                    }
                },
                {
                    "name": "Set content type",
                    "action": "set_variable",
                    "selector": "content_type",
                    "value": "premium"
                }
            ],
            "else_steps": [
                {
                    "name": "Extract standard content",
                    "action": "extract",
                    "selector": ".standard-content",
                    "value": {
                        "title": ".title",
                        "content": ".content"
                    }
                },
                {
                    "name": "Set content type",
                    "action": "set_variable",
                    "selector": "content_type",
                    "value": "standard"
                }
            ]
        },
        {
            "name": "Create result object",
            "action": "execute_script",
            "value": "result = { content_type: content_type, data: content_type === 'premium' ? extract_premium_content : extract_standard_content }; set_variable('result', result);"
        },
        {
            "name": "Save results",
            "action": "save",
            "value": "{{output_file}}",
            "data": "{{result}}"
        }
    ]
)

# Create a workflow executor instance
executor = WorkflowExecutor(engine)

# Execute the workflow
results = executor.execute_workflow(workflow)

# Stop the engine
engine.stop()
```

### Example 5: Loop-Based Workflow

```python
from src.automata.core import AutomationEngine
from src.automata.workflow import WorkflowBuilder, WorkflowExecutor

# Create an automation engine instance
engine = AutomationEngine()
engine.start()

# Create a workflow builder instance
builder = WorkflowBuilder()

# Build a workflow
workflow = builder.build_workflow(
    name="Loop-Based Workflow",
    "version": "1.0.0",
    description="A workflow with loops",
    variables={
        "base_url": "https://example.com",
        "output_file": "data.json",
        "pages": [1, 2, 3],
        "results": []
    },
    steps=[
        {
            "name": "Initialize results",
            "action": "set_variable",
            "selector": "results",
            "value": []
        },
        {
            "name": "Loop through pages",
            "action": "loop",
            "value": {
                "type": "for_each",
                "items": "{{pages}}",
                "variable": "page",
                "steps": [
                    {
                        "name": "Navigate to page",
                        "action": "navigate",
                        "value": "{{base_url}}?page={{page}}"
                    },
                    {
                        "name": "Wait for content to load",
                        "action": "wait_for",
                        "selector": ".content",
                        "timeout": 10
                    },
                    {
                        "name": "Extract data",
                        "action": "extract",
                        "selector": ".item",
                        "value": {
                            "title": ".title",
                            "description": ".description"
                        }
                    },
                    {
                        "name": "Add to results",
                        "action": "execute_script",
                        "value": "results = results + extract_data; set_variable('results', results);"
                    }
                ]
            }
        },
        {
            "name": "Save results",
            "action": "save",
            "value": "{{output_file}}",
            "data": "{{results}}"
        }
    ]
)

# Create a workflow executor instance
executor = WorkflowExecutor(engine)

# Execute the workflow
results = executor.execute_workflow(workflow)

# Stop the engine
engine.stop()
```

This concludes the API documentation for Automata. For more information on using Automata, refer to the user guide and workflow examples.
