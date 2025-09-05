
"""
MCP logic functions for check group management.
"""
from typing import Optional

from pingera_mcp import PingeraClient
from pingera_mcp.tools import CheckGroupsTools


async def _list_check_groups_logic(
    client: PingeraClient,
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
    tools = CheckGroupsTools(client)
    return await tools.list_check_groups(page, page_size)


async def _get_check_group_details_logic(client: PingeraClient, group_id: str) -> str:
    """
    Get detailed information about a specific check group.

    Args:
        group_id: The unique identifier of the check group

    Returns:
        JSON with check group details including name, description, and configuration.
    """
    tools = CheckGroupsTools(client)
    return await tools.get_check_group_details(group_id)


async def _get_checks_in_group_logic(
    client: PingeraClient,
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
    tools = CheckGroupsTools(client)
    return await tools.get_checks_in_group(group_id, page, page_size)
