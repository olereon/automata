"""
Variable management system for storing and using dynamic values.
"""

import json
import re
import os
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from ..core.errors import AutomationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class VariableManager:
    """Manages variables for storing and using dynamic values."""

    def __init__(self):
        """Initialize the variable manager."""
        self.variables = {}
        self.variable_history = {}

    def set_variable(self, name: str, value: Any, persist: bool = False) -> None:
        """
        Set a variable value.

        Args:
            name: Variable name
            value: Variable value
            persist: Whether to persist the variable to disk
        """
        try:
            # Store the variable
            self.variables[name] = value
            
            # Record in history
            if name not in self.variable_history:
                self.variable_history[name] = []
            
            self.variable_history[name].append({
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "action": "set"
            })
            
            # Persist to disk if requested
            if persist:
                self._persist_variable(name, value)
            
            logger.debug(f"Variable '{name}' set to: {value}")
        
        except Exception as e:
            logger.error(f"Error setting variable '{name}': {e}")
            raise AutomationError(f"Error setting variable '{name}': {e}")

    def get_variable(self, name: str, default: Any = None) -> Any:
        """
        Get a variable value.

        Args:
            name: Variable name
            default: Default value if variable doesn't exist

        Returns:
            Variable value or default
        """
        try:
            # Try to get from memory
            if name in self.variables:
                return self.variables[name]
            
            # Try to load from disk
            value = self._load_variable(name)
            if value is not None:
                self.variables[name] = value
                return value
            
            # Return default
            return default
        
        except Exception as e:
            logger.error(f"Error getting variable '{name}': {e}")
            return default

    def delete_variable(self, name: str) -> bool:
        """
        Delete a variable.

        Args:
            name: Variable name

        Returns:
            True if variable was deleted, False otherwise
        """
        try:
            # Remove from memory
            if name in self.variables:
                del self.variables[name]
                
                # Record in history
                if name not in self.variable_history:
                    self.variable_history[name] = []
                
                self.variable_history[name].append({
                    "value": None,
                    "timestamp": datetime.now().isoformat(),
                    "action": "delete"
                })
            
            # Remove from disk
            self._delete_persisted_variable(name)
            
            logger.debug(f"Variable '{name}' deleted")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting variable '{name}': {e}")
            return False

    def list_variables(self) -> List[str]:
        """
        List all variable names.

        Returns:
            List of variable names
        """
        try:
            # Get variables from memory
            variables = list(self.variables.keys())
            
            # Get variables from disk
            persisted_variables = self._list_persisted_variables()
            
            # Combine and deduplicate
            all_variables = list(set(variables + persisted_variables))
            
            return sorted(all_variables)
        
        except Exception as e:
            logger.error(f"Error listing variables: {e}")
            return []

    def clear_variables(self) -> None:
        """
        Clear all variables.
        """
        try:
            # Clear memory
            self.variables = {}
            
            # Clear disk
            self._clear_persisted_variables()
            
            logger.debug("All variables cleared")
        
        except Exception as e:
            logger.error(f"Error clearing variables: {e}")
            raise AutomationError(f"Error clearing variables: {e}")

    def substitute_variables(self, text: str) -> str:
        """
        Substitute variables in a text string.

        Args:
            text: Text with variable placeholders

        Returns:
            Text with variables substituted
        """
        try:
            # Match ${variable} or $variable patterns
            pattern = r'\$\{?([a-zA-Z_][a-zA-Z0-9_]*)\}?'
            
            def replace_match(match):
                var_name = match.group(1)
                var_value = self.get_variable(var_name, "")
                return str(var_value)
            
            # Replace all matches
            result = re.sub(pattern, replace_match, text)
            
            return result
        
        except Exception as e:
            logger.error(f"Error substituting variables in text: {e}")
            return text

    def evaluate_expression(self, expression: str) -> Any:
        """
        Evaluate an expression with variables.

        Args:
            expression: Expression to evaluate

        Returns:
            Result of evaluation
        """
        try:
            # Substitute variables first
            substituted = self.substitute_variables(expression)
            
            # Evaluate the expression
            # Note: This is a simplified evaluation for basic expressions
            # In a production system, you would want to use a proper expression evaluator
            try:
                # Try to evaluate as a Python expression
                result = eval(substituted, {"__builtins__": {}}, {})
                return result
            except:
                # If evaluation fails, return the substituted string
                return substituted
        
        except Exception as e:
            logger.error(f"Error evaluating expression '{expression}': {e}")
            return expression

    def get_variable_history(self, name: str) -> List[Dict[str, Any]]:
        """
        Get the history of a variable.

        Args:
            name: Variable name

        Returns:
            List of historical values
        """
        return self.variable_history.get(name, [])

    def export_variables(self, file_path: str, names: Optional[List[str]] = None) -> None:
        """
        Export variables to a file.

        Args:
            file_path: Path to export file
            names: List of variable names to export (None for all)
        """
        try:
            # Get variables to export
            if names is None:
                variables_to_export = self.variables.copy()
            else:
                variables_to_export = {name: self.get_variable(name) for name in names}
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Export to JSON
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(variables_to_export, f, indent=2, default=str)
            
            logger.info(f"Variables exported to: {file_path}")
        
        except Exception as e:
            logger.error(f"Error exporting variables: {e}")
            raise AutomationError(f"Error exporting variables: {e}")

    def import_variables(self, file_path: str, merge: bool = True) -> None:
        """
        Import variables from a file.

        Args:
            file_path: Path to import file
            merge: Whether to merge with existing variables
        """
        try:
            # Load variables from JSON
            with open(file_path, "r", encoding="utf-8") as f:
                imported_variables = json.load(f)
            
            # Import variables
            if not merge:
                self.clear_variables()
            
            for name, value in imported_variables.items():
                self.set_variable(name, value)
            
            logger.info(f"Variables imported from: {file_path}")
        
        except Exception as e:
            logger.error(f"Error importing variables: {e}")
            raise AutomationError(f"Error importing variables: {e}")

    def _persist_variable(self, name: str, value: Any) -> None:
        """
        Persist a variable to disk.

        Args:
            name: Variable name
            value: Variable value
        """
        try:
            # Create variables directory if it doesn't exist
            variables_dir = os.path.join(os.getcwd(), ".automata", "variables")
            os.makedirs(variables_dir, exist_ok=True)
            
            # Save variable to file
            file_path = os.path.join(variables_dir, f"{name}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(value, f, default=str)
        
        except Exception as e:
            logger.error(f"Error persisting variable '{name}': {e}")

    def _load_variable(self, name: str) -> Any:
        """
        Load a variable from disk.

        Args:
            name: Variable name

        Returns:
            Variable value or None if not found
        """
        try:
            # Check if variable file exists
            file_path = os.path.join(os.getcwd(), ".automata", "variables", f"{name}.json")
            if not os.path.exists(file_path):
                return None
            
            # Load variable from file
            with open(file_path, "r", encoding="utf-8") as f:
                value = json.load(f)
            
            return value
        
        except Exception as e:
            logger.error(f"Error loading variable '{name}': {e}")
            return None

    def _delete_persisted_variable(self, name: str) -> None:
        """
        Delete a persisted variable from disk.

        Args:
            name: Variable name
        """
        try:
            # Check if variable file exists
            file_path = os.path.join(os.getcwd(), ".automata", "variables", f"{name}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
        
        except Exception as e:
            logger.error(f"Error deleting persisted variable '{name}': {e}")

    def _list_persisted_variables(self) -> List[str]:
        """
        List all persisted variables.

        Returns:
            List of variable names
        """
        try:
            # Check if variables directory exists
            variables_dir = os.path.join(os.getcwd(), ".automata", "variables")
            if not os.path.exists(variables_dir):
                return []
            
            # List all JSON files in the directory
            variable_files = [f for f in os.listdir(variables_dir) if f.endswith(".json")]
            
            # Extract variable names (remove .json extension)
            variable_names = [f[:-5] for f in variable_files]
            
            return variable_names
        
        except Exception as e:
            logger.error(f"Error listing persisted variables: {e}")
            return []

    def _clear_persisted_variables(self) -> None:
        """
        Clear all persisted variables.
        """
        try:
            # Check if variables directory exists
            variables_dir = os.path.join(os.getcwd(), ".automata", "variables")
            if not os.path.exists(variables_dir):
                return
            
            # Remove all JSON files in the directory
            for filename in os.listdir(variables_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(variables_dir, filename)
                    os.remove(file_path)
        
        except Exception as e:
            logger.error(f"Error clearing persisted variables: {e}")

    def create_variable_from_regex(self, name: str, text: str, pattern: str, group: int = 0) -> bool:
        """
        Create a variable from a regex match.

        Args:
            name: Variable name
            text: Text to search in
            pattern: Regex pattern
            group: Regex group to extract

        Returns:
            True if variable was created, False otherwise
        """
        try:
            # Compile regex pattern
            regex = re.compile(pattern)
            
            # Search for pattern
            match = regex.search(text)
            
            if match:
                # Extract group
                value = match.group(group)
                
                # Set variable
                self.set_variable(name, value)
                
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error creating variable '{name}' from regex: {e}")
            return False

    def create_variable_from_json_path(self, name: str, json_data: Union[str, Dict], path: str) -> bool:
        """
        Create a variable from a JSON path.

        Args:
            name: Variable name
            json_data: JSON data (string or dict)
            path: JSON path (e.g., "user.address.city")

        Returns:
            True if variable was created, False otherwise
        """
        try:
            # Parse JSON if it's a string
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
            
            # Navigate path
            keys = path.split(".")
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return False
            
            # Set variable
            self.set_variable(name, value)
            
            return True
        
        except Exception as e:
            logger.error(f"Error creating variable '{name}' from JSON path: {e}")
            return False

    def increment_variable(self, name: str, increment: int = 1) -> int:
        """
        Increment a numeric variable.

        Args:
            name: Variable name
            increment: Increment value

        Returns:
            New variable value
        """
        try:
            # Get current value
            current = self.get_variable(name, 0)
            
            # Ensure it's a number
            if not isinstance(current, (int, float)):
                current = 0
            
            # Increment
            new_value = current + increment
            
            # Set variable
            self.set_variable(name, new_value)
            
            return new_value
        
        except Exception as e:
            logger.error(f"Error incrementing variable '{name}': {e}")
            raise AutomationError(f"Error incrementing variable '{name}': {e}")

    def append_to_variable(self, name: str, value: Any, delimiter: str = "") -> Any:
        """
        Append a value to a variable.

        Args:
            name: Variable name
            value: Value to append
            delimiter: Delimiter to use (for strings)

        Returns:
            New variable value
        """
        try:
            # Get current value
            current = self.get_variable(name, "")
            
            # Append value
            if isinstance(current, str) and isinstance(value, str):
                new_value = current + delimiter + value
            elif isinstance(current, list):
                new_value = current + [value]
            else:
                # Convert to string and append
                new_value = str(current) + delimiter + str(value)
            
            # Set variable
            self.set_variable(name, new_value)
            
            return new_value
        
        except Exception as e:
            logger.error(f"Error appending to variable '{name}': {e}")
            raise AutomationError(f"Error appending to variable '{name}': {e}")
