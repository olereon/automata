"""
Pytest configuration and shared fixtures.
"""

import asyncio
import json
import os
import tempfile
from typing import Dict, Any, List, Optional
import pytest
from playwright.async_api import Browser, BrowserContext, Page
from src.automata.core.browser import BrowserManager
from src.automata.core.wait import WaitUtils
from src.automata.core.selector import ElementSelector
from src.automata.utils.variables import VariableManager
from src.automata.utils.conditional import ConditionalProcessor
from src.automata.utils.loops import LoopProcessor
from src.automata.workflow import (
    WorkflowSchema,
    WorkflowBuilder,
    WorkflowValidator,
    WorkflowTemplateManager,
    WorkflowExecutionEngine
)
from src.automata.tools.selector_generator import SelectorGenerator
from src.automata.tools.action_builder import ActionBuilder
from src.automata.utils.file_io import FileIO


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser():
    """Launch a browser for testing."""
    browser_manager = BrowserManager()
    browser = await browser_manager.launch_browser(headless=True)
    yield browser
    await browser.close()


@pytest.fixture
async def context(browser):
    """Create a browser context for testing."""
    browser_manager = BrowserManager()
    context = await browser_manager.create_context(browser)
    yield context
    await context.close()


@pytest.fixture
async def page(context):
    """Create a page for testing."""
    page = await context.new_page()
    page.set_default_timeout(5000)
    yield page
    await page.close()


@pytest.fixture
def browser_manager():
    """Create a browser manager for testing."""
    return BrowserManager()


@pytest.fixture
def wait_utils():
    """Create a wait utils for testing."""
    return WaitUtils()


@pytest.fixture
def element_selector():
    """Create an element selector for testing."""
    return ElementSelector()


@pytest.fixture
def variable_manager():
    """Create a variable manager for testing."""
    return VariableManager()


@pytest.fixture
def condition_processor(variable_manager):
    """Create a condition processor for testing."""
    return ConditionalProcessor(variable_manager)


@pytest.fixture
def loop_processor(variable_manager, condition_processor):
    """Create a loop processor for testing."""
    return LoopProcessor(variable_manager, condition_processor)


@pytest.fixture
def workflow_schema():
    """Create a workflow schema for testing."""
    return WorkflowSchema()


@pytest.fixture
def workflow_builder():
    """Create a workflow builder for testing."""
    return WorkflowBuilder()


@pytest.fixture
def workflow_validator(workflow_schema):
    """Create a workflow validator for testing."""
    return WorkflowValidator(workflow_schema)


@pytest.fixture
def workflow_template_manager(workflow_schema, workflow_validator):
    """Create a workflow template manager for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield WorkflowTemplateManager(
            templates_dir=temp_dir,
            schema=workflow_schema,
            validator=workflow_validator
        )


@pytest.fixture
def workflow_execution_engine(
    browser_manager,
    wait_utils,
    element_selector,
    variable_manager,
    condition_processor,
    loop_processor,
    workflow_schema,
    workflow_validator
):
    """Create a workflow execution engine for testing."""
    return WorkflowExecutionEngine(
        browser_manager=browser_manager,
        wait_utils=wait_utils,
        element_selector=element_selector,
        variable_manager=variable_manager,
        condition_processor=condition_processor,
        loop_processor=loop_processor,
        schema=workflow_schema,
        validator=workflow_validator
    )


@pytest.fixture
def selector_generator():
    """Create a selector generator for testing."""
    return SelectorGenerator()


@pytest.fixture
def action_builder():
    """Create an action builder for testing."""
    return ActionBuilder()


@pytest.fixture
def file_io():
    """Create a file I/O utility for testing."""
    return FileIO()


@pytest.fixture
def sample_workflow():
    """Create a sample workflow for testing."""
    return {
        "name": "Test Workflow",
        "version": "1.0.0",
        "description": "A test workflow for testing purposes",
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
            },
            {
                "name": "Submit search",
                "action": "click",
                "selector": "#search-button"
            },
            {
                "name": "Wait for results",
                "action": "wait_for",
                "selector": ".results",
                "timeout": 10
            }
        ]
    }


@pytest.fixture
def sample_html_file():
    """Create a sample HTML file for testing."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Test Page</h1>
        <div class="container">
            <form id="search-form">
                <input type="text" id="search" name="search" placeholder="Search...">
                <button type="submit" id="search-button">Search</button>
            </form>
            <div class="results">
                <div class="result-item">
                    <h2 class="title">Result 1</h2>
                    <p class="description">Description 1</p>
                </div>
                <div class="result-item">
                    <h2 class="title">Result 2</h2>
                    <p class="description">Description 2</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        return f.name


@pytest.fixture
def sample_workflow_file(sample_workflow):
    """Create a sample workflow file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_workflow, f, indent=2)
        return f.name


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
