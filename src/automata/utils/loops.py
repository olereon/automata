"""
Loop processor for repetitive tasks.
"""

import time
from typing import Dict, Any, Optional, List, Union, Callable, Iterator
from ..core.errors import AutomationError
from ..core.logger import get_logger
from .variables import VariableManager
from .conditional import ConditionalProcessor

logger = get_logger(__name__)


class LoopProcessor:
    """Processes loops for repetitive tasks."""

    def __init__(self, variable_manager: Optional[VariableManager] = None,
                 conditional_processor: Optional[ConditionalProcessor] = None):
        """
        Initialize the loop processor.

        Args:
            variable_manager: Variable manager instance
            conditional_processor: Conditional processor instance
        """
        self.variable_manager = variable_manager or VariableManager()
        self.conditional_processor = conditional_processor or ConditionalProcessor(self.variable_manager)

    def process_for_loop(self, loop_dict: Dict[str, Any]) -> List[Any]:
        """
        Process a FOR loop.

        Args:
            loop_dict: FOR loop dictionary

        Returns:
            List of results from each iteration

        Raises:
            AutomationError: If FOR loop cannot be processed
        """
        try:
            # Get loop parameters
            loop_var = loop_dict.get("var")
            start = loop_dict.get("start")
            end = loop_dict.get("end")
            step = loop_dict.get("step", 1)
            actions = loop_dict.get("actions")
            
            if loop_var is None:
                raise AutomationError("Missing loop variable")
            
            if start is None:
                raise AutomationError("Missing loop start value")
            
            if end is None:
                raise AutomationError("Missing loop end value")
            
            if actions is None:
                raise AutomationError("Missing loop actions")
            
            # Substitute variables in parameters
            if isinstance(start, str):
                start = self.variable_manager.substitute_variables(start)
            
            if isinstance(end, str):
                end = self.variable_manager.substitute_variables(end)
            
            if isinstance(step, str):
                step = self.variable_manager.substitute_variables(step)
            
            # Evaluate expressions if needed
            if isinstance(start, str) and start.startswith("${") and start.endswith("}"):
                start = self.variable_manager.evaluate_expression(start[2:-1])
            
            if isinstance(end, str) and end.startswith("${") and end.endswith("}"):
                end = self.variable_manager.evaluate_expression(end[2:-1])
            
            if isinstance(step, str) and step.startswith("${") and step.endswith("}"):
                step = self.variable_manager.evaluate_expression(step[2:-1])
            
            # Convert to appropriate types
            try:
                start = int(start)
                end = int(end)
                step = int(step)
            except (ValueError, TypeError):
                raise AutomationError("Invalid loop parameters: must be integers")
            
            # Process loop
            results = []
            for i in range(start, end, step):
                # Set loop variable
                self.variable_manager.set_variable(loop_var, i)
                
                # Process actions
                result = self._process_actions(actions)
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error processing FOR loop: {e}")
            raise AutomationError(f"Error processing FOR loop: {e}")

    def process_for_each_loop(self, loop_dict: Dict[str, Any]) -> List[Any]:
        """
        Process a FOR EACH loop.

        Args:
            loop_dict: FOR EACH loop dictionary

        Returns:
            List of results from each iteration

        Raises:
            AutomationError: If FOR EACH loop cannot be processed
        """
        try:
            # Get loop parameters
            loop_var = loop_dict.get("var")
            items = loop_dict.get("items")
            actions = loop_dict.get("actions")
            
            if loop_var is None:
                raise AutomationError("Missing loop variable")
            
            if items is None:
                raise AutomationError("Missing loop items")
            
            if actions is None:
                raise AutomationError("Missing loop actions")
            
            # Substitute variables in items
            if isinstance(items, str):
                items = self.variable_manager.substitute_variables(items)
            
            # Evaluate expression if needed
            if isinstance(items, str) and items.startswith("${") and items.endswith("}"):
                items = self.variable_manager.evaluate_expression(items[2:-1])
            
            # Ensure items is iterable
            if not isinstance(items, (list, tuple, set, dict)):
                if isinstance(items, str):
                    # Split string by comma if it's a string
                    items = [item.strip() for item in items.split(",")]
                else:
                    # Convert to list
                    items = [items]
            
            # Process loop
            results = []
            for index, item in enumerate(items):
                # Set loop variables
                self.variable_manager.set_variable(loop_var, item)
                self.variable_manager.set_variable(f"{loop_var}_index", index)
                
                # Process actions
                result = self._process_actions(actions)
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error processing FOR EACH loop: {e}")
            raise AutomationError(f"Error processing FOR EACH loop: {e}")

    def process_while_loop(self, loop_dict: Dict[str, Any]) -> List[Any]:
        """
        Process a WHILE loop.

        Args:
            loop_dict: WHILE loop dictionary

        Returns:
            List of results from each iteration

        Raises:
            AutomationError: If WHILE loop cannot be processed
        """
        try:
            # Get loop parameters
            condition = loop_dict.get("condition")
            actions = loop_dict.get("actions")
            max_iterations = loop_dict.get("max_iterations", 1000)
            
            if condition is None:
                raise AutomationError("Missing loop condition")
            
            if actions is None:
                raise AutomationError("Missing loop actions")
            
            # Process loop
            results = []
            iteration = 0
            
            while self._evaluate_condition(condition) and iteration < max_iterations:
                # Set iteration variable
                self.variable_manager.set_variable("loop_iteration", iteration)
                
                # Process actions
                result = self._process_actions(actions)
                results.append(result)
                
                # Increment iteration
                iteration += 1
            
            if iteration >= max_iterations:
                logger.warning(f"WHILE loop reached maximum iterations: {max_iterations}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error processing WHILE loop: {e}")
            raise AutomationError(f"Error processing WHILE loop: {e}")

    def process_do_while_loop(self, loop_dict: Dict[str, Any]) -> List[Any]:
        """
        Process a DO WHILE loop.

        Args:
            loop_dict: DO WHILE loop dictionary

        Returns:
            List of results from each iteration

        Raises:
            AutomationError: If DO WHILE loop cannot be processed
        """
        try:
            # Get loop parameters
            condition = loop_dict.get("condition")
            actions = loop_dict.get("actions")
            max_iterations = loop_dict.get("max_iterations", 1000)
            
            if condition is None:
                raise AutomationError("Missing loop condition")
            
            if actions is None:
                raise AutomationError("Missing loop actions")
            
            # Process loop
            results = []
            iteration = 0
            
            # Execute at least once
            while True:
                # Set iteration variable
                self.variable_manager.set_variable("loop_iteration", iteration)
                
                # Process actions
                result = self._process_actions(actions)
                results.append(result)
                
                # Increment iteration
                iteration += 1
                
                # Check condition and max iterations
                if not self._evaluate_condition(condition) or iteration >= max_iterations:
                    break
            
            if iteration >= max_iterations:
                logger.warning(f"DO WHILE loop reached maximum iterations: {max_iterations}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error processing DO WHILE loop: {e}")
            raise AutomationError(f"Error processing DO WHILE loop: {e}")

    def process_repeat_loop(self, loop_dict: Dict[str, Any]) -> List[Any]:
        """
        Process a REPEAT loop.

        Args:
            loop_dict: REPEAT loop dictionary

        Returns:
            List of results from each iteration

        Raises:
            AutomationError: If REPEAT loop cannot be processed
        """
        try:
            # Get loop parameters
            times = loop_dict.get("times")
            actions = loop_dict.get("actions")
            
            if times is None:
                raise AutomationError("Missing loop times")
            
            if actions is None:
                raise AutomationError("Missing loop actions")
            
            # Substitute variables in times
            if isinstance(times, str):
                times = self.variable_manager.substitute_variables(times)
            
            # Evaluate expression if needed
            if isinstance(times, str) and times.startswith("${") and times.endswith("}"):
                times = self.variable_manager.evaluate_expression(times[2:-1])
            
            # Convert to integer
            try:
                times = int(times)
            except (ValueError, TypeError):
                raise AutomationError("Invalid loop times: must be an integer")
            
            # Process loop
            results = []
            for i in range(times):
                # Set iteration variable
                self.variable_manager.set_variable("loop_iteration", i)
                
                # Process actions
                result = self._process_actions(actions)
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Error processing REPEAT loop: {e}")
            raise AutomationError(f"Error processing REPEAT loop: {e}")

    def process_until_loop(self, loop_dict: Dict[str, Any]) -> List[Any]:
        """
        Process an UNTIL loop.

        Args:
            loop_dict: UNTIL loop dictionary

        Returns:
            List of results from each iteration

        Raises:
            AutomationError: If UNTIL loop cannot be processed
        """
        try:
            # Get loop parameters
            condition = loop_dict.get("condition")
            actions = loop_dict.get("actions")
            max_iterations = loop_dict.get("max_iterations", 1000)
            
            if condition is None:
                raise AutomationError("Missing loop condition")
            
            if actions is None:
                raise AutomationError("Missing loop actions")
            
            # Process loop
            results = []
            iteration = 0
            
            while not self._evaluate_condition(condition) and iteration < max_iterations:
                # Set iteration variable
                self.variable_manager.set_variable("loop_iteration", iteration)
                
                # Process actions
                result = self._process_actions(actions)
                results.append(result)
                
                # Increment iteration
                iteration += 1
            
            if iteration >= max_iterations:
                logger.warning(f"UNTIL loop reached maximum iterations: {max_iterations}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error processing UNTIL loop: {e}")
            raise AutomationError(f"Error processing UNTIL loop: {e}")

    def process_loop_with_timeout(self, loop_dict: Dict[str, Any]) -> List[Any]:
        """
        Process a loop with a timeout.

        Args:
            loop_dict: Loop dictionary with timeout

        Returns:
            List of results from each iteration

        Raises:
            AutomationError: If loop cannot be processed
        """
        try:
            # Get loop parameters
            loop_type = loop_dict.get("type")
            timeout = loop_dict.get("timeout", 60)  # Default timeout: 60 seconds
            
            if loop_type is None:
                raise AutomationError("Missing loop type")
            
            if timeout is None:
                raise AutomationError("Missing loop timeout")
            
            # Substitute variables in timeout
            if isinstance(timeout, str):
                timeout = self.variable_manager.substitute_variables(timeout)
            
            # Evaluate expression if needed
            if isinstance(timeout, str) and timeout.startswith("${") and timeout.endswith("}"):
                timeout = self.variable_manager.evaluate_expression(timeout[2:-1])
            
            # Convert to float
            try:
                timeout = float(timeout)
            except (ValueError, TypeError):
                raise AutomationError("Invalid loop timeout: must be a number")
            
            # Process loop with timeout
            start_time = time.time()
            results = []
            
            while time.time() - start_time < timeout:
                # Process one iteration based on loop type
                if loop_type == "for":
                    # Create a copy of the loop dict for one iteration
                    for_loop_dict = loop_dict.copy()
                    for_loop_dict.pop("type")
                    for_loop_dict.pop("timeout")
                    
                    # Process the FOR loop for one iteration
                    # This is a simplified approach - in a real implementation,
                    # you would need to track the loop state between iterations
                    result = self.process_for_loop(for_loop_dict)
                    results.append(result)
                    break
                
                elif loop_type == "while":
                    # Create a copy of the loop dict for one iteration
                    while_loop_dict = loop_dict.copy()
                    while_loop_dict.pop("type")
                    while_loop_dict.pop("timeout")
                    
                    # Check condition
                    condition = while_loop_dict.get("condition")
                    if not self._evaluate_condition(condition):
                        break
                    
                    # Process actions
                    actions = while_loop_dict.get("actions")
                    result = self._process_actions(actions)
                    results.append(result)
                
                elif loop_type == "for_each":
                    # Create a copy of the loop dict for one iteration
                    for_each_loop_dict = loop_dict.copy()
                    for_each_loop_dict.pop("type")
                    for_each_loop_dict.pop("timeout")
                    
                    # This is a simplified approach - in a real implementation,
                    # you would need to track the loop state between iterations
                    result = self.process_for_each_loop(for_each_loop_dict)
                    results.append(result)
                    break
                
                else:
                    raise AutomationError(f"Unknown loop type: {loop_type}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error processing loop with timeout: {e}")
            raise AutomationError(f"Error processing loop with timeout: {e}")

    def _evaluate_condition(self, condition: Union[Dict, List]) -> bool:
        """
        Evaluate a condition.

        Args:
            condition: Condition dictionary or list

        Returns:
            True if condition is met, False otherwise
        """
        if isinstance(condition, dict):
            return self.conditional_processor.evaluate_condition(condition)
        elif isinstance(condition, list):
            return self.conditional_processor.evaluate_conditions(condition, "AND")
        else:
            raise AutomationError(f"Invalid condition format: {type(condition)}")

    def _process_actions(self, actions: Any) -> Any:
        """
        Process a block of actions.

        Args:
            actions: Actions to process

        Returns:
            Result of processing
        """
        # This is a placeholder for processing actions
        # In a real implementation, this would delegate to an action processor
        return actions

    def create_for_loop(self, var: str, start: Any, end: Any, step: Any = 1,
                       actions: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a FOR loop dictionary.

        Args:
            var: Loop variable name
            start: Start value
            end: End value
            step: Step value
            actions: Actions to execute

        Returns:
            FOR loop dictionary
        """
        loop_dict = {
            "type": "for",
            "var": var,
            "start": start,
            "end": end,
            "step": step,
            "actions": actions
        }
        
        return loop_dict

    def create_for_each_loop(self, var: str, items: Any,
                            actions: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a FOR EACH loop dictionary.

        Args:
            var: Loop variable name
            items: Items to iterate over
            actions: Actions to execute

        Returns:
            FOR EACH loop dictionary
        """
        loop_dict = {
            "type": "for_each",
            "var": var,
            "items": items,
            "actions": actions
        }
        
        return loop_dict

    def create_while_loop(self, condition: Union[Dict, List], actions: Optional[Any] = None,
                         max_iterations: int = 1000) -> Dict[str, Any]:
        """
        Create a WHILE loop dictionary.

        Args:
            condition: Loop condition
            actions: Actions to execute
            max_iterations: Maximum iterations

        Returns:
            WHILE loop dictionary
        """
        loop_dict = {
            "type": "while",
            "condition": condition,
            "actions": actions,
            "max_iterations": max_iterations
        }
        
        return loop_dict

    def create_do_while_loop(self, condition: Union[Dict, List], actions: Optional[Any] = None,
                            max_iterations: int = 1000) -> Dict[str, Any]:
        """
        Create a DO WHILE loop dictionary.

        Args:
            condition: Loop condition
            actions: Actions to execute
            max_iterations: Maximum iterations

        Returns:
            DO WHILE loop dictionary
        """
        loop_dict = {
            "type": "do_while",
            "condition": condition,
            "actions": actions,
            "max_iterations": max_iterations
        }
        
        return loop_dict

    def create_repeat_loop(self, times: int, actions: Optional[Any] = None) -> Dict[str, Any]:
        """
        Create a REPEAT loop dictionary.

        Args:
            times: Number of times to repeat
            actions: Actions to execute

        Returns:
            REPEAT loop dictionary
        """
        loop_dict = {
            "type": "repeat",
            "times": times,
            "actions": actions
        }
        
        return loop_dict

    def create_until_loop(self, condition: Union[Dict, List], actions: Optional[Any] = None,
                         max_iterations: int = 1000) -> Dict[str, Any]:
        """
        Create an UNTIL loop dictionary.

        Args:
            condition: Loop condition
            actions: Actions to execute
            max_iterations: Maximum iterations

        Returns:
            UNTIL loop dictionary
        """
        loop_dict = {
            "type": "until",
            "condition": condition,
            "actions": actions,
            "max_iterations": max_iterations
        }
        
        return loop_dict

    def create_loop_with_timeout(self, loop_type: str, timeout: float,
                                loop_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a loop with timeout dictionary.

        Args:
            loop_type: Type of loop (for, while, for_each)
            timeout: Timeout in seconds
            loop_params: Loop parameters

        Returns:
            Loop with timeout dictionary
        """
        loop_dict = {
            "type": loop_type,
            "timeout": timeout
        }
        
        # Add loop parameters
        loop_dict.update(loop_params)
        
        return loop_dict
