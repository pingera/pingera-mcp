"""Check results, uptime, response times, status history and multi-region executions."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pingera.api import ChecksApi, ChecksUnifiedResultsApi, ExecutionGroupsApi
from pydantic import Field

from ..api import api, parse_time
from ..registry import tool
from ._types import CheckId, PageNumber, PageSize, Time

ResultStatus = Literal["ok", "failed", "degraded", "timeout", "pending"]
Region = Annotated[str | None, Field(description="Only results from this region (ID or alias, see list_check_regions).")]
MultiRegion = Annotated[
    bool | None, Field(description="Only multi-region executions (true) or only single-region runs (false).")
]


@tool("results")
def list_check_results(
    check_id: CheckId,
    failed_only: Annotated[bool | None, Field(description="Only failed, degraded or timed-out results.")] = None,
    start: Time = None,
    end: Time = None,
    page: PageNumber = None,
    page_size: PageSize = None,
) -> Any:
    """List a check's results (newest first) with status, response time, region and error message."""
    return api(ChecksApi).v1_checks_check_id_results_get(
        check_id=check_id,
        failed_only=failed_only,
        start_date=parse_time(start),
        end_date=parse_time(end),
        page=page,
        page_size=page_size,
    )


@tool("results")
def get_check_result(
    check_id: CheckId, result_id: Annotated[str, Field(description="Result ID (see list_check_results).")]
) -> Any:
    """Get one check result in full: timings, HTTP response, SSL/DNS/port scan details, Playwright logs and errors."""
    return api(ChecksApi).v1_checks_check_id_results_check_result_id_get(check_id=check_id, check_result_id=result_id)


@tool("results")
def search_results(
    check_id: Annotated[str | None, Field(description="Only results of this check.")] = None,
    status: ResultStatus | None = None,
    check_type: Annotated[str | None, Field(description="Only results of this check type, e.g. web, api, synthetic.")] = None,
    result_type: Annotated[
        Literal["regular", "on_demand"] | None, Field(description="Scheduled runs ('regular') or on-demand runs.")
    ] = None,
    region: Region = None,
    is_multi_region: MultiRegion = None,
    execution_group_id: Annotated[str | None, Field(description="Only results of this multi-region execution.")] = None,
    has_alerts: Annotated[bool | None, Field(description="Only results that fired (true) or did not fire (false) alerts.")] = None,
    start: Time = None,
    end: Time = None,
    page: PageNumber = None,
    page_size: PageSize = None,
) -> Any:
    """Search results across all checks (scheduled and on-demand), e.g. every failure in the last hour."""
    return api(ChecksUnifiedResultsApi).v1_checks_all_results_get(
        check_id=check_id,
        status=status,
        check_type=check_type,
        result_type=result_type,
        region=region,
        is_multi_region=is_multi_region,
        execution_group_id=execution_group_id,
        has_alerts=has_alerts,
        start_date=parse_time(start),
        end_date=parse_time(end),
        page=page,
        page_size=page_size,
    )


@tool("results")
def get_check_uptime(check_id: CheckId, start: Time = None, end: Time = None) -> Any:
    """Get a check's uptime percentage, average response time and hourly status breakdown (default: last 24 hours)."""
    return api(ChecksApi).v1_checks_check_id_uptime_get(
        check_id=check_id, start_time=parse_time(start), end_time=parse_time(end)
    )


@tool("results")
def get_check_status_periods(check_id: CheckId, page: PageNumber = None, page_size: PageSize = None) -> Any:
    """Get the periods when a check was up, failing or degraded and how long each lasted (newest first)."""
    return api(ChecksApi).v1_checks_check_id_status_history_get(check_id=check_id, page=page, page_size=page_size)


@tool("results")
def get_response_times(
    check_id: CheckId,
    region: Region = None,
    status: ResultStatus | None = None,
    is_multi_region: MultiRegion = None,
    start: Time = None,
    end: Time = None,
) -> Any:
    """Get a check's response time series and average/p95/p99 per region, to compare regions or spot slowdowns."""
    return api(ChecksUnifiedResultsApi).v1_checks_check_id_response_times_get(
        check_id=check_id,
        region=region,
        status=status,
        is_multi_region=is_multi_region,
        start_date=parse_time(start),
        end_date=parse_time(end),
    )


@tool("results")
def get_status_counts(
    check_id: Annotated[str | None, Field(description="One check; all checks when omitted.")] = None,
    check_type: Annotated[str | None, Field(description="Only checks of this type.")] = None,
    region: Region = None,
    status: ResultStatus | None = None,
    is_multi_region: MultiRegion = None,
    has_alerts: Annotated[bool | None, Field(description="Only results that fired (true) or did not fire (false) alerts.")] = None,
    start: Time = None,
    end: Time = None,
) -> Any:
    """Count results by status and region over a period, for one check or all checks."""
    return api(ChecksUnifiedResultsApi).v1_checks_status_history_get(
        check_id=check_id,
        check_type=check_type,
        region=region,
        status=status,
        is_multi_region=is_multi_region,
        has_alerts=has_alerts,
        start_date=parse_time(start),
        end_date=parse_time(end),
    )


@tool("results")
def list_execution_groups(
    check_id: CheckId,
    status: Annotated[str | None, Field(description="Execution status filter.")] = None,
    page: PageNumber = None,
    page_size: PageSize = None,
) -> Any:
    """List a multi-region check's executions; each groups the simultaneous runs from all its regions."""
    return api(ExecutionGroupsApi).v1_checks_check_id_execution_groups_get(
        check_id=check_id, status=status, page=page, page_size=page_size
    )


@tool("results")
def get_execution_group(
    group_id: Annotated[str, Field(description="Execution group ID (see list_execution_groups).")],
    include_regional_results: Annotated[bool, Field(description="Add the result from every region.")] = True,
) -> Any:
    """Get a multi-region execution: overall outcome and, optionally, each region's result."""
    executions = api(ExecutionGroupsApi)
    group = executions.v1_execution_groups_group_id_get(group_id=group_id)
    if not include_regional_results:
        return group
    return {"execution_group": group, "regional_results": executions.v1_execution_groups_group_id_regional_results_get(group_id=group_id)}
