"""
MCP Server implementation for browser automation.
"""

import asyncio
import json
import logging
import platform
import sys
from typing import Dict, Any, Optional, List

from aiohttp import web, web_runner
from aiohttp.web import Application, Response, Request

from .config import MCPServerConfig
from ..core.logger import get_logger

logger = get_logger(__name__)


class MCPServer:
    """MCP Server for browser automation."""
    
    def __init__(self, config: Optional[MCPServerConfig] = None, host: str = "localhost", port: int = 8080):
        """
        Initialize MCP Server.
        
        Args:
            config: MCP Server configuration
            host: Server host (used if config not provided)
            port: Server port (used if config not provided)
        """
        if config is None:
            config = MCPServerConfig()
            config.set_server_host(host)
            config.set_server_port(port)
        
        self.config = config
        self.host = config.get_server_host()
        self.port = config.get_server_port()
        self.app = None
        self.runner = None
        self.site = None
        self.browser_manager = None
        self.is_running = False
        
        # Set up logging
        logging.basicConfig(level=getattr(logging, config.get_log_level()))
    
    async def start(self) -> web_runner.AppRunner:
        """
        Start the MCP Server.
        
        Returns:
            AppRunner instance
        """
        if self.is_running:
            logger.warning("MCP Server is already running")
            return self.runner
        
        try:
            # Create web application
            self.app = web.Application()
            
            # Set up routes
            self._setup_routes()
            
            # Create and start runner
            self.runner = web_runner.AppRunner(self.app)
            await self.runner.setup()
            
            # Create site
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            self.is_running = True
            logger.info(f"MCP Server started on {self.host}:{self.port}")
            
            return self.runner
            
        except Exception as e:
            logger.error(f"Failed to start MCP Server: {e}")
            raise
    
    async def stop(self, runner: Optional[web_runner.AppRunner] = None) -> None:
        """
        Stop the MCP Server.
        
        Args:
            runner: AppRunner instance (if None, uses self.runner)
        """
        if not self.is_running:
            logger.warning("MCP Server is not running")
            return
        
        try:
            runner_to_stop = runner or self.runner
            
            if runner_to_stop:
                await runner_to_stop.cleanup()
            
            self.is_running = False
            logger.info("MCP Server stopped")
            
        except Exception as e:
            logger.error(f"Error stopping MCP Server: {e}")
    
    def _setup_routes(self) -> None:
        """Set up HTTP routes for the server."""
        self.app.router.add_get('/', self._handle_root)
        self.app.router.add_get('/health', self._handle_health)
        self.app.router.add_post('/stop', self._handle_stop)
        self.app.router.add_get('/commands', self._handle_commands_list)
        self.app.router.add_get('/commands/{command_type}', self._handle_command_schema)
        self.app.router.add_post('/command', self._handle_command)
        self.app.router.add_post('/commands', self._handle_commands)
    
    async def _handle_root(self, request: Request) -> Response:
        """Handle root endpoint."""
        return web.json_response({
            "name": "Automata MCP Server",
            "version": "1.0.0",
            "status": "running"
        })
    
    async def _handle_health(self, request: Request) -> Response:
        """Handle health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "version": "1.0.0",
            "platform": platform.system(),
            "python_version": sys.version
        })
    
    async def _handle_stop(self, request: Request) -> Response:
        """Handle stop endpoint."""
        try:
            # Schedule server stop
            asyncio.create_task(self._schedule_stop())
            return web.json_response({"success": True})
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=500)
    
    async def _schedule_stop(self) -> None:
        """Schedule server stop with a small delay."""
        await asyncio.sleep(0.1)  # Small delay to allow response to be sent
        await self.stop()
    
    async def _handle_commands_list(self, request: Request) -> Response:
        """Handle commands list endpoint."""
        commands = [
            "navigate",
            "click",
            "fill",
            "screenshot",
            "wait_for_selector",
            "wait_for_navigation",
            "execute_script",
            "get_title",
            "get_url",
            "get_content",
            "snapshot"
        ]
        return web.json_response({"commands": commands})
    
    async def _handle_command_schema(self, request: Request) -> Response:
        """Handle command schema endpoint."""
        command_type = request.match_info['command_type']
        
        schemas = {
            "navigate": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"}
                },
                "required": ["url"]
            },
            "click": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector"}
                },
                "required": ["selector"]
            },
            "fill": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector"},
                    "value": {"type": "string", "description": "Value to fill"}
                },
                "required": ["selector", "value"]
            },
            "screenshot": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to save screenshot"}
                }
            },
            "wait_for_selector": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector"},
                    "timeout": {"type": "integer", "description": "Timeout in milliseconds"}
                },
                "required": ["selector"]
            },
            "wait_for_navigation": {
                "type": "object",
                "properties": {
                    "timeout": {"type": "integer", "description": "Timeout in milliseconds"}
                }
            },
            "execute_script": {
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "JavaScript script to execute"}
                },
                "required": ["script"]
            },
            "get_title": {
                "type": "object",
                "properties": {}
            },
            "get_url": {
                "type": "object",
                "properties": {}
            },
            "get_content": {
                "type": "object",
                "properties": {}
            },
            "snapshot": {
                "type": "object",
                "properties": {}
            }
        }
        
        schema = schemas.get(command_type)
        if schema:
            return web.json_response({"schema": schema})
        else:
            return web.json_response({"error": f"Unknown command type: {command_type}"}, status=404)
    
    async def _handle_command(self, request: Request) -> Response:
        """Handle single command endpoint."""
        try:
            command = await request.json()
            result = await self._execute_command(command)
            return web.json_response({"success": True, "result": result})
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)
    
    async def _handle_commands(self, request: Request) -> Response:
        """Handle multiple commands endpoint."""
        try:
            data = await request.json()
            commands = data.get("commands", [])
            
            results = []
            for command in commands:
                try:
                    result = await self._execute_command(command)
                    results.append({"success": True, "result": result})
                except Exception as e:
                    results.append({"success": False, "error": str(e)})
            
            return web.json_response({"results": results})
            
        except Exception as e:
            logger.error(f"Error executing commands: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)
    
    async def _execute_command(self, command: Dict[str, Any]) -> Any:
        """
        Execute a single command.
        
        Args:
            command: Command dictionary
            
        Returns:
            Command result
            
        Raises:
            ValueError: If command is invalid
            NotImplementedError: If command is not implemented
        """
        if not isinstance(command, dict) or "type" not in command:
            raise ValueError("Invalid command format")
        
        command_type = command["type"]
        
        # For now, return placeholder responses
        # In a real implementation, these would interact with a browser
        if command_type == "navigate":
            url = command.get("url")
            if not url:
                raise ValueError("Navigate command requires 'url' parameter")
            return {"status": "navigated", "url": url}
        
        elif command_type == "click":
            selector = command.get("selector")
            if not selector:
                raise ValueError("Click command requires 'selector' parameter")
            return {"status": "clicked", "selector": selector}
        
        elif command_type == "fill":
            selector = command.get("selector")
            value = command.get("value")
            if not selector or value is None:
                raise ValueError("Fill command requires 'selector' and 'value' parameters")
            return {"status": "filled", "selector": selector, "value": value}
        
        elif command_type == "screenshot":
            path = command.get("path")
            # In a real implementation, this would take and save a screenshot
            return {"status": "screenshot_taken", "path": path}
        
        elif command_type == "wait_for_selector":
            selector = command.get("selector")
            timeout = command.get("timeout")
            if not selector:
                raise ValueError("Wait for selector command requires 'selector' parameter")
            return {"status": "element_found", "selector": selector, "timeout": timeout}
        
        elif command_type == "wait_for_navigation":
            timeout = command.get("timeout")
            return {"status": "navigation_complete", "timeout": timeout}
        
        elif command_type == "execute_script":
            script = command.get("script")
            if not script:
                raise ValueError("Execute script command requires 'script' parameter")
            return {"status": "script_executed", "result": None}
        
        elif command_type == "get_title":
            return {"title": "Example Page Title"}
        
        elif command_type == "get_url":
            return {"url": "https://example.com"}
        
        elif command_type == "get_content":
            return {"content": "<html><body>Example content</body></html>"}
        
        elif command_type == "snapshot":
            return {"snapshot": {"title": "Example", "url": "https://example.com"}}
        
        else:
            raise NotImplementedError(f"Command type '{command_type}' not implemented")
