"""
MCP Server implementation for Pingera monitoring service.
"""
import logging
import json
from typing import Optional, Dict, Any, List

from mcp.server.fastmcp import FastMCP

from .config import Config
from pingera_mcp import PingeraClient
from pingera_mcp.auth import get_request_client
from pingera_mcp.middleware import ToolFilterMiddleware
from pingera_mcp.tools import (
        StatusTools,
        PagesTools,
        ComponentTools,
        ChecksTools,
        AlertsTools,
        HeartbeatsTools,
        IncidentsTools,
        PlaywrightGeneratorTools,
        CheckGroupsTools, # Import CheckGroupsTools
        SecretsTools, # Import SecretsTools
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pingera-mcp-server")

def create_mcp_server(config: Config) -> FastMCP:
    """Create and configure MCP server with the given configuration."""
    # In stdio mode, require credentials from environment
    # In SSE mode, credentials will come from request headers
    if config.transport_mode == "stdio":
        if not config.api_key and not config.jwt_token:
            logger.error("Either PINGERA_API_KEY or PINGERA_JWT_TOKEN environment variable is required for stdio mode")
            raise ValueError("Either PINGERA_API_KEY or PINGERA_JWT_TOKEN is required for stdio mode")

        auth_method = "JWT Bearer token" if config.jwt_token else "API Key"
        logger.info(f"Starting Pingera MCP Server in {config.mode} mode (stdio transport)")
        logger.info(f"Using {auth_method} for authentication")
    else:
        logger.info(f"Starting Pingera MCP Server in {config.mode} mode (SSE transport)")
        if config.require_auth_header:
            logger.info("Server configured to require Authorization header from clients")
        else:
            logger.info("Server will accept requests without Authorization header (using env credentials)")

    # Create MCP server
    if config.transport_mode == "sse":
        mcp_server = FastMCP(
            config.server_name, 
            host=config.http_host, 
            port=config.http_port
        )
    else:
        mcp_server = FastMCP(config.server_name)
    
    # Add middleware for tool filtering
    from .tool_registry import tool_registry
    filter_middleware = ToolFilterMiddleware(config, tool_registry)
    mcp_server.add_middleware(middleware=filter_middleware)
    
    logger.info("Tool filtering middleware registered successfully")

    # Initialize Pingera client for stdio mode (will be overridden per-request in SSE mode)
    pingera_client = PingeraClient(
        api_key=config.api_key if config.api_key else None,
        jwt_token=config.jwt_token if config.jwt_token else None,
        base_url=config.base_url,
        timeout=config.timeout,
        max_retries=config.max_retries
    ) if config.transport_mode == "stdio" else None

    return mcp_server

# Global variables - will be initialized by initialize_server()
config = None
mcp = None
pingera_client = None
status_tools = None
pages_tools = None
component_tools = None
checks_tools = None
alerts_tools = None
heartbeats_tools = None
incidents_tools = None
playwright_tools = None
check_groups_tools = None
secrets_tools = None

# Helper function to update the client for tools
def _update_tools_client():
    """
    Updates the PingeraClient for each tool instance.
    In SSE mode, this ensures the client is updated with the latest request context.
    """
    global status_tools, pages_tools, component_tools, checks_tools, alerts_tools, heartbeats_tools, incidents_tools, playwright_tools, check_groups_tools, secrets_tools

    # In SSE mode, get the client from the request context
    if config and config.transport_mode != "stdio":
        request_client = get_request_client(config, pingera_client)
        if request_client:
            status_tools.client = request_client
            pages_tools.client = request_client
            component_tools.client = request_client
            checks_tools.client = request_client
            alerts_tools.client = request_client
            heartbeats_tools.client = request_client
            incidents_tools.client = request_client
            playwright_tools.client = request_client
            check_groups_tools.client = request_client
            secrets_tools.client = request_client

# Import tool registry and registration functions
from .tool_registry import tool_registry
from .tool_registration import (
    register_pages_tools,
    register_components_tools,
    register_checks_tools,
    register_alerts_tools,
    register_heartbeats_tools,
    register_incidents_tools,
    register_check_groups_tools,
    register_secrets_tools,
    register_playwright_tools,
    register_status_tools,
)

# Register all tool definitions when module loads
register_pages_tools()
register_components_tools()
register_checks_tools()
register_alerts_tools()
register_heartbeats_tools()
register_incidents_tools()
register_check_groups_tools()
register_secrets_tools()
register_playwright_tools()
register_status_tools()


# Register tools based on configuration
def register_tools():
    """Register all tools - middleware will handle filtering based on mode and client request."""
    # Register all tools compatible with server mode
    # Middleware will filter based on:
    # - --tools flag (stdio mode)
    # - X-MCP-Tools header (SSE mode)
    # - read-only/read-write mode
    tools_to_register = tool_registry.get_tools_to_register(
        requested_tools=None,  # Register all tools
        is_read_write_mode=config.is_read_write()
    )

    logger.info(f"Registering {len(tools_to_register)} tools (middleware will filter based on request)")
    for tool_name, register_func in tools_to_register.items():
        logger.debug(f"Registering tool: {tool_name}")
        register_func(mcp)

def initialize_server(cli_args=None):
    """Initialize the server with CLI arguments."""
    global config, mcp, pingera_client, status_tools, pages_tools, component_tools
    global checks_tools, alerts_tools, heartbeats_tools, incidents_tools
    global playwright_tools, check_groups_tools, secrets_tools

    # Load configuration with CLI args
    config = Config(cli_args=cli_args)

    # Create MCP server
    mcp = create_mcp_server(config)

    # Initialize Pingera client
    if config.transport_mode == "stdio":
        pingera_client = PingeraClient(
            api_key=config.api_key if config.api_key else None,
            jwt_token=config.jwt_token if config.jwt_token else None,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries
        )
        auth_method = "JWT Bearer token" if config.jwt_token else "API Key"
        logger.info(f"Using Pingera SDK client with {auth_method} authentication")
    else:
        pingera_client = PingeraClient(
            api_key=config.api_key if config.api_key else "placeholder",
            jwt_token=config.jwt_token if config.jwt_token else None,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries
        )
        logger.info(f"SSE mode: Client will be created per-request from Authorization headers")

    # Initialize tool instances
    status_tools = StatusTools(pingera_client)
    pages_tools = PagesTools(pingera_client)
    component_tools = ComponentTools(pingera_client)
    checks_tools = ChecksTools(pingera_client)
    alerts_tools = AlertsTools(pingera_client)
    heartbeats_tools = HeartbeatsTools(pingera_client)
    incidents_tools = IncidentsTools(pingera_client)
    playwright_tools = PlaywrightGeneratorTools(pingera_client)
    check_groups_tools = CheckGroupsTools(pingera_client)
    secrets_tools = SecretsTools(pingera_client)

    # Register tools
    register_tools()

    return mcp