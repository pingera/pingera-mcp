"""Status page passwords and custom sender email domains."""

from __future__ import annotations

from typing import Annotated, Any

from pingera.api import PagePasswordsApi, StatusPagesApi
from pingera.models import PagePasswordCreate, PagePasswordUpdate
from pydantic import Field

from ..api import api
from ..registry import model_tool, tool
from ._types import PageId

PasswordId = Annotated[str, Field(description="Password ID (see list_page_passwords).")]


@tool("page_access")
def list_page_passwords(page_id: PageId) -> Any:
    """List the passwords that unlock a private status page (labels, hints, expiry; not the passwords)."""
    return api(PagePasswordsApi).v1_pages_page_id_passwords_get(page_id=page_id)


model_tool(
    "page_access",
    "create_page_password",
    model=PagePasswordCreate,
    path=[("page_id", "Status page ID.")],
    call=lambda body, page_id: api(PagePasswordsApi).v1_pages_page_id_passwords_post(
        page_id=page_id, page_password_create=body
    ),
    description="Add a password that visitors can use to open a private status page.",
)

model_tool(
    "page_access",
    "update_page_password",
    model=PagePasswordUpdate,
    partial=True,
    path=[("page_id", "Status page ID."), ("password_id", "Password ID.")],
    call=lambda body, page_id, password_id: api(PagePasswordsApi).v1_pages_page_id_passwords_password_id_put(
        page_id=page_id, password_id=password_id, page_password_update=body
    ),
    idempotent=True,
    description="Change a status page password, its hint or expiry, or deactivate it with `active`.",
)


@tool("page_access", access="write", destructive=True, idempotent=True)
def delete_page_password(page_id: PageId, password_id: PasswordId) -> Any:
    """Delete a status page password; visitors can no longer use it."""
    return api(PagePasswordsApi).v1_pages_page_id_passwords_password_id_delete(page_id=page_id, password_id=password_id)


@tool("page_access")
def get_page_email_domain(page_id: PageId) -> Any:
    """Get the custom sender email domain of a status page, its verification state and DNS records."""
    return api(StatusPagesApi).v1_pages_page_id_email_domain_get(page_id=page_id)


@tool("page_access", access="write", idempotent=True)
def generate_page_email_domain_records(page_id: PageId) -> Any:
    """Generate the DNS records (verification, DKIM, SPF, DMARC) to add for the page's sender email domain."""
    return api(StatusPagesApi).v1_pages_page_id_email_domain_records_post(page_id=page_id)


@tool("page_access", access="run")
def verify_page_email_domain(page_id: PageId) -> Any:
    """Check the DNS records of the page's sender email domain and verify it."""
    return api(StatusPagesApi).v1_pages_page_id_email_domain_verify_post(page_id=page_id)
