"""Argument types shared by the toolsets."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

PageNumber = Annotated[int | None, Field(ge=1, description="Page number, starting at 1.")]
PageSize = Annotated[int | None, Field(ge=1, le=100, description="Items per page (max 100).")]
Time = Annotated[
    str | None,
    Field(description="ISO 8601 timestamp (UTC if no offset), 'now', or a relative time such as '30m', '24h', '7d' (that long ago)."),
]

CheckId = Annotated[str, Field(description="Check ID (see list_checks).")]
PageId = Annotated[str, Field(description="Status page ID (see list_status_pages).")]
ComponentId = Annotated[str, Field(description="Component ID (see list_components).")]
IncidentId = Annotated[str, Field(description="Incident ID (see list_incidents).")]
