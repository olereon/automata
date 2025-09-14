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
- Support for multiple authentication methods
- Workflow-based automation with JSON configuration
- Robust element selection with fallback mechanisms
- Conditional logic and looping capabilities
- Session persistence and cookie management

## Installation

### Prerequisites

- Python 3.11 or higher
- Chromium browser (installed automatically by Playwright)

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
│       └── workflows/       # Workflow management
├── tests/                   # Test files
├── docs/                    # Documentation
├── venv/                    # Virtual environment
├── Makefile                 # Build commands
└── setup.py                 # Package configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
