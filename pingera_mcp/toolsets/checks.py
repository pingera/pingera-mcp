"""Monitoring checks: configuration, regions and on-demand runs."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pingera.api import ChecksApi, CheckGroupsApi, OnDemandChecksApi
from pingera.models import ExecuteCustomCheckRequest, Generated, MonitorCheck, MonitorCheck1
from pydantic import Field

from .. import reference
from ..api import api, parse_time
from ..registry import model_tool, tool
from ._types import CheckId, PageNumber, PageSize, Time

CheckType = Literal["web", "api", "ssl", "tcp", "synthetic", "multistep", "icmp", "dns", "portscan"]
CheckStatus = Literal["ok", "failed", "degraded", "timeout", "pending", "paused"]

_FIELD_DESCRIPTIONS = {
    "parameters": reference.CHECK_PARAMETERS_SHORT,
    "secrets": "Secrets injected as environment variables: [{'secret_id': '...', 'env_variable': 'API_TOKEN'}].",
}


@tool("checks")
def list_checks(
    name: Annotated[str | None, Field(description="Case-insensitive partial match on the check name.")] = None,
    type: CheckType | None = None,
    status: Annotated[
        str | None, Field(description="Status filter, comma separated: ok, failed, degraded, timeout, pending, paused.")
    ] = None,
    group_id: Annotated[str | None, Field(description="Only checks in this group; 'ungrouped' for checks without a group.")] = None,
    include_uptime: Annotated[bool | None, Field(description="Add uptime statistics for the period to every check.")] = None,
    start: Time = None,
    end: Time = None,
    page: PageNumber = None,
    page_size: PageSize = None,
) -> Any:
    """List monitoring checks with their type, target, schedule and current status."""
    return api(ChecksApi).v1_checks_get(
        name=name,
        type=type,
        status=status,
        group_id=group_id,
        include_uptime=include_uptime,
        start_date=parse_time(start),
        end_date=parse_time(end),
        page=page,
        page_size=page_size,
    )


@tool("checks")
def get_check(
    check_id: CheckId,
    include_uptime: Annotated[bool | None, Field(description="Add uptime statistics for the period.")] = None,
    start: Time = None,
    end: Time = None,
) -> Any:
    """Get a check's full configuration (including type-specific parameters and attached secrets) and status."""
    return api(ChecksApi).v1_checks_check_id_get(
        check_id=check_id, include_uptime=include_uptime, start_date=parse_time(start), end_date=parse_time(end)
    )


@tool("checks")
def list_check_regions(check_type: CheckType | None = None) -> Any:
    """List the regions checks can run from (IDs, aliases and supported check types), including private locations."""
    return api(ChecksApi).v1_checks_get_regions_get(check_type=check_type)


model_tool(
    "checks",
    "create_check",
    model=MonitorCheck,
    exclude={"position"},
    descriptions=_FIELD_DESCRIPTIONS,
    call=lambda body: api(ChecksApi).v1_checks_post(monitor_check=body),
    description=(
        "Create a monitoring check. Set `url` for web/api/synthetic/multistep checks and `host` (plus `port` for tcp) "
        "for the other types, and either `interval` (seconds, min 30) or scheduling_type='cron' with `cron_schedule`. "
        "Use get_reference('check_types') for the type-specific `parameters`."
    ),
)

model_tool(
    "checks",
    "update_check",
    model=MonitorCheck1,
    partial=True,
    descriptions=_FIELD_DESCRIPTIONS,
    path=[("check_id", "ID of the check to update.")],
    call=lambda body, check_id: api(ChecksApi).v1_checks_check_id_patch(check_id=check_id, monitor_check1=body),
    idempotent=True,
    description=(
        "Change a check. Only the fields you pass are changed; `parameters` replaces the whole parameters object, so "
        "read the check first and send the merged value. Pause or resume a check with `active`."
    ),
)


@tool("checks", access="write", destructive=True, idempotent=True)
def delete_check(check_id: CheckId) -> Any:
    """Delete a check together with its results and alert rules. This cannot be undone."""
    return api(ChecksApi).v1_checks_check_id_delete(check_id=check_id)


@tool("checks", access="write", idempotent=True)
def move_check_to_group(
    check_id: CheckId,
    group_id: Annotated[str | None, Field(description="Target check group ID; omit or null to remove the check from its group.")] = None,
) -> Any:
    """Move a check into a check group, or out of any group."""
    return api(CheckGroupsApi).v1_checks_check_id_group_patch(check_id=check_id, generated=Generated(group_id=group_id))


@tool("checks", access="run")
def run_check(check_id: CheckId) -> Any:
    """Run an existing check right now, outside its schedule. Returns a job ID; poll get_check_job for the result."""
    return api(OnDemandChecksApi).v1_checks_check_id_execute_post(check_id=check_id)


model_tool(
    "checks",
    "run_custom_check",
    model=ExecuteCustomCheckRequest,
    descriptions=_FIELD_DESCRIPTIONS
    | {"secrets": "Secrets injected as environment variables: [{'secret_id': '...', 'env_variable': 'API_TOKEN'}]."},
    call=lambda body: api(OnDemandChecksApi).v1_checks_execute_post(execute_custom_check_request=body),
    access="run",
    description=(
        "Run a one-off check without saving it, e.g. to test a URL, port, DNS record or Playwright script from chosen "
        "regions. Returns a job ID; poll get_check_job for the result. Uses credits like a scheduled run."
    ),
)


@tool("checks")
def get_check_job(job_id: Annotated[str, Field(description="Job ID returned by run_check or run_custom_check.")]) -> Any:
    """Get the status and, once finished, the results of an on-demand check run."""
    return api(OnDemandChecksApi).v1_checks_jobs_job_id_get(job_id=job_id)


@tool("checks")
def list_check_jobs(
    status: Annotated[str | None, Field(description="Job status filter, e.g. pending, running, completed, failed.")] = None,
    page: PageNumber = None,
    per_page: PageSize = None,
) -> Any:
    """List recent on-demand check runs."""
    return api(OnDemandChecksApi).v1_checks_jobs_get(status=status, page=page, per_page=per_page)
