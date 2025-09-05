#!/usr/bin/env python3
"""
Main entry point for the Pingera MCP Server.
Selects the runtime mode (HTTP or STDIO) based on configuration.
"""
import uvicorn
from .mcp_server import mcp, config, logger

def main():
    """
    Runs the MCP server in the mode specified by the configuration.
    """
    if config.mode == 'http':
        logger.info(f"Starting Uvicorn server on http://0.0.0.0:8000")
        # The 'mcp' object is a valid ASGI application that uvicorn can serve.
        uvicorn.run(mcp, host="0.0.0.0", port=8000)
    elif config.mode == 'stdio':
        logger.info("Starting MCP server in STDIO mode.")
        # mcp.run() starts the server listening on stdin/stdout.
        mcp.run()
    else:
        logger.error(f"Invalid MCP_MODE: '{config.mode}'. Choose 'stdio' or 'http'.")

if __name__ == "__main__":
    main()