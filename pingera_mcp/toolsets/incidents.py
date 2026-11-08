"""Status page incidents, incident updates, scheduled maintenance, postmortems and incident templates."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import StatusPagesIncidentsApi, StatusPagesIncidentTemplatesApi
from pingera.models import (
    IncidentCreate,
    IncidentPostmortem,
    IncidentTemplate,
    IncidentTemplate1,
    IncidentUpdateCreate,
    IncidentUpdateEdit,
    IncidentUpdateSchemaEdit,
    LogPastIncident,
)
from pydantic import Field

from ..api import api
from ..registry import model_tool, tool
from ._types import IncidentId, PageId

UpdateId = Annotated[str, Field(description="Incident update ID (see list_incident_updates).")]
TemplateId = Annotated[str, Field(description="Incident template ID (see list_incident_templates).")]

_COMPONENTS = (
    "Affected components and their status, e.g. {'<component_id>': 'major_outage'} "
    "(statuses: see list_component_statuses)."
)
_TEMPLATE_COMPONENTS = (
    "Components to pre-select, e.g. {'<component_id>': 'major_outage'}. For maintenance templates the status is "
    "always stored as under_maintenance."
)
_FROM_TEMPLATE = (
    " To start from a saved template (list_incident_templates), copy its `title` to `name` and its `body`, `status` "
    "and `components`, then adjust them."
)
_SYSTEM_FIELDS = {"scheduled_reminded_at"}
_INCIDENT_PATH = [("page_id", "Status page ID."), ("incident_id", "Incident ID.")]


def _incidents():
    return api(StatusPagesIncidentsApi)


def _templates():
    return api(StatusPagesIncidentTemplatesApi)


@tool("incidents")
def list_incidents(
    page_id: PageId,
    component_id: Annotated[str | None, Field(description="Only incidents affecting this component.")] = None,
) -> Any:
    """List a status page's incidents and maintenance windows, newest first."""
    return _incidents().v1_pages_page_id_incidents_get(page_id=page_id, component_id=component_id)


@tool("incidents")
def list_unresolved_incidents(page_id: PageId) -> Any:
    """List a status page's incidents that are not resolved yet."""
    return _incidents().v1_pages_page_id_incidents_unresolved_get(page_id=page_id)


@tool("incidents")
def list_maintenances(
    page_id: PageId,
    status: Annotated[str | None, Field(description="Maintenance status filter: scheduled, in_progress, verifying or completed.")] = None,
) -> Any:
    """List a status page's scheduled maintenance windows."""
    return _incidents().v1_pages_page_id_incidents_maintenance_get(page_id=page_id, status=status)


@tool("incidents")
def get_incident(page_id: PageId, incident_id: IncidentId) -> Any:
    """Get an incident with its status, impact, affected components and timeline."""
    return _incidents().v1_pages_page_id_incidents_incident_id_get(page_id=page_id, incident_id=incident_id)


@tool("incidents")
def list_incident_updates(page_id: PageId, incident_id: IncidentId) -> Any:
    """List the updates (timeline entries) posted to an incident."""
    return _incidents().v1_pages_page_id_incidents_incident_id_incident_updates_get(
        page_id=page_id, incident_id=incident_id
    )


@tool("incidents")
def get_incident_options() -> Any:
    """List the valid incident statuses, maintenance statuses and impact levels."""
    incidents = _incidents()
    return {
        "incident_statuses": incidents.v1_incident_statuses_get(),
        "maintenance_statuses": incidents.v1_maintenance_statuses_get(),
        "impacts": incidents.v1_incident_impacts_get(),
    }


@tool("incidents")
def get_incident_postmortem(page_id: PageId, incident_id: IncidentId) -> Any:
    """Get an incident's postmortem (published text and draft)."""
    return _incidents().v1_pages_page_id_incidents_incident_id_postmortem_get(page_id=page_id, incident_id=incident_id)


model_tool(
    "incidents",
    "create_incident",
    model=IncidentCreate,
    exclude=_SYSTEM_FIELDS,
    descriptions={"components": _COMPONENTS},
    path=[("page_id", "Status page ID.")],
    call=lambda body, page_id: _incidents().v1_pages_page_id_incidents_post(page_id=page_id, incident_create=body),
    description=(
        "Open an incident on a status page, or schedule maintenance (status 'scheduled', impact 'maintenance', "
        "`scheduled_for` and `scheduled_until`). `body` is the first public update. Valid values: get_incident_options."
        + _FROM_TEMPLATE
        + " For maintenance templates, set `scheduled_until` to `scheduled_for` plus `duration_minutes`."
    ),
)

model_tool(
    "incidents",
    "update_incident",
    model=IncidentUpdateSchemaEdit,
    partial=True,
    exclude=_SYSTEM_FIELDS,
    descriptions={"components": _COMPONENTS},
    path=_INCIDENT_PATH,
    call=lambda body, page_id, incident_id: _incidents().v1_pages_page_id_incidents_incident_id_patch(
        page_id=page_id, incident_id=incident_id, incident_update_schema_edit=body
    ),
    idempotent=True,
    description=(
        "Change an incident (name, status, impact, components, schedule). Passing `body` with a new `status` also "
        "posts a timeline update; to only post an update use add_incident_update."
    ),
)


