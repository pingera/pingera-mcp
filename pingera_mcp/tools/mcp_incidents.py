"""
MCP logic functions for incident management.
"""
from typing import Optional, Dict, Any
import json
from pingera_mcp import PingeraClient
from pingera_mcp.tools import IncidentsTools
import logging

logger = logging.getLogger(__name__)


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
    events that that need to be communicated to users
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


async def _get_incident_update_details_logic(client, page_id: str, incident_id: str, update_id: str) -> str:
    """Get detailed information about a specific incident update."""
    try:
        logger.info(f"Getting incident update details - page: {page_id}, incident: {incident_id}, update: {update_id}")

        with client._get_api_client() as api_client:
            from pingera.api import IncidentsApi
            incidents_api = IncidentsApi(api_client)

            update = incidents_api.v1_pages_page_id_incidents_incident_id_updates_update_id_get(
                page_id=page_id, incident_id=incident_id, update_id=update_id
            )

            update_data = {}
            if hasattr(update, '__dict__'):
                update_data = update.__dict__
            elif hasattr(update, 'to_dict'):
                update_data = update.to_dict()
            else:
                update_data = {"raw_response": str(update)}

            return json.dumps({
                "success": True,
                "page_id": page_id,
                "incident_id": incident_id,
                "update_id": update_id,
                "update": update_data
            })

    except Exception as e:
        logger.error(f"Error getting incident update details: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _create_incident_logic(
    client,
    page_id: str,
    name: str,
    status: str,
    body: Optional[str] = None,
    impact: Optional[str] = None,
    deliver_notifications: Optional[bool] = True,
    components: Optional[Dict[str, str]] = None
) -> str:
    """Create a new incident on a status page to communicate issues to users."""
    try:
        logger.info(f"Creating incident on page {page_id}: {name}")

        incident_data = {
            "name": name,
            "status": status,
            "body": body,
            "impact": impact,
            "deliver_notifications": deliver_notifications,
            "components": components or {}
        }

        # Filter out None values
        filtered_data = {k: v for k, v in incident_data.items() if v is not None}

        with client._get_api_client() as api_client:
            from pingera.api import IncidentsApi
            from pingera.models import Incident
            incidents_api = IncidentsApi(api_client)

            incident_model = Incident(**filtered_data)
            result = incidents_api.v1_pages_page_id_incidents_post(
                page_id=page_id, incident=incident_model
            )

            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}

            return json.dumps({
                "success": True,
                "page_id": page_id,
                "incident": result_data
            })

    except Exception as e:
        logger.error(f"Error creating incident: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _update_incident_logic(
    client,
    page_id: str,
    incident_id: str,
    name: Optional[str] = None,
    status: Optional[str] = None,
    body: Optional[str] = None,
    impact: Optional[str] = None,
    deliver_notifications: Optional[bool] = None,
    components: Optional[Dict[str, str]] = None,
    **kwargs
) -> str:
    """Update configuration for an existing incident (full update)."""
    try:
        logger.info(f"Updating incident {incident_id} on page {page_id}")

        incident_data = {
            "name": name,
            "status": status,
            "body": body,
            "impact": impact,
            "deliver_notifications": deliver_notifications,
            "components": components,
            **kwargs  # Include any additional parameters
        }

        # Filter out None values
        filtered_data = {k: v for k, v in incident_data.items() if v is not None}

        if not filtered_data:
            return json.dumps({
                "success": False,
                "error": "No update data provided"
            })

        with client._get_api_client() as api_client:
            from pingera.api import IncidentsApi
            from pingera.models import Incident
            incidents_api = IncidentsApi(api_client)

            incident_model = Incident(**filtered_data)
            result = incidents_api.v1_pages_page_id_incidents_incident_id_put(
                page_id=page_id, incident_id=incident_id, incident=incident_model
            )

            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}

            return json.dumps({
                "success": True,
                "page_id": page_id,
                "incident_id": incident_id,
                "incident": result_data
            })

    except Exception as e:
        logger.error(f"Error updating incident {incident_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _add_incident_update_logic(client, page_id: str, incident_id: str, update_data: dict) -> str:
    """Add a new status update to an existing incident."""
    try:
        logger.info(f"Adding update to incident {incident_id} on page {page_id}")

        with client._get_api_client() as api_client:
            from pingera.api import IncidentsApi
            from pingera.models import IncidentUpdate
            incidents_api = IncidentsApi(api_client)

            update_model = IncidentUpdate(**update_data)
            result = incidents_api.v1_pages_page_id_incidents_incident_id_updates_post(
                page_id=page_id, incident_id=incident_id, incident_update=update_model
            )

            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}

            return json.dumps({
                "success": True,
                "page_id": page_id,
                "incident_id": incident_id,
                "update": result_data
            })

    except Exception as e:
        logger.error(f"Error adding incident update: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _update_incident_update_logic(client, page_id: str, incident_id: str, update_id: str, update_data: dict) -> str:
    """Edit an existing incident status update."""
    try:
        logger.info(f"Updating incident update {update_id}")

        with client._get_api_client() as api_client:
            from pingera.api import IncidentsApi
            from pingera.models import IncidentUpdate
            incidents_api = IncidentsApi(api_client)

            update_model = IncidentUpdate(**update_data)
            result = incidents_api.v1_pages_page_id_incidents_incident_id_updates_update_id_put(
                page_id=page_id, incident_id=incident_id, update_id=update_id, incident_update=update_model
            )

            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}

            return json.dumps({
                "success": True,
                "page_id": page_id,
                "incident_id": incident_id,
                "update_id": update_id,
                "update": result_data
            })

    except Exception as e:
        logger.error(f"Error updating incident update: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _delete_incident_update_logic(client, page_id: str, incident_id: str, update_id: str) -> str:
    """Delete a specific incident status update."""
    try:
        logger.info(f"Deleting incident update {update_id}")

        with client._get_api_client() as api_client:
            from pingera.api import IncidentsApi
            incidents_api = IncidentsApi(api_client)

            incidents_api.v1_pages_page_id_incidents_incident_id_updates_update_id_delete(
                page_id=page_id, incident_id=incident_id, update_id=update_id
            )

            return json.dumps({
                "success": True,
                "deleted": True,
                "page_id": page_id,
                "incident_id": incident_id,
                "update_id": update_id,
                "message": f"Incident update {update_id} deleted successfully"
            })

    except Exception as e:
        logger.error(f"Error deleting incident update: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })