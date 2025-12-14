
"""Tool registration functions for pages domain."""

from typing import Optional
from ..tool_registry import tool_registry


def register_pages_tools():
    """Register all pages-related tools."""
    
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
            from ..mcp_server import _update_tools_client, pages_tools
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
            from ..mcp_server import _update_tools_client, pages_tools
            _update_tools_client()
            return await pages_tools.get_page_details(page_id)
        return get_page_details
    
    # Continue with create_page, update_page, patch_page, delete_page...
    # (I'll show the pattern, you can extract the rest similarly)
