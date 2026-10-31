"""Check groups."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import CheckGroupsApi
from pingera.models import CheckGroup1, CheckGroup2
from pydantic import Field

from ..api import api
from ..registry import model_tool, tool
from ._types import PageNumber, PageSize

GroupId = Annotated[str, Field(description="Check group ID (see list_check_groups).")]
_EXCLUDE = {"checks_count"}


@tool("check_groups")
def list_check_groups(page: PageNumber = None, page_size: PageSize = None) -> Any:
    """List check groups with their color, position and number of checks."""
    return api(CheckGroupsApi).v1_check_groups_get(page=page, page_size=page_size)


@tool("check_groups")
def get_check_group(group_id: GroupId) -> Any:
    """Get a check group: name, description, color, position and number of checks."""
    return api(CheckGroupsApi).v1_check_groups_group_id_get(group_id=group_id)


@tool("check_groups")
def list_group_checks(group_id: GroupId, page: PageNumber = None, page_size: PageSize = None) -> Any:
    """List the checks in a check group."""
    return api(CheckGroupsApi).v1_check_groups_group_id_checks_get(group_id=group_id, page=page, page_size=page_size)


model_tool(
    "check_groups",
    "create_check_group",
    model=CheckGroup1,
    exclude=_EXCLUDE,
    call=lambda body: api(CheckGroupsApi).v1_check_groups_post(check_group1=body),
    description="Create a check group. Add checks with move_check_to_group or the `group_id` of create/update_check.",
)

model_tool(
    "check_groups",
    "update_check_group",
    model=CheckGroup2,
    partial=True,
    exclude=_EXCLUDE,
    path=[("group_id", "ID of the check group.")],
    call=lambda body, group_id: api(CheckGroupsApi).v1_check_groups_group_id_patch(group_id=group_id, check_group2=body),
    idempotent=True,
    description="Change a check group. Only the fields you pass are changed.",
)


@tool("check_groups", access="write", destructive=True, idempotent=True)
def delete_check_group(group_id: GroupId) -> Any:
    """Delete a check group. Its checks are kept and become ungrouped."""
    return api(CheckGroupsApi).v1_check_groups_group_id_delete(group_id=group_id)
