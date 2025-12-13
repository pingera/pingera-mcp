#!/usr/bin/env python3
"""
MCP Server entry point for Pingera monitoring service.
"""
import asyncio
import logging
import argparse
import os

from .config import Config
from .mcp_server import mcp, config


async def main():
    """Main entry point for the MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Pingera MCP Server")
    parser.add_argument(
        "--tools",
        type=str,
        help="Comma-separated list of tools to expose (e.g., 'list_pages,list_checks')"
    )
    args = parser.parse_args()

    # Set allowed tools from CLI if provided
    if args.tools:
        os.environ["PINGERA_ALLOWED_TOOLS"] = args.tools
        # Reload config to pick up the new environment variable
        from .config import Config
        global config
        config = Config()

    logger = logging.getLogger("pingera-mcp-server")

    if config.allowed_tools:
        logger.info(f"Limiting exposed tools to: {config.allowed_tools}")

    logger.info("Starting MCP server in stdio mode")

    try:
        # Import here to avoid circular dependency
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await mcp.run(read_stream, write_stream, mcp.create_initialization_options())
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())