"""
JSON command parser and validator for the MCP Server.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from jsonschema import validate, ValidationError

from ..core.logger import get_logger
from .exceptions import CommandValidationError

logger = get_logger(__name__)


class CommandParser:
    """Parser and validator for JSON commands."""

    def __init__(self):
        """Initialize command parser."""
        self._command_schemas = self._get_command_schemas()
        self._command_handlers = {}

    def _get_command_schemas(self) -> Dict[str, Dict[str, Any]]:
        """
        Get JSON schemas for all supported commands.

        Returns:
            Dictionary mapping command types to their schemas
        """
        return {
            "navigate": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["navigate"]},
                    "url": {"type": "string", "format": "uri"},
                    "timeout": {"type": "integer", "minimum": 0},
                    "wait_until": {
                        "type": "string",
                        "enum": ["load", "domcontentloaded", "networkidle"]
                    }
                },
                "required": ["type", "url"],
                "additionalProperties": False
            },
            "click": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["click"]},
                    "selector": {"type": "string"},
                    "xpath": {"type": "string"},
                    "text": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 0},
                    "button": {
                        "type": "string",
                        "enum": ["left", "right", "middle"]
                    },
                    "click_count": {"type": "integer", "minimum": 1},
                    "position": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"}
                        },
                        "required": ["x", "y"]
                    }
                },
                "required": ["type"],
                "oneOf": [
                    {"required": ["selector"]},
                    {"required": ["xpath"]},
                    {"required": ["text"]}
                ],
                "additionalProperties": False
            },
            "type": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["type"]},
                    "selector": {"type": "string"},
                    "xpath": {"type": "string"},
                    "text": {"type": "string"},
                    "value": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 0},
                    "delay": {"type": "integer", "minimum": 0},
                    "clear": {"type": "boolean"}
                },
                "required": ["type", "value"],
                "oneOf": [
                    {"required": ["selector"]},
                    {"required": ["xpath"]},
                    {"required": ["text"]}
                ],
                "additionalProperties": False
            },
            "hover": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["hover"]},
                    "selector": {"type": "string"},
                    "xpath": {"type": "string"},
                    "text": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 0},
                    "position": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"}
                        },
                        "required": ["x", "y"]
                    }
                },
                "required": ["type"],
                "oneOf": [
                    {"required": ["selector"]},
                    {"required": ["xpath"]},
                    {"required": ["text"]}
                ],
                "additionalProperties": False
            },
            "wait": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["wait"]},
                    "selector": {"type": "string"},
                    "xpath": {"type": "string"},
                    "text": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 0},
                    "state": {
                        "type": "string",
                        "enum": ["visible", "hidden", "enabled", "disabled"]
                    },
                    "for": {"type": "integer", "minimum": 0}
                },
                "required": ["type"],
                "oneOf": [
                    {"required": ["selector"]},
                    {"required": ["xpath"]},
                    {"required": ["text"]},
                    {"required": ["for"]}
                ],
                "additionalProperties": False
            },
            "screenshot": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["screenshot"]},
                    "path": {"type": "string"},
                    "format": {
                        "type": "string",
                        "enum": ["png", "jpeg"]
                    },
                    "quality": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 100
                    },
                    "full_page": {"type": "boolean"},
                    "selector": {"type": "string"},
                    "xpath": {"type": "string"},
                    "text": {"type": "string"}
                },
                "required": ["type"],
                "additionalProperties": False
            },
            "execute_script": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["execute_script"]},
                    "script": {"type": "string"},
                    "args": {
                        "type": "array",
                        "items": {}
                    }
                },
                "required": ["type", "script"],
                "additionalProperties": False
            },
            "get_text": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["get_text"]},
                    "selector": {"type": "string"},
                    "xpath": {"type": "string"},
                    "text": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 0}
                },
                "required": ["type"],
                "oneOf": [
                    {"required": ["selector"]},
                    {"required": ["xpath"]},
                    {"required": ["text"]}
                ],
                "additionalProperties": False
            },
            "get_attribute": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["get_attribute"]},
                    "selector": {"type": "string"},
                    "xpath": {"type": "string"},
                    "text": {"type": "string"},
                    "attribute": {"type": "string"},
                    "timeout": {"type": "integer", "minimum": 0}
                },
                "required": ["type", "attribute"],
                "oneOf": [
                    {"required": ["selector"]},
                    {"required": ["xpath"]},
                    {"required": ["text"]}
                ],
                "additionalProperties": False
            },
            "back": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["back"]},
                    "wait_until": {
                        "type": "string",
                        "enum": ["load", "domcontentloaded", "networkidle"]
                    }
                },
                "required": ["type"],
                "additionalProperties": False
            },
            "forward": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["forward"]},
                    "wait_until": {
                        "type": "string",
                        "enum": ["load", "domcontentloaded", "networkidle"]
                    }
                },
                "required": ["type"],
                "additionalProperties": False
            },
            "refresh": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["refresh"]},
                    "wait_until": {
                        "type": "string",
                        "enum": ["load", "domcontentloaded", "networkidle"]
                    }
                },
                "required": ["type"],
                "additionalProperties": False
            },
            "get_cookies": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["get_cookies"]},
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "names": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["type"],
                "additionalProperties": False
            },
            "set_cookie": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["set_cookie"]},
                    "name": {"type": "string"},
                    "value": {"type": "string"},
                    "url": {"type": "string"},
                    "domain": {"type": "string"},
                    "path": {"type": "string"},
                    "expires": {"type": "number"},
                    "http_only": {"type": "boolean"},
                    "secure": {"type": "boolean"},
                    "same_site": {
                        "type": "string",
                        "enum": ["Strict", "Lax", "None"]
                    }
                },
                "required": ["type", "name", "value"],
                "additionalProperties": False
            },
            "delete_cookies": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["delete_cookies"]},
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "names": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["type"],
                "additionalProperties": False
            },
            "new_tab": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["new_tab"]},
                    "url": {"type": "string", "format": "uri"}
                },
                "required": ["type"],
                "additionalProperties": False
            },
            "switch_tab": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["switch_tab"]},
                    "index": {"type": "integer", "minimum": 0},
                    "url": {"type": "string", "format": "uri"},
                    "title": {"type": "string"}
                },
                "required": ["type"],
                "oneOf": [
                    {"required": ["index"]},
                    {"required": ["url"]},
                    {"required": ["title"]}
                ],
                "additionalProperties": False
            },
            "close_tab": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["close_tab"]},
                    "index": {"type": "integer", "minimum": 0}
                },
                "required": ["type"],
                "additionalProperties": False
            },
            "get_tabs": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["get_tabs"]}
                },
                "required": ["type"],
                "additionalProperties": False
            }
        }

    def parse_command(self, command_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse and validate a single command.

        Args:
            command_data: Command data as JSON string or dictionary

        Returns:
            Parsed and validated command dictionary

        Raises:
            CommandValidationError: If command is invalid
        """
        # Parse JSON if needed
        if isinstance(command_data, str):
            try:
                command = json.loads(command_data)
            except json.JSONDecodeError as e:
                raise CommandValidationError(f"Invalid JSON: {e}", command_data)
        else:
            command = command_data.copy()

        # Validate command structure
        if not isinstance(command, dict):
            raise CommandValidationError("Command must be a dictionary", command)

        if "type" not in command:
            raise CommandValidationError("Command must have a 'type' field", command)

        command_type = command["type"]
        if command_type not in self._command_schemas:
            raise CommandValidationError(f"Unknown command type: {command_type}", command)

        # Validate against schema
        schema = self._command_schemas[command_type]
        try:
            validate(command, schema)
        except ValidationError as e:
            raise CommandValidationError(f"Command validation failed: {e.message}", command)

        # Apply default values
        command = self._apply_defaults(command, command_type)

        logger.debug(f"Parsed command: {command}")
        return command

    def parse_commands(self, commands_data: Union[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Parse and validate multiple commands.

        Args:
            commands_data: Commands data as JSON string or list of dictionaries

        Returns:
            List of parsed and validated command dictionaries

        Raises:
            CommandValidationError: If any command is invalid
        """
        # Parse JSON if needed
        if isinstance(commands_data, str):
            try:
                commands = json.loads(commands_data)
            except json.JSONDecodeError as e:
                raise CommandValidationError(f"Invalid JSON: {e}", commands_data)
        else:
            commands = commands_data.copy()

        # Validate commands structure
        if not isinstance(commands, list):
            raise CommandValidationError("Commands must be a list", commands)

        # Parse each command
        parsed_commands = []
        for i, command in enumerate(commands):
            try:
                parsed_command = self.parse_command(command)
                parsed_commands.append(parsed_command)
            except CommandValidationError as e:
                raise CommandValidationError(
                    f"Command at index {i} failed validation: {e.message}",
                    {"command": command, "index": i}
                )

        logger.info(f"Parsed {len(parsed_commands)} commands")
        return parsed_commands

    def _apply_defaults(self, command: Dict[str, Any], command_type: str) -> Dict[str, Any]:
        """
        Apply default values to a command.

        Args:
            command: Command dictionary
            command_type: Type of command

        Returns:
            Command with default values applied
        """
        # Create a copy to avoid modifying the original
        result = command.copy()

        # Apply common defaults
        if "timeout" not in result and command_type in [
            "navigate", "click", "type", "hover", "wait", "get_text", "get_attribute"
        ]:
            result["timeout"] = 30000

        # Apply command-specific defaults
        if command_type == "navigate" and "wait_until" not in result:
            result["wait_until"] = "load"

        if command_type == "click" and "button" not in result:
            result["button"] = "left"

        if command_type == "click" and "click_count" not in result:
            result["click_count"] = 1

        if command_type == "type" and "delay" not in result:
            result["delay"] = 0

        if command_type == "type" and "clear" not in result:
            result["clear"] = True

        if command_type == "screenshot" and "format" not in result:
            result["format"] = "png"

        if command_type == "screenshot" and "quality" not in result:
            result["quality"] = 100

        if command_type == "screenshot" and "full_page" not in result:
            result["full_page"] = False

        if command_type in ["back", "forward", "refresh"] and "wait_until" not in result:
            result["wait_until"] = "load"

        return result

    def register_command_handler(self, command_type: str, handler) -> None:
        """
        Register a custom command handler.

        Args:
            command_type: Type of command to handle
            handler: Handler function
        """
        self._command_handlers[command_type] = handler
        logger.debug(f"Registered handler for command type: {command_type}")

    def get_supported_commands(self) -> List[str]:
        """
        Get list of supported command types.

        Returns:
            List of supported command types
        """
        return list(self._command_schemas.keys())

    def get_command_schema(self, command_type: str) -> Optional[Dict[str, Any]]:
        """
        Get JSON schema for a command type.

        Args:
            command_type: Type of command

        Returns:
            JSON schema for the command type, or None if not found
        """
        return self._command_schemas.get(command_type)
