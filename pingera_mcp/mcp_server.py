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

    # Create MCP server with host/port for SSE mode
    if config.transport_mode == "sse":
        mcp_server = FastMCP(config.server_name, host=config.http_host, port=config.http_port)
    else:
        mcp_server = FastMCP(config.server_name)

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

# Import tool registry
from .tool_registry import tool_registry

# Define a conditional decorator to conditionally register tools
def conditional_mcp_tool():
    """
    Decorator that conditionally registers an MCP tool.
    It will only register the tool if the tool registry system is NOT being used,
    otherwise it will skip registration.
    """
    # This is a simplified conditional decorator. In a real-world scenario,
    # you might want to check if the tool is already registered or if there's
    # a specific flag to enable/disable this behavior.
    # For this example, we assume that if tool_registry is active, we skip.
    if tool_registry.is_active(): # Assuming tool_registry has an is_active method or similar
        def decorator(func):
            return func
        return decorator
    else:
        # If tool_registry is not active, fall back to the original @mcp.tool() behavior
        return mcp.tool

# Register PoC tools using the registry pattern
@tool_registry.register("list_pages", requires_write=False)
def register_list_pages(mcp_instance):
    @mcp_instance.tool()
    async def list_pages(
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

        Returns:
            JSON with list of status pages including their names, IDs, domains, and configuration details.
        """
        _update_tools_client()
        return await pages_tools.list_pages(page, per_page, status)
    return list_pages

@tool_registry.register("get_page_details", requires_write=False)
def register_get_page_details(mcp_instance):
    @mcp_instance.tool()
    async def get_page_details(page_id: int) -> str:
        """
        Get detailed information about a specific status page.

        Args:
            page_id: The unique identifier of the status page

        Returns:
            JSON with complete page details including settings, components, branding, and configuration.
        """
        _update_tools_client()
        return await pages_tools.get_page_details(page_id)
    return get_page_details

@tool_registry.register("create_page", requires_write=True)
def register_create_page(mcp_instance):
    @mcp_instance.tool()
    async def create_page(
        name: str,
        subdomain: Optional[str] = None,
        domain: Optional[str] = None,
        url: Optional[str] = None,
        language: Optional[str] = None,
        headline: Optional[str] = None,
        page_description: Optional[str] = None,
        time_zone: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        viewers_must_be_team_members: Optional[bool] = None,
        hidden_from_search: Optional[bool] = None,
        allow_page_subscribers: Optional[bool] = None,
        allow_incident_subscribers: Optional[bool] = None,
        allow_email_subscribers: Optional[bool] = None,
        allow_sms_subscribers: Optional[bool] = None,
        allow_webhook_subscribers: Optional[bool] = None,
        allow_rss_atom_feeds: Optional[bool] = None,
        support_url: Optional[str] = None,
    ) -> str:
        """
        Create a new status page.

        Args:
            name: Display name of the status page (required)
            subdomain: Subdomain for accessing the status page (e.g., 'mycompany' for mycompany.pingera.ru)
            domain: Custom domain for the status page
            url: Company URL - users will be redirected there when clicking on the logo
            language: Language for the status page interface ("ru" or "en")
            headline: Headline text displayed on the status page
            page_description: Brief description of what this status page monitors
            time_zone: Timezone for displaying dates and times on the status page
            country: Country where your organization is located
            city: City where your organization is located
            state: State/region where your organization is located
            viewers_must_be_team_members: Whether only team members can view this page (True = private, False = public)
            hidden_from_search: Whether to hide this page from search engines
            allow_page_subscribers: Whether to allow users to subscribe to page updates
            allow_incident_subscribers: Whether to allow users to subscribe to incident updates
            allow_email_subscribers: Whether to allow email subscriptions
            allow_sms_subscribers: Whether to allow SMS subscriptions
            allow_webhook_subscribers: Whether to allow webhook subscriptions
            allow_rss_atom_feeds: Whether to provide RSS/Atom feeds
            support_url: URL to your support or contact page

        Returns:
            JSON string containing the created page details
        """
        _update_tools_client()
        return await pages_tools.create_page(
            name=name,
            subdomain=subdomain,
            domain=domain,
            url=url,
            language=language,
            headline=headline,
            page_description=page_description,
            time_zone=time_zone,
            country=country,
            city=city,
            state=state,
            viewers_must_be_team_members=viewers_must_be_team_members,
            hidden_from_search=hidden_from_search,
            allow_page_subscribers=allow_page_subscribers,
            allow_incident_subscribers=allow_incident_subscribers,
            allow_email_subscribers=allow_email_subscribers,
            allow_sms_subscribers=allow_sms_subscribers,
            allow_webhook_subscribers=allow_webhook_subscribers,
            allow_rss_atom_feeds=allow_rss_atom_feeds,
            support_url=support_url,
        )
    return create_page



# Register tools based on configuration
def register_tools():
    """Register tools based on server configuration and client request."""

    if config.transport_mode == "stdio":
        # In stdio mode, only register requested tools that are compatible with server mode
        requested_tools = config.requested_tools  # None if --tools flag not provided
        tools_to_register = tool_registry.get_tools_to_register(
            requested_tools=requested_tools,
            is_read_write_mode=config.is_read_write()
        )

        logger.info(f"Registering {len(tools_to_register)} tools for stdio mode")
        for tool_name, register_func in tools_to_register.items():
            logger.debug(f"Registering tool: {tool_name}")
            register_func(mcp)

    else:  # SSE mode
        # In SSE mode, register all tools compatible with server mode
        # (tool list filtering happens at runtime based on request headers)
        tools_to_register = tool_registry.get_tools_to_register(
            requested_tools=None,  # Register all tools
            is_read_write_mode=config.is_read_write()
        )

        logger.info(f"Registering {len(tools_to_register)} tools for SSE mode")
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