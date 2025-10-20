
"""
Page management tool decorators.
"""
from typing import Optional


def register_pages_tools(mcp, config, pages_tools, update_tools_client_func):
    """Register all page-related MCP tools."""
    
    @mcp.tool()
    async def list_pages(
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

        Returns:
            JSON with list of status pages including their names, IDs, domains, and configuration details.
        """
        update_tools_client_func()
        return await pages_tools.list_pages(page, per_page, status)

    @mcp.tool()
    async def get_page_details(page_id: int) -> str:
        """
        Get detailed information about a specific status page.

        Args:
            page_id: The unique identifier of the status page

        Returns:
            JSON with complete page details including settings, components, branding, and configuration.
        """
        update_tools_client_func()
        return await pages_tools.get_page_details(page_id)

    if config.is_read_write():
        @mcp.tool()
        async def create_page(
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
            """Create a new status page."""
            update_tools_client_func()
            return await pages_tools.create_page(
                name=name, subdomain=subdomain, domain=domain, url=url,
                language=language, headline=headline, page_description=page_description,
                time_zone=time_zone, country=country, city=city, state=state,
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

        @mcp.tool()
        async def update_page(
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
            """FULL UPDATE: Replace all page configuration (PUT method)."""
            update_tools_client_func()
            return await pages_tools.update_page(
                page_id=page_id, name=name, subdomain=subdomain, domain=domain,
                url=url, language=language, headline=headline,
                page_description=page_description, time_zone=time_zone,
                country=country, city=city, state=state,
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

        @mcp.tool()
        async def patch_page(
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
            """RECOMMENDED: Partially update specific fields of a status page (PATCH method)."""
            update_tools_client_func()
            return await pages_tools.patch_page(
                page_id=page_id, name=name, subdomain=subdomain, domain=domain,
                url=url, language=language, headline=headline,
                page_description=page_description, time_zone=time_zone,
                country=country, city=city, state=state,
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

        @mcp.tool()
        async def delete_page(page_id: str) -> str:
            """Permanently delete a status page and all its associated data."""
            update_tools_client_func()
            return await pages_tools.delete_page(page_id)
