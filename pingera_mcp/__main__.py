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

try:
    # Access the internal tool manager to get the registered tool object
    tool_object = mcp._tool_manager.get_tool("list_pages")

    print("\n" + "="*50)
    print("TOOL VERIFICATION")
    print("="*50)
    print(f"Successfully retrieved tool: '{tool_object.name}'")
    print("\n--- Registered Description ---")
    print(tool_object.description)
    print("------------------------------\n")
except Exception as e:
    print(f"Could not verify tool registration: {e}")

if __name__ == "__main__":
    main()