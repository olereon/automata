"""
MCP Bridge module for browser automation.
"""

from .config import MCPConfiguration
from .client import MCPClient
from .bridge import MCPBridgeConnector

__all__ = ['MCPConfiguration', 'MCPClient', 'MCPBridgeConnector']