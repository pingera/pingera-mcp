"""
ASGI application entry point for production deployment.
This module provides the ASGI app for running with uvicorn or other ASGI servers.
"""
import os
import logging
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pingera-mcp-asgi")

# Ensure we're in SSE mode for production
os.environ.setdefault('TRANSPORT_MODE', 'sse')
os.environ.setdefault('HTTP_HOST', '0.0.0.0')
os.environ.setdefault('HTTP_PORT', '8000')

logger.info("Loading Pingera MCP Server in SSE mode for production")

# Import the mcp server after setting environment variables
from .mcp_server import mcp

# FastMCP provides different ways to access the ASGI app
# Try multiple approaches for compatibility
app: Any = None

# Approach 1: Direct app attribute (FastMCP 2.x)
if hasattr(mcp, 'app'):
    app = mcp.app
    logger.info("Successfully loaded ASGI app from mcp.app")

# Approach 2: Get app from _app attribute (some versions)
elif hasattr(mcp, '_app'):
    app = mcp._app
    logger.info("Successfully loaded ASGI app from mcp._app")

# Approach 3: Call get_app() method if available
elif hasattr(mcp, 'get_app'):
    app = mcp.get_app()
    logger.info("Successfully loaded ASGI app from mcp.get_app()")

# Approach 4: Create app explicitly with create_app()
elif hasattr(mcp, 'create_app'):
    app = mcp.create_app()
    logger.info("Successfully loaded ASGI app from mcp.create_app()")

if app is None:
    logger.error("Unable to get ASGI app from FastMCP")
    logger.error("Available FastMCP attributes: %s", dir(mcp))
    raise RuntimeError(
        "Unable to get ASGI app from FastMCP. "
        "Ensure FastMCP is properly initialized with SSE transport mode. "
        "You may need to run the server with: python -m pingera_mcp"
    )

logger.info("ASGI app successfully loaded and ready for uvicorn")
