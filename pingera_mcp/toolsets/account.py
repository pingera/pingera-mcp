"""Organization details and usage."""

from __future__ import annotations

from typing import Any

from pingera.api import OrganizationsApi, UsageApi

from ..api import api
from ..registry import tool


@tool("account")
def get_organization(org_id: str) -> Any:
    """Get an organization's details: name, plan, timezone and settings (org IDs come from check_connection)."""
    return api(OrganizationsApi).v1_organizations_org_id_get(org_id=org_id)


@tool("account")
def get_usage() -> Any:
    """Get the organization's current usage against its plan limits: credits, checks, status pages and more."""
    return api(UsageApi).v1_usage_get()
