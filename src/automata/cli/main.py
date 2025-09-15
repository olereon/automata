"""
Automata CLI module.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

import click
from click import echo, style

from ..core.browser import BrowserManager
from ..core.engine import AutomationEngine
from ..core.logger import get_logger
from ..core.session_manager import SessionManager
from ..core.selector import ElementSelector
from ..core.wait import WaitUtils
from ..tools.selector_generator import SelectorGenerator
from ..tools.parser import HTMLParser
from ..tools.action_builder import ActionBuilder
from ..tools.browser_explorer import BrowserExplorer
from ..workflow.builder import WorkflowBuilder
from ..workflow.engine import WorkflowExecutionEngine
from ..workflow.validator import WorkflowValidator
from ..mcp.config import MCPConfiguration
from ..mcp.bridge import MCPBridgeConnector, MCPBridgeConnectionError

logger = get_logger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--mcp-bridge', is_flag=True, help='Use MCP Bridge for browser automation')
@click.option('--mcp-config', type=click.Path(), help='Path to MCP configuration file')
@click.pass_context
def cli(ctx, verbose, mcp_bridge, mcp_config):
    """Automata CLI for browser automation and workflow execution."""
    # Set up logging
    if verbose:
        logger.setLevel('DEBUG')
    
    # Set up context
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['mcp_bridge'] = mcp_bridge
    ctx.obj['mcp_config'] = mcp_config


@cli.command()
@click.option('--headless/--visible', default=True, help='Run browser in headless mode (default: headless)')
@click.option('--url', help='URL to navigate to')
@click.pass_context
def test(ctx, headless, url):
    """Test MCP Bridge connection."""
    try:
        # Get MCP configuration
        mcp_config_path = ctx.obj.get('mcp_config')
        
        # Load MCP configuration (from file if specified, otherwise default)
        if mcp_config_path:
            mcp_config = MCPConfiguration()
            mcp_config.load_from_file(mcp_config_path)
        else:
            mcp_config = MCPConfiguration.load_default()
        
        # Initialize browser manager with MCP Bridge
        browser_manager = BrowserManager(
            headless=headless,
            use_mcp_bridge=True,
            mcp_config=mcp_config
        )
        
        # Start browser
        echo(style("Starting MCP Bridge...", fg="blue"))
        asyncio.run(browser_manager.start())
        
        # Navigate to URL if provided
        if url:
            echo(style(f"Navigating to: {url}", fg="blue"))
            asyncio.run(browser_manager.new_page(url))
        
        # Test basic functionality
        echo(style("Testing MCP Bridge functionality...", fg="blue"))
        
        # Get page title
        try:
            title = asyncio.run(browser_manager.get_page_title())
            echo(style(f"Page title: {title}", fg="green"))
        except Exception as e:
            echo(style(f"Failed to get page title: {e}", fg="red"))
        
        # Get page URL
        try:
            page_url = asyncio.run(browser_manager.get_page_url())
            echo(style(f"Page URL: {page_url}", fg="green"))
        except Exception as e:
            echo(style(f"Failed to get page URL: {e}", fg="red"))
        
        # Take snapshot
        try:
            snapshot = asyncio.run(browser_manager.take_snapshot())
            echo(style(f"Took snapshot: {len(str(snapshot))} characters", fg="green"))
        except Exception as e:
            echo(style(f"Failed to take snapshot: {e}", fg="red"))
        
        # Stop browser
        echo(style("Stopping MCP Bridge...", fg="blue"))
        asyncio.run(browser_manager.stop())
        
        echo(style("MCP Bridge test completed successfully!", fg="green"))
        
    except Exception as e:
        echo(style(f"Error testing MCP Bridge: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option('--server-url', default='ws://localhost:8080', help='MCP server URL')
@click.option('--timeout', default=30000, help='Timeout in milliseconds')
@click.option('--retry-attempts', default=3, help='Number of retry attempts')
@click.option('--retry-delay', default=1000, help='Delay between retries in milliseconds')
@click.option('--extension-mode/--no-extension-mode', default=False, help='Enable extension mode')
@click.option('--extension-port', default=9222, help='Extension port')
@click.pass_context
def config(ctx, server_url, timeout, retry_attempts, retry_delay, extension_mode, extension_port):
    """Configure MCP Bridge settings."""
    try:
        # Initialize MCP configuration
        mcp_config = MCPConfiguration()
        
        # Set configuration values
        mcp_config.set_server_url(server_url)
        mcp_config.set_timeout(timeout)
        mcp_config.set_retry_attempts(retry_attempts)
        mcp_config.set_retry_delay(retry_delay)
        mcp_config.set_bridge_extension_mode(extension_mode)
        mcp_config.set_bridge_extension_port(extension_port)
        
        # Save configuration
        config_path = Path.home() / ".automata" / "mcp_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        mcp_config.save_to_file(str(config_path))
        
        echo(style(f"MCP configuration saved to: {config_path}", fg="green"))
        
    except Exception as e:
        echo(style(f"Error configuring MCP Bridge: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option('--headless/--visible', default=True, help='Run browser in headless mode (default: headless)')
@click.option('--url', required=True, help='URL to navigate to')
@click.option('--output', '-o', type=click.Path(), help='Output file for selectors')
@click.pass_context
def generate_selectors(ctx, headless, url, output):
    """Generate CSS selectors for a web page."""
    try:
        # Get MCP configuration if using MCP Bridge
        use_mcp_bridge = ctx.obj.get('mcp_bridge', False)
        mcp_config_path = ctx.obj.get('mcp_config')
        
        if use_mcp_bridge:
            # Load MCP configuration
            mcp_config = MCPConfiguration()
            if mcp_config_path:
                mcp_config.load_from_file(mcp_config_path)
            
            # Configure browser manager for MCP Bridge
            engine.browser_manager.use_mcp_bridge = True
            engine.browser_manager.mcp_config = mcp_config
        
        # Initialize browser manager
        browser_manager = BrowserManager(headless=headless, use_mcp_bridge=use_mcp_bridge)
        
        # Start browser
        echo(style("Starting browser...", fg="blue"))
        asyncio.run(browser_manager.start())
        
        # Navigate to URL
        echo(style(f"Navigating to: {url}", fg="blue"))
        page = asyncio.run(browser_manager.new_page(url))
        
        # Generate selectors
        echo(style("Generating selectors...", fg="blue"))
        selector_generator = SelectorGenerator()
        selectors = asyncio.run(selector_generator.generate_selectors(page))
        
        # Output selectors
        if output:
            with open(output, 'w') as f:
                json.dump(selectors, f, indent=2)
            echo(style(f"Selectors saved to: {output}", fg="green"))
        else:
            echo(json.dumps(selectors, indent=2))
        
        # Stop browser
        echo(style("Stopping browser...", fg="blue"))
        asyncio.run(browser_manager.stop())
        
    except Exception as e:
        echo(style(f"Error generating selectors: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option('--headless/--visible', default=True, help='Run browser in headless mode (default: headless)')
@click.option('--workflow', '-w', required=True, type=click.Path(exists=True), help='Workflow file to execute')
@click.option('--session', '-s', type=click.Path(), help='Session file to load/save')
@click.option('--output', '-o', type=click.Path(), help='Output file for results')
@click.pass_context
def run(ctx, headless, workflow, session, output):
    """Execute a workflow."""
    try:
        # Get MCP configuration if using MCP Bridge
        use_mcp_bridge = ctx.obj.get('mcp_bridge', False)
        mcp_config_path = ctx.obj.get('mcp_config')
        
        if use_mcp_bridge:
            # Load MCP configuration
            mcp_config = MCPConfiguration()
            if mcp_config_path:
                mcp_config.load_from_file(mcp_config_path)
            
            # Configure browser manager for MCP Bridge
            engine.browser_manager.use_mcp_bridge = True
            engine.browser_manager.mcp_config = mcp_config
        
        # Load workflow
        echo(style(f"Loading workflow: {workflow}", fg="blue"))
        with open(workflow, 'r') as f:
            workflow_data = json.load(f)
        
        # Initialize workflow engine
        workflow_engine = WorkflowExecutionEngine(
            headless=headless,
            use_mcp_bridge=use_mcp_bridge
        )
        
        # Load session if specified
        if session and Path(session).exists():
            echo(style(f"Loading session: {session}", fg="blue"))
            with open(session, 'r') as f:
                session_data = json.load(f)
            workflow_engine.load_session(session_data)
        
        # Execute workflow
        echo(style("Executing workflow...", fg="blue"))
        result = asyncio.run(workflow_engine.execute_workflow(workflow_data))
        
        # Save session if specified
        if session:
            echo(style(f"Saving session: {session}", fg="blue"))
            session_data = workflow_engine.save_session()
            with open(session, 'w') as f:
                json.dump(session_data, f, indent=2)
        
        # Output results
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            echo(style(f"Results saved to: {output}", fg="green"))
        else:
            echo(json.dumps(result, indent=2))
        
        # Clean up
        echo(style("Cleaning up...", fg="blue"))
        asyncio.run(workflow_engine.stop())
        
        echo(style("Workflow executed successfully!", fg="green"))
        
    except Exception as e:
        echo(style(f"Error executing workflow: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option('--workflow', '-w', required=True, type=click.Path(exists=True), help='Workflow file to validate')
@click.pass_context
def validate(ctx, workflow):
    """Validate a workflow file."""
    try:
        # Load workflow
        echo(style(f"Loading workflow: {workflow}", fg="blue"))
        with open(workflow, 'r') as f:
            workflow_data = json.load(f)
        
        # Validate workflow
        echo(style("Validating workflow...", fg="blue"))
        validator = WorkflowValidator()
        is_valid, errors = validator.validate(workflow_data)
        
        if is_valid:
            echo(style("Workflow is valid!", fg="green"))
        else:
            echo(style("Workflow validation failed:", fg="red"))
            for error in errors:
                echo(style(f"  - {error}", fg="red"))
            sys.exit(1)
        
    except Exception as e:
        echo(style(f"Error validating workflow: {e}", fg="red"))
        sys.exit(1)


@cli.command()
@click.option('--url', required=True, help='URL to explore')
@click.option('--headless/--visible', default=True, help='Run browser in headless mode (default: headless)')
@click.option('--output', '-o', type=click.Path(), help='Output file for exploration results')
@click.pass_context
def explore(ctx, url, headless, output):
    """Explore a web page and extract information."""
    try:
        # Get MCP configuration if using MCP Bridge
        use_mcp_bridge = ctx.obj.get('mcp_bridge', False)
        mcp_config_path = ctx.obj.get('mcp_config')
        
        if use_mcp_bridge:
            # Load MCP configuration
            mcp_config = MCPConfiguration()
            if mcp_config_path:
                mcp_config.load_from_file(mcp_config_path)
            
            # Configure browser manager for MCP Bridge
            engine.browser_manager.use_mcp_bridge = True
            engine.browser_manager.mcp_config = mcp_config
        
        # Initialize browser manager
        browser_manager = BrowserManager(headless=headless, use_mcp_bridge=use_mcp_bridge)
        
        # Start browser
        echo(style("Starting browser...", fg="blue"))
        asyncio.run(browser_manager.start())
        
        # Navigate to URL
        echo(style(f"Navigating to: {url}", fg="blue"))
        page = asyncio.run(browser_manager.new_page(url))
        
        # Explore page
        echo(style("Exploring page...", fg="blue"))
        explorer = BrowserExplorer()
        exploration_result = asyncio.run(explorer.explore_page(page))
        
        # Output results
        if output:
            with open(output, 'w') as f:
                json.dump(exploration_result, f, indent=2)
            echo(style(f"Exploration results saved to: {output}", fg="green"))
        else:
            echo(json.dumps(exploration_result, indent=2))
        
        # Stop browser
        echo(style("Stopping browser...", fg="blue"))
        asyncio.run(browser_manager.stop())
        
    except Exception as e:
        echo(style(f"Error exploring page: {e}", fg="red"))
        sys.exit(1)


# MCP command group
@cli.group()
def mcp():
    """MCP Bridge commands."""
    pass


@mcp.command()
@click.option('--headless/--visible', default=True, help='Run browser in headless mode (default: headless)')
@click.option('--url', help='URL to navigate to')
@click.option('--test-mode', is_flag=True, help='Test mode - don\'t fail if MCP server is not available')
@click.pass_context
def test(ctx, headless, url, test_mode):
    """Test MCP Bridge connection."""
    try:
        # Get MCP configuration
        mcp_config_path = ctx.obj.get('mcp_config')
        
        # Load MCP configuration (from file if specified, otherwise default)
        if mcp_config_path:
            mcp_config = MCPConfiguration()
            mcp_config.load_from_file(mcp_config_path)
        else:
            mcp_config = MCPConfiguration.load_default()
        
        # Initialize browser manager with MCP Bridge
        browser_manager = BrowserManager(
            headless=headless,
            use_mcp_bridge=True,
            mcp_config=mcp_config
        )
        
        # Set test mode if specified
        if test_mode:
            browser_manager.mcp_bridge_test_mode = True
        
        # Start browser
        echo(style("Starting MCP Bridge...", fg="blue"))
        if test_mode:
            echo(style("Test mode enabled - will continue even if MCP server is not available", fg="yellow"))
        
        try:
            asyncio.run(browser_manager.start())
        except MCPBridgeConnectionError as e:
            if test_mode:
                echo(style(f"MCP Bridge connection failed (expected in test mode): {e}", fg="yellow"))
                echo(style("MCP Bridge test completed in test mode!", fg="green"))
                return
            else:
                raise
        
        # Navigate to URL if provided
        if url:
            echo(style(f"Navigating to: {url}", fg="blue"))
            asyncio.run(browser_manager.new_page(url))
        
        # Test basic functionality
        echo(style("Testing MCP Bridge functionality...", fg="blue"))
        
        # Get page title
        try:
            title = asyncio.run(browser_manager.get_page_title())
            echo(style(f"Page title: {title}", fg="green"))
        except Exception as e:
            echo(style(f"Failed to get page title: {e}", fg="red"))
        
        # Get page URL
        try:
            page_url = asyncio.run(browser_manager.get_page_url())
            echo(style(f"Page URL: {page_url}", fg="green"))
        except Exception as e:
            echo(style(f"Failed to get page URL: {e}", fg="red"))
        
        # Take snapshot
        try:
            snapshot = asyncio.run(browser_manager.take_snapshot())
            echo(style(f"Took snapshot: {len(str(snapshot))} characters", fg="green"))
        except Exception as e:
            echo(style(f"Failed to take snapshot: {e}", fg="red"))
        
        # Stop browser
        echo(style("Stopping MCP Bridge...", fg="blue"))
        asyncio.run(browser_manager.stop())
        
        echo(style("MCP Bridge test completed successfully!", fg="green"))
        
    except Exception as e:
        echo(style(f"Error testing MCP Bridge: {e}", fg="red"))
        sys.exit(1)


# Global engine instance
engine = AutomationEngine()


if __name__ == '__main__':
    cli()
