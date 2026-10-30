"""PDF uptime reports."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import ReportsApi
from pingera.models import ReportRequest
from pydantic import Field

from ..api import PingeraToolError, api, parse_time
from ..registry import tool
from ._types import PageNumber, PageSize


@tool("reports")
def list_reports(page: PageNumber = None, page_size: PageSize = None) -> Any:
    """List requested PDF reports with their period, status and download link."""
    return api(ReportsApi).v1_reports_get(page=page, page_size=page_size)


@tool("reports")
def get_report(report_id: Annotated[str, Field(description="Report ID (see list_reports).")]) -> Any:
    """Get a report's status and, when ready, its download link."""
    return api(ReportsApi).v1_reports_report_id_get(report_id=report_id)


@tool("reports", access="run")
def request_report(
    start: Annotated[str, Field(description="Report period start: ISO 8601 or relative like '30d'.")],
    end: Annotated[str, Field(description="Report period end: ISO 8601, 'now' or relative.")] = "now",
    check_ids: Annotated[list[str] | None, Field(description="Checks to include; all active checks when omitted.")] = None,
) -> Any:
    """Request a PDF uptime report for a period. It is generated in the background; poll get_report."""
    start_date, end_date = parse_time(start), parse_time(end)
    if start_date is None or end_date is None:
        raise PingeraToolError("Both start and end are required.")
    return api(ReportsApi).v1_reports_post(
        report_request=ReportRequest(start_date=start_date, end_date=end_date, check_ids=check_ids)
    )
