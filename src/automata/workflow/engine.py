"""
Workflow execution engine.
"""

import asyncio
import json
import os
import time
from typing import Dict, Any, List, Optional, Union, Callable
from playwright.async_api import Page, Browser, BrowserContext
from ..core.errors import AutomationError
from ..core.logger import get_logger
from ..core.engine import AutomationEngine
from ..core.browser import BrowserManager
from ..utils import FileIO
from ..utils import VariableManager
from ..utils import ConditionalProcessor
from ..utils import LoopProcessor
from ..core.wait import WaitUtils
from ..tools import HTMLParser
from ..tools import SelectorGenerator
from ..tools import ActionBuilder
from .schema import WorkflowSchema
from .validator import WorkflowValidator

logger = get_logger(__name__)


class WorkflowExecutionEngine:
    """Executes automation workflows."""

    def __init__(self,
                 browser_manager: Optional[BrowserManager] = None,
                 wait_utils: Optional[WaitUtils] = None,
                 html_parser: Optional[HTMLParser] = None,
                 selector_generator: Optional[SelectorGenerator] = None,
                 action_builder: Optional[ActionBuilder] = None,
                 file_io: Optional[FileIO] = None,
                 variable_manager: Optional[VariableManager] = None,
                 conditional_processor: Optional[ConditionalProcessor] = None,
                 loop_processor: Optional[LoopProcessor] = None,
                 schema: Optional[WorkflowSchema] = None,
                 validator: Optional[WorkflowValidator] = None):
        """
        Initialize the workflow execution engine.

        Args:
            browser_manager: Browser manager instance
            session_manager: Session manager instance
            wait_manager: Wait manager instance
            element_selector: Element selector instance
            variable_manager: Variable manager instance
            condition_processor: Condition processor instance
            loop_processor: Loop processor instance
            schema: Workflow schema instance
            validator: Workflow validator instance
        """
        self.browser_manager = browser_manager or BrowserManager()
        self.wait_utils = wait_utils or WaitUtils()
        self.html_parser = html_parser or HTMLParser()
        self.selector_generator = selector_generator or SelectorGenerator()
        self.action_builder = action_builder or ActionBuilder()
        self.file_io = file_io or FileIO()
        self.variable_manager = variable_manager or VariableManager()
        self.conditional_processor = conditional_processor or ConditionalProcessor(self.variable_manager)
        self.loop_processor = loop_processor or LoopProcessor(self.variable_manager, self.conditional_processor)
        self.schema = schema or WorkflowSchema()
        self.validator = validator or WorkflowValidator(self.schema)
        
        # Execution state
        self.workflow = None
        self.current_step_index = 0
        self.execution_context = {}
        self.execution_results = []
        self.browser = None
        self.context = None
        self.page = None
        self.is_running = False
        self.is_paused = False
        self.should_stop = False
        self.skip_cleanup = False
        
        # Action handlers
        self.action_handlers = {
            "navigate": self._handle_navigate,
            "click": self._handle_click,
            "type": self._handle_type,
            "hover": self._handle_hover,
            "wait_for": self._handle_wait_for,
            "wait": self._handle_wait,
            "get_text": self._handle_get_text,
            "get_attribute": self._handle_get_attribute,
            "screenshot": self._handle_screenshot,
            "execute_script": self._handle_execute_script,
            "evaluate": self._handle_evaluate,
            "extract": self._handle_extract,
            "save": self._handle_save,
            "load": self._handle_load,
            "set_variable": self._handle_set_variable,
            "if": self._handle_if,
            "loop": self._handle_loop,
            "goto": self._handle_goto,
            "stop": self._handle_stop,
            "pause": self._handle_pause,
            "resume": self._handle_resume
        }

    async def execute_workflow(self, workflow: Dict[str, Any], variables: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a workflow.

        Args:
            workflow: Workflow dictionary
            variables: Initial variables

        Returns:
            List of execution results
        """
        try:
            # Validate workflow before execution
            if not self.validator.validate_workflow(workflow):
                raise AutomationError("Cannot execute invalid workflow")
            
            # Initialize execution state
            self.workflow = workflow
            self.current_step_index = 0
            self.execution_context = {}
            self.execution_results = []
            self.is_running = True
            self.is_paused = False
            self.should_stop = False
            
            # Set up browser and page
            await self._setup_browser()
            
            # Set up variables
            logger.info("WORKFLOW_SETUP: Setting up variables...")
            
            # Preserve credential variables before clearing
            credential_vars = {}
            for var_name in ["email", "password", "username", "token", "api_key"]:
                var_value = self.variable_manager.get_variable(var_name)
                if var_value is not None:
                    credential_vars[var_name] = var_value
                    logger.info(f"WORKFLOW_SETUP: Preserving credential variable '{var_name}'")
            
            # Clear all variables
            self.variable_manager.clear()
            
            # Restore credential variables
            if credential_vars:
                logger.info(f"WORKFLOW_SETUP: Restoring credential variables: {list(credential_vars.keys())}")
                self.variable_manager.set_variables(credential_vars)
            
            # Log workflow variables
            workflow_vars = workflow.get("variables", {})
            logger.info(f"WORKFLOW_SETUP: Workflow variables: {workflow_vars}")
            self.variable_manager.set_variables(workflow_vars)
            
            # Log additional variables
            if variables:
                logger.info(f"WORKFLOW_SETUP: Additional variables: {variables}")
                self.variable_manager.set_variables(variables)
            
            # Log all variables after setup
            all_vars = self.variable_manager.list_variables()
            logger.info(f"WORKFLOW_SETUP: All variables after setup: {all_vars}")
            
            # Log workflow execution start
            logger.info(f"Starting execution of workflow '{workflow['name']}' v{workflow['version']}")
            
            # Execute steps
            steps = workflow.get("steps", [])
            while self.current_step_index < len(steps) and self.is_running and not self.should_stop:
                if self.is_paused:
                    await asyncio.sleep(0.1)
                    continue
                
                # Get current step
                step = steps[self.current_step_index]
                
                # Execute step
                result = await self._execute_step(step)
                
                # Add result to execution results
                self.execution_results.append(result)
                
                # Move to next step unless specified otherwise
                if result.get("next_step_index") is not None:
                    self.current_step_index = result["next_step_index"]
                else:
                    self.current_step_index += 1
            
            # Clean up
            await self._cleanup()
            
            # Log workflow execution completion
            logger.info(f"Completed execution of workflow '{workflow['name']}' v{workflow['version']}")
            
            return self.execution_results
        
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            await self._cleanup()
            raise AutomationError(f"Error executing workflow: {e}")

    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow step.

        Args:
            step: Step dictionary

        Returns:
            Step execution result
        """
        try:
            step_name = step.get("name", "")
            step_action = step.get("action", "")
            
            logger.info(f"Executing step '{step_name}' with action '{step_action}'")
            
            # Create step result
            result = {
                "step_name": step_name,
                "step_action": step_action,
                "start_time": time.time(),
                "status": "running",
                "error": None,
                "data": None,
                "next_step_index": None
            }
            
            try:
                # Check if step has a condition
                if "condition" in step:
                    condition_result = await self.conditional_processor.evaluate_condition(step["condition"])
                    if not condition_result:
                        logger.info(f"Step '{step_name}' condition not met, skipping")
                        result["status"] = "skipped"
                        result["end_time"] = time.time()
                        return result
                
                # Get action handler
                action_handler = self.action_handlers.get(step_action)
                if not action_handler:
                    raise AutomationError(f"Unknown action: {step_action}")
                
                # Execute action
                action_result = await action_handler(step)
                
                # Update result
                result["status"] = "completed"
                result["data"] = action_result
                
                # Check if step has a next_step
                if "next_step" in step and step["next_step"]:
                    next_step_name = step["next_step"]
                    next_step_index = self._find_step_index_by_name(next_step_name)
                    if next_step_index is not None:
                        result["next_step_index"] = next_step_index
                        logger.info(f"Step '{step_name}' will jump to step '{next_step_name}' (index {next_step_index})")
                
                logger.info(f"Step '{step_name}' completed successfully")
            
            except Exception as e:
                logger.error(f"Error executing step '{step_name}': {e}")
                result["status"] = "failed"
                result["error"] = str(e)
                
                # Handle step error based on on_error setting
                on_error = step.get("on_error", "stop")
                if on_error == "stop":
                    self.should_stop = True
                    logger.error(f"Stopping workflow execution due to error in step '{step_name}'")
                elif on_error == "retry":
                    retry_config = step.get("retry", {"max_attempts": 3, "delay": 1})
                    max_attempts = retry_config.get("max_attempts", 3)
                    delay = retry_config.get("delay", 1)
                    
                    # Get current retry count
                    retry_count = self.execution_context.get(f"{step_name}_retry_count", 0)
                    
                    if retry_count < max_attempts:
                        # Increment retry count
                        self.execution_context[f"{step_name}_retry_count"] = retry_count + 1
                        
                        # Wait before retry
                        logger.info(f"Retrying step '{step_name}' in {delay} seconds (attempt {retry_count + 1}/{max_attempts})")
                        await asyncio.sleep(delay)
                        
                        # Retry step
                        result["next_step_index"] = self.current_step_index
                    else:
                        # Max retries reached
                        logger.error(f"Max retries reached for step '{step_name}', stopping workflow execution")
                        self.should_stop = True
                elif on_error == "continue":
                    logger.warning(f"Continuing workflow execution despite error in step '{step_name}'")
            
            # Update end time
            result["end_time"] = time.time()
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing step '{step_name}': {e}")
            return {
                "step_name": step_name,
                "step_action": step_action,
                "start_time": time.time(),
                "end_time": time.time(),
                "status": "failed",
                "error": str(e),
                "data": None,
                "next_step_index": None
            }

    async def _setup_browser(self) -> None:
        """Set up browser and page for workflow execution."""
        try:
            # Start browser and create context
            await self.browser_manager.start()
            
            # Create page
            self.page = await self.browser_manager.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(30000)
            
            # Get browser and context from browser manager
            self.browser = self.browser_manager.browser
            self.context = self.browser_manager.context
            
            logger.info("Browser and page set up for workflow execution")
        
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            raise AutomationError(f"Error setting up browser: {e}")

    async def _cleanup(self) -> None:
        """Clean up after workflow execution."""
        logger.info("DEBUG: Workflow engine _cleanup() called")
        
        # Skip cleanup if requested (e.g., for session saving)
        if self.skip_cleanup:
            logger.info("DEBUG: Skipping cleanup as requested")
            return
            
        try:
            # Close page
            if self.page:
                logger.info("DEBUG: Closing page")
                await self.page.close()
                self.page = None
            
            # Close context
            if self.context:
                logger.info("DEBUG: Closing context")
                await self.context.close()
                self.context = None
            
            # Close browser
            if self.browser:
                logger.info("DEBUG: Closing browser")
                await self.browser.close()
                self.browser = None
            
            # Reset execution state
            self.is_running = False
            self.is_paused = False
            self.should_stop = False
            
            logger.info("DEBUG: Browser and page cleaned up after workflow execution")
            logger.info("Browser and page cleaned up after workflow execution")
        
        except Exception as e:
            logger.error(f"Error cleaning up browser: {e}")

    def _find_step_index_by_name(self, step_name: str) -> Optional[int]:
        """
        Find the index of a step by name.

        Args:
            step_name: Step name

        Returns:
            Step index or None if not found
        """
        if not self.workflow:
            return None
        
        steps = self.workflow.get("steps", [])
        for i, step in enumerate(steps):
            if step.get("name") == step_name:
                return i
        
        return None

    async def cleanup_browser(self) -> None:
        """
        Clean up browser resources when explicitly requested.
        This method should be called after session saving is complete.
        """
        logger.info("DEBUG: Workflow engine cleanup_browser() called")
        logger.info(f"DEBUG: cleanup_browser - Initial state - page: {self.page is not None}, context: {self.context is not None}, browser: {self.browser is not None}")
        
        try:
            # Close page
            if self.page:
                logger.info("DEBUG: cleanup_browser - Closing page...")
                await self.page.close()
                self.page = None
                logger.info("DEBUG: cleanup_browser - Page closed successfully")
            else:
                logger.info("DEBUG: cleanup_browser - No page to close")
            
            # Close context
            if self.context:
                logger.info("DEBUG: cleanup_browser - Closing context...")
                await self.context.close()
                self.context = None
                logger.info("DEBUG: cleanup_browser - Context closed successfully")
            else:
                logger.info("DEBUG: cleanup_browser - No context to close")
            
            # Close browser
            if self.browser:
                logger.info("DEBUG: cleanup_browser - Closing browser...")
                await self.browser.close()
                self.browser = None
                logger.info("DEBUG: cleanup_browser - Browser closed successfully")
            else:
                logger.info("DEBUG: cleanup_browser - No browser to close")
            
            # Reset execution state
            logger.info("DEBUG: cleanup_browser - Resetting execution state...")
            self.is_running = False
            self.is_paused = False
            self.should_stop = False
            logger.info("DEBUG: cleanup_browser - Execution state reset")
            
            logger.info("DEBUG: cleanup_browser - All browser resources cleaned up successfully")
            logger.info("Browser resources cleaned up")
        
        except Exception as e:
            logger.error(f"DEBUG: cleanup_browser - Error during cleanup: {e}")
            logger.error(f"DEBUG: cleanup_browser - Error type: {type(e).__name__}")
            import traceback
            logger.error(f"DEBUG: cleanup_browser - Traceback: {traceback.format_exc()}")
            raise

    # Action handlers
    async def _handle_navigate(self, step: Dict[str, Any]) -> Any:
        """
        Handle navigate action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        url = step.get("url", "") or step.get("value", "")
        if not url:
            raise AutomationError("URL is required for navigate action")
        
        # Substitute variables in URL
        url = self.variable_manager.substitute_variables(url)
        
        # Navigate to URL
        await self.page.goto(url)
        
        return {"url": url}

    async def _handle_click(self, step: Dict[str, Any]) -> Any:
        """
        Handle click action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        selector = step.get("selector", "")
        if not selector:
            raise AutomationError("Selector is required for click action")
        
        # Substitute variables in selector
        selector = self.variable_manager.substitute_variables(selector)
        
        # Click element
        await self.html_parser.click_element(self.page, selector)
        
        return {"selector": selector}

    async def _handle_type(self, step: Dict[str, Any]) -> Any:
        """
        Handle type action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        selector = step.get("selector", "")
        value = step.get("value", "")
        
        if not selector:
            raise AutomationError("Selector is required for type action")
        
        if value is None:
            raise AutomationError("Value is required for type action")
        
        # DEBUG: Log original values before substitution
        logger.info(f"TYPE_ACTION_DEBUG: Original selector: '{selector}', Original value: '{value}'")
        
        # List all available variables before substitution
        available_vars = self.variable_manager.list_variables()
        logger.info(f"TYPE_ACTION_DEBUG: Available variables before substitution: {available_vars}")
        
        # Substitute variables in selector and value
        selector = self.variable_manager.substitute_variables(selector)
        value = self.variable_manager.substitute_variables(str(value))
        
        # DEBUG: Log values after substitution
        logger.info(f"TYPE_ACTION_DEBUG: After substitution - selector: '{selector}', value: '{value}'")
        
        # Type value into element
        await self.html_parser.type_text(self.page, selector, value)
        
        return {"selector": selector, "value": value}

    async def _handle_hover(self, step: Dict[str, Any]) -> Any:
        """
        Handle hover action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        selector = step.get("selector", "")
        if not selector:
            raise AutomationError("Selector is required for hover action")
        
        # Substitute variables in selector
        selector = self.variable_manager.substitute_variables(selector)
        
        # Hover over element
        await self.html_parser.hover_element(self.page, selector)
        
        return {"selector": selector}

    async def _handle_wait_for(self, step: Dict[str, Any]) -> Any:
        """
        Handle wait_for action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        selector = step.get("selector", "")
        timeout = step.get("timeout", 30)
        
        if not selector:
            raise AutomationError("Selector is required for wait_for action")
        
        # Substitute variables in selector
        selector = self.variable_manager.substitute_variables(selector)
        
        # Wait for element
        await self.wait_utils.wait_for_selector(self.page, selector, timeout * 1000)
        
        return {"selector": selector, "timeout": timeout}

    async def _handle_wait(self, step: Dict[str, Any]) -> Any:
        """
        Handle wait action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        duration = step.get("value", 1)
        
        try:
            duration = float(duration)
        except (ValueError, TypeError):
            raise AutomationError("Duration must be a number for wait action")
        
        # Wait for specified duration
        await asyncio.sleep(duration)
        
        return {"duration": duration}

    async def _handle_get_text(self, step: Dict[str, Any]) -> Any:
        """
        Handle get_text action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        selector = step.get("selector", "")
        if not selector:
            raise AutomationError("Selector is required for get_text action")
        
        # Substitute variables in selector
        selector = self.variable_manager.substitute_variables(selector)
        
        # Get text from element
        text = await self.html_parser.get_text(self.page, selector)
        
        return {"selector": selector, "text": text}

    async def _handle_get_attribute(self, step: Dict[str, Any]) -> Any:
        """
        Handle get_attribute action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        selector = step.get("selector", "")
        attribute = step.get("value", "")
        
        if not selector:
            raise AutomationError("Selector is required for get_attribute action")
        
        if not attribute:
            raise AutomationError("Attribute is required for get_attribute action")
        
        # Substitute variables in selector and attribute
        selector = self.variable_manager.substitute_variables(selector)
        attribute = self.variable_manager.substitute_variables(attribute)
        
        # Get attribute from element
        attr_value = await self.html_parser.get_attribute(self.page, selector, attribute)
        
        return {"selector": selector, "attribute": attribute, "value": attr_value}

    async def _handle_screenshot(self, step: Dict[str, Any]) -> Any:
        """
        Handle screenshot action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        path = step.get("value", "screenshot.png")
        
        # Substitute variables in path
        path = self.variable_manager.substitute_variables(path)
        
        # Take screenshot
        await self.page.screenshot(path=path)
        
        return {"path": path}

    async def _handle_execute_script(self, step: Dict[str, Any]) -> Any:
        """
        Handle execute_script action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        script = step.get("value", "")
        if not script:
            raise AutomationError("Script is required for execute_script action")
        
        # Substitute variables in script
        script = self.variable_manager.substitute_variables(script)
        
        # Execute script
        result = await self.page.evaluate(script)
        
        return {"script": script, "result": result}

    async def _handle_evaluate(self, step: Dict[str, Any]) -> Any:
        """
        Handle evaluate action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        expression = step.get("value", "")
        if not expression:
            raise AutomationError("Expression is required for evaluate action")
        
        # Substitute variables in expression
        expression = self.variable_manager.substitute_variables(expression)
        
        # Evaluate expression
        result = await self.page.evaluate(expression)
        
        return {"expression": expression, "result": result}

    async def _handle_extract(self, step: Dict[str, Any]) -> Any:
        """
        Handle extract action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        selector = step.get("selector", "")
        config = step.get("value", {})
        
        if not selector:
            raise AutomationError("Selector is required for extract action")
        
        # Substitute variables in selector
        selector = self.variable_manager.substitute_variables(selector)
        
        # Extract data from elements
        data = await self.html_parser.extract_data(self.page, selector, config)
        
        return {"selector": selector, "data": data}

    async def _handle_save(self, step: Dict[str, Any]) -> Any:
        """
        Handle save action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        file_path = step.get("value", "")
        data = step.get("data", self.execution_results)
        
        if not file_path:
            raise AutomationError("File path is required for save action")
        
        # Substitute variables in file path
        file_path = self.variable_manager.substitute_variables(file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save data to file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        return {"file_path": file_path, "data": data}

    async def _handle_load(self, step: Dict[str, Any]) -> Any:
        """
        Handle load action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        file_path = step.get("value", "")
        if not file_path:
            raise AutomationError("File path is required for load action")
        
        # Substitute variables in file path
        file_path = self.variable_manager.substitute_variables(file_path)
        
        # Load data from file
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return {"file_path": file_path, "data": data}

    async def _handle_set_variable(self, step: Dict[str, Any]) -> Any:
        """
        Handle set_variable action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        name = step.get("selector", "")
        value = step.get("value", "")
        
        if not name:
            raise AutomationError("Variable name is required for set_variable action")
        
        # Substitute variables in name and value
        name = self.variable_manager.substitute_variables(name)
        value = self.variable_manager.substitute_variables(str(value))
        
        # Set variable
        self.variable_manager.set_variable(name, value)
        
        return {"name": name, "value": value}

    async def _handle_if(self, step: Dict[str, Any]) -> Any:
        """
        Handle if action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        condition = step.get("value", {})
        if not condition:
            raise AutomationError("Condition is required for if action")
        
        # Evaluate condition
        condition_result = await self.conditional_processor.evaluate_condition(condition)
        
        return {"condition": condition, "result": condition_result}

    async def _handle_loop(self, step: Dict[str, Any]) -> Any:
        """
        Handle loop action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        loop_config = step.get("value", {})
        if not loop_config:
            raise AutomationError("Loop configuration is required for loop action")
        
        # Execute loop
        loop_result = await self.loop_processor.execute_loop(loop_config, self._execute_step)
        
        return {"loop": loop_config, "result": loop_result}

    async def _handle_goto(self, step: Dict[str, Any]) -> Any:
        """
        Handle goto action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        step_name = step.get("value", "")
        if not step_name:
            raise AutomationError("Step name is required for goto action")
        
        # Find step index
        step_index = self._find_step_index_by_name(step_name)
        if step_index is None:
            raise AutomationError(f"Step '{step_name}' not found")
        
        return {"step_name": step_name, "step_index": step_index}

    async def _handle_stop(self, step: Dict[str, Any]) -> Any:
        """
        Handle stop action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        self.should_stop = True
        return {"action": "stop"}

    async def _handle_pause(self, step: Dict[str, Any]) -> Any:
        """
        Handle pause action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        self.is_paused = True
        return {"action": "pause"}

    async def _handle_resume(self, step: Dict[str, Any]) -> Any:
        """
        Handle resume action.

        Args:
            step: Step dictionary

        Returns:
            Action result
        """
        self.is_paused = False
        return {"action": "resume"}

    def get_execution_results(self) -> List[Dict[str, Any]]:
        """
        Get the execution results.

        Returns:
            List of execution results
        """
        return self.execution_results

    def is_execution_running(self) -> bool:
        """
        Check if execution is running.

        Returns:
            True if execution is running, False otherwise
        """
        return self.is_running

    def is_execution_paused(self) -> bool:
        """
        Check if execution is paused.

        Returns:
            True if execution is paused, False otherwise
        """
        return self.is_paused

    def pause_execution(self) -> None:
        """Pause the execution."""
        self.is_paused = True
        logger.info("Workflow execution paused")

    def resume_execution(self) -> None:
        """Resume the execution."""
        self.is_paused = False
        logger.info("Workflow execution resumed")

    def stop_execution(self) -> None:
        """Stop the execution."""
        self.should_stop = True
        logger.info("Workflow execution stop requested")

    def get_execution_status(self) -> Dict[str, Any]:
        """
        Get the execution status.

        Returns:
            Execution status dictionary
        """
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "should_stop": self.should_stop,
            "current_step_index": self.current_step_index,
            "total_steps": len(self.workflow.get("steps", [])) if self.workflow else 0,
            "execution_results_count": len(self.execution_results)
        }
