#!/usr/bin/env python3.11
"""
Script to start the MCP server for testing the MCP Bridge extension functionality.
"""

import asyncio
import argparse
import logging
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from automata.mcp_server.server import MCPServer
from automata.core.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Main function to run the MCP server."""
    parser = argparse.ArgumentParser(description='Start the MCP server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--log-level', default='INFO', help='Log level')
    
    args = parser.parse_args()
    
    # Set log level
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    
    # Create and start the server
    server = MCPServer(host=args.host, port=args.port)
    runner = await server.start()
    
    logger.info(f"MCP Server started on {args.host}:{args.port}")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Keep the server running
        await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Shutting down MCP server...")
    finally:
        await server.stop(runner)
        logger.info("MCP Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
