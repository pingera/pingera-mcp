"""Status page components, component groups and component uptime."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import StatusPagesComponentsApi
from pingera.models import Component, Component1, ComponentUptimeBulkRequest
from pydantic import Field

from ..api import api
from ..registry import model_tool, tool
from ._types import ComponentId, PageId

UptimePeriod = Annotated[
    str | None,
    Field(description="Period bound as YYYY, YYYY-MM or YYYY-MM-DD (UTC). Defaults: the last 90 days."),
]

_COMPONENT_EXCLUDE = {"page_id", "group"}
_GROUP_EXCLUDE = {"page_id", "group", "group_id", "status", "only_show_if_degraded", "start_date"}


def _components():
    return api(StatusPagesComponentsApi)


@tool("components")
def list_components(
    page_id: PageId,
    show_groups: Annotated[bool | None, Field(description="Include component groups in the list.")] = None,
    show_deleted: Annotated[bool | None, Field(description="Include deleted components.")] = None,
) -> Any:
    """List a status page's components with their IDs, status, group and position."""
    return _components().v1_pages_page_id_components_get(
        page_id=page_id, show_groups=show_groups, show_deleted=show_deleted
    )


@tool("components")
def get_component(page_id: PageId, component_id: ComponentId) -> Any:
    """Get a status page component: status, description, group and display settings."""
    return _components().v1_pages_page_id_components_component_id_get(page_id=page_id, component_id=component_id)


@tool("components")
def list_component_groups(
    page_id: PageId,
    show_deleted: Annotated[bool | None, Field(description="Include deleted groups.")] = None,
) -> Any:
    """List a status page's component groups and the components in them."""
    return _components().v1_pages_page_id_component_groups_get(page_id=page_id, show_deleted=show_deleted)


@tool("components")
def get_component_group(page_id: PageId, group_id: Annotated[str, Field(description="Component group ID.")]) -> Any:
    """Get a component group and its member components."""
    return _components().v1_pages_page_id_component_groups_component_id_get(page_id=page_id, component_id=group_id)


@tool("components")
def list_component_statuses() -> Any:
    """List the valid component statuses (operational, degraded_performance, partial_outage, ...)."""
    return _components().v1_component_statuses_get()


@tool("components")
def get_component_uptime(page_id: PageId, component_id: ComponentId, start: UptimePeriod = None, end: UptimePeriod = None) -> Any:
    """Get a component's uptime percentage and daily outage breakdown for a period."""
    return _components().v1_pages_page_id_components_component_id_uptime_get(
        page_id=page_id, component_id=component_id, start=start, end=end
    )


@tool("components")
def get_page_uptime(
    page_id: PageId,
    component_ids: Annotated[
        list[str] | None, Field(description="Components to include; all components of the page when omitted.")
    ] = None,
    start: UptimePeriod = None,
    end: UptimePeriod = None,
) -> Any:
    """Get uptime percentage and outage time for several (by default all) components of a status page."""
    if not component_ids:
        listed = _components().v1_pages_page_id_components_get(page_id=page_id)
        component_ids = [item["id"] for item in listed if isinstance(item, dict) and not item.get("group")]
    if not component_ids:
        return {"components": [], "message": "The page has no components."}
    return _components().v1_pages_page_id_components_uptime_post(
        page_id=page_id,
        component_uptime_bulk_request=ComponentUptimeBulkRequest(component_ids=component_ids),
        start=start,
        end=end,
    )


model_tool(
    "components",
    "create_component",
    model=Component,
    exclude=_COMPONENT_EXCLUDE,
    path=[("page_id", "ID of the status page.")],
    call=lambda body, page_id: _components().v1_pages_page_id_components_post(page_id=page_id, component=body),
    description="Add a component (a service or part of the system shown on the status page). Put it in a group with `group_id`.",
)

model_tool(
    "components",
    "update_component",
    model=Component1,
    partial=True,
    exclude=_COMPONENT_EXCLUDE,
    path=[("page_id", "ID of the status page."), ("component_id", "ID of the component to update.")],
    call=lambda body, page_id, component_id: _components().v1_pages_page_id_components_component_id_patch(
        page_id=page_id, component_id=component_id, component1=body
    ),
    idempotent=True,
    description=(
        "Change a component, e.g. its `status` (see list_component_statuses), name, description or group. "
        "Only the fields you pass are changed."
    ),
)


@tool("components", access="write", destructive=True, idempotent=True)
def delete_component(page_id: PageId, component_id: ComponentId) -> Any:
    """Delete a component from a status page."""
    return _components().v1_pages_page_id_components_component_id_delete(page_id=page_id, component_id=component_id)


model_tool(
    "components",
    "create_component_group",
    model=Component,
    exclude=_GROUP_EXCLUDE,
    path=[("page_id", "ID of the status page.")],
    call=lambda body, page_id: _components().v1_pages_page_id_component_groups_post(page_id=page_id, component=body),
    description="Create a component group. Then move components into it with update_component(group_id=...).",
)

model_tool(
    "components",
    "update_component_group",
    model=Component1,
    partial=True,
    exclude=_GROUP_EXCLUDE,
    path=[("page_id", "ID of the status page."), ("group_id", "ID of the component group.")],
    call=lambda body, page_id, group_id: _components().v1_pages_page_id_component_groups_component_id_patch(
        page_id=page_id, component_id=group_id, component1=body
    ),
    idempotent=True,
    description="Rename or reorder a component group. Only the fields you pass are changed.",
)


@tool("components", access="write", destructive=True, idempotent=True)
def delete_component_group(page_id: PageId, group_id: Annotated[str, Field(description="Component group ID.")]) -> Any:
    """Delete a component group. Its components are kept and become ungrouped."""
    return _components().v1_pages_page_id_component_groups_component_id_delete(page_id=page_id, component_id=group_id)
