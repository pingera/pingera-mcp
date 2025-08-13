"""
MCP Server implementation for Pingera monitoring service.
"""
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP

from config import Config
from pingera import PingeraClient
from pingera.tools import PagesTools, StatusTools, ComponentTools
from pingera.resources import PagesResources, StatusResources, ComponentResources


def create_mcp_server(config: Config) -> FastMCP:
    """
    Create and configure the MCP server for Pingera.

    Args:
        config: Configuration object

    Returns:
        FastMCP: Configured MCP server
    """
    logger = logging.getLogger(__name__)

    # Initialize Pingera client (SDK-based)
    pingera_client = PingeraClient(
        api_key=config.api_key,
        base_url=config.base_url,
        timeout=config.timeout,
        max_retries=config.max_retries
    )
    logger.info("Using Pingera SDK client")

    # Initialize tool and resource handlers
    pages_tools = PagesTools(pingera_client)
    status_tools = StatusTools(pingera_client)
    component_tools = ComponentTools(pingera_client)
    pages_resources = PagesResources(pingera_client)
    status_resources = StatusResources(pingera_client, config)
    component_resources = ComponentResources(pingera_client)

    # Create MCP server
    mcp = FastMCP(config.server_name)

    # Register resources
    @mcp.resource("pingera://pages")
    async def get_pages_resource() -> str:
        return await pages_resources.get_pages_resource()

    @mcp.resource("pingera://pages/{page_id}")
    async def get_page_resource(page_id: str) -> str:
        return await pages_resources.get_page_resource(page_id)

    @mcp.resource("pingera://status")
    async def get_status_resource() -> str:
        return await status_resources.get_status_resource()

    # Register read-only tools
    @mcp.tool()
    async def list_pages(
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        status: Optional[str] = None
    ) -> str:
        return await pages_tools.list_pages(page, per_page, status)

    @mcp.tool()
    async def get_page_details(page_id: int) -> str:
        return await pages_tools.get_page_details(page_id)

    @mcp.tool()
    async def test_pingera_connection() -> str:
        return await status_tools.test_pingera_connection()

    @mcp.tool()
    async def list_component_groups(
        page_id: str,
        show_deleted: Optional[bool] = False
    ) -> str:
        return await component_tools.list_component_groups(page_id, show_deleted)

    @mcp.tool()
    async def get_component_details(page_id: str, component_id: str) -> str:
        return await component_tools.get_component_details(page_id, component_id)

    # Register write tools only if in read-write mode
    if config.is_read_write():
        logger.info("Read-write mode enabled - adding write operations")

        @mcp.tool()
        async def create_page(
            name: str,
            subdomain: Optional[str] = None,
            domain: Optional[str] = None,
            url: Optional[str] = None,
            language: Optional[str] = None,
            **kwargs
        ) -> str:
            return await pages_tools.create_page(name, subdomain, domain, url, language, **kwargs)

        @mcp.tool()
        async def update_page(
            page_id: str,
            name: Optional[str] = None,
            subdomain: Optional[str] = None,
            domain: Optional[str] = None,
            url: Optional[str] = None,
            language: Optional[str] = None,
            **kwargs
        ) -> str:
            return await pages_tools.update_page(page_id, name, subdomain, domain, url, language, **kwargs)

        @mcp.tool()
        async def patch_page(page_id: str, **kwargs) -> str:
            return await pages_tools.patch_page(page_id, **kwargs)

        @mcp.tool()
        async def delete_page(page_id: str) -> str:
            return await pages_tools.delete_page(page_id)

        @mcp.tool()
        async def create_component(
            page_id: str,
            name: str,
            description: Optional[str] = None,
            group: Optional[bool] = False,
            group_id: Optional[str] = None,
            only_show_if_degraded: Optional[bool] = None,
            position: Optional[int] = None,
            showcase: Optional[bool] = None,
            status: Optional[str] = None,
            **kwargs
        ) -> str:
            return await component_tools.create_component(
                page_id, name, description, group, group_id, 
                only_show_if_degraded, position, showcase, status, **kwargs
            )

        @mcp.tool()
        async def update_component(
            page_id: str,
            component_id: str,
            name: Optional[str] = None,
            description: Optional[str] = None,
            group: Optional[bool] = None,
            group_id: Optional[str] = None,
            only_show_if_degraded: Optional[bool] = None,
            position: Optional[int] = None,
            showcase: Optional[bool] = None,
            status: Optional[str] = None,
            **kwargs
        ) -> str:
            return await component_tools.update_component(
                page_id, component_id, name, description, group, group_id,
                only_show_if_degraded, position, showcase, status, **kwargs
            )

        @mcp.tool()
        async def patch_component(page_id: str, component_id: str, **kwargs) -> str:
            return await component_tools.patch_component(page_id, component_id, **kwargs)

        @mcp.tool()
        async def delete_component(page_id: str, component_id: str) -> str:
            return await component_tools.delete_component(page_id, component_id)

    return mcp