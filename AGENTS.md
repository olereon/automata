# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Build System
- Uses Makefile with explicit Python 3.11 requirement
- all the Python commands start with python3.11 (NOT python or python3)
- Key commands: `make setup`, `make check`, `make test`, `make test-cov`
- Tests use specific pytest markers - check existing tests for marker conventions

## Code Style
- Black formatter with 100-character line length (not default 88)
- flake8 ignores: E203, W503, E722
- Follow existing patterns for async/await usage with Playwright

## Code Size Guidelines
- Core files for main functionality can reach above 1000 lines of code
- More than 1600 lines should be avoided
- When a file is approaching this threshold, it should be properly refactored and optimized

## Architecture Patterns
- Layered architecture: CLI, GUI, and core engine components
- Plugin architecture for extensibility
- Consistent error handling patterns throughout codebase
- Asynchronous programming with asyncio - follow existing coroutine patterns

## Use of brave-search MCP server for troubleshooting information
- Code and Debug Modes are encouraged to use brave-search MCP server to look online the information and documentation for troubleshooting

## Use of tavily MCP server for research and analysis
- Code and Architect Modes are encouraged to use tavily MCP server to look online for the relevant information needed for research and analysis 

## Use of sequentialthinking MCP for complex planning, problem solving, and debugging
- Code, Debug, and Architect Modes are encouraged to use the sequentialthinking MCP server for complex and extended tasks involing hard issue solving, multi-phased debugging, and elaborate codebase architecture or feature design planning.


## Git commands and tools
- Prefer running `git status` via the `execute_command` tool instead of `git_status`; it is more reliable.

## Creating and editing the file
- Prefer running execute_command tool or another suitable direct tool to create the file. Avoid using write_file tool. 

## Use of todo.md for Modes subtask execution
- Code Mode ALLOWED and ENCOURAGED to create task specific todo list files, with naming schema: {task_name}_todo.md. Or use the dedicated coder_todo.md
- ONLY READ or UPDATE the task status in the tasks.md. Code Mode is PROHIBITED from creating a new tasks.md file if it already exists.
- Modes can create and manage their own TODO file(s) (naming schema: {task_name}_todo.md) to track the execution of their given task with its subtasks. 

## MVP prd and Todo list files location
- mvp prd is located in mvp_prd.md (/home/olereon/workspace/github.com/olereon/0_GLM-RooCode/automata/docs/mvp_prd.md)
- todo list is located in tasks.md (/home/olereon/workspace/github.com/olereon/0_GLM-RooCode/automata/tasks.md)

## Update the tasks.md todo list
- NEVER COMPLETELY REWRITE or CREATE a new tasks.md file if it already exists. ALWAYS USE a separate dedicated todo file for task execution.  
- after successful completion of the task from the todo list, update the list with checked [x] status inside the [ ] for this task.

## Retry in case of Failure in tool or command use
- When encountering a failure in tool or command use, first, carefully review and analyze your previous actions.
  Think hard about a different possible approach to achieve the same goal or use a direct execution_command tool and then try it out. 

## IMPORTANT REMINDER for Modes Orchestration and Task Delegation

- When delegating tasks to other Agent Modes, ALWAYS provide concise, accurate, and sufficient context for them to use during task execution.