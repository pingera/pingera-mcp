#!/usr/bin/env python3
"""
Entry point for the MCP server.
"""
import argparse

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Pingera MCP Server")
    parser.add_argument(
        "--tools",
        type=str,
        help="Comma-separated list of tools to expose (e.g., list_pages,get_page_details)"
    )
    args = parser.parse_args()

    # Initialize server with CLI args
    from .mcp_server import initialize_server
    mcp = initialize_server(cli_args=args)

    # Get config to determine transport mode
    from .mcp_server import config

    # Start the server based on transport mode
    if config.transport_mode == "stdio":
        mcp.run()
    else:
        mcp.run(transport="sse")