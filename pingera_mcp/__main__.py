#!/usr/bin/env python3
"""
Main entry point for the Pingera MCP server.
"""
import logging
from .mcp_server import mcp, config

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Run the FastMCP server in appropriate mode
    if config.transport_mode == "sse":
        logger.info(f"Starting MCP server in SSE mode on {config.http_host}:{config.http_port}")
        mcp.run(transport="sse", host=config.http_host, port=config.http_port)
    else:
        logger.info("Starting MCP server in stdio mode")
        mcp.run()