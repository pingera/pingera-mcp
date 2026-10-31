"""Status pages."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import StatusPagesApi
from pingera.models import Page, Page1
from pydantic import Field

from ..api import api
from ..registry import model_tool, tool
from ._types import PageId, PageNumber, PageSize

# Branding, analytics and email settings: available through the `advanced` argument.
_ADVANCED = {
    name
    for name in Page.model_fields
    if name.startswith("css_")
    or name.endswith("_logo")
    or name in {"hero_cover", "yandex_metrica_id", "google_analytics_id", "notifications_email_footer", "ip_restrictions", "city", "state", "country"}
} | {"notifications_from_email", "notifications_from_name"}
_EXCLUDE = {"activity_score", "template"}


@tool("pages")
def list_status_pages(page: PageNumber = None, page_size: PageSize = None) -> Any:
    """List the organization's status pages with their IDs, names, subdomains and custom domains."""
    return api(StatusPagesApi).v1_pages_get(page=page, page_size=page_size)


@tool("pages")
def get_status_page(page_id: PageId) -> Any:
    """Get a status page's full configuration: branding, domains, subscriptions, privacy and language."""
    return api(StatusPagesApi).v1_pages_page_id_get(page_id=page_id)


@tool("pages")
def find_status_page_by_domain(
    domain: Annotated[str, Field(description="Custom domain or Pingera subdomain, e.g. 'status.example.com' or 'acme'.")],
) -> Any:
    """Find a status page by its domain and get its public state: overall status, components and active incidents."""
    return api(StatusPagesApi).v1_pages_by_domain_domain_get(domain=domain)


@tool("pages")
def list_page_templates() -> Any:
    """List the visual templates a status page can use (the `template` field of create/update_status_page)."""
    return api(StatusPagesApi).v1_pages_get_templates_get()


model_tool(
    "pages",
    "create_status_page",
    model=Page,
    exclude=_EXCLUDE,
    advanced=_ADVANCED,
    call=lambda body: api(StatusPagesApi).v1_pages_post(page=body),
    description=(
        "Create a status page. Only `name` is required; set `subdomain` for <subdomain>.pingera.ru or `domain` "
        "for a custom domain."
    ),
)

model_tool(
    "pages",
    "update_status_page",
    model=Page1,
    partial=True,
    exclude=_EXCLUDE,
    advanced=_ADVANCED,
    path=[("page_id", "ID of the status page to update.")],
    call=lambda body, page_id: api(StatusPagesApi).v1_pages_page_id_patch(page_id=page_id, page1=body),
    idempotent=True,
    description="Change a status page's settings. Only the fields you pass are changed.",
)


@tool("pages", access="write", destructive=True, idempotent=True)
def delete_status_page(page_id: PageId) -> Any:
    """Delete a status page with its components, incidents and subscribers. This cannot be undone."""
    return api(StatusPagesApi).v1_pages_page_id_delete(page_id=page_id)
