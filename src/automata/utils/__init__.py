"""
Utility modules for web automation.

This module provides various utilities:
- File I/O utilities for reading/writing external data
- Variable management system for storing and using dynamic values
- Conditional logic processor (IF/ELSE statements)
- Loop processor for repetitive tasks
"""

from .file_io import FileIO
from .variables import VariableManager
from .conditional import ConditionalProcessor
from .loops import LoopProcessor

__all__ = [
    "FileIO",
    "VariableManager",
    "ConditionalProcessor",
    "LoopProcessor"
]
