#!/usr/bin/env python3
"""
Main entry point for the Pingera MCP Server.
"""
import asyncio
import logging
import os
import sys
from typing import Optional

from config import Config
from mcp_server import create_mcp_server


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


def main() -> None:
    """Main entry point."""
    # Load configuration
    config = Config()
    
    # Setup logging
    setup_logging(debug=config.debug)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting Pingera MCP Server in {config.mode} mode")
    
    # Validate API key
    if not config.api_key:
        logger.error("PINGERA_API_KEY environment variable is required")
        sys.exit(1)
    
    # Create and run the MCP server
    try:
        server = create_mcp_server(config)
        logger.info("MCP Server created successfully")
        
        # Run the server
        server.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down Pingera MCP Server...")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
