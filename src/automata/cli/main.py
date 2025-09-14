"""
Main CLI entry point for web automation.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List, Optional, Union
import click
from click import echo, style, prompt, confirm
from ..core.errors import AutomationError
from ..core.logger import get_logger, setup_logging
from ..workflow import (
    WorkflowSchema,
    WorkflowBuilder,
    WorkflowValidator,
    WorkflowTemplateManager,
    WorkflowExecutionEngine
)
from ..helper import (
    HtmlParser,
    SelectorGenerator,
    ActionBuilder,
    FileIO,
    VariableManager,
    ConditionProcessor,
    LoopProcessor
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
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level)
    
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


@workflow.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.pass_context
def execute(ctx, file_path):
    """Execute a workflow from a file."""
    try:
        # Initialize workflow execution engine
        engine = WorkflowExecutionEngine()
        
        # Load workflow
        builder = WorkflowBuilder()
        workflow = builder.load_workflow(file_path)
        
        # Execute workflow
        results = asyncio.run(engine.execute_workflow(workflow))
        
        # Print results
        echo(style(f"Workflow executed successfully with {len(results)} steps", fg="green"))
        
        # Print execution summary
        completed = sum(1 for r in results if r.get("status") == "completed")
        failed = sum(1 for r in results if r.get("status") == "failed")
        skipped = sum(1 for r in results if r.get("status") == "skipped")
        
        echo(f"Completed: {completed}, Failed: {failed}, Skipped: {skipped}")
        
        # Print failed steps if any
        if failed > 0:
            echo(style("\nFailed steps:", fg="red"))
            for result in results:
                if result.get("status") == "failed":
                    echo(f"  - {result.get('step_name')}: {result.get('error')}")
    
    except Exception as e:
        echo(style(f"Error executing workflow: {e}", fg="red"))
        sys.exit(1)


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
        parser = HtmlParser()
        
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
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def generate_selectors(ctx, file_path, output):
    """Generate selectors from HTML file."""
    try:
        # Initialize selector generator
        generator = SelectorGenerator()
        
        # Generate selectors
        selectors = generator.generate_from_file(file_path)
        
        # Determine output file path
        if not output:
            output = f"{os.path.splitext(file_path)[0]}_selectors.json"
        
        # Save selectors
        generator.save_selectors(selectors, output)
        
        echo(style(f"Selectors generated and saved to: {output}", fg="green"))
    
    except Exception as e:
        echo(style(f"Error generating selectors: {e}", fg="red"))
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
