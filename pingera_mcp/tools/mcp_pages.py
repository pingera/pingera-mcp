
"""
MCP tool logic for page management.
"""
from typing import Optional
from pingera_mcp import PingeraClient
from pingera_mcp.tools import PagesTools

async def _list_pages_logic(
    client: PingeraClient,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """
    List all status pages in your Pingera account.

    This is typically the first tool you should use to discover available pages and their IDs.
    Each page has a unique ID that you'll need for other operations like listing incidents or components.

    Args:
        page: Page number for pagination (default: 1)
        per_page: Number of items per page (default: 20, max: 100)
        status: Filter pages by status ('active', 'inactive').

    Returns:
        JSON with list of status pages including their names, IDs, domains, and configuration details.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    pages_tools = PagesTools(client)
    return await pages_tools.list_pages(page, per_page, status)

async def _get_page_details_logic(client: PingeraClient, page_id: int) -> str:
    """
    Get detailed information about a specific status page.

    Args:
        page_id: The unique identifier of the status page

    Returns:
        JSON with complete page details including settings, components, branding, and configuration.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    pages_tools = PagesTools(client)
    return await pages_tools.get_page_details(page_id)

async def _create_page_logic(
    client: PingeraClient,
    name: str,
    subdomain: Optional[str] = None,
    domain: Optional[str] = None,
    url: Optional[str] = None,
    language: Optional[str] = None,
    headline: Optional[str] = None,
    page_description: Optional[str] = None,
    time_zone: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    viewers_must_be_team_members: Optional[bool] = None,
    hidden_from_search: Optional[bool] = None,
    allow_page_subscribers: Optional[bool] = None,
    allow_incident_subscribers: Optional[bool] = None,
    allow_email_subscribers: Optional[bool] = None,
    allow_sms_subscribers: Optional[bool] = None,
    allow_webhook_subscribers: Optional[bool] = None,
    allow_rss_atom_feeds: Optional[bool] = None,
    support_url: Optional[str] = None,
) -> str:
    """
    Create a new status page.

    Args:
        name: Display name of the status page (required)
        subdomain: Subdomain for accessing the status page (e.g., 'mycompany' for mycompany.pingera.ru)
        domain: Custom domain for the status page
        url: Company URL - users will be redirected there when clicking on the logo
        language: Language for the status page interface ("ru" or "en")
        headline: Headline text displayed on the status page
        page_description: Brief description of what this status page monitors
        time_zone: Timezone for displaying dates and times on the status page
        country: Country where your organization is located
        city: City where your organization is located
        state: State/region where your organization is located
        viewers_must_be_team_members: Whether only team members can view this page (True = private, False = public)
        hidden_from_search: Whether to hide this page from search engines
        allow_page_subscribers: Whether to allow users to subscribe to page updates
        allow_incident_subscribers: Whether to allow users to subscribe to incident updates
        allow_email_subscribers: Whether to allow email subscriptions
        allow_sms_subscribers: Whether to allow SMS subscriptions
        allow_webhook_subscribers: Whether to allow webhook subscriptions
        allow_rss_atom_feeds: Whether to provide RSS/Atom feeds
        support_url: URL to your support or contact page

    Returns:
        JSON string containing the created page details
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    pages_tools = PagesTools(client)
    return await pages_tools.create_page(
        name=name,
        subdomain=subdomain,
        domain=domain,
        url=url,
        language=language,
        headline=headline,
        page_description=page_description,
        time_zone=time_zone,
        country=country,
        city=city,
        state=state,
        viewers_must_be_team_members=viewers_must_be_team_members,
        hidden_from_search=hidden_from_search,
        allow_page_subscribers=allow_page_subscribers,
        allow_incident_subscribers=allow_incident_subscribers,
        allow_email_subscribers=allow_email_subscribers,
        allow_sms_subscribers=allow_sms_subscribers,
        allow_webhook_subscribers=allow_webhook_subscribers,
        allow_rss_atom_feeds=allow_rss_atom_feeds,
        support_url=support_url,
    )

async def _patch_page_logic(
    client: PingeraClient,
    page_id: str,
    name: Optional[str] = None,
    subdomain: Optional[str] = None,
    domain: Optional[str] = None,
    url: Optional[str] = None,
    language: Optional[str] = None,
    headline: Optional[str] = None,
    page_description: Optional[str] = None,
    time_zone: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    viewers_must_be_team_members: Optional[bool] = None,
    hidden_from_search: Optional[bool] = None,
    allow_page_subscribers: Optional[bool] = None,
    allow_incident_subscribers: Optional[bool] = None,
    allow_email_subscribers: Optional[bool] = None,
    allow_sms_subscribers: Optional[bool] = None,
    allow_webhook_subscribers: Optional[bool] = None,
    allow_rss_atom_feeds: Optional[bool] = None,
    support_url: Optional[str] = None,
) -> str:
    """
    RECOMMENDED: Partially update specific fields of a status page (PATCH method).

    Use this for simple updates like changing the name, description, or other individual fields.
    Only the fields you specify will be updated, leaving other settings unchanged.
    This is the preferred method for most page updates.

    Args:
        page_id: The unique identifier of the page to patch
        name: Display name of the status page
        subdomain: Subdomain for accessing the status page
        domain: Custom domain for the status page
        url: Company URL for logo redirect
        language: Language for the status page interface ("ru" or "en")
        headline: Headline text displayed on the status page
        page_description: Brief description of what this status page monitors
        time_zone: Timezone for displaying dates and times on the status page
        country: Country where your organization is located
        city: City where your organization is located
        state: State/region where your organization is located
        viewers_must_be_team_members: Whether only team members can view this page
        hidden_from_search: Whether to hide this page from search engines
        allow_page_subscribers: Whether to allow users to subscribe to page updates
        allow_incident_subscribers: Whether to allow users to subscribe to incident updates
        allow_email_subscribers: Whether to allow email subscriptions
        allow_sms_subscribers: Whether to allow SMS subscriptions
        allow_webhook_subscribers: Whether to allow webhook subscriptions
        allow_rss_atom_feeds: Whether to provide RSS/Atom feeds
        support_url: URL to your support or contact page

    Returns:
        JSON with updated page configuration.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    pages_tools = PagesTools(client)
    return await pages_tools.patch_page(
        page_id=page_id,
        name=name,
        subdomain=subdomain,
        domain=domain,
        url=url,
        language=language,
        headline=headline,
        page_description=page_description,
        time_zone=time_zone,
        country=country,
        city=city,
        state=state,
        viewers_must_be_team_members=viewers_must_be_team_members,
        hidden_from_search=hidden_from_search,
        allow_page_subscribers=allow_page_subscribers,
        allow_incident_subscribers=allow_incident_subscribers,
        allow_email_subscribers=allow_email_subscribers,
        allow_sms_subscribers=allow_sms_subscribers,
        allow_webhook_subscribers=allow_webhook_subscribers,
        allow_rss_atom_feeds=allow_rss_atom_feeds,
        support_url=support_url,
    )

async def _delete_page_logic(client: PingeraClient, page_id: str) -> str:
    """
    Permanently delete a status page and all its associated data.

    WARNING: This action cannot be undone. All components, incidents,
    and historical data associated with this page will be deleted.

    Args:
        page_id: The unique identifier of the page to delete

    Returns:
        JSON confirming successful deletion.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    pages_tools = PagesTools(client)
    return await pages_tools.delete_page(page_id)
