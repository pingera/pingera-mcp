#!/usr/bin/env python3
"""
Main entry point for Pingera MCP Server.
"""
import argparse
from .mcp_server import mcp, config

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Pingera MCP Server')
    parser.add_argument(
        '--tools',
        type=str,
        help='Comma-separated list of tools to expose (e.g., list_pages,create_page,list_checks)'
    )
    return parser.parse_args()

def main() -> None:
    """Run the MCP server."""
    # Note: CLI args are already parsed in config initialization
    # This is just for documentation - the config is created before this runs
    mcp.run()

if __name__ == "__main__":
    main()