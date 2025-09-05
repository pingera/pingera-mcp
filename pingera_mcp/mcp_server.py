"""
MCP Server implementation for Pingera monitoring service.
Supports dual-mode operation (stdio, http).
"""
import logging
import os
from typing import Optional, Annotated

from mcp.server.fastmcp import FastMCP
from fastapi import Depends, HTTPException, status, Header

from pingera_mcp import PingeraClient
from pingera_mcp.tools import PagesTools

# --- CONFIGURATION ---
class Config:
    def __init__(self):
        self.api_key = os.getenv("PINGERA_API_KEY")
        self.base_url = os.getenv("PINGERA_BASE_URL", "https://api.pingera.io/v1")
        self.timeout = int(os.getenv("PINGERA_TIMEOUT", 30))
        self.max_retries = int(os.getenv("PINGERA_MAX_RETRIES", 3))
        self.server_name = os.getenv("PINGERA_SERVER_NAME", "Pingera MCP Server")
        self.mode = os.getenv("MCP_MODE", "stdio").lower()

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
async def get_pingera_client_for_http(auth: Annotated[str | None, Header(alias="Authorization")] = None) -> PingeraClient:
    """Dependency for HTTP mode: creates a PingeraClient from the Authorization header."""
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header is missing")
    try:
        scheme, token = auth.split()
        if scheme.lower() != "bearer": raise ValueError
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization scheme. Use 'Bearer <key>'")
    return PingeraClient(api_key=token, base_url=config.base_url)

ClientDep = Annotated[PingeraClient, Depends(get_pingera_client_for_http)]

# --- 1. CORE TOOL LOGIC (SINGLE SOURCE OF TRUTH) ---
async def _list_pages_logic(
    client: PingeraClient,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """
    List all status pages in your Pingera account.

    This is typically the first tool you should use to discover available pages and their IDs.
    Each page has a unique ID that you'll need for other operations like listing incidents or components.

    Args:
        page: Page number for pagination (default: 1)
        per_page: Number of items per page (default: 20, max: 100)
        status: Filter pages by status ('active', 'inactive').

    Returns:
        JSON with list of status pages including their names, IDs, domains, and configuration details.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    pages_tools = PagesTools(client)
    return await pages_tools.list_pages(page, per_page, status)

# --- 2. PROGRAMMATIC REGISTRATION ---
TOOL_REGISTRY = [
    ("list_pages", _list_pages_logic),
]

for tool_name, logic_func in TOOL_REGISTRY:
    tool_to_register = None

    if config.mode == 'stdio':
        async def stdio_wrapper(
            page: Optional[int] = None,
            per_page: Optional[int] = None,
            status: Optional[str] = None
        ):
            return await logic_func(stdio_pingera_client, page=page, per_page=per_page, status=status)
        tool_to_register = stdio_wrapper
    else:  # http mode
        async def http_wrapper(
            page: Optional[int] = None,
            per_page: Optional[int] = None,
            status: Optional[str] = None,
            client: ClientDep = None
        ):
            return await logic_func(client, page=page, per_page=per_page, status=status)
        tool_to_register = http_wrapper

    # THE FIX: Manually assign the docstring to the wrapper function itself
    # before registration. This ensures the framework reads it correctly.
    tool_to_register.__doc__ = logic_func.__doc__

    # Now, register the fully prepared wrapper function.
    mcp.add_tool(fn=tool_to_register, name=tool_name)

logger.info(f"Registered {len(TOOL_REGISTRY)} tools in '{config.mode}' mode.")