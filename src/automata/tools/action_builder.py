"""
Action builder tool for creating interaction commands.
"""

import json
from typing import Dict, Any, Optional, List, Union, Tuple
from enum import Enum
from ..core.errors import AutomationError
from ..core.logger import get_logger

logger = get_logger(__name__)


class ActionType(Enum):
    """Enumeration of supported action types."""
    NAVIGATE = "navigate"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    HOVER = "hover"
    FILL = "fill"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    UPLOAD_FILE = "upload_file"
    PRESS_KEY = "press_key"
    WAIT_FOR = "wait_for"
    WAIT_FOR_NAVIGATION = "wait_for_navigation"
    SCREENSHOT = "screenshot"
    EXECUTE_SCRIPT = "execute_script"
    SWITCH_TO_FRAME = "switch_to_frame"
    SWITCH_TO_PARENT_FRAME = "switch_to_parent_frame"
    SWITCH_TO_DEFAULT_CONTENT = "switch_to_default_content"


class ActionBuilder:
    """Builds interaction commands for web automation."""

    def __init__(self):
        """Initialize the action builder."""
        self.actions = []
        self.current_action = None

    def navigate(self, url: str, timeout: Optional[int] = None) -> 'ActionBuilder':
        """
        Add a navigate action.

        Args:
            url: URL to navigate to
            timeout: Timeout in milliseconds

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.NAVIGATE.value,
            "url": url
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        self._add_action(action)
        return self

    def click(self, selector: str, selector_type: str = "css", timeout: Optional[int] = None, 
              force: bool = False, position: Optional[Dict[str, float]] = None) -> 'ActionBuilder':
        """
        Add a click action.

        Args:
            selector: Element selector
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds
            force: Whether to force the click
            position: Position to click at ({"x": 0.5, "y": 0.5} for center)

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.CLICK.value,
            "selector": selector,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        if force:
            action["force"] = force
        
        if position is not None:
            action["position"] = position
        
        self._add_action(action)
        return self

    def double_click(self, selector: str, selector_type: str = "css", timeout: Optional[int] = None,
                    force: bool = False, position: Optional[Dict[str, float]] = None) -> 'ActionBuilder':
        """
        Add a double click action.

        Args:
            selector: Element selector
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds
            force: Whether to force the click
            position: Position to click at ({"x": 0.5, "y": 0.5} for center)

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.DOUBLE_CLICK.value,
            "selector": selector,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        if force:
            action["force"] = force
        
        if position is not None:
            action["position"] = position
        
        self._add_action(action)
        return self

    def right_click(self, selector: str, selector_type: str = "css", timeout: Optional[int] = None,
                   force: bool = False, position: Optional[Dict[str, float]] = None) -> 'ActionBuilder':
        """
        Add a right click action.

        Args:
            selector: Element selector
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds
            force: Whether to force the click
            position: Position to click at ({"x": 0.5, "y": 0.5} for center)

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.RIGHT_CLICK.value,
            "selector": selector,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        if force:
            action["force"] = force
        
        if position is not None:
            action["position"] = position
        
        self._add_action(action)
        return self

    def hover(self, selector: str, selector_type: str = "css", timeout: Optional[int] = None,
             position: Optional[Dict[str, float]] = None) -> 'ActionBuilder':
        """
        Add a hover action.

        Args:
            selector: Element selector
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds
            position: Position to hover at ({"x": 0.5, "y": 0.5} for center)

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.HOVER.value,
            "selector": selector,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        if position is not None:
            action["position"] = position
        
        self._add_action(action)
        return self

    def fill(self, selector: str, value: str, selector_type: str = "css", timeout: Optional[int] = None,
           clear: bool = True, delay: Optional[int] = None) -> 'ActionBuilder':
        """
        Add a fill action.

        Args:
            selector: Element selector
            value: Value to fill
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds
            clear: Whether to clear the field before filling
            delay: Delay between keystrokes in milliseconds

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.FILL.value,
            "selector": selector,
            "value": value,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        if not clear:
            action["clear"] = clear
        
        if delay is not None:
            action["delay"] = delay
        
        self._add_action(action)
        return self

    def select(self, selector: str, value: Union[str, List[str]], selector_type: str = "css",
             timeout: Optional[int] = None) -> 'ActionBuilder':
        """
        Add a select action.

        Args:
            selector: Element selector
            value: Value(s) to select
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.SELECT.value,
            "selector": selector,
            "value": value,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        self._add_action(action)
        return self

    def check(self, selector: str, selector_type: str = "css", timeout: Optional[int] = None,
            force: bool = False) -> 'ActionBuilder':
        """
        Add a check action.

        Args:
            selector: Element selector
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds
            force: Whether to force the check

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.CHECK.value,
            "selector": selector,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        if force:
            action["force"] = force
        
        self._add_action(action)
        return self

    def uncheck(self, selector: str, selector_type: str = "css", timeout: Optional[int] = None,
              force: bool = False) -> 'ActionBuilder':
        """
        Add an uncheck action.

        Args:
            selector: Element selector
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds
            force: Whether to force the uncheck

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.UNCHECK.value,
            "selector": selector,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        if force:
            action["force"] = force
        
        self._add_action(action)
        return self

    def upload_file(self, selector: str, file_path: str, selector_type: str = "css",
                 timeout: Optional[int] = None) -> 'ActionBuilder':
        """
        Add an upload file action.

        Args:
            selector: Element selector
            file_path: Path to the file to upload
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.UPLOAD_FILE.value,
            "selector": selector,
            "file_path": file_path,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        self._add_action(action)
        return self

    def press_key(self, selector: str, key: str, selector_type: str = "css", timeout: Optional[int] = None,
                delay: Optional[int] = None) -> 'ActionBuilder':
        """
        Add a press key action.

        Args:
            selector: Element selector
            key: Key to press
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds
            delay: Delay after key press in milliseconds

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.PRESS_KEY.value,
            "selector": selector,
            "key": key,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        if delay is not None:
            action["delay"] = delay
        
        self._add_action(action)
        return self

    def wait_for(self, selector: str, selector_type: str = "css", state: str = "visible",
               timeout: Optional[int] = None) -> 'ActionBuilder':
        """
        Add a wait for action.

        Args:
            selector: Element selector
            selector_type: Type of selector (css or xpath)
            state: State to wait for (visible, hidden, attached, detached)
            timeout: Timeout in milliseconds

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.WAIT_FOR.value,
            "selector": selector,
            "selector_type": selector_type,
            "state": state
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        self._add_action(action)
        return self

    def wait_for_navigation(self, timeout: Optional[int] = None, url: Optional[str] = None,
                          wait_until: Optional[str] = None) -> 'ActionBuilder':
        """
        Add a wait for navigation action.

        Args:
            timeout: Timeout in milliseconds
            url: URL to wait for
            wait_until: When to consider navigation succeeded (load, domcontentloaded, networkidle)

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.WAIT_FOR_NAVIGATION.value
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        if url is not None:
            action["url"] = url
        
        if wait_until is not None:
            action["wait_until"] = wait_until
        
        self._add_action(action)
        return self

    def screenshot(self, path: Optional[str] = None, full_page: bool = False,
                selector: Optional[str] = None, selector_type: str = "css") -> 'ActionBuilder':
        """
        Add a screenshot action.

        Args:
            path: Path to save the screenshot
            full_page: Whether to take a full page screenshot
            selector: Element selector for element screenshot
            selector_type: Type of selector (css or xpath)

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.SCREENSHOT.value
        }
        
        if path is not None:
            action["path"] = path
        
        if full_page:
            action["full_page"] = full_page
        
        if selector is not None:
            action["selector"] = selector
            action["selector_type"] = selector_type
        
        self._add_action(action)
        return self

    def execute_script(self, script: str, arg: Optional[Any] = None) -> 'ActionBuilder':
        """
        Add an execute script action.

        Args:
            script: JavaScript script to execute
            arg: Argument to pass to the script

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.EXECUTE_SCRIPT.value,
            "script": script
        }
        
        if arg is not None:
            action["arg"] = arg
        
        self._add_action(action)
        return self

    def switch_to_frame(self, selector: str, selector_type: str = "css",
                       timeout: Optional[int] = None) -> 'ActionBuilder':
        """
        Add a switch to frame action.

        Args:
            selector: Frame selector
            selector_type: Type of selector (css or xpath)
            timeout: Timeout in milliseconds

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.SWITCH_TO_FRAME.value,
            "selector": selector,
            "selector_type": selector_type
        }
        
        if timeout is not None:
            action["timeout"] = timeout
        
        self._add_action(action)
        return self

    def switch_to_parent_frame(self) -> 'ActionBuilder':
        """
        Add a switch to parent frame action.

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.SWITCH_TO_PARENT_FRAME.value
        }
        
        self._add_action(action)
        return self

    def switch_to_default_content(self) -> 'ActionBuilder':
        """
        Add a switch to default content action.

        Returns:
            ActionBuilder instance for method chaining
        """
        action = {
            "type": ActionType.SWITCH_TO_DEFAULT_CONTENT.value
        }
        
        self._add_action(action)
        return self

    def _add_action(self, action: Dict[str, Any]) -> None:
        """
        Add an action to the list.

        Args:
            action: Action dictionary
        """
        self.actions.append(action)
        self.current_action = action

    def build(self) -> List[Dict[str, Any]]:
        """
        Build the list of actions.

        Returns:
            List of action dictionaries
        """
        return self.actions.copy()

    def clear(self) -> 'ActionBuilder':
        """
        Clear all actions.

        Returns:
            ActionBuilder instance for method chaining
        """
        self.actions = []
        self.current_action = None
        return self

    def save(self, file_path: str) -> None:
        """
        Save actions to a file.

        Args:
            file_path: Path to save the file
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.actions, f, indent=2)
            
            logger.info(f"Actions saved to: {file_path}")
        
        except Exception as e:
            logger.error(f"Error saving actions: {e}")
            raise AutomationError(f"Error saving actions: {e}")

    def load(self, file_path: str) -> 'ActionBuilder':
        """
        Load actions from a file.

        Args:
            file_path: Path to the file

        Returns:
            ActionBuilder instance for method chaining
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.actions = json.load(f)
            
            logger.info(f"Actions loaded from: {file_path}")
            return self
        
        except Exception as e:
            logger.error(f"Error loading actions: {e}")
            raise AutomationError(f"Error loading actions: {e}")

    def validate(self) -> List[str]:
        """
        Validate all actions.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        for i, action in enumerate(self.actions):
            action_type = action.get("type")
            
            if not action_type:
                errors.append(f"Action {i+1}: Missing type")
                continue
            
            try:
                action_enum = ActionType(action_type)
            except ValueError:
                errors.append(f"Action {i+1}: Invalid type '{action_type}'")
                continue
            
            # Validate based on action type
            if action_enum in [ActionType.CLICK, ActionType.DOUBLE_CLICK, ActionType.RIGHT_CLICK,
                              ActionType.HOVER, ActionType.FILL, ActionType.SELECT, ActionType.CHECK,
                              ActionType.UNCHECK, ActionType.UPLOAD_FILE, ActionType.PRESS_KEY,
                              ActionType.WAIT_FOR, ActionType.SWITCH_TO_FRAME]:
                if "selector" not in action:
                    errors.append(f"Action {i+1}: Missing selector")
                
                if "selector_type" not in action:
                    errors.append(f"Action {i+1}: Missing selector type")
                elif action["selector_type"] not in ["css", "xpath"]:
                    errors.append(f"Action {i+1}: Invalid selector type '{action['selector_type']}'")
            
            if action_enum == ActionType.NAVIGATE:
                if "url" not in action:
                    errors.append(f"Action {i+1}: Missing URL")
            
            if action_enum == ActionType.FILL:
                if "value" not in action:
                    errors.append(f"Action {i+1}: Missing value")
            
            if action_enum == ActionType.UPLOAD_FILE:
                if "file_path" not in action:
                    errors.append(f"Action {i+1}: Missing file path")
            
            if action_enum == ActionType.PRESS_KEY:
                if "key" not in action:
                    errors.append(f"Action {i+1}: Missing key")
            
            if action_enum == ActionType.EXECUTE_SCRIPT:
                if "script" not in action:
                    errors.append(f"Action {i+1}: Missing script")
        
        return errors

    def get_action_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get an action by index.

        Args:
            index: Action index

        Returns:
            Action dictionary or None if not found
        """
        if 0 <= index < len(self.actions):
            return self.actions[index]
        return None

    def remove_action_by_index(self, index: int) -> 'ActionBuilder':
        """
        Remove an action by index.

        Args:
            index: Action index

        Returns:
            ActionBuilder instance for method chaining
        """
        if 0 <= index < len(self.actions):
            self.actions.pop(index)
        
        return self

    def insert_action(self, index: int, action: Dict[str, Any]) -> 'ActionBuilder':
        """
        Insert an action at a specific index.

        Args:
            index: Action index
            action: Action dictionary

        Returns:
            ActionBuilder instance for method chaining
        """
        if 0 <= index <= len(self.actions):
            self.actions.insert(index, action)
        
        return self

    def replace_action(self, index: int, action: Dict[str, Any]) -> 'ActionBuilder':
        """
        Replace an action at a specific index.

        Args:
            index: Action index
            action: Action dictionary

        Returns:
            ActionBuilder instance for method chaining
        """
        if 0 <= index < len(self.actions):
            self.actions[index] = action
        
        return self

    def get_actions_by_type(self, action_type: Union[ActionType, str]) -> List[Dict[str, Any]]:
        """
        Get all actions of a specific type.

        Args:
            action_type: Action type (enum or string)

        Returns:
            List of matching actions
        """
        if isinstance(action_type, ActionType):
            type_str = action_type.value
        else:
            type_str = action_type
        
        return [action for action in self.actions if action.get("type") == type_str]

    def remove_actions_by_type(self, action_type: Union[ActionType, str]) -> 'ActionBuilder':
        """
        Remove all actions of a specific type.

        Args:
            action_type: Action type (enum or string)

        Returns:
            ActionBuilder instance for method chaining
        """
        if isinstance(action_type, ActionType):
            type_str = action_type.value
        else:
            type_str = action_type
        
        self.actions = [action for action in self.actions if action.get("type") != type_str]
        return self

    def __len__(self) -> int:
        """Get the number of actions."""
        return len(self.actions)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Get an action by index."""
        return self.actions[index]

    def __setitem__(self, index: int, action: Dict[str, Any]) -> None:
        """Set an action by index."""
        self.actions[index] = action

    def __delitem__(self, index: int) -> None:
        """Delete an action by index."""
        del self.actions[index]

    def __iter__(self):
        """Iterate over actions."""
        return iter(self.actions)
