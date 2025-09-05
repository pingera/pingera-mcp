
"""
MCP logic functions for incident management.
"""
from typing import Optional, Dict, Any

from pingera_mcp import PingeraClient
from pingera_mcp.tools import IncidentsTools


async def _list_incidents_logic(
    client: PingeraClient,
    page_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """
    List all incidents for a specific status page.

    Incidents represent service outages, maintenance windows, or other
    events that affect your services and need to be communicated to users
    through your status page.

    Args:
        page_id: The ID of the status page to get incidents for
        page: Page number for pagination
        page_size: Number of incidents per page
        status: Filter by incident status ('investigating', 'identified', 'monitoring', 'resolved')

    Returns:
        JSON with list of incidents including titles, status, impact level, and timestamps.
    """
    tools = IncidentsTools(client)
    return await tools.list_incidents(page_id, page, page_size, status)


async def _create_incident_logic(
    client: PingeraClient,
    page_id: str,
    name: str,
    status: str,
    body: Optional[str] = None,
    impact: Optional[str] = None,
    deliver_notifications: Optional[bool] = True,
    components: Optional[Dict[str, str]] = None
) -> str:
    """
    Create a new incident on a status page to communicate issues to users.

    Post an incident when you need to inform users about service outages,
    maintenance, or other events affecting your services.

    Args:
        page_id: The ID of the status page to post the incident on
        name: The name/title of the incident (1-200 characters, required)
        status: Current status of the incident (required, e.g., 'investigating', 'identified', 'monitoring', 'resolved')
        body: The initial update body content for the incident
        impact: Impact level ('none', 'minor', 'major', 'critical')
        deliver_notifications: Whether to send notifications when creating this incident (default: True)
        components: A dictionary mapping component IDs to their status during incident creation

    Returns:
        JSON with created incident details including ID and public URL.
    """
    tools = IncidentsTools(client)
    return await tools.create_incident(page_id, name, status, body, impact, deliver_notifications, components)


async def _patch_incident_logic(
    client: PingeraClient,
    page_id: str,
    incident_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    body: Optional[str] = None,
    impact: Optional[str] = None,
    deliver_notifications: Optional[bool] = None,
    components: Optional[Dict[str, str]] = None,
    auto_transition_to_maintenance_state: Optional[bool] = None,
    auto_transition_to_operational_state: Optional[bool] = None,
    auto_transition_deliver_notifications_at_start: Optional[bool] = None,
    auto_transition_deliver_notifications_at_end: Optional[bool] = None,
    scheduled_for: Optional[str] = None,
    scheduled_until: Optional[str] = None,
    scheduled_remind_prior: Optional[bool] = None,
    scheduled_auto_in_progress: Optional[bool] = None,
    scheduled_auto_completed: Optional[bool] = None,
    reminder_intervals: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    RECOMMENDED: Partially update specific fields of an incident (PATCH method).

    Use this for simple updates like changing the name, status, description, or other individual fields.
    Only the fields you specify will be updated, leaving other settings unchanged.
    This is the preferred method for most incident updates.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident
        name: The name/title of the incident
        status: The current status of the incident
        body: The main description/body content of the incident
        impact: The impact level of the incident
        deliver_notifications: Whether to send notifications when updating this incident
        components: Dictionary mapping component IDs to their status
        auto_transition_to_maintenance_state: Whether to auto transition components to maintenance
        auto_transition_to_operational_state: Whether to auto transition components to operational
        auto_transition_deliver_notifications_at_start: Whether to deliver notifications at start
        auto_transition_deliver_notifications_at_end: Whether to deliver notifications at end
        scheduled_for: For scheduled maintenance, when maintenance starts (ISO format)
        scheduled_until: For scheduled maintenance, when maintenance ends (ISO format)
        scheduled_remind_prior: Whether to send reminder notifications before scheduled maintenance
        scheduled_auto_in_progress: Whether scheduled maintenance should auto be marked in progress
        scheduled_auto_completed: Whether scheduled maintenance should auto be marked completed
        reminder_intervals: Intervals for reminder notifications
        metadata: Additional metadata associated with the incident

    Returns:
        JSON with updated incident configuration.
    """
    tools = IncidentsTools(client)
    return await tools.patch_incident(
        page_id, incident_id, name, status, body, impact, deliver_notifications, components,
        auto_transition_to_maintenance_state, auto_transition_to_operational_state,
        auto_transition_deliver_notifications_at_start, auto_transition_deliver_notifications_at_end,
        scheduled_for, scheduled_until, scheduled_remind_prior, scheduled_auto_in_progress,
        scheduled_auto_completed, reminder_intervals, metadata
    )


async def _delete_incident_logic(client: PingeraClient, page_id: str, incident_id: str) -> str:
    """
    Delete an incident from a status page permanently.

    This removes the incident and all its updates from the status page.
    Use with caution as this action cannot be undone.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident to delete

    Returns:
        JSON confirming successful deletion.
    """
    tools = IncidentsTools(client)
    return await tools.delete_incident(page_id, incident_id)


async def _get_incident_details_logic(client: PingeraClient, page_id: str, incident_id: str) -> str:
    """
    Get detailed information about a specific incident.

    Shows complete incident details including description, affected components,
    impact level, timeline, and all status updates posted during the incident.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident

    Returns:
        JSON with incident details including description, components, updates, and resolution timeline.
    """
    tools = IncidentsTools(client)
    return await tools.get_incident_details(page_id, incident_id)


async def _get_incident_updates_logic(client: PingeraClient, page_id: str, incident_id: str) -> str:
    """
    Get all status updates posted during an incident.

    Shows chronological list of updates that were posted to keep users
    informed about the incident progress, investigation, and resolution.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident

    Returns:
        JSON with list of incident updates including timestamps, status changes, and messages.
    """
    tools = IncidentsTools(client)
    return await tools.get_incident_updates(page_id, incident_id)


async def _get_incident_update_details_logic(client: PingeraClient, page_id: str, incident_id: str, update_id: str) -> str:
    """
    Get detailed information about a specific incident update.

    Shows the complete content of a specific status update that was posted
    during an incident, including the message, timestamp, and status change.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident
        update_id: The unique identifier of the specific update

    Returns:
        JSON with update details including message content, timestamp, and status information.
    """
    tools = IncidentsTools(client)
    return await tools.get_incident_update_details(page_id, incident_id, update_id)


async def _add_incident_update_logic(client: PingeraClient, page_id: str, incident_id: str, update_data: dict) -> str:
    """
    Add a new status update to an existing incident.

    Post updates to keep users informed about incident progress,
    investigation findings, or resolution steps.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident
        update_data: Dictionary with update details including:
            - body: The update message text
            - status: New incident status if changed
            - deliver_notifications: Whether to notify subscribers

    Returns:
        JSON with created update details including timestamp and content.
    """
    tools = IncidentsTools(client)
    return await tools.add_incident_update(page_id, incident_id, update_data)


async def _update_incident_update_logic(client: PingeraClient, page_id: str, incident_id: str, update_id: str, update_data: dict) -> str:
    """
    Edit an existing incident status update.

    Modify the content or status of a previously posted incident update.
    Useful for correcting typos or adding additional information.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident
        update_id: The unique identifier of the update to modify
        update_data: Dictionary with updated content and settings

    Returns:
        JSON with updated incident update details.
    """
    tools = IncidentsTools(client)
    return await tools.update_incident_update(page_id, incident_id, update_id, update_data)


async def _delete_incident_update_logic(client: PingeraClient, page_id: str, incident_id: str, update_id: str) -> str:
    """
    Delete a specific incident status update.

    Remove an incident update from the timeline. This action cannot
    be undone and may confuse users if the update was already public.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident
        update_id: The unique identifier of the update to delete

    Returns:
        JSON confirming successful deletion.
    """
    tools = IncidentsTools(client)
    return await tools.delete_incident_update(page_id, incident_id, update_id)
