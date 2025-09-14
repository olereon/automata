"""
JSON schema for automation workflow definition.
"""

import json
from typing import Dict, Any, List, Optional, Union
from ..core.errors import AutomationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class WorkflowSchema:
    """Manages the JSON schema for automation workflow definition."""

    def __init__(self):
        """Initialize the workflow schema."""
        self.schema = self._get_schema()

    def get_schema(self) -> Dict[str, Any]:
        """
        Get the workflow schema.

        Returns:
            Workflow schema dictionary
        """
        return self.schema

    def validate_workflow(self, workflow: Dict[str, Any]) -> bool:
        """
        Validate a workflow against the schema.

        Args:
            workflow: Workflow dictionary

        Returns:
            True if workflow is valid, False otherwise
        """
        try:
            # Basic validation
            if not isinstance(workflow, dict):
                logger.error("Workflow must be a dictionary")
                return False
            
            # Check required fields
            required_fields = ["name", "version", "steps"]
            for field in required_fields:
                if field not in workflow:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate name
            if not isinstance(workflow["name"], str) or not workflow["name"].strip():
                logger.error("Workflow name must be a non-empty string")
                return False
            
            # Validate version
            if not isinstance(workflow["version"], str) or not workflow["version"].strip():
                logger.error("Workflow version must be a non-empty string")
                return False
            
            # Validate steps
            if not isinstance(workflow["steps"], list) or not workflow["steps"]:
                logger.error("Workflow steps must be a non-empty list")
                return False
            
            # Validate each step
            for i, step in enumerate(workflow["steps"]):
                if not self._validate_step(step, i):
                    return False
            
            # Validate optional fields
            if "description" in workflow and not isinstance(workflow["description"], str):
                logger.error("Workflow description must be a string")
                return False
            
            if "variables" in workflow and not isinstance(workflow["variables"], dict):
                logger.error("Workflow variables must be a dictionary")
                return False
            
            if "timeout" in workflow:
                try:
                    timeout = float(workflow["timeout"])
                    if timeout <= 0:
                        logger.error("Workflow timeout must be a positive number")
                        return False
                except (ValueError, TypeError):
                    logger.error("Workflow timeout must be a number")
                    return False
            
            if "retry" in workflow and not isinstance(workflow["retry"], dict):
                logger.error("Workflow retry must be a dictionary")
                return False
            
            if "on_error" in workflow and not isinstance(workflow["on_error"], str):
                logger.error("Workflow on_error must be a string")
                return False
            
            if "tags" in workflow and not isinstance(workflow["tags"], list):
                logger.error("Workflow tags must be a list")
                return False
            
            logger.info("Workflow validation passed")
            return True
        
        except Exception as e:
            logger.error(f"Error validating workflow: {e}")
            return False

    def _validate_step(self, step: Dict[str, Any], index: int) -> bool:
        """
        Validate a workflow step.

        Args:
            step: Step dictionary
            index: Step index

        Returns:
            True if step is valid, False otherwise
        """
        try:
            # Check required fields
            if not isinstance(step, dict):
                logger.error(f"Step {index} must be a dictionary")
                return False
            
            required_fields = ["name", "action"]
            for field in required_fields:
                if field not in step:
                    logger.error(f"Step {index} missing required field: {field}")
                    return False
            
            # Validate name
            if not isinstance(step["name"], str) or not step["name"].strip():
                logger.error(f"Step {index} name must be a non-empty string")
                return False
            
            # Validate action
            if not isinstance(step["action"], str) or not step["action"].strip():
                logger.error(f"Step {index} action must be a non-empty string")
                return False
            
            # Validate optional fields
            if "description" in step and not isinstance(step["description"], str):
                logger.error(f"Step {index} description must be a string")
                return False
            
            if "selector" in step and not isinstance(step["selector"], str):
                logger.error(f"Step {index} selector must be a string")
                return False
            
            if "value" in step and not isinstance(step["value"], (str, int, float, bool, list, dict)):
                logger.error(f"Step {index} value must be a string, number, boolean, list, or dictionary")
                return False
            
            if "timeout" in step:
                try:
                    timeout = float(step["timeout"])
                    if timeout <= 0:
                        logger.error(f"Step {index} timeout must be a positive number")
                        return False
                except (ValueError, TypeError):
                    logger.error(f"Step {index} timeout must be a number")
                    return False
            
            if "retry" in step and not isinstance(step["retry"], dict):
                logger.error(f"Step {index} retry must be a dictionary")
                return False
            
            if "on_error" in step and not isinstance(step["on_error"], str):
                logger.error(f"Step {index} on_error must be a string")
                return False
            
            if "condition" in step and not isinstance(step["condition"], (dict, list)):
                logger.error(f"Step {index} condition must be a dictionary or list")
                return False
            
            if "loop" in step and not isinstance(step["loop"], dict):
                logger.error(f"Step {index} loop must be a dictionary")
                return False
            
            if "variables" in step and not isinstance(step["variables"], dict):
                logger.error(f"Step {index} variables must be a dictionary")
                return False
            
            if "next_step" in step and not isinstance(step["next_step"], str):
                logger.error(f"Step {index} next_step must be a string")
                return False
            
            # Validate condition if present
            if "condition" in step:
                if not self._validate_condition(step["condition"], f"Step {index}"):
                    return False
            
            # Validate loop if present
            if "loop" in step:
                if not self._validate_loop(step["loop"], f"Step {index}"):
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating step {index}: {e}")
            return False

    def _validate_condition(self, condition: Union[Dict, List], context: str) -> bool:
        """
        Validate a condition.

        Args:
            condition: Condition dictionary or list
            context: Context for error messages

        Returns:
            True if condition is valid, False otherwise
        """
        try:
            if isinstance(condition, dict):
                # Single condition
                required_fields = ["left", "operator", "right"]
                for field in required_fields:
                    if field not in condition:
                        logger.error(f"{context} condition missing required field: {field}")
                        return False
                
                # Validate operator
                valid_operators = [
                    "==", "!=", ">", ">=", "<", "<=",
                    "contains", "not_contains", "starts_with", "ends_with",
                    "matches", "exists", "not_exists", "is_true", "is_false",
                    "in", "not_in"
                ]
                if condition["operator"] not in valid_operators:
                    logger.error(f"{context} condition has invalid operator: {condition['operator']}")
                    return False
            
            elif isinstance(condition, list):
                # Multiple conditions
                for i, cond in enumerate(condition):
                    if not isinstance(cond, dict):
                        logger.error(f"{context} condition {i} must be a dictionary")
                        return False
                    
                    if not self._validate_condition(cond, f"{context} condition {i}"):
                        return False
            
            else:
                logger.error(f"{context} condition must be a dictionary or list")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating {context} condition: {e}")
            return False

    def _validate_loop(self, loop: Dict[str, Any], context: str) -> bool:
        """
        Validate a loop.

        Args:
            loop: Loop dictionary
            context: Context for error messages

        Returns:
            True if loop is valid, False otherwise
        """
        try:
            # Check required fields
            if "type" not in loop:
                logger.error(f"{context} loop missing required field: type")
                return False
            
            # Validate type
            valid_types = ["for", "for_each", "while", "do_while", "repeat", "until"]
            if loop["type"] not in valid_types:
                logger.error(f"{context} loop has invalid type: {loop['type']}")
                return False
            
            # Validate type-specific fields
            if loop["type"] == "for":
                required_fields = ["var", "start", "end", "actions"]
                for field in required_fields:
                    if field not in loop:
                        logger.error(f"{context} FOR loop missing required field: {field}")
                        return False
            
            elif loop["type"] == "for_each":
                required_fields = ["var", "items", "actions"]
                for field in required_fields:
                    if field not in loop:
                        logger.error(f"{context} FOR EACH loop missing required field: {field}")
                        return False
            
            elif loop["type"] in ["while", "do_while", "until"]:
                required_fields = ["condition", "actions"]
                for field in required_fields:
                    if field not in loop:
                        logger.error(f"{context} {loop['type'].upper()} loop missing required field: {field}")
                        return False
                
                # Validate condition
                if not self._validate_condition(loop["condition"], f"{context} {loop['type'].upper()} loop"):
                    return False
            
            elif loop["type"] == "repeat":
                required_fields = ["times", "actions"]
                for field in required_fields:
                    if field not in loop:
                        logger.error(f"{context} REPEAT loop missing required field: {field}")
                        return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error validating {context} loop: {e}")
            return False

    def create_workflow_template(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Create a workflow template.

        Args:
            name: Workflow name
            description: Workflow description

        Returns:
            Workflow template dictionary
        """
        return {
            "name": name,
            "version": "1.0.0",
            "description": description,
            "variables": {},
            "steps": [],
            "timeout": 300,
            "retry": {
                "max_attempts": 3,
                "delay": 1
            },
            "on_error": "stop",
            "tags": []
        }

    def create_step_template(self, name: str, action: str, description: str = "") -> Dict[str, Any]:
        """
        Create a step template.

        Args:
            name: Step name
            action: Step action
            description: Step description

        Returns:
            Step template dictionary
        """
        return {
            "name": name,
            "action": action,
            "description": description,
            "selector": "",
            "value": "",
            "timeout": 30,
            "retry": {
                "max_attempts": 3,
                "delay": 1
            },
            "on_error": "stop",
            "variables": {},
            "next_step": ""
        }

    def export_schema(self, file_path: str) -> None:
        """
        Export the schema to a file.

        Args:
            file_path: Path to export file
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.schema, f, indent=2)
            
            logger.info(f"Schema exported to: {file_path}")
        
        except Exception as e:
            logger.error(f"Error exporting schema: {e}")
            raise AutomationError(f"Error exporting schema: {e}")

    def _get_schema(self) -> Dict[str, Any]:
        """
        Get the workflow schema.

        Returns:
            Workflow schema dictionary
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Automation Workflow",
            "description": "Schema for automation workflow definition",
            "type": "object",
            "required": ["name", "version", "steps"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Workflow name"
                },
                "version": {
                    "type": "string",
                    "description": "Workflow version"
                },
                "description": {
                    "type": "string",
                    "description": "Workflow description"
                },
                "variables": {
                    "type": "object",
                    "description": "Workflow variables",
                    "additionalProperties": {
                        "oneOf": [
                            {"type": "string"},
                            {"type": "number"},
                            {"type": "boolean"},
                            {"type": "array"},
                            {"type": "object"}
                        ]
                    }
                },
                "steps": {
                    "type": "array",
                    "description": "Workflow steps",
                    "items": {
                        "type": "object",
                        "required": ["name", "action"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Step name"
                            },
                            "action": {
                                "type": "string",
                                "description": "Step action"
                            },
                            "description": {
                                "type": "string",
                                "description": "Step description"
                            },
                            "selector": {
                                "type": "string",
                                "description": "Element selector"
                            },
                            "value": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "number"},
                                    {"type": "boolean"},
                                    {"type": "array"},
                                    {"type": "object"}
                                ],
                                "description": "Step value"
                            },
                            "timeout": {
                                "type": "number",
                                "minimum": 0,
                                "description": "Step timeout in seconds"
                            },
                            "retry": {
                                "type": "object",
                                "properties": {
                                    "max_attempts": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "description": "Maximum retry attempts"
                                    },
                                    "delay": {
                                        "type": "number",
                                        "minimum": 0,
                                        "description": "Delay between retries in seconds"
                                    }
                                },
                                "description": "Step retry configuration"
                            },
                            "on_error": {
                                "type": "string",
                                "enum": ["stop", "continue", "retry"],
                                "description": "Action to take on error"
                            },
                            "condition": {
                                "oneOf": [
                                    {
                                        "type": "object",
                                        "required": ["left", "operator", "right"],
                                        "properties": {
                                            "left": {
                                                "oneOf": [
                                                    {"type": "string"},
                                                    {"type": "number"},
                                                    {"type": "boolean"}
                                                ]
                                            },
                                            "operator": {
                                                "type": "string",
                                                "enum": [
                                                    "==", "!=", ">", ">=", "<", "<=",
                                                    "contains", "not_contains", "starts_with", "ends_with",
                                                    "matches", "exists", "not_exists", "is_true", "is_false",
                                                    "in", "not_in"
                                                ]
                                            },
                                            "right": {
                                                "oneOf": [
                                                    {"type": "string"},
                                                    {"type": "number"},
                                                    {"type": "boolean"}
                                                ]
                                            }
                                        }
                                    },
                                    {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "required": ["left", "operator", "right"],
                                            "properties": {
                                                "left": {
                                                    "oneOf": [
                                                        {"type": "string"},
                                                        {"type": "number"},
                                                        {"type": "boolean"}
                                                    ]
                                                },
                                                "operator": {
                                                    "type": "string",
                                                    "enum": [
                                                        "==", "!=", ">", ">=", "<", "<=",
                                                        "contains", "not_contains", "starts_with", "ends_with",
                                                        "matches", "exists", "not_exists", "is_true", "is_false",
                                                        "in", "not_in"
                                                    ]
                                                },
                                                "right": {
                                                    "oneOf": [
                                                        {"type": "string"},
                                                        {"type": "number"},
                                                        {"type": "boolean"}
                                                    ]
                                                }
                                            }
                                        }
                                    }
                                ],
                                "description": "Step condition"
                            },
                            "loop": {
                                "type": "object",
                                "required": ["type"],
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["for", "for_each", "while", "do_while", "repeat", "until"],
                                        "description": "Loop type"
                                    }
                                },
                                "oneOf": [
                                    {
                                        "properties": {
                                            "type": {"enum": ["for"]},
                                            "var": {"type": "string"},
                                            "start": {"type": "number"},
                                            "end": {"type": "number"},
                                            "step": {"type": "number"},
                                            "actions": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/properties/steps/items"
                                                }
                                            }
                                        },
                                        "required": ["var", "start", "end", "actions"]
                                    },
                                    {
                                        "properties": {
                                            "type": {"enum": ["for_each"]},
                                            "var": {"type": "string"},
                                            "items": {
                                                "oneOf": [
                                                    {"type": "array"},
                                                    {"type": "string"}
                                                ]
                                            },
                                            "actions": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/properties/steps/items"
                                                }
                                            }
                                        },
                                        "required": ["var", "items", "actions"]
                                    },
                                    {
                                        "properties": {
                                            "type": {"enum": ["while", "do_while", "until"]},
                                            "condition": {
                                                "oneOf": [
                                                    {
                                                        "type": "object",
                                                        "required": ["left", "operator", "right"],
                                                        "properties": {
                                                            "left": {
                                                                "oneOf": [
                                                                    {"type": "string"},
                                                                    {"type": "number"},
                                                                    {"type": "boolean"}
                                                                ]
                                                            },
                                                            "operator": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "==", "!=", ">", ">=", "<", "<=",
                                                                    "contains", "not_contains", "starts_with", "ends_with",
                                                                    "matches", "exists", "not_exists", "is_true", "is_false",
                                                                    "in", "not_in"
                                                                ]
                                                            },
                                                            "right": {
                                                                "oneOf": [
                                                                    {"type": "string"},
                                                                    {"type": "number"},
                                                                    {"type": "boolean"}
                                                                ]
                                                            }
                                                        }
                                                    },
                                                    {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "required": ["left", "operator", "right"],
                                                            "properties": {
                                                                "left": {
                                                                    "oneOf": [
                                                                        {"type": "string"},
                                                                        {"type": "number"},
                                                                        {"type": "boolean"}
                                                                    ]
                                                                },
                                                                "operator": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "==", "!=", ">", ">=", "<", "<=",
                                                                        "contains", "not_contains", "starts_with", "ends_with",
                                                                        "matches", "exists", "not_exists", "is_true", "is_false",
                                                                        "in", "not_in"
                                                                    ]
                                                                },
                                                                "right": {
                                                                    "oneOf": [
                                                                        {"type": "string"},
                                                                        {"type": "number"},
                                                                        {"type": "boolean"}
                                                                    ]
                                                                }
                                                            }
                                                        }
                                                    }
                                                ]
                                            },
                                            "actions": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/properties/steps/items"
                                                }
                                            },
                                            "max_iterations": {
                                                "type": "integer",
                                                "minimum": 1
                                            }
                                        },
                                        "required": ["condition", "actions"]
                                    },
                                    {
                                        "properties": {
                                            "type": {"enum": ["repeat"]},
                                            "times": {
                                                "type": "integer",
                                                "minimum": 1
                                            },
                                            "actions": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/properties/steps/items"
                                                }
                                            }
                                        },
                                        "required": ["times", "actions"]
                                    }
                                ],
                                "description": "Step loop"
                            },
                            "variables": {
                                "type": "object",
                                "description": "Step variables",
                                "additionalProperties": {
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "number"},
                                        {"type": "boolean"},
                                        {"type": "array"},
                                        {"type": "object"}
                                    ]
                                }
                            },
                            "next_step": {
                                "type": "string",
                                "description": "Next step name"
                            }
                        }
                    }
                },
                "timeout": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Workflow timeout in seconds"
                },
                "retry": {
                    "type": "object",
                    "properties": {
                        "max_attempts": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Maximum retry attempts"
                        },
                        "delay": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Delay between retries in seconds"
                        }
                    },
                    "description": "Workflow retry configuration"
                },
                "on_error": {
                    "type": "string",
                    "enum": ["stop", "continue", "retry"],
                    "description": "Action to take on error"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Workflow tags"
                }
            }
        }
