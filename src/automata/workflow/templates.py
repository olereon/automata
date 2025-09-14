"""
Workflow templates and reuse functionality.
"""

import json
import os
import glob
from typing import Dict, Any, List, Optional, Union
from ..core.errors import AutomationError
from ..core.logger import get_logger
from .schema import WorkflowSchema
from .validator import WorkflowValidator

logger = get_logger(__name__)


class WorkflowTemplateManager:
    """Manages workflow templates and reuse functionality."""

    def __init__(self, 
                 templates_dir: str = "templates",
                 schema: Optional[WorkflowSchema] = None,
                 validator: Optional[WorkflowValidator] = None):
        """
        Initialize the workflow template manager.

        Args:
            templates_dir: Directory to store templates
            schema: Workflow schema instance
            validator: Workflow validator instance
        """
        self.templates_dir = templates_dir
        self.schema = schema or WorkflowSchema()
        self.validator = validator or WorkflowValidator(self.schema)
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.templates_dir, exist_ok=True)

    def create_template(self, 
                       name: str, 
                       workflow: Dict[str, Any], 
                       description: str = "",
                       tags: Optional[List[str]] = None,
                       overwrite: bool = False) -> str:
        """
        Create a workflow template.

        Args:
            name: Template name
            workflow: Workflow dictionary
            description: Template description
            tags: Template tags
            overwrite: Whether to overwrite existing template

        Returns:
            Path to created template file
        """
        try:
            # Validate workflow before creating template
            if not self.validator.validate_workflow(workflow):
                raise AutomationError("Cannot create template from invalid workflow")
            
            # Create template metadata
            template = {
                "name": name,
                "description": description,
                "tags": tags or [],
                "workflow": workflow
            }
            
            # Create template file path
            template_file = os.path.join(self.templates_dir, f"{name}.json")
            
            # Check if template already exists
            if os.path.exists(template_file) and not overwrite:
                raise AutomationError(f"Template '{name}' already exists")
            
            # Save template to file
            with open(template_file, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2)
            
            logger.info(f"Template '{name}' created at: {template_file}")
            
            return template_file
        
        except Exception as e:
            logger.error(f"Error creating template '{name}': {e}")
            raise AutomationError(f"Error creating template '{name}': {e}")

    def load_template(self, name: str) -> Dict[str, Any]:
        """
        Load a workflow template.

        Args:
            name: Template name

        Returns:
            Template dictionary
        """
        try:
            # Create template file path
            template_file = os.path.join(self.templates_dir, f"{name}.json")
            
            # Check if template exists
            if not os.path.exists(template_file):
                raise AutomationError(f"Template '{name}' not found")
            
            # Load template from file
            with open(template_file, "r", encoding="utf-8") as f:
                template = json.load(f)
            
            logger.info(f"Template '{name}' loaded from: {template_file}")
            
            return template
        
        except Exception as e:
            logger.error(f"Error loading template '{name}': {e}")
            raise AutomationError(f"Error loading template '{name}': {e}")

    def delete_template(self, name: str) -> None:
        """
        Delete a workflow template.

        Args:
            name: Template name
        """
        try:
            # Create template file path
            template_file = os.path.join(self.templates_dir, f"{name}.json")
            
            # Check if template exists
            if not os.path.exists(template_file):
                raise AutomationError(f"Template '{name}' not found")
            
            # Delete template file
            os.remove(template_file)
            
            logger.info(f"Template '{name}' deleted")
        
        except Exception as e:
            logger.error(f"Error deleting template '{name}': {e}")
            raise AutomationError(f"Error deleting template '{name}': {e}")

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available workflow templates.

        Returns:
            List of template metadata
        """
        try:
            templates = []
            
            # Get all JSON files in templates directory
            template_files = glob.glob(os.path.join(self.templates_dir, "*.json"))
            
            for template_file in template_files:
                try:
                    # Load template metadata
                    with open(template_file, "r", encoding="utf-8") as f:
                        template = json.load(f)
                    
                    # Extract metadata
                    metadata = {
                        "name": template.get("name", ""),
                        "description": template.get("description", ""),
                        "tags": template.get("tags", []),
                        "file": os.path.basename(template_file)
                    }
                    
                    templates.append(metadata)
                
                except Exception as e:
                    logger.warning(f"Error loading template metadata from {template_file}: {e}")
            
            logger.info(f"Found {len(templates)} templates")
            
            return templates
        
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            raise AutomationError(f"Error listing templates: {e}")

    def search_templates(self, 
                        query: str = "", 
                        tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for workflow templates.

        Args:
            query: Search query
            tags: Tags to filter by

        Returns:
            List of matching template metadata
        """
        try:
            # Get all templates
            templates = self.list_templates()
            
            # Filter templates based on query and tags
            matching_templates = []
            
            query_lower = query.lower()
            
            for template in templates:
                # Check if template matches query
                matches_query = not query or (
                    query_lower in template["name"].lower() or
                    query_lower in template["description"].lower()
                )
                
                # Check if template has all required tags
                matches_tags = not tags or all(
                    tag in template["tags"] for tag in tags
                )
                
                if matches_query and matches_tags:
                    matching_templates.append(template)
            
            logger.info(f"Found {len(matching_templates)} templates matching query '{query}' and tags {tags}")
            
            return matching_templates
        
        except Exception as e:
            logger.error(f"Error searching templates: {e}")
            raise AutomationError(f"Error searching templates: {e}")

    def get_template_workflow(self, name: str) -> Dict[str, Any]:
        """
        Get the workflow from a template.

        Args:
            name: Template name

        Returns:
            Workflow dictionary
        """
        try:
            # Load template
            template = self.load_template(name)
            
            # Get workflow from template
            workflow = template.get("workflow")
            if not workflow:
                raise AutomationError(f"Template '{name}' does not contain a workflow")
            
            return workflow
        
        except Exception as e:
            logger.error(f"Error getting workflow from template '{name}': {e}")
            raise AutomationError(f"Error getting workflow from template '{name}': {e}")

    def create_workflow_from_template(self, 
                                    template_name: str, 
                                    workflow_name: str,
                                    variables: Optional[Dict[str, Any]] = None,
                                    description: str = "") -> Dict[str, Any]:
        """
        Create a workflow from a template.

        Args:
            template_name: Template name
            workflow_name: Workflow name
            variables: Variables to substitute in the workflow
            description: Workflow description

        Returns:
            Workflow dictionary
        """
        try:
            # Get template workflow
            workflow = self.get_template_workflow(template_name)
            
            # Clone workflow
            new_workflow = json.loads(json.dumps(workflow))
            
            # Update workflow name and description
            new_workflow["name"] = workflow_name
            if description:
                new_workflow["description"] = description
            elif not new_workflow.get("description"):
                new_workflow["description"] = f"Workflow created from template '{template_name}'"
            
            # Substitute variables
            if variables:
                self._substitute_variables(new_workflow, variables)
            
            logger.info(f"Workflow '{workflow_name}' created from template '{template_name}'")
            
            return new_workflow
        
        except Exception as e:
            logger.error(f"Error creating workflow from template '{template_name}': {e}")
            raise AutomationError(f"Error creating workflow from template '{template_name}': {e}")

    def _substitute_variables(self, workflow: Dict[str, Any], variables: Dict[str, Any]) -> None:
        """
        Substitute variables in a workflow.

        Args:
            workflow: Workflow dictionary
            variables: Variables to substitute
        """
        try:
            # Convert workflow to JSON string
            workflow_json = json.dumps(workflow)
            
            # Substitute variables
            for var_name, var_value in variables.items():
                # Replace {{var_name}} with var_value
                workflow_json = workflow_json.replace(f"{{{{{var_name}}}}}", str(var_value))
            
            # Convert back to dictionary
            workflow.clear()
            workflow.update(json.loads(workflow_json))
        
        except Exception as e:
            logger.error(f"Error substituting variables: {e}")
            raise AutomationError(f"Error substituting variables: {e}")

    def create_builtin_templates(self) -> None:
        """Create built-in workflow templates."""
        try:
            # Template for login workflow
            login_workflow = {
                "name": "Login Workflow",
                "version": "1.0.0",
                "description": "Template for login workflows",
                "variables": {
                    "url": "https://example.com/login",
                    "username_selector": "#username",
                    "password_selector": "#password",
                    "submit_selector": "#submit",
                    "username": "{{username}}",
                    "password": "{{password}}"
                },
                "steps": [
                    {
                        "name": "Navigate to login page",
                        "action": "navigate",
                        "value": "{{url}}"
                    },
                    {
                        "name": "Enter username",
                        "action": "type",
                        "selector": "{{username_selector}}",
                        "value": "{{username}}"
                    },
                    {
                        "name": "Enter password",
                        "action": "type",
                        "selector": "{{password_selector}}",
                        "value": "{{password}}"
                    },
                    {
                        "name": "Submit login form",
                        "action": "click",
                        "selector": "{{submit_selector}}"
                    },
                    {
                        "name": "Wait for login to complete",
                        "action": "wait_for",
                        "selector": ".dashboard",
                        "timeout": 30
                    }
                ]
            }
            
            self.create_template(
                name="login",
                workflow=login_workflow,
                description="Template for login workflows",
                tags=["login", "authentication", "form"]
            )
            
            # Template for data extraction workflow
            extraction_workflow = {
                "name": "Data Extraction Workflow",
                "version": "1.0.0",
                "description": "Template for data extraction workflows",
                "variables": {
                    "url": "https://example.com/data",
                    "data_selector": ".data-item",
                    "output_file": "data.json"
                },
                "steps": [
                    {
                        "name": "Navigate to data page",
                        "action": "navigate",
                        "value": "{{url}}"
                    },
                    {
                        "name": "Wait for data to load",
                        "action": "wait_for",
                        "selector": "{{data_selector}}",
                        "timeout": 30
                    },
                    {
                        "name": "Extract data",
                        "action": "extract",
                        "selector": "{{data_selector}}",
                        "value": {
                            "fields": {
                                "title": ".title",
                                "description": ".description",
                                "price": ".price"
                            }
                        }
                    },
                    {
                        "name": "Save data to file",
                        "action": "save",
                        "value": "{{output_file}}"
                    }
                ]
            }
            
            self.create_template(
                name="extraction",
                workflow=extraction_workflow,
                description="Template for data extraction workflows",
                tags=["extraction", "data", "scraping"]
            )
            
            # Template for form submission workflow
            form_workflow = {
                "name": "Form Submission Workflow",
                "version": "1.0.0",
                "description": "Template for form submission workflows",
                "variables": {
                    "url": "https://example.com/form",
                    "form_selector": "form",
                    "submit_selector": "button[type='submit']",
                    "fields": {
                        "name": "{{name}}",
                        "email": "{{email}}",
                        "message": "{{message}}"
                    }
                },
                "steps": [
                    {
                        "name": "Navigate to form page",
                        "action": "navigate",
                        "value": "{{url}}"
                    },
                    {
                        "name": "Wait for form to load",
                        "action": "wait_for",
                        "selector": "{{form_selector}}",
                        "timeout": 30
                    },
                    {
                        "name": "Fill form fields",
                        "action": "fill_form",
                        "selector": "{{form_selector}}",
                        "value": "{{fields}}"
                    },
                    {
                        "name": "Submit form",
                        "action": "click",
                        "selector": "{{submit_selector}}"
                    },
                    {
                        "name": "Wait for submission to complete",
                        "action": "wait_for",
                        "selector": ".success-message",
                        "timeout": 30
                    }
                ]
            }
            
            self.create_template(
                name="form",
                workflow=form_workflow,
                description="Template for form submission workflows",
                tags=["form", "submission", "input"]
            )
            
            logger.info("Built-in templates created successfully")
        
        except Exception as e:
            logger.error(f"Error creating built-in templates: {e}")
            raise AutomationError(f"Error creating built-in templates: {e}")

    def export_template(self, name: str, file_path: str) -> None:
        """
        Export a template to a file.

        Args:
            name: Template name
            file_path: Path to export file
        """
        try:
            # Load template
            template = self.load_template(name)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Export template to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template, f, indent=2)
            
            logger.info(f"Template '{name}' exported to: {file_path}")
        
        except Exception as e:
            logger.error(f"Error exporting template '{name}': {e}")
            raise AutomationError(f"Error exporting template '{name}': {e}")

    def import_template(self, file_path: str, name: Optional[str] = None, overwrite: bool = False) -> str:
        """
        Import a template from a file.

        Args:
            file_path: Path to import file
            name: Template name (optional, will use name from file if not provided)
            overwrite: Whether to overwrite existing template

        Returns:
            Name of imported template
        """
        try:
            # Load template from file
            with open(file_path, "r", encoding="utf-8") as f:
                template = json.load(f)
            
            # Validate template
            if not isinstance(template, dict):
                raise AutomationError("Invalid template format")
            
            # Get template name
            template_name = name or template.get("name")
            if not template_name:
                raise AutomationError("Template name is required")
            
            # Validate workflow in template
            workflow = template.get("workflow")
            if not workflow:
                raise AutomationError("Template must contain a workflow")
            
            if not self.validator.validate_workflow(workflow):
                raise AutomationError("Template contains an invalid workflow")
            
            # Create template
            template_file = self.create_template(
                name=template_name,
                workflow=workflow,
                description=template.get("description", ""),
                tags=template.get("tags", []),
                overwrite=overwrite
            )
            
            logger.info(f"Template imported from: {file_path}")
            
            return template_name
        
        except Exception as e:
            logger.error(f"Error importing template from {file_path}: {e}")
            raise AutomationError(f"Error importing template from {file_path}: {e}")
