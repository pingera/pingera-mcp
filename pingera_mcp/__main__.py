#!/usr/bin/env python3
"""
Main entry point for the Pingera MCP Server.
Selects the runtime mode (HTTP or STDIO) based on configuration.
"""
from .mcp_server import mcp, config, logger

def main():
    """
    Runs the MCP server in the mode specified by the configuration.
    """
    if config.mode == 'http':
        logger.info(f"Starting MCP HTTP server on http://127.0.0.1:8000")

        mcp.run(transport="streamable-http")

    elif config.mode == 'stdio':
        logger.info("Starting MCP server in STDIO mode.")
        mcp.run()
    else:
        logger.error(f"Invalid MCP_MODE: '{config.mode}'. Choose 'stdio' or 'http'.")

if __name__ == "__main__":
    main()