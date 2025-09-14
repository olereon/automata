"""
Helper tools for web automation.

This module provides various tools to assist with web automation:
- HTML/XPath parser for extracting element information
- Selector generator for creating robust selectors
- Action builder for creating interaction commands
- Browser explorer for interactive browser exploration and session management
"""

from .parser import HTMLParser
from .selector_generator import SelectorGenerator
from .action_builder import ActionBuilder, ActionType
from .browser_explorer import BrowserExplorer

__all__ = [
    "HTMLParser",
    "SelectorGenerator",
    "ActionBuilder",
    "ActionType",
    "BrowserExplorer"
]
