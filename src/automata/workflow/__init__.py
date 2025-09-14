"""
Workflow management modules for web automation.

This module provides workflow management capabilities:
- JSON schema for automation workflow definition
- Workflow validation and error checking
- Workflow execution engine
"""

from .schema import WorkflowSchema
from .builder import WorkflowBuilder
from .validator import WorkflowValidator
from .templates import WorkflowTemplateManager
from .engine import WorkflowExecutionEngine

__all__ = [
    "WorkflowSchema",
    "WorkflowBuilder",
    "WorkflowValidator",
    "WorkflowTemplateManager",
    "WorkflowExecutionEngine"
]
