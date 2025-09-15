"""
Main CLI entry point for web automation.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from click import echo, style, prompt, confirm

from ..core.logger import get_logger
from ..core.browser import BrowserManager
from ..core.session_manager import SessionManager
from ..workflow import (
    WorkflowBuilder,
    WorkflowValidator,
    WorkflowTemplateManager,
    WorkflowExecutionEngine
)
from ..tools import (
    HTMLParser,
    SelectorGenerator,
    ActionBuilder,
    BrowserExplorer
)

logger = get_logger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', type=click.Path(), help='Path to configuration file')
@click.pass_context
def cli(ctx, verbose, config):
    """
    Web Automation CLI Tool.
    
    This tool provides commands for creating, managing, and executing
    web automation workflows.
    """
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logger = get_logger(level=log_level)
    
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config


@cli.group()
def workflow():
    """Workflow management commands."""
    pass


@workflow.command()
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def create(ctx, output):
    """Create a new workflow interactively."""
    try:
        # Initialize workflow builder
        builder = WorkflowBuilder()
        
        # Create workflow
        workflow = builder.create_workflow()
        
        # Determine output file path
        if not output:
            output = f"{workflow['name'].lower().replace(' ', '_')}.json"
        
        # Save workflow
        builder.save_workflow(output)
        
        echo(style(f"Workflow created and saved to: {output}", fg="green"))
    
    except Exception as e:
        echo(style(f"Error creating workflow: {e}", fg="red"))
        sys.exit(1)


async def _execute_workflow(ctx, file_path, credentials, session, headless, visible, save_session):
    """Execute a workflow from a file asynchronously."""
    try:
        # Initialize workflow builder and execution engine
        builder = WorkflowBuilder()
        engine = WorkflowExecutionEngine()
        
        # Load workflow from file
        workflow = builder.load_workflow(file_path)
        
        # Set up browser manager with headless/visible mode
        actual_headless = headless and not visible
        engine.browser_manager.headless = actual_headless
        
        # Load credentials if provided
        variables = {}
        if credentials:
            from ..auth.credentials_json import CredentialsJSON
            auth = CredentialsJSON()
            creds = auth.load_credentials(credentials)
            variables.update(creds)
        
        # Start browser before restoring session if needed
        if session:
            await engine.browser_manager.start()
            
            from ..core.session_manager import SessionManager
            session_manager = SessionManager()
            session_loaded = await session_manager.load_session(engine.browser_manager, session)
            if not session_loaded:
                echo(style(f"Failed to load session: {session}", fg="red"))
                await engine.browser_manager.stop()
                sys.exit(1)
        
        # Execute workflow, skipping cleanup if we need to save session
        skip_cleanup = save_session is not None
        results = await engine.execute_workflow(workflow, variables, skip_cleanup=skip_cleanup)
        
        # Save session if requested
        if save_session:
            from ..core.session_manager import SessionManager
            session_manager = SessionManager()
            session_path = await session_manager.save_session(
                engine.browser_manager, save_session
            )
            echo(style(f"Session saved to: {session_path}", fg="green"))
            
            # Clean up browser resources after session is saved
            await engine.cleanup_browser()
        else:
            # Clean up browser resources
            await engine.cleanup_browser()
        
        # Print execution results
        echo(style(f"Workflow executed successfully: {workflow['name']}", fg="green"))
        for result in results:
            status = result.get("status", "unknown")
            step_name = result.get("step_name", "unknown")
            if status == "completed":
                echo(style(f"  ✓ {step_name}", fg="green"))
            elif status == "failed":
                echo(style(f"  ✗ {step_name}: {result.get('error', 'Unknown error')}", fg="red"))
            elif status == "skipped":
                echo(style(f"  → {step_name} (skipped)", fg="yellow"))
        
        return results
    
    except Exception as e:
        echo(style(f"Error executing workflow: {e}", fg="red"))
        sys.exit(1)


@workflow.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--credentials', type=click.Path(exists=True), help='Path to JSON credentials file')
@click.option('--session', help='Session ID to restore')
@click.option('--headless', is_flag=True, default=True, help='Run browser in headless mode (default: True)')
@click.option('--visible', is_flag=True, help='Run browser in visible mode (overrides --headless)')
@click.option('--save-session', help='Save session with this ID after execution')
@click.pass_context
def execute(ctx, file_path, credentials, session, headless, visible, save_session):
    """Execute a workflow from a file."""
    asyncio.run(_execute_workflow(ctx, file_path, credentials, session, headless, visible, save_session))


@workflow.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--strict/--no-strict', default=True, help='Use strict validation')
@click.pass_context
def validate(ctx, file_path, strict):
    """Validate a workflow file."""
    try:
        # Initialize workflow validator
        validator = WorkflowValidator()
        
        # Validate workflow file
        is_valid = validator.validate_workflow_file(file_path, strict)
        
        if is_valid:
            echo(style("Workflow is valid!", fg="green"))
        else:
            echo(style("Workflow is invalid!", fg="red"))
            validator.print_errors()
            
            if validator.has_warnings():
                validator.print_warnings()
            
            sys.exit(1)
    
    except Exception as e:
        echo(style(f"Error validating workflow: {e}", fg="red"))
        sys.exit(1)


@workflow.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.pass_context
def edit(ctx, file_path):
    """Edit a workflow interactively."""
    try:
        # Initialize workflow builder
        builder = WorkflowBuilder()
        
        # Load workflow
        workflow = builder.load_workflow(file_path)
        
        # Edit workflow
        # This is a simplified version - in a real implementation,
        # you would have a more sophisticated editing interface
        echo(style("Editing workflow interactively", fg="blue"))
        echo(f"Current workflow: {workflow['name']}")
        
        # Edit workflow name
        name = prompt("Workflow name", default=workflow["name"])
        workflow["name"] = name
        
        # Edit workflow description
        description = prompt("Workflow description", default=workflow.get("description", ""))
        workflow["description"] = description
        
        # Save workflow
        builder.save_workflow(file_path)
        
        echo(style(f"Workflow edited and saved to: {file_path}", fg="green"))
    
    except Exception as e:
        echo(style(f"Error editing workflow: {e}", fg="red"))
        sys.exit(1)


@cli.group()
def template():
    """Template management commands."""
    pass


@template.command()
@click.argument('name')
@click.argument('workflow_file', type=click.Path(exists=True))
@click.option('--description', '-d', help='Template description')
@click.option('--tag', '-t', multiple=True, help='Template tags (can be specified multiple times)')
@click.pass_context
def create(ctx, name, workflow_file, description, tag):
    """Create a new template from a workflow file."""
    try:
        # Initialize template manager
        template_manager = WorkflowTemplateManager()
        
        # Load workflow
        builder = WorkflowBuilder()
        workflow = builder.load_workflow(workflow_file)
        
        # Create template
        template_file = template_manager.create_template(
            name=name,
            workflow=workflow,
            description=description or f"Template for {workflow['name']}",
            tags=list(tag) if tag else None
        )
        
        echo(style(f"Template created and saved to: {template_file}", fg="green"))
    
    except Exception as e:
        echo(style(f"Error creating template: {e}", fg="red"))
        sys.exit(1)


@template.command()
@click.argument('name')
@click.argument('workflow_name')
@click.option('--variable', '-v', multiple=True, help='Variables in format name=value (can be specified multiple times)')
@click.option('--description', '-d', help='Workflow description')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def use(ctx, name, workflow_name, variable, description, output):
    """Create a workflow from a template."""
    try:
        # Initialize template manager
        template_manager = WorkflowTemplateManager()
        
        # Parse variables
        variables = {}
        for var in variable:
            if '=' in var:
                var_name, var_value = var.split('=', 1)
                variables[var_name] = var_value
        
        # Create workflow from template
        workflow = template_manager.create_workflow_from_template(
            template_name=name,
            workflow_name=workflow_name,
            variables=variables,
            description=description
        )
        
        # Determine output file path
        if not output:
            output = f"{workflow_name.lower().replace(' ', '_')}.json"
        
        # Save workflow
        builder = WorkflowBuilder()
        builder.workflow = workflow
        builder.save_workflow(output)
        
        echo(style(f"Workflow created from template and saved to: {output}", fg="green"))
    
    except Exception as e:
        echo(style(f"Error creating workflow from template: {e}", fg="red"))
        sys.exit(1)


@template.command()
@click.pass_context
def list(ctx):
    """List all available templates."""
    try:
        # Initialize template manager
        template_manager = WorkflowTemplateManager()
        
        # List templates
        templates = template_manager.list_templates()
        
        if not templates:
            echo("No templates found.")
            return
        
        # Print templates
        echo(style("Available templates:", fg="blue"))
        for template in templates:
            echo(f"  - {template['name']}: {template['description']}")
            if template['tags']:
                echo(f"    Tags: {', '.join(template['tags'])}")
    
    except Exception as e:
        echo(style(f"Error listing templates: {e}", fg="red"))
        sys.exit(1)


@template.command()
@click.argument('query', required=False)
@click.option('--tag', '-t', multiple=True, help='Filter by tags (can be specified multiple times)')
@click.pass_context
def search(ctx, query, tag):
    """Search for templates."""
    try:
        # Initialize template manager
        template_manager = WorkflowTemplateManager()
        
        # Search templates
        templates = template_manager.search_templates(query=query or "", tags=list(tag) if tag else None)
        
        if not templates:
            echo("No templates found matching your search.")
            return
        
        # Print templates
        echo(style(f"Templates matching '{query or ''}':", fg="blue"))
        for template in templates:
            echo(f"  - {template['name']}: {template['description']}")
            if template['tags']:
                echo(f"    Tags: {', '.join(template['tags'])}")
    
    except Exception as e:
        echo(style(f"Error searching templates: {e}", fg="red"))
        sys.exit(1)


@template.command()
@click.argument('name')
@click.pass_context
def delete(ctx, name):
    """Delete a template."""
    try:
        # Initialize template manager
        template_manager = WorkflowTemplateManager()
        
        # Confirm deletion
        if not confirm(f"Are you sure you want to delete template '{name}'?"):
            echo("Template deletion cancelled.")
            return
        
        # Delete template
        template_manager.delete_template(name)
        
        echo(style(f"Template '{name}' deleted", fg="green"))
    
    except Exception as e:
        echo(style(f"Error deleting template: {e}", fg="red"))
        sys.exit(1)


@cli.group()
def helper():
    """Helper tool commands."""
    pass


@helper.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.pass_context
def parse_html(ctx, file_path):
    """Parse HTML file and extract element information."""
    try:
        # Initialize HTML parser
        parser = HTMLParser()
        
        # Parse HTML file
        elements = parser.parse_file(file_path)
        
        # Print elements
        echo(style(f"Found {len(elements)} elements in {file_path}:", fg="blue"))
        for element in elements:
            echo(f"  - {element['tag']}: {element.get('selector', '')}")
    
    except Exception as e:
        echo(style(f"Error parsing HTML: {e}", fg="red"))
        sys.exit(1)


@helper.command()
@click.option("--file", "-f", type=click.Path(exists=True), help="Path to HTML file")
@click.option("--html-fragment", help="Direct HTML fragment input")
@click.option("--fragment-file", type=click.Path(exists=True), help="Path to HTML fragment file")
@click.option("--stdin", is_flag=True, help="Read HTML fragment from stdin")
@click.option("--xpath-expression", help="Direct XPath expression input")
@click.option("--xpath-file", type=click.Path(exists=True), help="Path to XPath expression file")
@click.option("--html-context", help="HTML context for XPath evaluation")
@click.option("--html-context-file", type=click.Path(exists=True), help="Path to HTML context file")
@click.option('--targeting-mode', type=click.Choice(['all', 'selector', 'auto']), default='auto',
              help='How to target elements: all elements, specific selector, or auto-detection')
@click.option('--custom-selector', help='Custom selector to use when targeting-mode is "selector"')
@click.option('--selector-type', type=click.Choice(['css', 'xpath']), default='css',
              help='Type of custom selector (css or xpath)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def generate_selectors(ctx, file, html_fragment, fragment_file, stdin, xpath_expression, xpath_file, html_context, html_context_file, targeting_mode,
                      custom_selector, selector_type, output):
    """Generate selectors from HTML file or fragment."""
    try:
        # Initialize selector generator
        generator = SelectorGenerator()
        
        # Determine output file path first
        if not output:
            if file:
                output = f"{os.path.splitext(file)[0]}_selectors.json"
            elif fragment_file:
                output = f"{os.path.splitext(fragment_file)[0]}_selectors.json"
            else:
                output = "selectors.json"        # Validate XPath input options
        if xpath_expression or xpath_file:
            if not html_context and not html_context_file:
                echo(style("Error: HTML context is required when using XPath input. Use --html-context or --html-context-file", fg="red"))
                sys.exit(1)
            
            # Get HTML context
            if html_context_file:
                try:
                    with open(html_context_file, "r", encoding="utf-8") as f:
                        html_context_content = f.read()
                except Exception as e:
                    echo(style(f"Error reading HTML context file: {e}", fg="red"))
                    sys.exit(1)
            else:
                html_context_content = html_context
            
            # Generate selectors from XPath
            if xpath_expression:
                results = generator.generate_from_xpath(xpath_expression, html_context_content)
            elif xpath_file:
                results = generator.generate_from_xpath_file(xpath_file, html_context_content)
            
            # Save results to file
            with open(output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        elif file:
            # Use a simpler approach to avoid the argument parsing issue
            if custom_selector:
                # If custom selector is provided, use element_info format
                element_info = {}
                if selector_type == 'css':
                    element_info['css_selector'] = custom_selector
                else:
                    element_info['xpath'] = custom_selector
                
                selectors = generator.generate_from_file(file, element_info)
                # Save directly to file without storing in a variable
                with open(output, "w", encoding="utf-8") as f:
                    json.dump({'element_0': {'selectors': selectors, 'element_tag': 'unknown', 'element_text': ''}}, f, indent=2)
                logger.debug(f"Used generate_from_file method")
            else:
                # Use a simple approach that doesn't return complex data structures
                selectors = generator.generate_from_file_legacy(file)
                # Save directly to file without storing in a variable
                with open(output, "w", encoding="utf-8") as f:
                    json.dump({'element_0': {'selectors': selectors, 'element_tag': 'unknown', 'element_text': ''}}, f, indent=2)
                logger.debug(f"Used generate_from_file_legacy method")
        elif html_fragment:
            # Generate selectors from HTML fragment
            results = generator.generate_from_fragment(
                html_fragment, targeting_mode, custom_selector, selector_type
            )
            # Save directly to file without returning the results
            with open(output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        elif fragment_file:
            # Generate selectors from fragment file
            results = generator.generate_from_fragment_file(
                fragment_file, targeting_mode, custom_selector, selector_type
            )
            # Save directly to file without returning the results
            with open(output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        elif stdin:
            # Generate selectors from stdin
            results = generator.generate_from_stdin(
                targeting_mode, custom_selector, selector_type
            )
            # Save directly to file without returning the results
            with open(output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        else:
            echo(style("Error: No input source specified. Use --file, --html-fragment, --fragment-file, or --stdin", fg="red"))
            sys.exit(1)
        
        # Print summary
        echo(style(f"Selectors generated and saved to: {output}", fg="green"))
        
        # Read the results back from the file for processing
        with open(output, "r", encoding="utf-8") as f:
            results = json.load(f)
        
        # Process elements
        for i, (element_id, element_data) in enumerate(results.items()):
            try:
                best_type, best_selector = generator.get_best_selector(element_data['selectors'])
                # Check if element_tag exists, provide fallback if not
                element_tag = element_data.get('element_tag', 'unknown')
                echo(style(f"  - Element {i+1} ({element_tag}): {best_type} = {best_selector}", fg="green"))
            except Exception as e:
                logger.error(f"Error processing element {element_id}: {e}")
                echo(style(f"  - Element {i+1}: Error processing element data", fg="red"))
        
        # Explicitly exit to avoid any return value being interpreted as an argument
        sys.exit(0)
    
    except Exception as e:
        echo(style(f"Error generating selectors: {e}", fg="red"))
        sys.exit(1)
        sys.exit(1)

@helper.command()
@click.pass_context
def build_action(ctx):
    """Build an action interactively."""
    try:
        # Initialize action builder
        builder = ActionBuilder()
        
        # Build action
        action = builder.build_action_interactive()
        
        # Print action
        echo(style("Action built:", fg="green"))
        echo(json.dumps(action, indent=2))
    
    except Exception as e:
        echo(style(f"Error building action: {e}", fg="red"))
        sys.exit(1)


@cli.group()
def browser():
    """Browser exploration and session management commands."""
    pass


@browser.command()
@click.option('--headless/--visible', default=False, help='Run browser in headless mode (default: visible)')
@click.pass_context
def explore(ctx, headless):
    """Start an interactive browser exploration session."""
    try:
        # Initialize browser explorer
        explorer = BrowserExplorer(headless=not headless)
        
        # Start the browser
        asyncio.run(explorer.start())
        
        # Run interactive session
        asyncio.run(explorer.run_interactive())
        
        # Stop the browser
        asyncio.run(explorer.stop())
        
        echo(style("Browser exploration session ended", fg="green"))
    
    except KeyboardInterrupt:
        echo(style("\nBrowser exploration session interrupted", fg="yellow"))
        try:
            asyncio.run(explorer.stop())
        except:
            pass
    except Exception as e:
        echo(style(f"Error in browser exploration: {e}", fg="red"))
        sys.exit(1)


@cli.group()
def session():
    """Session management commands."""
    pass


@session.command()
@click.argument('session_id')
@click.option('--headless/--visible', default=True, help='Run browser in headless mode (default: headless)')
@click.option('--url', help='URL to navigate to before saving session')
@click.option('--expiry', type=int, help='Number of days until session expires (default: 30)')
@click.option('--encryption-key', help='Key for encrypting session data')
@click.pass_context
def save(ctx, session_id, headless, url, expiry, encryption_key):
    """Save a browser session."""
    try:
        # Initialize browser manager and session manager
        browser_manager = BrowserManager(headless=headless)
        session_manager = SessionManager(encryption_key=encryption_key)
        
        # Start the browser
        asyncio.run(browser_manager.start())
        
        # Create a new page and navigate to URL if provided
        if url:
            asyncio.run(browser_manager.new_page(url))
        
        # Save the session
        session_path = asyncio.run(session_manager.save_session(
            browser_manager, session_id, expiry_days=expiry
        ))
        
        # Stop the browser
        asyncio.run(browser_manager.stop())
        
        echo(style(f"Session saved to: {session_path}", fg="green"))
    
    except Exception as e:
        echo(style(f"Error saving session: {e}", fg="red"))
        sys.exit(1)


@session.command()
@click.argument('session_id')
@click.option('--headless/--visible', default=True, help='Run browser in headless mode (default: headless)')
@click.option('--url', help='URL to navigate to after loading session')
@click.option('--encryption-key', help='Key for decrypting session data')
@click.pass_context
def restore(ctx, session_id, headless, url, encryption_key):
    """Restore a browser session."""
    try:
        # Initialize browser manager and session manager
        browser_manager = BrowserManager(headless=headless)
        session_manager = SessionManager(encryption_key=encryption_key)
        
        # Start the browser
        asyncio.run(browser_manager.start())
        
        # Load the session
        session_loaded = asyncio.run(session_manager.load_session(browser_manager, session_id))
        
        if not session_loaded:
            echo(style(f"Failed to load session: {session_id}", fg="red"))
            asyncio.run(browser_manager.stop())
            sys.exit(1)
        
        # Create a new page and navigate to URL if provided
        if url:
            asyncio.run(browser_manager.new_page(url))
        
        # Stop the browser
        asyncio.run(browser_manager.stop())
        
        echo(style(f"Session restored successfully: {session_id}", fg="green"))
    
    except Exception as e:
        echo(style(f"Error restoring session: {e}", fg="red"))
        sys.exit(1)


@session.command()
@click.option('--include-expired', is_flag=True, help='Include expired sessions in the list')
@click.option('--encryption-key', help='Key for decrypting session data')
@click.pass_context
def list(ctx, include_expired, encryption_key):
    """List all saved sessions."""
    try:
        # Initialize session manager
        session_manager = SessionManager(encryption_key=encryption_key)
        
        # List sessions
        sessions = asyncio.run(session_manager.list_sessions(include_expired=include_expired))
        
        if not sessions:
            echo("No sessions found.")
            return
        
        # Print sessions
        echo(style("Saved sessions:", fg="blue"))
        for session in sessions:
            created_at = datetime.fromisoformat(session['created_at']) if session.get('created_at') else None
            created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "Unknown"
            
            status = "Expired" if session.get('is_expired') else "Active"
            status_color = "red" if session.get('is_expired') else "green"
            
            echo(f"  - {session['session_id']}:")
            echo(f"    Created: {created_str}")
            echo(f"    Status: ", nl=False)
            echo(style(status, fg=status_color))
            echo(f"    Cookies: {session['cookie_count']}")
            echo(f"    Local Storage: {'Yes' if session['has_local_storage'] else 'No'}")
            echo(f"    Session Storage: {'Yes' if session['has_session_storage'] else 'No'}")
            echo(f"    Expires in: {session['expiry_days']} days")
    
    except Exception as e:
        echo(style(f"Error listing sessions: {e}", fg="red"))
        sys.exit(1)


@session.command()
@click.argument('session_id')
@click.pass_context
def delete(ctx, session_id):
    """Delete a saved session."""
    try:
        # Initialize session manager
        session_manager = SessionManager()
        
        # Confirm deletion
        if not confirm(f"Are you sure you want to delete session '{session_id}'?"):
            echo("Session deletion cancelled.")
            return
        
        # Delete the session
        deleted = asyncio.run(session_manager.delete_session(session_id))
        
        if deleted:
            echo(style(f"Session '{session_id}' deleted", fg="green"))
        else:
            echo(style(f"Failed to delete session: {session_id}", fg="red"))
    
    except Exception as e:
        echo(style(f"Error deleting session: {e}", fg="red"))
        sys.exit(1)


@session.command()
@click.option('--encryption-key', help='Key for decrypting session data')
@click.pass_context
def cleanup(ctx, encryption_key):
    """Delete all expired sessions."""
    try:
        # Initialize session manager
        session_manager = SessionManager(encryption_key=encryption_key)
        
        # Clean up expired sessions
        deleted_count = asyncio.run(session_manager.cleanup_expired_sessions())
        
        if deleted_count > 0:
            echo(style(f"Cleaned up {deleted_count} expired sessions", fg="green"))
        else:
            echo("No expired sessions found.")
    
    except Exception as e:
        echo(style(f"Error cleaning up expired sessions: {e}", fg="red"))
        sys.exit(1)


@session.command()
@click.argument('session_id')
@click.option('--encryption-key', help='Key for decrypting session data')
@click.pass_context
def info(ctx, session_id, encryption_key):
    """Get information about a session."""
    try:
        # Initialize session manager
        session_manager = SessionManager(encryption_key=encryption_key)
        
        # Get session info
        session_info = asyncio.run(session_manager.get_session_info(session_id))
        
        if not session_info:
            echo(style(f"Session not found: {session_id}", fg="red"))
            return
        
        # Print session info
        echo(style(f"Session information for '{session_id}':", fg="blue"))
        
        created_at = datetime.fromisoformat(session_info['created_at']) if session_info.get('created_at') else None
        created_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "Unknown"
        
        status = "Expired" if session_info.get('is_expired') else "Active"
        status_color = "red" if session_info.get('is_expired') else "green"
        
        echo(f"  Created: {created_str}")
        echo(f"  Status: ", nl=False)
        echo(style(status, fg=status_color))
        echo(f"  Path: {session_info['path']}")
        echo(f"  Cookies: {session_info['cookie_count']}")
        echo(f"  Local Storage: {'Yes' if session_info['has_local_storage'] else 'No'}")
        echo(f"  Session Storage: {'Yes' if session_info['has_session_storage'] else 'No'}")
        echo(f"  Expires in: {session_info['expiry_days']} days")
        
        # Print metadata if available
        if 'metadata' in session_info:
            echo("  Metadata:")
            for key, value in session_info['metadata'].items():
                echo(f"    {key}: {value}")
    
    except Exception as e:
        echo(style(f"Error getting session info: {e}", fg="red"))
        sys.exit(1)


@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
@click.pass_context
def show(ctx):
    """Show current configuration."""
    try:
        # Initialize configuration
        config_dir = os.path.expanduser("~/.automata")
        config_file = os.path.join(config_dir, "config.json")
        
        # Check if configuration file exists
        if not os.path.exists(config_file):
            echo("No configuration file found.")
            return
        
        # Load configuration
        with open(config_file, "r") as f:
            config = json.load(f)
        
        # Print configuration
        echo(style("Current configuration:", fg="blue"))
        echo(json.dumps(config, indent=2))
    
    except Exception as e:
        echo(style(f"Error showing configuration: {e}", fg="red"))
        sys.exit(1)


@config.command()
@click.pass_context
def init(ctx):
    """Initialize configuration file."""
    try:
        # Initialize configuration
        config_dir = os.path.expanduser("~/.automata")
        config_file = os.path.join(config_dir, "config.json")
        
        # Create configuration directory if it doesn't exist
        os.makedirs(config_dir, exist_ok=True)
        
        # Check if configuration file already exists
        if os.path.exists(config_file):
            if not confirm("Configuration file already exists. Overwrite?"):
                echo("Configuration initialization cancelled.")
                return
        
        # Create default configuration
        config = {
            "browser": {
                "headless": True,
                "viewport": {
                    "width": 1280,
                    "height": 720
                }
            },
            "logging": {
                "level": "INFO",
                "file": None
            },
            "templates": {
                "directory": os.path.join(config_dir, "templates")
            }
        }
        
        # Save configuration
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        echo(style(f"Configuration initialized and saved to: {config_file}", fg="green"))
    
    except Exception as e:
        echo(style(f"Error initializing configuration: {e}", fg="red"))
        sys.exit(1)


if __name__ == '__main__':
    cli()