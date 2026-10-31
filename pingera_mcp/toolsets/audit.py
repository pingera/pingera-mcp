"""Organization audit log."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import AuditApi
from pydantic import Field

from ..api import api, parse_time
from ..registry import tool
from ._types import PageNumber, PageSize, Time


@tool("audit")
def list_audit_events(
    action: Annotated[str | None, Field(description="Only this action, e.g. create, update, delete, login.")] = None,
    entity_type: Annotated[str | None, Field(description="Only changes to this kind of object, e.g. check, page, alert_rule.")] = None,
    user_id: Annotated[str | None, Field(description="Only actions by this user.")] = None,
    start: Time = None,
    end: Time = None,
    page: PageNumber = None,
    per_page: PageSize = None,
) -> Any:
    """List the organization's audit log: who changed what and when."""
    return api(AuditApi).v1_audit_get(
        action=action,
        entity_type=entity_type,
        user_id=user_id,
        start_date=parse_time(start),
        end_date=parse_time(end),
        page=page,
        per_page=per_page,
    )
