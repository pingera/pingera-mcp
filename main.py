
#!/usr/bin/env python3
"""
Main entry point for the Pingera MCP Server.
"""
import asyncio
import logging
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server

from config import Config
from mcp_server import create_mcp_server


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),  # Use stderr for logs to avoid interfering with stdio
        ]
    )


async def main():
    """Main entry point for running the server in stdio mode."""
    # Load configuration
    config = Config()

    # Setup logging
    setup_logging(debug=config.debug)
    logger = logging.getLogger(__name__)

    # Validate API key
    if not config.api_key:
        logger.error("PINGERA_API_KEY environment variable is required")
        sys.exit(1)

    logger.info(f"Starting Pingera MCP Server in {config.mode} mode")

    # Create the FastMCP server
    fastmcp_server = create_mcp_server(config)
    
    # Get the underlying MCP server from FastMCP
    mcp_server = fastmcp_server._mcp_server
    
    logger.info("MCP Server created successfully")
    logger.info("Running in stdio mode...")

    # Run the server in stdio mode
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
