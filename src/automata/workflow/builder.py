"""
Workflow builder CLI tool.
"""

import json
import os
from typing import Dict, Any, List, Optional, Union
from click import echo, prompt, confirm, style
from ..core.errors import AutomationError
from ..core.logger import get_logger
from .schema import WorkflowSchema

logger = get_logger(__name__)


class WorkflowBuilder:
    """Builds automation workflows interactively."""

    def __init__(self, schema: Optional[WorkflowSchema] = None):
        """
        Initialize the workflow builder.

        Args:
            schema: Workflow schema instance
        """
        self.schema = schema or WorkflowSchema()
        self.workflow = None
        self.current_step = None

    def create_workflow(self) -> Dict[str, Any]:
        """
        Create a new workflow interactively.

        Returns:
            Workflow dictionary
        """
        try:
            echo(style("=== Create New Workflow ===", fg="blue", bold=True))
            
            # Get workflow name
            name = prompt("Workflow name", type=str)
            if not name:
                raise AutomationError("Workflow name is required")
            
            # Get workflow description
            description = prompt("Workflow description (optional)", type=str, default="")
            
            # Get workflow version
            version = prompt("Workflow version", type=str, default="1.0.0")
            if not version:
                raise AutomationError("Workflow version is required")
            
            # Create workflow template
            self.workflow = self.schema.create_workflow_template(name, description)
            self.workflow["version"] = version
            
            # Get workflow timeout
            timeout = prompt("Workflow timeout in seconds (optional)", type=int, default=300)
            if timeout > 0:
                self.workflow["timeout"] = timeout
            
            # Get workflow retry configuration
            if confirm("Configure retry settings?", default=True):
                max_attempts = prompt("Maximum retry attempts", type=int, default=3)
                delay = prompt("Delay between retries in seconds", type=float, default=1.0)
                self.workflow["retry"] = {
                    "max_attempts": max_attempts,
                    "delay": delay
                }
            
            # Get workflow on_error action
            on_error_options = ["stop", "continue", "retry"]
            echo("Action to take on error:")
            for i, option in enumerate(on_error_options):
                echo(f"{i+1}. {option}")
            
            on_error_choice = prompt("Choose an option", type=int, default=1)
            if 1 <= on_error_choice <= len(on_error_options):
                self.workflow["on_error"] = on_error_options[on_error_choice - 1]
            
            # Get workflow tags
            if confirm("Add tags?", default=False):
                tags = []
                while True:
                    tag = prompt("Tag (leave empty to finish)", type=str, default="")
                    if not tag:
                        break
                    tags.append(tag)
                self.workflow["tags"] = tags
            
            # Get workflow variables
            if confirm("Add variables?", default=False):
                variables = {}
                while True:
                    var_name = prompt("Variable name (leave empty to finish)", type=str, default="")
                    if not var_name:
                        break
                    
                    var_value = prompt("Variable value", type=str)
                    variables[var_name] = var_value
                
                self.workflow["variables"] = variables
            
            echo(style("Workflow created successfully!", fg="green"))
            
            return self.workflow
        
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise AutomationError(f"Error creating workflow: {e}")

    def add_step(self) -> Dict[str, Any]:
        """
        Add a step to the workflow interactively.

        Returns:
            Step dictionary
        """
        try:
            if not self.workflow:
                raise AutomationError("No workflow loaded")
            
            echo(style("=== Add Step ===", fg="blue", bold=True))
            
            # Get step name
            name = prompt("Step name", type=str)
            if not name:
                raise AutomationError("Step name is required")
            
            # Get step action
            action = prompt("Step action", type=str)
            if not action:
                raise AutomationError("Step action is required")
            
            # Get step description
            description = prompt("Step description (optional)", type=str, default="")
            
            # Create step template
            step = self.schema.create_step_template(name, action, description)
            
            # Get step selector
            selector = prompt("Element selector (optional)", type=str, default="")
            if selector:
                step["selector"] = selector
            
            # Get step value
            value = prompt("Step value (optional)", type=str, default="")
            if value:
                # Try to parse as JSON, otherwise keep as string
                try:
                    step["value"] = json.loads(value)
                except json.JSONDecodeError:
                    step["value"] = value
            
            # Get step timeout
            timeout = prompt("Step timeout in seconds (optional)", type=int, default=30)
            if timeout > 0:
                step["timeout"] = timeout
            
            # Get step retry configuration
            if confirm("Configure retry settings?", default=True):
                max_attempts = prompt("Maximum retry attempts", type=int, default=3)
                delay = prompt("Delay between retries in seconds", type=float, default=1.0)
                step["retry"] = {
                    "max_attempts": max_attempts,
                    "delay": delay
                }
            
            # Get step on_error action
            on_error_options = ["stop", "continue", "retry"]
            echo("Action to take on error:")
            for i, option in enumerate(on_error_options):
                echo(f"{i+1}. {option}")
            
            on_error_choice = prompt("Choose an option", type=int, default=1)
            if 1 <= on_error_choice <= len(on_error_options):
                step["on_error"] = on_error_options[on_error_choice - 1]
            
            # Get step variables
            if confirm("Add variables?", default=False):
                variables = {}
                while True:
                    var_name = prompt("Variable name (leave empty to finish)", type=str, default="")
                    if not var_name:
                        break
                    
                    var_value = prompt("Variable value", type=str)
                    variables[var_name] = var_value
                
                step["variables"] = variables
            
            # Get step next_step
            next_step = prompt("Next step name (optional)", type=str, default="")
            if next_step:
                step["next_step"] = next_step
            
            # Add step to workflow
            self.workflow["steps"].append(step)
            
            echo(style("Step added successfully!", fg="green"))
            
            return step
        
        except Exception as e:
            logger.error(f"Error adding step: {e}")
            raise AutomationError(f"Error adding step: {e}")

    def add_condition(self, step: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a condition to a step interactively.

        Args:
            step: Step to add condition to (optional)

        Returns:
            Condition dictionary
        """
        try:
            if not step and not self.current_step:
                raise AutomationError("No step selected")
            
            target_step = step or self.current_step
            
            echo(style("=== Add Condition ===", fg="blue", bold=True))
            
            # Get condition left value
            left = prompt("Left value", type=str)
            if not left:
                raise AutomationError("Left value is required")
            
            # Get condition operator
            valid_operators = [
                "==", "!=", ">", ">=", "<", "<=",
                "contains", "not_contains", "starts_with", "ends_with",
                "matches", "exists", "not_exists", "is_true", "is_false",
                "in", "not_in"
            ]
            echo("Operator:")
            for i, operator in enumerate(valid_operators):
                echo(f"{i+1}. {operator}")
            
            operator_choice = prompt("Choose an operator", type=int, default=1)
            if 1 <= operator_choice <= len(valid_operators):
                operator = valid_operators[operator_choice - 1]
            else:
                raise AutomationError("Invalid operator choice")
            
            # Get condition right value
            right = prompt("Right value", type=str)
            if not right:
                raise AutomationError("Right value is required")
            
            # Create condition
            condition = {
                "left": left,
                "operator": operator,
                "right": right
            }
            
            # Add condition to step
            target_step["condition"] = condition
            
            echo(style("Condition added successfully!", fg="green"))
            
            return condition
        
        except Exception as e:
            logger.error(f"Error adding condition: {e}")
            raise AutomationError(f"Error adding condition: {e}")

    def add_loop(self, step: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a loop to a step interactively.

        Args:
            step: Step to add loop to (optional)

        Returns:
            Loop dictionary
        """
        try:
            if not step and not self.current_step:
                raise AutomationError("No step selected")
            
            target_step = step or self.current_step
            
            echo(style("=== Add Loop ===", fg="blue", bold=True))
            
            # Get loop type
            valid_types = ["for", "for_each", "while", "do_while", "repeat", "until"]
            echo("Loop type:")
            for i, loop_type in enumerate(valid_types):
                echo(f"{i+1}. {loop_type}")
            
            type_choice = prompt("Choose a loop type", type=int, default=1)
            if 1 <= type_choice <= len(valid_types):
                loop_type = valid_types[type_choice - 1]
            else:
                raise AutomationError("Invalid loop type choice")
            
            # Create loop based on type
            loop = {"type": loop_type}
            
            if loop_type == "for":
                # Get FOR loop parameters
                var = prompt("Loop variable name", type=str)
                if not var:
                    raise AutomationError("Loop variable name is required")
                
                start = prompt("Start value", type=str)
                if not start:
                    raise AutomationError("Start value is required")
                
                end = prompt("End value", type=str)
                if not end:
                    raise AutomationError("End value is required")
                
                step = prompt("Step value", type=str, default="1")
                
                loop.update({
                    "var": var,
                    "start": start,
                    "end": end,
                    "step": step,
                    "actions": []
                })
            
            elif loop_type == "for_each":
                # Get FOR EACH loop parameters
                var = prompt("Loop variable name", type=str)
                if not var:
                    raise AutomationError("Loop variable name is required")
                
                items = prompt("Items (comma-separated or JSON array)", type=str)
                if not items:
                    raise AutomationError("Items are required")
                
                # Try to parse as JSON, otherwise split by comma
                try:
                    items = json.loads(items)
                except json.JSONDecodeError:
                    items = [item.strip() for item in items.split(",")]
                
                loop.update({
                    "var": var,
                    "items": items,
                    "actions": []
                })
            
            elif loop_type in ["while", "do_while", "until"]:
                # Get condition-based loop parameters
                condition_left = prompt("Condition left value", type=str)
                if not condition_left:
                    raise AutomationError("Condition left value is required")
                
                # Get condition operator
                echo("Condition operator:")
                for i, operator in enumerate(valid_operators):
                    echo(f"{i+1}. {operator}")
                
                operator_choice = prompt("Choose an operator", type=int, default=1)
                if 1 <= operator_choice <= len(valid_operators):
                    condition_operator = valid_operators[operator_choice - 1]
                else:
                    raise AutomationError("Invalid operator choice")
                
                condition_right = prompt("Condition right value", type=str)
                if not condition_right:
                    raise AutomationError("Condition right value is required")
                
                max_iterations = prompt("Maximum iterations (optional)", type=int, default=1000)
                
                loop.update({
                    "condition": {
                        "left": condition_left,
                        "operator": condition_operator,
                        "right": condition_right
                    },
                    "actions": [],
                    "max_iterations": max_iterations
                })
            
            elif loop_type == "repeat":
                # Get REPEAT loop parameters
                times = prompt("Number of times to repeat", type=str)
                if not times:
                    raise AutomationError("Number of times is required")
                
                loop.update({
                    "times": times,
                    "actions": []
                })
            
            # Add loop to step
            target_step["loop"] = loop
            
            echo(style("Loop added successfully!", fg="green"))
            
            return loop
        
        except Exception as e:
            logger.error(f"Error adding loop: {e}")
            raise AutomationError(f"Error adding loop: {e}")

    def save_workflow(self, file_path: str) -> None:
        """
        Save the workflow to a file.

        Args:
            file_path: Path to save file
        """
        try:
            if not self.workflow:
                raise AutomationError("No workflow loaded")
            
            # Validate workflow before saving
            if not self.schema.validate_workflow(self.workflow):
                raise AutomationError("Workflow validation failed")
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save workflow to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.workflow, f, indent=2)
            
            echo(style(f"Workflow saved to: {file_path}", fg="green"))
            logger.info(f"Workflow saved to: {file_path}")
        
        except Exception as e:
            logger.error(f"Error saving workflow: {e}")
            raise AutomationError(f"Error saving workflow: {e}")

    def load_workflow(self, file_path: str) -> Dict[str, Any]:
        """
        Load a workflow from a file.

        Args:
            file_path: Path to load file

        Returns:
            Workflow dictionary
        """
        try:
            # Load workflow from file
            with open(file_path, "r", encoding="utf-8") as f:
                workflow = json.load(f)
            
            # Validate workflow
            if not self.schema.validate_workflow(workflow):
                raise AutomationError("Workflow validation failed")
            
            self.workflow = workflow
            
            echo(style(f"Workflow loaded from: {file_path}", fg="green"))
            logger.info(f"Workflow loaded from: {file_path}")
            
            return workflow
        
        except Exception as e:
            logger.error(f"Error loading workflow: {e}")
            raise AutomationError(f"Error loading workflow: {e}")

    def list_steps(self) -> List[Dict[str, Any]]:
        """
        List all steps in the workflow.

        Returns:
            List of step dictionaries
        """
        if not self.workflow:
            raise AutomationError("No workflow loaded")
        
        return self.workflow.get("steps", [])

    def select_step(self) -> Optional[Dict[str, Any]]:
        """
        Select a step from the workflow.

        Returns:
            Selected step dictionary or None
        """
        try:
            steps = self.list_steps()
            if not steps:
                echo(style("No steps in workflow", fg="yellow"))
                return None
            
            echo(style("=== Select Step ===", fg="blue", bold=True))
            for i, step in enumerate(steps):
                echo(f"{i+1}. {step['name']} ({step['action']})")
            
            choice = prompt("Choose a step (leave empty to cancel)", type=int, default=0)
            if 1 <= choice <= len(steps):
                self.current_step = steps[choice - 1]
                return self.current_step
            
            return None
        
        except Exception as e:
            logger.error(f"Error selecting step: {e}")
            raise AutomationError(f"Error selecting step: {e}")

    def edit_step(self, step: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Edit a step in the workflow.

        Args:
            step: Step to edit (optional)

        Returns:
            Edited step dictionary
        """
        try:
            if not step and not self.current_step:
                raise AutomationError("No step selected")
            
            target_step = step or self.current_step
            
            echo(style("=== Edit Step ===", fg="blue", bold=True))
            echo(f"Editing step: {target_step['name']} ({target_step['action']})")
            
            # Edit step name
            name = prompt("Step name", type=str, default=target_step["name"])
            if not name:
                raise AutomationError("Step name is required")
            target_step["name"] = name
            
            # Edit step action
            action = prompt("Step action", type=str, default=target_step["action"])
            if not action:
                raise AutomationError("Step action is required")
            target_step["action"] = action
            
            # Edit step description
            description = prompt("Step description", type=str, default=target_step.get("description", ""))
            target_step["description"] = description
            
            # Edit step selector
            selector = prompt("Element selector", type=str, default=target_step.get("selector", ""))
            if selector:
                target_step["selector"] = selector
            elif "selector" in target_step:
                del target_step["selector"]
            
            # Edit step value
            value = prompt("Step value", type=str, default=str(target_step.get("value", "")))
            if value:
                # Try to parse as JSON, otherwise keep as string
                try:
                    target_step["value"] = json.loads(value)
                except json.JSONDecodeError:
                    target_step["value"] = value
            elif "value" in target_step:
                del target_step["value"]
            
            # Edit step timeout
            timeout = prompt("Step timeout in seconds", type=int, default=target_step.get("timeout", 30))
            if timeout > 0:
                target_step["timeout"] = timeout
            elif "timeout" in target_step:
                del target_step["timeout"]
            
            # Edit step retry configuration
            if confirm("Edit retry settings?", default=False):
                max_attempts = prompt("Maximum retry attempts", type=int, default=target_step.get("retry", {}).get("max_attempts", 3))
                delay = prompt("Delay between retries in seconds", type=float, default=target_step.get("retry", {}).get("delay", 1.0))
                target_step["retry"] = {
                    "max_attempts": max_attempts,
                    "delay": delay
                }
            elif "retry" in target_step:
                del target_step["retry"]
            
            # Edit step on_error action
            on_error_options = ["stop", "continue", "retry"]
            echo("Action to take on error:")
            for i, option in enumerate(on_error_options):
                echo(f"{i+1}. {option}")
            
            current_on_error = target_step.get("on_error", "stop")
            on_error_choice = prompt("Choose an option", type=int, default=on_error_options.index(current_on_error) + 1)
            if 1 <= on_error_choice <= len(on_error_options):
                target_step["on_error"] = on_error_options[on_error_choice - 1]
            
            # Edit step variables
            if confirm("Edit variables?", default=False):
                variables = target_step.get("variables", {}).copy()
                
                while True:
                    echo("Current variables:")
                    for var_name, var_value in variables.items():
                        echo(f"  {var_name}: {var_value}")
                    
                    action = prompt("Action (add/edit/remove/done)", type=str, default="done")
                    
                    if action.lower() == "done":
                        break
                    elif action.lower() in ["add", "edit"]:
                        var_name = prompt("Variable name", type=str)
                        if not var_name:
                            continue
                        
                        var_value = prompt("Variable value", type=str)
                        variables[var_name] = var_value
                    elif action.lower() == "remove":
                        var_name = prompt("Variable name to remove", type=str)
                        if var_name in variables:
                            del variables[var_name]
                
                if variables:
                    target_step["variables"] = variables
                elif "variables" in target_step:
                    del target_step["variables"]
            
            # Edit step next_step
            next_step = prompt("Next step name", type=str, default=target_step.get("next_step", ""))
            if next_step:
                target_step["next_step"] = next_step
            elif "next_step" in target_step:
                del target_step["next_step"]
            
            echo(style("Step edited successfully!", fg="green"))
            
            return target_step
        
        except Exception as e:
            logger.error(f"Error editing step: {e}")
            raise AutomationError(f"Error editing step: {e}")

    def remove_step(self, step: Optional[Dict[str, Any]] = None) -> None:
        """
        Remove a step from the workflow.

        Args:
            step: Step to remove (optional)
        """
        try:
            if not step and not self.current_step:
                raise AutomationError("No step selected")
            
            target_step = step or self.current_step
            
            if not confirm(f"Are you sure you want to remove step '{target_step['name']}'?", default=False):
                return
            
            # Remove step from workflow
            self.workflow["steps"].remove(target_step)
            
            # Clear current step if it was removed
            if self.current_step == target_step:
                self.current_step = None
            
            echo(style("Step removed successfully!", fg="green"))
        
        except Exception as e:
            logger.error(f"Error removing step: {e}")
            raise AutomationError(f"Error removing step: {e}")

    def reorder_steps(self) -> None:
        """
        Reorder steps in the workflow.
        """
        try:
            if not self.workflow:
                raise AutomationError("No workflow loaded")
            
            steps = self.list_steps()
            if len(steps) < 2:
                echo(style("Not enough steps to reorder", fg="yellow"))
                return
            
            echo(style("=== Reorder Steps ===", fg="blue", bold=True))
            
            # Show current order
            echo("Current order:")
            for i, step in enumerate(steps):
                echo(f"{i+1}. {step['name']} ({step['action']})")
            
            # Get new order
            new_order = []
            remaining_steps = steps.copy()
            
            while remaining_steps:
                echo("\nRemaining steps:")
                for i, step in enumerate(remaining_steps):
                    echo(f"{i+1}. {step['name']} ({step['action']})")
                
                choice = prompt("Choose a step to move next (leave empty to finish)", type=int, default=0)
                if 1 <= choice <= len(remaining_steps):
                    new_order.append(remaining_steps.pop(choice - 1))
                else:
                    break
            
            # Add remaining steps
            new_order.extend(remaining_steps)
            
            # Update workflow steps
            self.workflow["steps"] = new_order
            
            echo(style("Steps reordered successfully!", fg="green"))
        
        except Exception as e:
            logger.error(f"Error reordering steps: {e}")
            raise AutomationError(f"Error reordering steps: {e}")

    def validate_current_workflow(self) -> bool:
        """
        Validate the current workflow.

        Returns:
            True if workflow is valid, False otherwise
        """
        try:
            if not self.workflow:
                echo(style("No workflow loaded", fg="yellow"))
                return False
            
            if self.schema.validate_workflow(self.workflow):
                echo(style("Workflow is valid!", fg="green"))
                return True
            else:
                echo(style("Workflow is invalid!", fg="red"))
                return False
        
        except Exception as e:
            logger.error(f"Error validating workflow: {e}")
            echo(style(f"Error validating workflow: {e}", fg="red"))
            return False

    def export_schema(self, file_path: str) -> None:
        """
        Export the workflow schema to a file.

        Args:
            file_path: Path to export file
        """
        try:
            self.schema.export_schema(file_path)
            echo(style(f"Schema exported to: {file_path}", fg="green"))
        
        except Exception as e:
            logger.error(f"Error exporting schema: {e}")
            echo(style(f"Error exporting schema: {e}", fg="red"))
