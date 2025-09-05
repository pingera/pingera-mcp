
"""
MCP tool logic for component management.
"""
from typing import Optional
from pingera_mcp import PingeraClient
from pingera_mcp.tools import ComponentTools

async def _list_component_groups_logic(
    client: PingeraClient,
    page_id: str,
    show_deleted: Optional[bool] = False
) -> str:
    """
    Get only component groups (not individual components) for a status page.

    Use this tool specifically when someone asks for "component groups", "groups only",
    or wants to see just the organizational containers for components. This excludes
    individual components and shows only the group containers.

    Args:
        page_id: The ID of the status page (required, e.g., "tih6xo7z8v7n")
        show_deleted: Whether to include deleted component groups (default: False)

    Returns:
        JSON with list of component groups only, including their names, IDs, positions, and component counts.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    component_tools = ComponentTools(client)
    return await component_tools.list_component_groups(page_id, show_deleted)

async def _list_components_logic(
    client: PingeraClient,
    page_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """
    Get all components (individual services and groups) for a status page with their IDs.

    Use this tool when someone asks for "components", "all components", "component list",
    or wants to see services/systems on a status page. This includes both individual
    components and component groups with their unique identifiers.

    Args:
        page_id: The ID of the status page (required, e.g., "tih6xo7z8v7n")
        page: Page number for pagination (optional, default: 1)
        page_size: Number of components per page (optional, default: 20)

    Returns:
        JSON with complete list of components including names, IDs, status, type (group/individual), and configuration.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    component_tools = ComponentTools(client)
    return await component_tools.list_components(page_id, page, page_size)

async def _get_component_details_logic(client: PingeraClient, page_id: str, component_id: str) -> str:
    """
    Get detailed information about a specific component.

    Components represent individual services or systems that are monitored and displayed
    on your status page. Each component has a status and can be linked to monitoring checks.

    Args:
        page_id: The ID of the status page
        component_id: The unique identifier of the component

    Returns:
        JSON with component details including name, description, status, position, and linked checks.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    component_tools = ComponentTools(client)
    return await component_tools.get_component_details(page_id, component_id)

async def _create_component_logic(
    client: PingeraClient,
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
    """
    Create a new component or component group on a status page.

    Components represent individual services, systems, or features that users
    care about. They can be organized into groups and have their own status.

    Args:
        page_id: The ID of the status page to add the component to
        name: Display name for the component
        description: Optional description of what this component represents
        group: Whether this is a component group (True) or individual component (False)
        group_id: ID of parent group if this component belongs to a group
        only_show_if_degraded: Whether to hide when status is operational
        position: Display order position on the status page
        showcase: Whether to highlight this component prominently
        status: Initial status ('operational', 'degraded_performance', 'partial_outage', 'major_outage')

    Returns:
        JSON with created component details including ID and configuration.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    component_tools = ComponentTools(client)
    return await component_tools.create_component(
        page_id=page_id,
        name=name,
        description=description,
        group=group,
        group_id=group_id,
        only_show_if_degraded=only_show_if_degraded,
        position=position,
        showcase=showcase,
        status=status
    )

async def _patch_component_logic(
    client: PingeraClient,
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
    """
    RECOMMENDED: Partially update specific fields of a component (PATCH method).

    Use this for simple updates like changing the name, status, description, or other individual fields.
    Only the fields you specify will be updated, leaving other settings unchanged.
    This is the preferred method for most component updates.

    Args:
        page_id: The ID of the status page
        component_id: The unique identifier of the component
        name: Display name of the component
        description: Detailed description of the component
        group: Whether this component is a group container for other components
        group_id: ID of the group this component belongs to (if any)
        only_show_if_degraded: Whether to show this component only when it's not operational
        position: Display order position of the component on the status page
        showcase: Whether to prominently display this component on the status page
        status: Current operational status of the component
        start_date: Date when monitoring for this component started (ISO format)

    Returns:
        JSON with updated component configuration.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    component_tools = ComponentTools(client)
    return await component_tools.patch_component(
        page_id, component_id, name, description, group, group_id,
        only_show_if_degraded, position, showcase, status, start_date
    )

async def _delete_component_logic(client: PingeraClient, page_id: str, component_id: str) -> str:
    """
    Delete a component from a status page permanently.

    This removes the component from the status page display and
    deletes all associated historical status data.

    Args:
        page_id: The ID of the status page
        component_id: The unique identifier of the component to delete

    Returns:
        JSON confirming successful deletion.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    component_tools = ComponentTools(client)
    return await component_tools.delete_component(page_id, component_id)
