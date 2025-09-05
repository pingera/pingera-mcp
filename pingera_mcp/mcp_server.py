"""
MCP Server implementation for Pingera monitoring service.
This file handles server configuration and tool registration.
All tool logic is defined in the 'tools' package.
"""
import logging
import os
import inspect
from typing import Optional, Annotated

from mcp.server.fastmcp import FastMCP
from fastapi import Depends, HTTPException, status, Header

from pingera_mcp import PingeraClient
from pingera_mcp.tools import READ_ONLY_TOOLS, WRITE_TOOLS

# --- CONFIGURATION ---
class Config:
    def __init__(self):
        self.api_key = os.getenv("PINGERA_API_KEY")
        self.base_url = os.getenv("PINGERA_BASE_URL", "https://api.pingera.io/v1")
        self.timeout = int(os.getenv("PINGERA_TIMEOUT", 30))
        self.max_retries = int(os.getenv("PINGERA_MAX_RETRIES", 3))
        self.server_name = os.getenv("PINGERA_SERVER_NAME", "Pingera MCP Server")
        self.mode = os.getenv("MCP_MODE", "stdio").lower()
        self.access_level = os.getenv("PINGERA_ACCESS_LEVEL", "read-only").lower()

    def is_read_write(self) -> bool:
        """Check if server is configured for read-write operations."""
        return self.access_level == "read-write"

config = Config()

# --- LOGGING ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pingera-mcp-server")

# --- SERVER AND CLIENT SETUP ---
mcp = FastMCP(config.server_name)
stdio_pingera_client = None

if config.mode == 'stdio':
    logger.info("Server configured for STDIO mode.")
    if not config.api_key:
        raise ValueError("PINGERA_API_KEY is required for STDIO mode")
    stdio_pingera_client = PingeraClient(api_key=config.api_key, base_url=config.base_url)
else:
    logger.info("Server configured for HTTP multi-tenant mode.")

# --- HTTP DEPENDENCY ---
async def get_pingera_client_for_http(authorization: Annotated[str | None, Header()] = None) -> PingeraClient:
    """Dependency for HTTP mode: creates a PingeraClient from the Authorization header."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing")
    
    # Log the received header for debugging
    logger.info(f"Received Authorization header: {authorization[:20]}...")
    
    # Use the authorization header value directly as the API key
    try:
        client = PingeraClient(api_key=authorization, base_url=config.base_url)
        logger.info("PingeraClient created successfully for HTTP request")
        return client
    except Exception as e:
        logger.error(f"Failed to create PingeraClient: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize Pingera client")

ClientDep = Annotated[PingeraClient, Depends(get_pingera_client_for_http)]

# --- PROGRAMMATIC REGISTRATION ---
def register_tools(tool_list):
    """Register a list of tools with the MCP server."""
    for tool_name, logic_func in tool_list:
        # Create proper closures to avoid late binding issues
        def create_stdio_wrapper(func):
            async def stdio_wrapper(*args, **kwargs):
                return await func(stdio_pingera_client, *args, **kwargs)
            return stdio_wrapper

        def create_http_wrapper(func):
            async def http_wrapper(*args, client: ClientDep, **kwargs):
                logger.info(f"HTTP wrapper called for {tool_name} with client: {type(client)}")
                return await func(client, *args, **kwargs)
            return http_wrapper

        if config.mode == 'stdio':
            tool_to_register = create_stdio_wrapper(logic_func)
        else:
            tool_to_register = create_http_wrapper(logic_func)

        # Copy docstring and signature from logic function
        tool_to_register.__doc__ = logic_func.__doc__

        # Copy signature, handling client parameter properly for each mode
        sig = inspect.signature(logic_func)
        if config.mode == 'stdio':
            # Skip the first 'client' parameter for STDIO mode
            params = list(sig.parameters.values())[1:]
            tool_to_register.__signature__ = sig.replace(parameters=params)
        else:
            # For HTTP mode, keep the client parameter but move it to the end
            params = list(sig.parameters.values())[1:]  # Skip original client param
            # The dependency injection will handle the client parameter automatically
            tool_to_register.__signature__ = sig.replace(parameters=params)

        # Register the tool
        mcp.add_tool(fn=tool_to_register, name=tool_name)

# Register read-only tools
register_tools(READ_ONLY_TOOLS)
logger.info(f"Registered {len(READ_ONLY_TOOLS)} read-only tools in '{config.mode}' mode.")

# Register write tools if access level permits
if config.is_read_write():
    register_tools(WRITE_TOOLS)
    logger.info(f"Read-write access enabled: Registered {len(WRITE_TOOLS)} write tools.")
else:
    logger.info("Read-only access level: Write tools not registered.")

total_tools = len(READ_ONLY_TOOLS) + (len(WRITE_TOOLS) if config.is_read_write() else 0)
logger.info(f"Total registered tools: {total_tools}")