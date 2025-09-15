# Troubleshooting Guide and FAQ

## Table of Contents
- [Introduction](#introduction)
- [Common Issues](#common-issues)
  - [Installation and Setup Issues](#installation-and-setup-issues)
  - [Browser Issues](#browser-issues)
  - [Workflow Issues](#workflow-issues)
  - [Authentication Issues](#authentication-issues)
  - [Performance Issues](#performance-issues)
- [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
  - [General Questions](#general-questions)
  - [Technical Questions](#technical-questions)
  - [Workflow Questions](#workflow-questions)
  - [Browser Questions](#browser-questions)
  - [Authentication Questions](#authentication-questions)
- [Debugging Tips](#debugging-tips)
- [Getting Help](#getting-help)

## Introduction

This document provides a troubleshooting guide and frequently asked questions (FAQ) for Automata. If you're experiencing issues with Automata, this guide should help you identify and resolve them.

If you can't find a solution to your problem here, please refer to the "Getting Help" section at the end of this document.

## Common Issues

### Installation and Setup Issues

#### Issue: Python version not compatible

**Problem**: Automata requires Python 3.11, but you have a different version installed.

**Solution**: 
1. Check your Python version by running `python3.11 --version`.
2. If Python 3.11 is not installed, install it using your system's package manager or from the official Python website.
3. Make sure you're using Python 3.11 when running Automata commands.

#### Issue: Dependencies not installing correctly

**Problem**: When running `make setup`, some dependencies fail to install.

**Solution**:
1. Make sure you have the latest version of pip: `python3.11 -m pip install --upgrade pip`.
2. Try installing the dependencies manually: `python3.11 -m pip install -r requirements.txt`.
3. If you're still having issues, try creating a new virtual environment and installing the dependencies there.

#### Issue: WebSocket handler parameter mismatch error

**Problem**: When starting the MCP server, you encounter an error about WebSocket handler parameter mismatch, such as:
```
TypeError: websocket_handler() takes 2 positional arguments but 3 were given
```

**Solution**:
This error is caused by a breaking change in the websockets library v15.0.1, which changed the handler signature from `handler(websocket, path)` to `handler(websocket)`.

1. Check your websockets library version: `python3.11 -m pip show websockets`
2. If you have version 15.0.1 or higher, downgrade to a compatible version: `python3.11 -m pip install "websockets>=10.0,<15.0"`
3. The requirements.txt file has been updated to pin the websockets library version to prevent this issue
4. If you need to use a newer version of the websockets library, you'll need to update the WebSocket handler code in `src/automata/mcp_server/server.py` to remove the path parameter

For more details, see the comments in the WebSocket handler code in `src/automata/mcp_server/server.py` and the following documentation:
- [WebSocket Issue Resolution](../playwright_mcp_websocket_issue_resolution.md)
- [WebSocket Compatibility Guide](docs/websocket_compatibility_guide.md)
- [WebSocket Fix Summary](../websocket_fix_summary.md)

#### Issue: Playwright browsers not installing

**Problem**: When running `python3.11 -m playwright install`, the browsers fail to install.

**Solution**:
1. Make sure you have enough disk space for the browsers.
2. Try installing the browsers manually: `python3.11 -m playwright install chromium`.
3. If you're behind a proxy, configure the proxy settings: `export HTTP_PROXY=http://your-proxy:port` and `export HTTPS_PROXY=http://your-proxy:port`.

### Browser Issues

#### Issue: Browser not starting

**Problem**: When trying to start the browser, nothing happens or you get an error.

**Solution**:
1. Make sure Playwright browsers are installed: `python3.11 -m playwright install`.
2. Check if there are any conflicting browser processes running and close them.
3. Try running Automata with debug logging: `automata --log-level debug workflow execute my_workflow.json`.
4. If you're using a custom browser path, make sure it's correct.

#### Issue: Elements not found

**Problem**: Automata can't find elements on the page, even though they exist.

**Solution**:
1. Make sure the page has fully loaded before trying to interact with elements.
2. Use explicit waits: `wait_for_element_visible` instead of just `select_element`.
3. Check if the element is inside an iframe. If so, you need to switch to the iframe first.
4. Try using different selectors. CSS selectors are generally faster, but XPath selectors can be more flexible.
5. Use the helper tools to generate robust selectors: `automata helper generate-selectors page.html`.

#### Issue: Timeouts

**Problem**: Actions are timing out before they can complete.

**Solution**:
1. Increase the timeout value for the specific action.
2. Check if your internet connection is slow or unstable.
3. Make sure the page is not waiting for additional resources to load.
4. Use explicit waits instead of fixed timeouts where possible.

### Workflow Issues

#### Issue: Workflow validation fails

**Problem**: When trying to execute a workflow, validation fails with errors.

**Solution**:
1. Check the error messages to identify what's wrong with the workflow.
2. Make sure all required fields are present and correctly formatted.
3. Use the workflow validator to get detailed error information: `automata workflow validate my_workflow.json`.
4. Refer to the workflow schema documentation to ensure your workflow is correctly structured.

#### Issue: Workflow execution stops unexpectedly

**Problem**: Workflow execution stops in the middle without any clear error message.

**Solution**:
1. Run the workflow with debug logging: `automata --log-level debug workflow execute my_workflow.json`.
2. Check if there are any unhandled exceptions in your workflow.
3. Make sure error handling is properly configured for each action.
4. Try executing the workflow step by step to identify where it fails.

#### Issue: Variables not working correctly

**Problem**: Variables in your workflow are not being substituted correctly.

**Solution**:
1. Make sure variables are defined at the workflow level or in previous steps.
2. Check that variable names are spelled correctly in your workflow.
3. Use the correct syntax for variable substitution: `{{variable_name}}`.
4. Make sure variable values are of the correct type for the action you're using.

### Authentication Issues

#### Issue: Login fails

**Problem**: Authentication fails even with correct credentials.

**Solution**:
1. Make sure you're using the correct authentication method for the website.
2. Check if the website has any anti-automation measures in place.
3. Try adding delays between actions to simulate human behavior.
4. Make sure all required fields are filled in correctly.
5. Check if there are any CAPTCHAs or other challenges that need to be solved.

#### Issue: Session not persisting

**Problem**: After logging in, the session is not maintained between actions.

**Solution**:
1. Make sure cookies are enabled in the browser.
2. Try saving and restoring the session manually.
3. Check if the website uses any additional authentication mechanisms (e.g., CSRF tokens).
4. Make sure you're not clearing cookies or browsing data between actions.

### Performance Issues

#### Issue: Workflows running slowly

**Problem**: Your workflows are taking longer than expected to complete.

**Solution**:
1. Reduce unnecessary waits and delays in your workflow.
2. Use more specific selectors to speed up element selection.
3. Minimize the number of actions in your workflow.
4. Consider using parallel execution for independent actions.
5. Disable unnecessary browser features (e.g., images, JavaScript) if they're not needed.

#### Issue: High memory usage

**Problem**: Automata is using a lot of memory, especially when running long workflows.

**Solution**:
1. Make sure you're properly closing pages and tabs when they're no longer needed.
2. Avoid storing large amounts of data in variables.
3. Periodically clear the browser cache and cookies if they're not needed.
4. Consider breaking long workflows into smaller, separate workflows.

## Frequently Asked Questions (FAQ)

### General Questions

#### Q: What is Automata?

**A**: Automata is a powerful web automation tool that allows you to automate interactions with websites, extract data, fill out forms, and perform other web-based tasks programmatically.

#### Q: What are the system requirements for Automata?

**A**: Automata requires Python 3.11 or higher, and it supports Windows, macOS, and Linux. You'll also need enough disk space for the browser dependencies (approximately 300-500MB).

#### Q: Is Automata free to use?

**A**: Yes, Automata is open-source and free to use under the MIT license.

#### Q: Can I use Automata for commercial projects?

**A**: Yes, you can use Automata for both personal and commercial projects.

### Technical Questions

#### Q: How do I install Automata?

**A**: You can install Automata by cloning the repository and running the setup command:
```bash
git clone https://github.com/your-username/automata.git
cd automata
make setup
```

#### Q: How do I update Automata to the latest version?

**A**: You can update Automata by pulling the latest changes from the repository and running the setup command again:
```bash
git pull origin main
make setup
```

#### Q: What programming languages does Automata support?

**A**: Automata is built with Python, and workflows are defined in JSON format. You can also execute JavaScript code within your workflows using the `execute_script` action.

#### Q: Can I use Automata with other browsers besides Chromium?

**A**: Currently, Automata primarily supports Chromium, but it can be extended to support other browsers like Firefox and WebKit by modifying the browser manager.

### Workflow Questions

#### Q: How do I create a workflow?

**A**: You can create a workflow using the workflow builder CLI tool:
```bash
automata workflow create
```
This will start an interactive session where you can define your workflow.

#### Q: Can I reuse parts of my workflows in other workflows?

**A**: Yes, you can create workflow templates for common tasks and reuse them in multiple workflows. Use the `template` commands to manage your templates.

#### Q: How do I debug a workflow that's not working correctly?

**A**: You can debug a workflow by running it with debug logging:
```bash
automata --log-level debug workflow execute my_workflow.json
```
You can also use the `pause` and `resume` actions to step through your workflow.

#### Q: Can I run multiple workflows in parallel?

**A**: Yes, you can run multiple workflows in parallel by running multiple instances of Automata. However, be aware that this may increase resource usage.

### Browser Questions

#### Q: How do I configure Automata to use a proxy?

**A**: You can configure a proxy by setting the HTTP_PROXY and HTTPS_PROXY environment variables:
```bash
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

#### Q: Can I run Automata in headless mode?

**A**: Yes, you can run Automata in headless mode by setting the `headless` option to true in your configuration or by using the `--headless` command-line flag.

#### Q: How do I handle CAPTCHAs with Automata?

**A**: Automata doesn't have built-in CAPTCHA solving capabilities. However, you can integrate third-party CAPTCHA solving services or use manual intervention for CAPTCHAs.

#### Q: Can I Automata interact with iframes?

**A**: Yes, Automata can interact with iframes. You need to switch to the iframe first using the `switch_to_frame` action, interact with elements inside the iframe, and then switch back to the main frame.

### Authentication Questions

#### Q: What authentication methods does Automata support?

**A**: Automata supports various authentication methods, including form-based login, OAuth, cookie-based authentication, and custom authentication providers.

#### Q: How do I save and restore login sessions?

**A**: You can save and restore login sessions using the session management features:
```json
{
  "name": "Save session",
  "action": "save_session",
  "value": "session.json"
}
```
And later:
```json
{
  "name": "Restore session",
  "action": "load_session",
  "value": "session.json"
}
```

#### Q: Can I use Automata with websites that require two-factor authentication?

**A**: Yes, you can use Automata with websites that require two-factor authentication. You'll need to handle the second factor manually or integrate with a 2FA service.

#### Q: How do I handle CSRF tokens in forms?

**A**: You can handle CSRF tokens by extracting the token from the form and including it in your submission. Use the `get_attribute` action to extract the token value.

## Debugging Tips

### Enable Debug Logging

When you're having trouble with a workflow, enable debug logging to get more detailed information about what's happening:

```bash
automata --log-level debug workflow execute my_workflow.json
```

### Take Screenshots

If your workflow is failing at a certain point, take screenshots to see what the browser is displaying:

```json
{
  "name": "Take screenshot",
  "action": "screenshot",
  "value": "debug_screenshot.png"
}
```

### Save Page Source

Save the HTML source of the page when debugging issues:

```json
{
  "name": "Save page source",
  "action": "save_page_source",
  "value": "debug_page.html"
}
```

### Use the Helper Tools

Use the helper tools to understand the structure of the page and generate robust selectors:

```bash
automata helper parse-html page.html
automata helper generate-selectors page.html
```

### Step Through Your Workflow

Add `pause` actions to your workflow to step through it interactively:

```json
{
  "name": "Pause for debugging",
  "action": "pause"
}
```

### Check Element Visibility

Make sure elements are visible and interactable before trying to interact with them:

```json
{
  "name": "Check if button is visible",
  "action": "wait_for_element_visible",
  "selector": "#submit-button",
  "timeout": 10
}
```

### Handle Errors Gracefully

Add error handling to your actions to capture and handle errors:

```json
{
  "name": "Click button with error handling",
  "action": "click",
  "selector": "#submit-button",
  "on_error": "continue"
}
```

### Test Selectors Manually

Test your selectors manually using the browser's developer tools before using them in your workflow.

### Use Explicit Waits

Use explicit waits instead of fixed delays where possible:

```json
{
  "name": "Wait for content to load",
  "action": "wait_for",
  "selector": ".content",
  "timeout": 10
}
```

Instead of:

```json
{
  "name": "Wait for content to load",
  "action": "wait",
  "value": 5
}
```

## Getting Help

If you're still having trouble after trying the solutions in this guide, here are some ways to get help:

### Documentation

Make sure you've checked all the available documentation:
- [User Guide](user_guide.md)
- [Helper Tools Documentation](helper_tools.md)
- [Workflow Examples](workflow_examples.md)
- [API Documentation](api.md)

### Community Support

- Check the [GitHub Issues](https://github.com/your-username/automata/issues) page to see if someone else has had the same problem.
- Search the [GitHub Discussions](https://github.com/your-username/automata/discussions) for answers to common questions.
- Join our community chat (e.g., Discord, Slack) to ask questions and get help from other users.

### Reporting Bugs

If you think you've found a bug in Automata, please report it by creating a new issue on the [GitHub Issues](https://github.com/your-username/automata/issues) page. Make sure to include:

- A clear description of the problem
- Steps to reproduce the issue
- The expected behavior
- The actual behavior
- Any error messages or logs
- Your operating system and Automata version

### Feature Requests

If you have an idea for a new feature or improvement, please create a new issue on the [GitHub Issues](https://github.com/your-username/automata/issues) page and label it as a feature request.

### Contributing

If you'd like to contribute to Automata, please check the [Contributing Guidelines](CONTRIBUTING.md) for information on how to get started.

Remember, the more information you provide when asking for help, the easier it will be for others to assist you!
