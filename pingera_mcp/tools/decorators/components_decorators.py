
"""
Component management tool decorators.
"""
from typing import Optional


def register_components_tools(mcp, config, component_tools, update_tools_client_func):
    """Register all component-related MCP tools."""
    
    @mcp.tool()
    async def list_component_groups(
        page_id: str,
        show_deleted: Optional[bool] = False
    ) -> str:
        """Get only component groups (not individual components) for a status page."""
        update_tools_client_func()
        return await component_tools.list_component_groups(page_id, show_deleted)

    @mcp.tool()
    async def list_components(
        page_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """Get all components (individual services and groups) for a status page with their IDs."""
        update_tools_client_func()
        return await component_tools.list_components(page_id, page, page_size)

    @mcp.tool()
    async def get_component_details(page_id: str, component_id: str) -> str:
        """Get detailed information about a specific component."""
        update_tools_client_func()
        return await component_tools.get_component_details(page_id, component_id)

    if config.is_read_write():
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
            status: Optional[str] = None
        ) -> str:
            """Create a new component or component group on a status page."""
            update_tools_client_func()
            return await component_tools.create_component(
                page_id=page_id, name=name, description=description,
                group=group, group_id=group_id,
                only_show_if_degraded=only_show_if_degraded,
                position=position, showcase=showcase, status=status
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
            """FULL UPDATE: Replace all component configuration (PUT method)."""
            update_tools_client_func()
            return await component_tools.update_component(
                page_id, component_id, name, description, group, group_id,
                only_show_if_degraded, position, showcase, status, **kwargs
            )

        @mcp.tool()
        async def patch_component(
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
            start_date: Optional[str] = None
        ) -> str:
            """RECOMMENDED: Partially update specific fields of a component (PATCH method)."""
            update_tools_client_func()
            return await component_tools.patch_component(
                page_id, component_id, name, description, group, group_id,
                only_show_if_degraded, position, showcase, status, start_date
            )

        @mcp.tool()
        async def delete_component(page_id: str, component_id: str) -> str:
            """Delete a component from a status page permanently."""
            update_tools_client_func()
            return await component_tools.delete_component(page_id, component_id)
