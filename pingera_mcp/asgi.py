"""
ASGI application entry point for production deployment.
This module provides the ASGI app for running with uvicorn or other ASGI servers.
"""
import os
import logging

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

# FastMCP provides streamable_http_app() for SSE/HTTP transport
# This returns the ASGI application
try:
    # Try streamable_http_app() first (preferred for SSE mode)
    if hasattr(mcp, 'streamable_http_app'):
        app = mcp.streamable_http_app()
        logger.info("Successfully loaded ASGI app from mcp.streamable_http_app()")
    # Fallback to sse_app() if available
    elif hasattr(mcp, 'sse_app'):
        app = mcp.sse_app()
        logger.info("Successfully loaded ASGI app from mcp.sse_app()")
    else:
        raise AttributeError("Neither streamable_http_app nor sse_app found")
except Exception as e:
    logger.error(f"Failed to get ASGI app from FastMCP: {e}")
    logger.error(f"Available FastMCP attributes: {dir(mcp)}")
    raise RuntimeError(
        "Unable to get ASGI app from FastMCP. "
        "Ensure FastMCP is properly initialized with SSE transport mode. "
        "You may need to run the server with: python -m pingera_mcp"
    ) from e

logger.info("ASGI app successfully loaded and ready for uvicorn")
