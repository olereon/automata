"""
Workflow validation and error checking.
"""

import json
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from ..core.errors import AutomationError
from ..core.logger import get_logger
from .schema import WorkflowSchema

logger = get_logger(__name__)


class WorkflowValidator:
    """Validates workflows and provides error checking."""

    def __init__(self, schema: Optional[WorkflowSchema] = None):
        """
        Initialize the workflow validator.

        Args:
            schema: Workflow schema instance
        """
        self.schema = schema or WorkflowSchema()
        self.errors = []
        self.warnings = []

    def validate_workflow(self, workflow: Dict[str, Any], strict: bool = True) -> bool:
        """
        Validate a workflow against the schema.

        Args:
            workflow: Workflow dictionary
            strict: Whether to use strict validation

        Returns:
            True if workflow is valid, False otherwise
        """
        try:
            # Reset errors and warnings
            self.errors = []
            self.warnings = []
            
            # Basic validation
            if not isinstance(workflow, dict):
                self.errors.append("Workflow must be a dictionary")
                return False
            
            # Check required fields
            required_fields = ["name", "version", "steps"]
            for field in required_fields:
                if field not in workflow:
                    self.errors.append(f"Missing required field: {field}")
            
            if self.errors:
                return False
            
            # Validate name
            if not isinstance(workflow["name"], str) or not workflow["name"].strip():
                self.errors.append("Workflow name must be a non-empty string")
            
            # Validate version
            if not isinstance(workflow["version"], str) or not workflow["version"].strip():
                self.errors.append("Workflow version must be a non-empty string")
            
            # Validate steps
            if not isinstance(workflow["steps"], list) or not workflow["steps"]:
                self.errors.append("Workflow steps must be a non-empty list")
            
            if self.errors:
                return False
            
            # Validate each step
            for i, step in enumerate(workflow["steps"]):
                self._validate_step(step, i, strict)
            
            # Validate optional fields
            if "description" in workflow and not isinstance(workflow["description"], str):
                self.errors.append("Workflow description must be a string")
            
            if "variables" in workflow:
                if not isinstance(workflow["variables"], dict):
                    self.errors.append("Workflow variables must be a dictionary")
                else:
                    self._validate_variables(workflow["variables"], "workflow")
            
            if "timeout" in workflow:
                try:
                    timeout = float(workflow["timeout"])
                    if timeout <= 0:
                        self.errors.append("Workflow timeout must be a positive number")
                except (ValueError, TypeError):
                    self.errors.append("Workflow timeout must be a number")
            
            if "retry" in workflow:
                if not isinstance(workflow["retry"], dict):
                    self.errors.append("Workflow retry must be a dictionary")
                else:
                    self._validate_retry(workflow["retry"], "workflow")
            
            if "on_error" in workflow:
                if not isinstance(workflow["on_error"], str):
                    self.errors.append("Workflow on_error must be a string")
                elif workflow["on_error"] not in ["stop", "continue", "retry"]:
                    self.errors.append("Workflow on_error must be one of: stop, continue, retry")
            
            if "tags" in workflow:
                if not isinstance(workflow["tags"], list):
                    self.errors.append("Workflow tags must be a list")
                else:
                    for i, tag in enumerate(workflow["tags"]):
                        if not isinstance(tag, str):
                            self.errors.append(f"Workflow tag {i} must be a string")
            
            # Check for duplicate step names
            step_names = [step.get("name", "") for step in workflow.get("steps", [])]
            duplicate_names = self._find_duplicates(step_names)
            if duplicate_names:
                self.errors.append(f"Duplicate step names found: {', '.join(duplicate_names)}")
            
            # Check for circular references in next_step
            if strict:
                circular_refs = self._check_circular_references(workflow)
                if circular_refs:
                    self.errors.append(f"Circular references found in next_step: {', '.join(circular_refs)}")
            
            # Log validation results
            if self.errors:
                logger.error(f"Workflow validation failed with {len(self.errors)} errors")
                for error in self.errors:
                    logger.error(f"  - {error}")
            else:
                logger.info("Workflow validation passed")
                if self.warnings:
                    logger.warning(f"Workflow validation passed with {len(self.warnings)} warnings")
                    for warning in self.warnings:
                        logger.warning(f"  - {warning}")
            
            return len(self.errors) == 0
        
        except Exception as e:
            logger.error(f"Error validating workflow: {e}")
            self.errors.append(f"Error validating workflow: {e}")
            return False

    def _validate_step(self, step: Dict[str, Any], index: int, strict: bool = True) -> None:
        """
        Validate a workflow step.

        Args:
            step: Step dictionary
            index: Step index
            strict: Whether to use strict validation
        """
        try:
            # Check required fields
            if not isinstance(step, dict):
                self.errors.append(f"Step {index} must be a dictionary")
                return
            
            required_fields = ["name", "action"]
            for field in required_fields:
                if field not in step:
                    self.errors.append(f"Step {index} missing required field: {field}")
            
            if self.errors:
                return
            
            # Validate name
            if not isinstance(step["name"], str) or not step["name"].strip():
                self.errors.append(f"Step {index} name must be a non-empty string")
            
            # Validate action
            if not isinstance(step["action"], str) or not step["action"].strip():
                self.errors.append(f"Step {index} action must be a non-empty string")
            
            # Validate optional fields
            if "description" in step and not isinstance(step["description"], str):
                self.errors.append(f"Step {index} description must be a string")
            
            if "selector" in step and not isinstance(step["selector"], str):
                self.errors.append(f"Step {index} selector must be a string")
            
            if "value" in step and not isinstance(step["value"], (str, int, float, bool, list, dict)):
                self.errors.append(f"Step {index} value must be a string, number, boolean, list, or dictionary")
            
            if "timeout" in step:
                try:
                    timeout = float(step["timeout"])
                    if timeout <= 0:
                        self.errors.append(f"Step {index} timeout must be a positive number")
                except (ValueError, TypeError):
                    self.errors.append(f"Step {index} timeout must be a number")
            
            if "retry" in step:
                if not isinstance(step["retry"], dict):
                    self.errors.append(f"Step {index} retry must be a dictionary")
                else:
                    self._validate_retry(step["retry"], f"Step {index}")
            
            if "on_error" in step:
                if not isinstance(step["on_error"], str):
                    self.errors.append(f"Step {index} on_error must be a string")
                elif step["on_error"] not in ["stop", "continue", "retry"]:
                    self.errors.append(f"Step {index} on_error must be one of: stop, continue, retry")
            
            if "condition" in step:
                if not isinstance(step["condition"], (dict, list)):
                    self.errors.append(f"Step {index} condition must be a dictionary or list")
                else:
                    self._validate_condition(step["condition"], f"Step {index}")
            
            if "loop" in step:
                if not isinstance(step["loop"], dict):
                    self.errors.append(f"Step {index} loop must be a dictionary")
                else:
                    self._validate_loop(step["loop"], f"Step {index}")
            
            if "variables" in step:
                if not isinstance(step["variables"], dict):
                    self.errors.append(f"Step {index} variables must be a dictionary")
                else:
                    self._validate_variables(step["variables"], f"Step {index}")
            
            if "next_step" in step:
                if not isinstance(step["next_step"], str):
                    self.errors.append(f"Step {index} next_step must be a string")
                elif strict and step["next_step"]:
                    # Check if next_step references a valid step
                    # This will be checked in the main validate_workflow method
            
            # Check for incompatible combinations
            if "condition" in step and "loop" in step:
                self.warnings.append(f"Step {index} has both condition and loop - this may lead to unexpected behavior")
            
            if "selector" in step and step["action"] not in ["click", "type", "hover", "wait_for", "get_text", "get_attribute", "screenshot"]:
                self.warnings.append(f"Step {index} has a selector but action '{step['action']}' may not use it")
        
        except Exception as e:
            logger.error(f"Error validating step {index}: {e}")
            self.errors.append(f"Error validating step {index}: {e}")

    def _validate_condition(self, condition: Union[Dict, List], context: str) -> None:
        """
        Validate a condition.

        Args:
            condition: Condition dictionary or list
            context: Context for error messages
        """
        try:
            if isinstance(condition, dict):
                # Single condition
                required_fields = ["left", "operator", "right"]
                for field in required_fields:
                    if field not in condition:
                        self.errors.append(f"{context} condition missing required field: {field}")
                
                if self.errors:
                    return
                
                # Validate operator
                valid_operators = [
                    "==", "!=", ">", ">=", "<", "<=",
                    "contains", "not_contains", "starts_with", "ends_with",
                    "matches", "exists", "not_exists", "is_true", "is_false",
                    "in", "not_in"
                ]
                if condition["operator"] not in valid_operators:
                    self.errors.append(f"{context} condition has invalid operator: {condition['operator']}")
                
                # Validate operator-specific requirements
                if condition["operator"] in ["exists", "not_exists", "is_true", "is_false"]:
                    # These operators don't need a right value
                    pass
                elif condition["operator"] in ["contains", "not_contains", "starts_with", "ends_with", "matches"]:
                    # These operators require string values
                    if not isinstance(condition["left"], str) or not isinstance(condition["right"], str):
                        self.errors.append(f"{context} condition with operator '{condition['operator']}' requires string values")
                elif condition["operator"] in ["in", "not_in"]:
                    # These operators require the right value to be a list
                    if not isinstance(condition["right"], list):
                        self.errors.append(f"{context} condition with operator '{condition['operator']}' requires right value to be a list")
            
            elif isinstance(condition, list):
                # Multiple conditions
                for i, cond in enumerate(condition):
                    if not isinstance(cond, dict):
                        self.errors.append(f"{context} condition {i} must be a dictionary")
                    else:
                        self._validate_condition(cond, f"{context} condition {i}")
            
            else:
                self.errors.append(f"{context} condition must be a dictionary or list")
        
        except Exception as e:
            logger.error(f"Error validating {context} condition: {e}")
            self.errors.append(f"Error validating {context} condition: {e}")

    def _validate_loop(self, loop: Dict[str, Any], context: str) -> None:
        """
        Validate a loop.

        Args:
            loop: Loop dictionary
            context: Context for error messages
        """
        try:
            # Check required fields
            if "type" not in loop:
                self.errors.append(f"{context} loop missing required field: type")
                return
            
            # Validate type
            valid_types = ["for", "for_each", "while", "do_while", "repeat", "until"]
            if loop["type"] not in valid_types:
                self.errors.append(f"{context} loop has invalid type: {loop['type']}")
                return
            
            # Validate type-specific fields
            if loop["type"] == "for":
                required_fields = ["var", "start", "end", "actions"]
                for field in required_fields:
                    if field not in loop:
                        self.errors.append(f"{context} FOR loop missing required field: {field}")
                
                if self.errors:
                    return
                
                # Validate start, end, and step are numbers
                for field in ["start", "end", "step"]:
                    if field in loop:
                        try:
                            float(loop[field])
                        except (ValueError, TypeError):
                            self.errors.append(f"{context} FOR loop {field} must be a number")
            
            elif loop["type"] == "for_each":
                required_fields = ["var", "items", "actions"]
                for field in required_fields:
                    if field not in loop:
                        self.errors.append(f"{context} FOR EACH loop missing required field: {field}")
                
                if self.errors:
                    return
                
                # Validate items is iterable
                if not isinstance(loop["items"], (list, tuple, set, dict, str)):
                    self.errors.append(f"{context} FOR EACH loop items must be iterable")
            
            elif loop["type"] in ["while", "do_while", "until"]:
                required_fields = ["condition", "actions"]
                for field in required_fields:
                    if field not in loop:
                        self.errors.append(f"{context} {loop['type'].upper()} loop missing required field: {field}")
                
                if self.errors:
                    return
                
                # Validate condition
                self._validate_condition(loop["condition"], f"{context} {loop['type'].upper()} loop")
                
                # Validate max_iterations
                if "max_iterations" in loop:
                    if not isinstance(loop["max_iterations"], int) or loop["max_iterations"] <= 0:
                        self.errors.append(f"{context} {loop['type'].upper()} loop max_iterations must be a positive integer")
            
            elif loop["type"] == "repeat":
                required_fields = ["times", "actions"]
                for field in required_fields:
                    if field not in loop:
                        self.errors.append(f"{context} REPEAT loop missing required field: {field}")
                
                if self.errors:
                    return
                
                # Validate times is a positive integer
                try:
                    times = int(loop["times"])
                    if times <= 0:
                        self.errors.append(f"{context} REPEAT loop times must be a positive integer")
                except (ValueError, TypeError):
                    self.errors.append(f"{context} REPEAT loop times must be a positive integer")
            
            # Validate actions
            if "actions" in loop and isinstance(loop["actions"], list):
                for i, action in enumerate(loop["actions"]):
                    if not isinstance(action, dict):
                        self.errors.append(f"{context} loop action {i} must be a dictionary")
                    else:
                        self._validate_step(action, f"{context} loop action {i}")
        
        except Exception as e:
            logger.error(f"Error validating {context} loop: {e}")
            self.errors.append(f"Error validating {context} loop: {e}")

    def _validate_retry(self, retry: Dict[str, Any], context: str) -> None:
        """
        Validate a retry configuration.

        Args:
            retry: Retry dictionary
            context: Context for error messages
        """
        try:
            # Check max_attempts
            if "max_attempts" in retry:
                if not isinstance(retry["max_attempts"], int) or retry["max_attempts"] <= 0:
                    self.errors.append(f"{context} retry max_attempts must be a positive integer")
            
            # Check delay
            if "delay" in retry:
                try:
                    delay = float(retry["delay"])
                    if delay < 0:
                        self.errors.append(f"{context} retry delay must be a non-negative number")
                except (ValueError, TypeError):
                    self.errors.append(f"{context} retry delay must be a number")
        
        except Exception as e:
            logger.error(f"Error validating {context} retry: {e}")
            self.errors.append(f"Error validating {context} retry: {e}")

    def _validate_variables(self, variables: Dict[str, Any], context: str) -> None:
        """
        Validate variables.

        Args:
            variables: Variables dictionary
            context: Context for error messages
        """
        try:
            for var_name, var_value in variables.items():
                if not isinstance(var_name, str) or not var_name.strip():
                    self.errors.append(f"{context} variable name must be a non-empty string")
                
                if not isinstance(var_value, (str, int, float, bool, list, dict)):
                    self.errors.append(f"{context} variable '{var_name}' must be a string, number, boolean, list, or dictionary")
        
        except Exception as e:
            logger.error(f"Error validating {context} variables: {e}")
            self.errors.append(f"Error validating {context} variables: {e}")

    def _find_duplicates(self, items: List[str]) -> List[str]:
        """
        Find duplicate items in a list.

        Args:
            items: List of items

        Returns:
            List of duplicate items
        """
        seen = {}
        duplicates = []
        
        for item in items:
            if item in seen:
                seen[item] += 1
                if seen[item] == 2:  # Only add to duplicates once
                    duplicates.append(item)
            else:
                seen[item] = 1
        
        return duplicates

    def _check_circular_references(self, workflow: Dict[str, Any]) -> List[str]:
        """
        Check for circular references in next_step.

        Args:
            workflow: Workflow dictionary

        Returns:
            List of step names involved in circular references
        """
        try:
            steps = workflow.get("steps", [])
            step_names = [step.get("name", "") for step in steps]
            
            # Build a graph of next_step references
            graph = {}
            for step in steps:
                step_name = step.get("name", "")
                next_step = step.get("next_step", "")
                
                if step_name and next_step and next_step in step_names:
                    if step_name not in graph:
                        graph[step_name] = []
                    graph[step_name].append(next_step)
            
            # Check for circular references using DFS
            visited = set()
            recursion_stack = set()
            circular_refs = []
            
            def dfs(node, path):
                if node in recursion_stack:
                    # Found a circular reference
                    cycle_start = path.index(node)
                    cycle = path[cycle_start:] + [node]
                    circular_refs.append(" -> ".join(cycle))
                    return
                
                if node in visited:
                    return
                
                visited.add(node)
                recursion_stack.add(node)
                
                if node in graph:
                    for neighbor in graph[node]:
                        dfs(neighbor, path + [node])
                
                recursion_stack.remove(node)
            
            for step_name in step_names:
                if step_name not in visited:
                    dfs(step_name, [])
            
            return circular_refs
        
        except Exception as e:
            logger.error(f"Error checking circular references: {e}")
            return []

    def get_errors(self) -> List[str]:
        """
        Get the validation errors.

        Returns:
            List of error messages
        """
        return self.errors

    def get_warnings(self) -> List[str]:
        """
        Get the validation warnings.

        Returns:
            List of warning messages
        """
        return self.warnings

    def has_errors(self) -> bool:
        """
        Check if there are any validation errors.

        Returns:
            True if there are errors, False otherwise
        """
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """
        Check if there are any validation warnings.

        Returns:
            True if there are warnings, False otherwise
        """
        return len(self.warnings) > 0

    def print_errors(self) -> None:
        """Print the validation errors."""
        if self.errors:
            print("Validation Errors:")
            for error in self.errors:
                print(f"  - {error}")

    def print_warnings(self) -> None:
        """Print the validation warnings."""
        if self.warnings:
            print("Validation Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

    def export_errors(self, file_path: str) -> None:
        """
        Export the validation errors to a file.

        Args:
            file_path: Path to export file
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({
                    "errors": self.errors,
                    "warnings": self.warnings
                }, f, indent=2)
            
            logger.info(f"Validation errors exported to: {file_path}")
        
        except Exception as e:
            logger.error(f"Error exporting validation errors: {e}")
            raise AutomationError(f"Error exporting validation errors: {e}")

    def validate_workflow_file(self, file_path: str, strict: bool = True) -> bool:
        """
        Validate a workflow file.

        Args:
            file_path: Path to workflow file
            strict: Whether to use strict validation

        Returns:
            True if workflow is valid, False otherwise
        """
        try:
            # Load workflow from file
            with open(file_path, "r", encoding="utf-8") as f:
                workflow = json.load(f)
            
            # Validate workflow
            return self.validate_workflow(workflow, strict)
        
        except Exception as e:
            logger.error(f"Error validating workflow file: {e}")
            self.errors.append(f"Error validating workflow file: {e}")
            return False