@tool("incidents", access="write", destructive=True, idempotent=True)
def delete_incident(page_id: PageId, incident_id: IncidentId) -> Any:
    """Delete an incident and its updates from a status page."""
    return _incidents().v1_pages_page_id_incidents_incident_id_delete(page_id=page_id, incident_id=incident_id)


model_tool(
    "incidents",
    "add_incident_update",
    model=IncidentUpdateCreate,
    path=_INCIDENT_PATH,
    call=lambda body, page_id, incident_id: _incidents().v1_pages_page_id_incidents_incident_id_incident_updates_post(
        page_id=page_id, incident_id=incident_id, incident_update_create=body
    ),
    description=(
        "Post a timeline update to an incident (e.g. identified, monitoring, resolved) and notify subscribers. "
        "To use a saved incident template, copy its `body` and `status` (the incident title is not changed)."
    ),
)

model_tool(
    "incidents",
    "edit_incident_update",
    model=IncidentUpdateEdit,
    partial=True,
    descriptions={"components": _COMPONENTS},
    path=[*_INCIDENT_PATH, ("update_id", "Incident update ID.")],
    call=lambda body, page_id, incident_id, update_id: _incidents().v1_pages_page_id_incidents_incident_id_incident_updates_incident_update_id_patch(
        page_id=page_id, incident_id=incident_id, incident_update_id=update_id, incident_update_edit=body
    ),
    idempotent=True,
    description="Fix the text or component statuses of an already posted incident update.",
)


@tool("incidents", access="write", destructive=True, idempotent=True)
def delete_incident_update(page_id: PageId, incident_id: IncidentId, update_id: UpdateId) -> Any:
    """Delete one update from an incident's timeline."""
    return _incidents().v1_pages_page_id_incidents_incident_id_incident_updates_incident_update_id_delete(
        page_id=page_id, incident_id=incident_id, incident_update_id=update_id
    )


model_tool(
    "incidents",
    "log_past_incident",
    model=LogPastIncident,
    path=[("page_id", "Status page ID.")],
    call=lambda body, page_id: _incidents().v1_pages_page_id_incidents_log_past_incident_post(
        page_id=page_id, log_past_incident=body
    ),
    description=(
        "Record an incident that already happened, with its timeline, so it appears in the page history and uptime. "
        "`incident_updates` are in chronological order; the last one usually has status 'resolved'."
    ),
)

model_tool(
    "incidents",
    "save_incident_postmortem",
    model=IncidentPostmortem,
    partial=True,
    exclude={"incident_id", "preview_key", "body_updated_at", "body_draft_updated_at", "published_at"},
    path=_INCIDENT_PATH,
    call=lambda body, page_id, incident_id: _incidents().v1_pages_page_id_incidents_incident_id_postmortem_put(
        page_id=page_id, incident_id=incident_id, incident_postmortem=body
    ),
    idempotent=True,
    description="Save an incident postmortem (Markdown). Write to `body_draft`, then publish with publish_incident_postmortem.",
)


@tool("incidents", access="write", idempotent=True)
def publish_incident_postmortem(page_id: PageId, incident_id: IncidentId) -> Any:
    """Publish an incident's postmortem draft on the status page."""
    return _incidents().v1_pages_page_id_incidents_incident_id_postmortem_publish_put(
        page_id=page_id, incident_id=incident_id
    )


@tool("incidents")
def list_incident_templates(
    page_id: PageId,
    type: Annotated[str | None, Field(description="Only 'incident' or only 'maintenance' templates.")] = None,
) -> Any:
    """List a status page's saved incident and maintenance templates (title, message, status, components, duration)."""
    return _templates().v1_pages_page_id_incident_templates_get(page_id=page_id, type=type)


@tool("incidents")
def get_incident_template(page_id: PageId, template_id: TemplateId) -> Any:
    """Get one incident or maintenance template with its full message."""
    return _templates().v1_pages_page_id_incident_templates_template_id_get(page_id=page_id, template_id=template_id)


model_tool(
    "incidents",
    "create_incident_template",
    model=IncidentTemplate,
    descriptions={"components": _TEMPLATE_COMPONENTS},
    path=[("page_id", "Status page ID.")],
    call=lambda body, page_id: _templates().v1_pages_page_id_incident_templates_post(
        page_id=page_id, incident_template=body
    ),
    description=(
        "Save a reusable incident or maintenance template on a status page (max 50 per page). `status` is only for "
        "incident templates, `duration_minutes` only for maintenance templates."
    ),
)

model_tool(
    "incidents",
    "update_incident_template",
    model=IncidentTemplate1,
    partial=True,
    descriptions={"components": _TEMPLATE_COMPONENTS},
    path=[("page_id", "Status page ID."), ("template_id", "Incident template ID.")],
    call=lambda body, page_id, template_id: _templates().v1_pages_page_id_incident_templates_template_id_patch(
        page_id=page_id, template_id=template_id, incident_template1=body
    ),
    idempotent=True,
    description="Change an incident or maintenance template; only the fields passed are updated.",
)


@tool("incidents", access="write", destructive=True, idempotent=True)
def delete_incident_template(page_id: PageId, template_id: TemplateId) -> Any:
    """Delete an incident or maintenance template; incidents created from it are not affected."""
    return _templates().v1_pages_page_id_incident_templates_template_id_delete(page_id=page_id, template_id=template_id)

