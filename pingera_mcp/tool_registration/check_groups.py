
"""Tool registration functions for check_groups domain."""

from typing import Optional
from ..tool_registry import tool_registry


def register_check_groups_tools():
    """Register all check_groups-related tools."""
    
    @tool_registry.register("list_check_groups", requires_write=False)
    def register_list_check_groups(mcp_instance):
        @mcp_instance.tool()
        async def list_check_groups(
            page: Optional[int] = None,
            page_size: Optional[int] = None
        ) -> str:
            """
            List all check groups in your account.
        
            Check groups are containers that help organize monitoring checks into logical
            collections. Use this tool to see all available groups and their basic information.
        
            Args:
                page: Page number for pagination (default: 1)
                page_size: Number of items per page (default: 20, max: 100)
        
            Returns:
                JSON with list of check groups including their names, IDs, and check counts.
            """
            from ..mcp_server import _update_tools_client, check_groups_tools
            _update_tools_client()
            return await check_groups_tools.list_check_groups(page, page_size)
        return list_check_groups
    
    @tool_registry.register("get_check_group_details", requires_write=False)
    def register_get_check_group_details(mcp_instance):
        @mcp_instance.tool()
        async def get_check_group_details(group_id: str) -> str:
            """
            Get detailed information about a specific check group.
        
            Args:
                group_id: The unique identifier of the check group
        
            Returns:
                JSON with check group details including name, description, and configuration.
            """
            from ..mcp_server import _update_tools_client, check_groups_tools
            _update_tools_client()
            return await check_groups_tools.get_check_group_details(group_id)
        return get_check_group_details
    
    @tool_registry.register("get_checks_in_group", requires_write=False)
    def register_get_checks_in_group(mcp_instance):
        @mcp_instance.tool()
        async def get_checks_in_group(
            group_id: str,
            page: Optional[int] = None,
            page_size: Optional[int] = None
        ) -> str:
            """
            Get all monitoring checks that belong to a specific check group.
        
            Use this tool to see which checks are organized under a particular group.
            This helps understand the monitoring setup and check organization.
        
            Args:
                group_id: The unique identifier of the check group
                page: Page number for pagination (default: 1)
                page_size: Number of items per page (default: 20, max: 100)
        
            Returns:
                JSON with list of checks in the group including their names, URLs, types, and status.
            """
            from ..mcp_server import _update_tools_client, check_groups_tools
            _update_tools_client()
            return await check_groups_tools.get_checks_in_group(group_id, page, page_size)
        return get_checks_in_group
    
    @tool_registry.register("create_check_group", requires_write=True)
    def register_create_check_group(mcp_instance):
        @mcp_instance.tool()
        async def create_check_group(group_data: dict) -> str:
            """
            Create a new check group.
        
            Args:
                group_data: Dictionary containing check group configuration
        
            Returns:
                JSON string containing created check group data
            """
            from ..mcp_server import _update_tools_client, check_groups_tools
            _update_tools_client()
            return await check_groups_tools.create_check_group(group_data)
        return create_check_group
    
    @tool_registry.register("update_check_group", requires_write=True)
    def register_update_check_group(mcp_instance):
        @mcp_instance.tool()
        async def update_check_group(group_id: str, group_data: dict) -> str:
            """
            Update an existing check group.
        
            Args:
                group_id: ID of the check group to update
                group_data: Dictionary containing updated group configuration
        
            Returns:
                JSON string containing updated check group data
            """
            from ..mcp_server import _update_tools_client, check_groups_tools
            _update_tools_client()
            return await check_groups_tools.update_check_group(group_id, group_data)
        return update_check_group
    
    @tool_registry.register("delete_check_group", requires_write=True)
    def register_delete_check_group(mcp_instance):
        @mcp_instance.tool()
        async def delete_check_group(group_id: str) -> str:
            """
            Delete a check group. All checks in the group will be moved to ungrouped.
        
            Args:
                group_id: ID of the check group to delete
        
            Returns:
                JSON string confirming deletion
            """
            from ..mcp_server import _update_tools_client, check_groups_tools
            _update_tools_client()
            return await check_groups_tools.delete_check_group(group_id)
        return delete_check_group
    
    @tool_registry.register("assign_check_to_group", requires_write=True)
    def register_assign_check_to_group(mcp_instance):
        @mcp_instance.tool()
        async def assign_check_to_group(check_id: str, group_id: Optional[str] = None) -> str:
            """
            Assign a check to a group or remove it from a group.
        
            Args:
                check_id: ID of the check to assign
                group_id: ID of the group to assign to (or None to ungroup)
        
            Returns:
                JSON string confirming assignment
            """
            from ..mcp_server import _update_tools_client, check_groups_tools
            _update_tools_client()
            return await check_groups_tools.assign_check_to_group(check_id, group_id)
        return assign_check_to_group
