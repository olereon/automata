"""
Conditional logic processor (IF/ELSE statements).
"""

import json
import re
from typing import Dict, Any, Optional, List, Union, Tuple, Callable
from ..core.errors import AutomationError
from ..core.logger import get_logger
from .variables import VariableManager

logger = get_logger(__name__)


class ConditionalProcessor:
    """Processes conditional logic (IF/ELSE statements)."""

    def __init__(self, variable_manager: Optional[VariableManager] = None):
        """
        Initialize the conditional processor.

        Args:
            variable_manager: Variable manager instance
        """
        self.variable_manager = variable_manager or VariableManager()
        self.operators = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            "contains": lambda a, b: b in a if isinstance(a, (str, list, dict)) else False,
            "not_contains": lambda a, b: b not in a if isinstance(a, (str, list, dict)) else True,
            "starts_with": lambda a, b: str(a).startswith(str(b)),
            "ends_with": lambda a, b: str(a).endswith(str(b)),
            "matches": lambda a, b: bool(re.search(str(b), str(a))),
            "exists": lambda a, b: a is not None,
            "not_exists": lambda a, b: a is None,
            "is_true": lambda a, b: bool(a),
            "is_false": lambda a, b: not bool(a),
            "in": lambda a, b: a in b if isinstance(b, (list, dict, set, tuple)) else False,
            "not_in": lambda a, b: a not in b if isinstance(b, (list, dict, set, tuple)) else True,
        }

    def evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Evaluate a condition.

        Args:
            condition: Condition dictionary

        Returns:
            True if condition is met, False otherwise

        Raises:
            AutomationError: If condition cannot be evaluated
        """
        try:
            # Get condition parts
            left = condition.get("left")
            operator = condition.get("operator")
            right = condition.get("right")
            
            # Substitute variables
            if isinstance(left, str):
                left = self.variable_manager.substitute_variables(left)
            
            if isinstance(right, str):
                right = self.variable_manager.substitute_variables(right)
            
            # Evaluate expressions
            if isinstance(left, str) and left.startswith("${") and left.endswith("}"):
                left = self.variable_manager.evaluate_expression(left[2:-1])
            
            if isinstance(right, str) and right.startswith("${") and right.endswith("}"):
                right = self.variable_manager.evaluate_expression(right[2:-1])
            
            # Get operator function
            if operator not in self.operators:
                raise AutomationError(f"Unknown operator: {operator}")
            
            op_func = self.operators[operator]
            
            # Evaluate condition
            result = op_func(left, right)
            
            logger.debug(f"Condition evaluated: {left} {operator} {right} = {result}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            raise AutomationError(f"Error evaluating condition: {e}")

    def evaluate_conditions(self, conditions: List[Dict[str, Any]], logic: str = "AND") -> bool:
        """
        Evaluate multiple conditions with logic.

        Args:
            conditions: List of condition dictionaries
            logic: Logic to use (AND, OR)

        Returns:
            True if conditions are met, False otherwise

        Raises:
            AutomationError: If conditions cannot be evaluated
        """
        try:
            if not conditions:
                return True
            
            if logic.upper() == "AND":
                result = True
                for condition in conditions:
                    if not self.evaluate_condition(condition):
                        result = False
                        break
            elif logic.upper() == "OR":
                result = False
                for condition in conditions:
                    if self.evaluate_condition(condition):
                        result = True
                        break
            else:
                raise AutomationError(f"Unknown logic: {logic}")
            
            logger.debug(f"Conditions evaluated with {logic} logic: {result}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error evaluating conditions: {e}")
            raise AutomationError(f"Error evaluating conditions: {e}")

    def process_if_else(self, if_else_dict: Dict[str, Any]) -> Any:
        """
        Process an IF/ELSE structure.

        Args:
            if_else_dict: IF/ELSE dictionary

        Returns:
            Result of processing

        Raises:
            AutomationError: If IF/ELSE cannot be processed
        """
        try:
            # Get IF condition
            if_condition = if_else_dict.get("if")
            
            if if_condition is None:
                raise AutomationError("Missing IF condition")
            
            # Evaluate IF condition
            if isinstance(if_condition, dict):
                # Single condition
                if_result = self.evaluate_condition(if_condition)
            elif isinstance(if_condition, list):
                # Multiple conditions with AND logic
                if_result = self.evaluate_conditions(if_condition, "AND")
            else:
                raise AutomationError("Invalid IF condition format")
            
            # Process based on result
            if if_result:
                # Process THEN block
                then_block = if_else_dict.get("then")
                if then_block is not None:
                    return self._process_block(then_block)
            else:
                # Process ELSE IF blocks
                elif_blocks = if_else_dict.get("elif", [])
                for elif_block in elif_blocks:
                    elif_condition = elif_block.get("if")
                    
                    if isinstance(elif_condition, dict):
                        elif_result = self.evaluate_condition(elif_condition)
                    elif isinstance(elif_condition, list):
                        elif_result = self.evaluate_conditions(elif_condition, "AND")
                    else:
                        raise AutomationError("Invalid ELIF condition format")
                    
                    if elif_result:
                        then_block = elif_block.get("then")
                        if then_block is not None:
                            return self._process_block(then_block)
                        break
                
                # Process ELSE block
                else_block = if_else_dict.get("else")
                if else_block is not None:
                    return self._process_block(else_block)
            
            return None
        
        except Exception as e:
            logger.error(f"Error processing IF/ELSE: {e}")
            raise AutomationError(f"Error processing IF/ELSE: {e}")

    def process_switch_case(self, switch_dict: Dict[str, Any]) -> Any:
        """
        Process a SWITCH/CASE structure.

        Args:
            switch_dict: SWITCH/CASE dictionary

        Returns:
            Result of processing

        Raises:
            AutomationError: If SWITCH/CASE cannot be processed
        """
        try:
            # Get switch value
            switch_value = switch_dict.get("switch")
            
            if switch_value is None:
                raise AutomationError("Missing SWITCH value")
            
            # Substitute variables
            if isinstance(switch_value, str):
                switch_value = self.variable_manager.substitute_variables(switch_value)
            
            # Evaluate expression if needed
            if isinstance(switch_value, str) and switch_value.startswith("${") and switch_value.endswith("}"):
                switch_value = self.variable_manager.evaluate_expression(switch_value[2:-1])
            
            # Process CASE blocks
            case_blocks = switch_dict.get("cases", [])
            for case_block in case_blocks:
                case_value = case_block.get("case")
                
                # Substitute variables
                if isinstance(case_value, str):
                    case_value = self.variable_manager.substitute_variables(case_value)
                
                # Evaluate expression if needed
                if isinstance(case_value, str) and case_value.startswith("${") and case_value.endswith("}"):
                    case_value = self.variable_manager.evaluate_expression(case_value[2:-1])
                
                # Check if values match
                if switch_value == case_value:
                    then_block = case_block.get("then")
                    if then_block is not None:
                        return self._process_block(then_block)
                    break
            
            # Process DEFAULT block
            default_block = switch_dict.get("default")
            if default_block is not None:
                return self._process_block(default_block)
            
            return None
        
        except Exception as e:
            logger.error(f"Error processing SWITCH/CASE: {e}")
            raise AutomationError(f"Error processing SWITCH/CASE: {e}")

    def _process_block(self, block: Any) -> Any:
        """
        Process a block of actions.

        Args:
            block: Block to process

        Returns:
            Result of processing
        """
        # This is a placeholder for processing actions
        # In a real implementation, this would delegate to an action processor
        return block

    def add_custom_operator(self, name: str, func: Callable[[Any, Any], bool]) -> None:
        """
        Add a custom operator.

        Args:
            name: Operator name
            func: Operator function
        """
        self.operators[name] = func
        logger.debug(f"Added custom operator: {name}")

    def remove_custom_operator(self, name: str) -> bool:
        """
        Remove a custom operator.

        Args:
            name: Operator name

        Returns:
            True if operator was removed, False otherwise
        """
        if name in self.operators and name not in [
            "==", "!=", ">", ">=", "<", "<=", "contains", "not_contains",
            "starts_with", "ends_with", "matches", "exists", "not_exists",
            "is_true", "is_false", "in", "not_in"
        ]:
            del self.operators[name]
            logger.debug(f"Removed custom operator: {name}")
            return True
        return False

    def list_operators(self) -> List[str]:
        """
        List all available operators.

        Returns:
            List of operator names
        """
        return list(self.operators.keys())

    def parse_condition_string(self, condition_str: str) -> Dict[str, Any]:
        """
        Parse a condition string into a condition dictionary.

        Args:
            condition_str: Condition string (e.g., "var1 == var2")

        Returns:
            Condition dictionary

        Raises:
            AutomationError: If condition string cannot be parsed
        """
        try:
            # Trim whitespace
            condition_str = condition_str.strip()
            
            # Find operator
            operator = None
            for op in sorted(self.operators.keys(), key=len, reverse=True):
                if op in condition_str:
                    operator = op
                    break
            
            if operator is None:
                raise AutomationError(f"No operator found in condition: {condition_str}")
            
            # Split into left and right
            parts = condition_str.split(operator, 1)
            if len(parts) != 2:
                raise AutomationError(f"Invalid condition format: {condition_str}")
            
            left = parts[0].strip()
            right = parts[1].strip()
            
            # Create condition dictionary
            condition = {
                "left": left,
                "operator": operator,
                "right": right
            }
            
            return condition
        
        except Exception as e:
            logger.error(f"Error parsing condition string: {e}")
            raise AutomationError(f"Error parsing condition string: {e}")

    def create_condition(self, left: Any, operator: str, right: Any) -> Dict[str, Any]:
        """
        Create a condition dictionary.

        Args:
            left: Left value
            operator: Operator
            right: Right value

        Returns:
            Condition dictionary

        Raises:
            AutomationError: If operator is not valid
        """
        if operator not in self.operators:
            raise AutomationError(f"Unknown operator: {operator}")
        
        return {
            "left": left,
            "operator": operator,
            "right": right
        }

    def create_if_else(self, if_condition: Union[Dict, List], then_block: Any,
                      elif_blocks: Optional[List[Dict]] = None, else_block: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create an IF/ELSE dictionary.

        Args:
            if_condition: IF condition
            then_block: THEN block
            elif_blocks: ELIF blocks (optional)
            else_block: ELSE block (optional)

        Returns:
            IF/ELSE dictionary
        """
        if_else_dict = {
            "if": if_condition,
            "then": then_block
        }
        
        if elif_blocks:
            if_else_dict["elif"] = elif_blocks
        
        if else_block:
            if_else_dict["else"] = else_block
        
        return if_else_dict

    def create_switch_case(self, switch_value: Any, cases: List[Dict],
                          default_block: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a SWITCH/CASE dictionary.

        Args:
            switch_value: SWITCH value
            cases: CASE blocks
            default_block: DEFAULT block (optional)

        Returns:
            SWITCH/CASE dictionary
        """
        switch_dict = {
            "switch": switch_value,
            "cases": cases
        }
        
        if default_block:
            switch_dict["default"] = default_block
        
        return switch_dict

    def create_case(self, case_value: Any, then_block: Any) -> Dict[str, Any]:
        """
        Create a CASE dictionary.

        Args:
            case_value: CASE value
            then_block: THEN block

        Returns:
            CASE dictionary
        """
        return {
            "case": case_value,
            "then": then_block
        }
