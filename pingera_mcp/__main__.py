#!/usr/bin/env python3
"""
Main entry point for the Pingera MCP server.
"""
import logging
import argparse
from .mcp_server import mcp, config

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Pingera MCP Server")
    parser.add_argument(
        "--tools",
        type=str,
        help="Comma-separated list of tools to expose (e.g., list_pages,get_page_details)",
        default=None
    )
    args = parser.parse_args()

    # Set allowed tools if specified via CLI (overrides env variable)
    if args.tools:
        config.set_allowed_tools(args.tools)

    # Log tool filtering status before starting
    if config.allowed_tools:
        logger.info(f"Limiting exposed tools to: {config.allowed_tools}")

    # Run the FastMCP server in appropriate mode
    if config.transport_mode == "sse":
        logger.info(f"Starting MCP server in SSE mode on {config.http_host}:{config.http_port}")
        mcp.run(transport="streamable-http")
    else:
        logger.info("Starting MCP server in stdio mode")
        mcp.run()