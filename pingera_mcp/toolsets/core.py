"""Always-enabled tools: connection check and reference documentation."""

from __future__ import annotations

from typing import Any, Literal

from pingera.api import OrganizationsApi

from .. import reference
from ..api import api
from ..registry import tool


@tool("core", title="Check Pingera connection")
def check_connection() -> Any:
    """Verify that the Pingera API is reachable with the current credentials.

    Returns the organizations the credentials belong to. Use it first when other tools fail with
    authentication errors.
    """
    return {"connected": True, "organizations": api(OrganizationsApi).v1_organizations_get()}


@tool("core", title="Get Pingera reference")
def get_reference(topic: Literal["check_types", "alerts"]) -> Any:
    """Get reference documentation.

    check_types: check types and their `parameters` (regions, multi-region runs, HTTP requests, assertions,
    Playwright scripts and runtime). alerts: alert rule conditions, multi-region modes and channel configuration.
    """
    return reference.TOPICS[topic][1]
