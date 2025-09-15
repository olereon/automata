# Automata Product Requirements Document (PRD)

## Table of Contents
1. [Overview](#overview)
2. [Key Features & Functionality](#key-features--functionality)
3. [User Roles & Personas](#user-roles--personas)
4. [Technical Architecture](#technical-architecture)
5. [User Flows and Experience](#user-flows-and-experience)
6. [Approximate Quality Level](#approximate-quality-level)
7. [Pain Points & Limitations](#pain-points--limitations)
8. [Future Considerations](#future-considerations)

## 1. Overview

Automata is a powerful web automation tool designed to simplify and streamline interactions with websites. It enables users to automate repetitive web tasks, extract data from web pages, fill out forms, and perform various other web-based operations programmatically. Built with Python and leveraging Playwright for browser automation, Automata provides a flexible and extensible framework for both simple and complex automation workflows.

### Primary Purpose

The primary purpose of Automata is to provide users with a comprehensive solution for web automation that is accessible to both technical and non-technical users. By offering a combination of CLI tools, workflow templates, and helper utilities, Automata aims to reduce the complexity of web automation while maintaining the flexibility needed for advanced use cases.

## 2. Key Features & Functionality

### Core Automation Engine
- **Browser Management**: Full control over Chromium browser instances, including launching, configuring, and managing browser sessions.
- **Element Selection**: Robust element selection strategies with fallback mechanisms, supporting CSS selectors, XPath, and text-based selection.
- **Wait Management**: Comprehensive wait utilities for handling dynamic content, including explicit waits and conditional waits.
- **Error Handling**: Sophisticated error handling and recovery mechanisms, including retry logic and error logging.
- **Session Management**: Persistent session handling, including cookies, localStorage, and sessionStorage management.
- **WebSocket Compatibility**: Resolved MCP server WebSocket handler parameter mismatch issue with websockets library version 15.0.1 and higher.

### Authentication System
- **Multiple Authentication Methods**: Support for form-based login, OAuth, cookie-based authentication, and custom authentication providers.
- **Environment Variable Authentication**: Secure credential management using environment variables.
- **Credential File Authentication**: Support for storing credentials in encrypted files.
- **Interactive Login**: Manual intervention for complex authentication scenarios.
- **Session Persistence**: Save and restore browser sessions for seamless authentication across workflow runs.

### Helper Tools
- **HTML/XPath Parser**: Extract element information from HTML files and web pages.
- **Selector Generator**: Convert HTML elements to robust CSS selectors with optimization for reliability.
- **Action Builder**: Create interaction commands with a simple, intuitive interface.
- **File I/O Utilities**: Read and write data in various formats (JSON, CSV, XML, text, binary).
- **Variable Management**: Store and use dynamic values throughout workflows.
- **Conditional Logic**: Implement IF/ELSE statements for decision-making in workflows.
- **Loop Processor**: Handle repetitive tasks with various loop types (for, while, for_each).

### Workflow System
- **JSON Schema**: Well-defined schema for automation workflow definitions.
- **Workflow Builder**: Interactive CLI tool for creating and modifying workflows.
- **Workflow Validation**: Comprehensive error checking and validation of workflow definitions.
- **Workflow Templates**: Reusable workflow templates for common automation scenarios.
- **Workflow Execution**: Powerful execution engine with support for variables, conditions, and loops.

### CLI Interface
- **Command Structure**: Well-organized CLI structure using the Click framework.
- **Workflow Commands**: Commands for executing, managing, and debugging workflows.
- **Template Commands**: Commands for managing workflow templates.
- **Helper Commands**: Commands for using helper tools.
- **Configuration Management**: Support for environment variables and configuration files.
- **Progress Reporting**: Real-time progress updates during workflow execution.
- **Help System**: Comprehensive help documentation for all commands.

### Testing and Quality Assurance
- **Unit Tests**: Comprehensive unit tests for core engine components.
- **Integration Tests**: Tests for helper tools and their interactions.
- **End-to-End Tests**: Complete workflow execution tests.
- **Test Coverage**: Detailed coverage reporting with pytest markers.
- **Test Fixtures**: Mock data and fixtures for consistent testing.

## 3. User Roles & Personas

### 1. Developer/Technical User
**Profile**: Software developer with programming experience, comfortable with CLI tools and JSON configuration.
**Needs**: 
- Fine-grained control over automation workflows
- Integration with existing development workflows
- Extensibility for custom automation scenarios
**Usage Patterns**:
- Creates complex workflows with custom logic
- Integrates Automata with other tools and systems
- Contributes to the project by developing custom plugins and extensions

### 2. QA Engineer/Tester
**Profile**: Quality assurance professional focused on testing web applications.
**Needs**:
- Automated testing of web applications
- Form validation testing
- Regression testing
**Usage Patterns**:
- Creates test workflows for web applications
- Uses Automata for form validation and link checking
- Implements performance testing scenarios

### 3. Data Analyst/Researcher
**Profile**: Professional who needs to extract data from websites for analysis.
**Needs**:
- Web scraping capabilities
- Data extraction from complex web pages
- Handling of pagination and dynamic content
**Usage Patterns**:
- Creates workflows for scraping data from multiple pages
- Extracts structured data from unstructured web content
- Automates data collection processes

### 4. Business User/Non-Technical User
**Profile**: Business professional with limited technical expertise.
**Needs**:
- Automation of repetitive web tasks
- Simple form filling and data entry
- Pre-built templates for common scenarios
**Usage Patterns**:
- Uses pre-built workflow templates for common tasks
- Relies on the interactive workflow builder
- Focuses on high-level automation goals rather than technical details

## 4. Technical Architecture

### High-Level Structure
Automata follows a layered architecture with clear separation of concerns:

1. **Core Engine Layer**: Provides the fundamental automation capabilities using Playwright.
2. **Authentication Layer**: Handles various authentication methods and session management.
3. **Helper Tools Layer**: Offers utilities for parsing HTML, generating selectors, and building actions.
4. **Workflow Layer**: Manages workflow creation, validation, and execution.
5. **CLI Layer**: Provides the command-line interface for interacting with all components.

### Major Components
- **AutomationEngine**: Central orchestrator that coordinates all other components.
- **BrowserManager**: Manages browser instances and provides browser control methods.
- **SessionManager**: Handles browser sessions, including cookies and storage.
- **ElementSelector**: Provides methods for selecting elements on web pages.
- **WaitManager**: Offers utilities for waiting for various conditions.
- **ErrorHandler**: Implements error handling and recovery mechanisms.
- **AuthManager**: Manages authentication methods and session persistence.
- **HtmlParser**: Parses HTML files and extracts element information.
- **SelectorGenerator**: Generates robust CSS selectors from HTML elements.
- **ActionBuilder**: Builds action definitions for various interactions.
- **FileIO**: Handles reading and writing files in various formats.
- **WorkflowBuilder**: Creates and manages workflow definitions.
- **WorkflowValidator**: Validates workflow definitions.
- **WorkflowExecutor**: Executes workflow definitions.
- **CLI**: Provides the command-line interface.

### Technologies Used (Tech Stack)
- **Python 3.11**: Primary programming language.
- **Playwright**: Browser automation library.
- **Click**: Command-line interface framework.
- **pytest**: Testing framework.
- **Black**: Code formatter.
- **flake8**: Code linter.
- **JSON**: Configuration and workflow definition format.
- **Asyncio**: Asynchronous programming support.

## 5. User Flows and Experience

### CLI Use

#### 1. Installation and Setup
1. User clones the repository.
2. User runs `make setup` to install dependencies and Playwright browsers.
3. User verifies installation by running `automata --version`.

#### 2. Creating a Workflow
1. User runs `automata workflow create` to start the interactive workflow builder.
2. User provides workflow details (name, version, description).
3. User adds variables to the workflow.
4. User adds steps to the workflow, defining actions for each step.
5. User saves the workflow to a JSON file.

#### 3. Executing a Workflow
1. User runs `automata workflow execute my_workflow.json`.
2. Automata starts the browser and executes the workflow steps.
3. User sees progress updates as the workflow executes.
4. User receives a completion message with any results or errors.

#### 4. Using Helper Tools
1. User runs `automata helper parse-html page.html` to parse an HTML file.
2. User runs `automata helper generate-selectors page.html` to generate selectors.
3. User runs `automata helper build-action` to create an action definition.

#### 5. Managing Templates
1. User runs `automata template list` to see available templates.
2. User runs `automata template use login` to use a login template.
3. User provides values for template variables.
4. User saves the resulting workflow.

### Core User Journeys

#### 1. Web Scraping Journey
1. User identifies a website with data to scrape.
2. User navigates to the website and saves the HTML.
3. User uses the HTML parser to understand the page structure.
4. User uses the selector generator to create selectors for target elements.
5. User creates a workflow with steps to navigate to the page and extract data.
6. User executes the workflow and saves the extracted data.

#### 2. Form Submission Journey
1. User identifies a form to fill out and submit.
2. User creates a workflow with variables for form data.
3. User adds steps to navigate to the form, fill out fields, and submit.
4. User adds error handling and confirmation checks.
5. User executes the workflow and verifies successful submission.

#### 3. Authentication Journey
1. User identifies a website requiring authentication.
2. User creates a workflow with login steps.
3. User configures authentication method (form-based, OAuth, etc.).
4. User adds steps to verify successful login.
5. User saves the session for future use.
6. User executes the workflow and confirms session persistence.

#### 4. Testing Journey
1. User identifies test scenarios for a web application.
2. User creates workflows for each test scenario.
3. User adds validation steps to verify expected results.
4. User executes the workflows as part of a test suite.
5. User reviews test results and identifies any issues.

## 6. Approximate Quality Level

### Codebase Size and Quality
The Automata codebase is of a normal size for a project of this scope, with approximately 48 completed tasks covering all major functionality areas. The code is well-organized with clear separation of concerns, following established design patterns and best practices.

### Code Quality Indicators
- **Code Formatting**: Consistent formatting using Black with 100-character line length.
- **Code Style**: Adherence to flake8 standards with specified ignores (E203, W503, E722).
- **Documentation**: Comprehensive documentation including user guides, API documentation, and troubleshooting guides.
- **Testing**: Extensive test coverage with unit tests, integration tests, and end-to-end tests.
- **Error Handling**: Robust error handling throughout the codebase with appropriate logging and recovery mechanisms.

### Non-Crucial Parts
- **Minor Tests**: Some edge cases and error conditions may have limited test coverage.
- **Documentation Examples**: While comprehensive, some advanced use cases could benefit from additional examples.
- **Performance Optimization**: The codebase is functional but not optimized for maximum performance in all scenarios.

### Overall Assessment
The codebase is of high quality with a good balance between functionality, maintainability, and extensibility. It follows established software engineering practices and includes comprehensive documentation and testing. The code is lean and focused, with minimal bloat or unnecessary complexity.

## 7. Pain Points & Limitations

### Current Limitations
1. **Browser Support**: Currently limited to Chromium browser, with no support for Firefox or WebKit.
2. **Visual Interface**: No graphical user interface, which may limit accessibility for non-technical users.
3. **CAPTCHA Handling**: No built-in support for solving CAPTCHAs, which are common on many websites.
4. **Mobile Support**: No support for mobile device emulation or mobile-specific automation.
5. **Parallel Execution**: Limited support for parallel execution of workflows, which could impact performance for large-scale automation.
6. **Cloud Integration**: No built-in integration with cloud services for distributed execution or storage.

### Known Issues
1. **Dynamic Content**: Some complex dynamic content scenarios may require additional wait strategies.
2. **Element Detection**: In some cases, element detection may fail due to timing issues or complex page structures.
3. **Session Persistence**: Session persistence may not work correctly with all websites, especially those with additional security measures.
4. **Error Recovery**: While error handling is robust, some complex error scenarios may not be handled gracefully.
5. **Resource Usage**: Long-running workflows may consume significant memory and CPU resources.

### Areas for Improvement
1. **Performance**: Optimization of resource usage and execution speed.
2. **Usability**: Enhanced user interface and workflow visualization.
3. **Extensibility**: Improved plugin system for third-party extensions.
4. **Documentation**: Additional examples and use case documentation.
5. **Testing**: Expanded test coverage for edge cases and error conditions.

## 8. Future Considerations

### Visualizer Tool
A visual workflow editor would significantly improve the user experience, especially for non-technical users. This would involve:
- Designing a visual representation of workflows
- Creating a drag-and-drop interface for building workflows
- Implementing real-time visualization of workflow execution

### Advanced Selector Strategies
Enhanced element detection capabilities would improve reliability and reduce maintenance:
- AI-assisted element detection using machine learning
- Computer vision for element recognition
- Adaptive selectors that can handle page structure changes

### Plugin System
A robust plugin architecture would enable third-party extensions:
- Plugin discovery and installation mechanism
- API for plugin development
- Security model for plugin execution

### Performance Optimization
Improvements to execution speed and resource usage:
- Parallel execution of independent workflow steps
- Resource pooling and reuse
- Optimized wait strategies and element detection

### Cloud Integration
Support for distributed execution and cloud storage:
- Cloud-based workflow execution
- Integration with cloud storage services
- Scalable architecture for large-scale automation

### Mobile Support
Expansion to mobile device automation:
- Mobile device emulation
- Mobile-specific element selection strategies
- Mobile app automation capabilities

### Enhanced Authentication
Additional authentication methods and security features:
- Biometric authentication support
- Multi-factor authentication automation
- Enhanced security for credential storage

### WebSocket Compatibility Fix
A critical fix has been implemented to resolve WebSocket handler parameter compatibility issues with the websockets library version 15.0.1 and higher:

- **Issue**: The MCP server implementation was affected by a breaking change in the websockets library that changed the handler signature from `handler(websocket, path)` to `handler(websocket)`, causing a `TypeError` when establishing WebSocket connections.
- **Resolution**:
  - Fixed WebSocket handler parameter signature in the MCP server
  - Updated dependency version constraints to prevent incompatible versions
  - Enhanced error handling and logging for better debugging
  - Created comprehensive documentation for the fix
- **Impact**: This fix ensures reliable WebSocket communication between the MCP client and server, which is essential for the proper functioning of the MCP Bridge extension and browser automation tools.

These future enhancements would build upon the solid foundation established in the MVP, extending Automata's capabilities and addressing current limitations while maintaining its core strengths of flexibility, extensibility, and ease of use.
