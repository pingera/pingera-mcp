"""
MCP tools for page management.
"""
import json
from typing import Optional

from .base import BaseTools
from ..exceptions import PingeraError


class PagesTools(BaseTools):
    """Tools for managing status pages."""

    async def list_pages(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        status: Optional[str] = None
    ) -> str:
        """
        List monitored pages from Pingera.

        Args:
            page: Page number for pagination
            per_page: Number of items per page (max 100)
            status: Filter by page status

        Returns:
            str: JSON string containing list of pages
        """
        try:
            self.logger.info(f"Listing pages - page: {page}, per_page: {per_page}, status: {status}")

            # Validate parameters
            if per_page is not None and per_page > 100:
                per_page = 100

            pages_response = self.client.get_pages(
                page=page,
                per_page=per_page,
                status=status
            )

            # COMPREHENSIVE LOGGING of SDK response
            self.logger.info(f"=== SDK RESPONSE ANALYSIS ===")
            self.logger.info(f"Response type: {type(pages_response)}")
            self.logger.info(f"Response is list: {isinstance(pages_response, list)}")

            if hasattr(pages_response, '__dict__'):
                self.logger.info(f"Response __dict__: {pages_response.__dict__}")

            if hasattr(pages_response, 'attribute_map'):
                self.logger.info(f"Response attribute_map: {pages_response.attribute_map}")

            all_attrs = [attr for attr in dir(pages_response) if not attr.startswith('_')]
            self.logger.info(f"Response public attributes: {all_attrs}")

            # Handle SDK response format - the SDK returns pages directly as a list
            if isinstance(pages_response, list):
                # SDK returns pages as direct list
                self.logger.info(f"Processing {len(pages_response)} pages from direct list")
                pages_list = []
                for i, page in enumerate(pages_response):
                    self.logger.info(f"--- PROCESSING PAGE {i+1} ---")
                    self.logger.info(f"Page type: {type(page)}")
                    if hasattr(page, '__dict__'):
                        self.logger.info(f"Page __dict__: {page.__dict__}")

                    converted_page = self._convert_sdk_object_to_dict(page)
                    pages_list.append(converted_page)
                    self.logger.info(f"Converted page keys: {list(converted_page.keys())}")

            else:
                # Try different response structures
                self.logger.info("Response is not a direct list, trying nested structures...")

                if hasattr(pages_response, 'pages') and pages_response.pages:
                    self.logger.info(f"Found pages in response.pages: {len(pages_response.pages)}")
                    pages_list = [self._convert_sdk_object_to_dict(page) for page in pages_response.pages]
                elif hasattr(pages_response, 'data') and pages_response.data:
                    self.logger.info(f"Found pages in response.data: {len(pages_response.data)}")
                    pages_list = [self._convert_sdk_object_to_dict(page) for page in pages_response.data]
                else:
                    self.logger.error("Could not find pages in any expected location!")
                    self.logger.error(f"Available attributes: {[attr for attr in dir(pages_response) if not attr.startswith('_')]}")
                    pages_list = []

            # Since pagination is not supported, return all results
            total = len(pages_list)
            current_page = 1
            items_per_page = total

            data = {
                "pages": pages_list,
                "total": total,
                "page": current_page,
                "per_page": items_per_page
            }

            return self._success_response(data)

        except PingeraError as e:
            self.logger.error(f"Error listing pages: {e}")
            return self._error_response(str(e), {"pages": [], "total": 0})

    async def get_page_details(self, page_id: int) -> str:
        """
        Get detailed information about a specific page.

        Args:
            page_id: ID of the page to retrieve

        Returns:
            str: JSON string containing page details
        """
        try:
            self.logger.info(f"Getting page details for ID: {page_id}")
            page = self.client.get_page(page_id)

            # Handle SDK response format
            page_data = self._convert_sdk_object_to_dict(page)

            return self._success_response(page_data)

        except PingeraError as e:
            self.logger.error(f"Error getting page details for {page_id}: {e}")
            return self._error_response(str(e), None)

    async def create_page(
        self,
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
            str: JSON string containing the created page details
        """
        try:
            # 1. Collect all arguments into a dictionary
            page_data = {
                "name": name,
                "subdomain": subdomain,
                "domain": domain,
                "url": url,
                "language": language,
                "headline": headline,
                "page_description": page_description,
                "time_zone": time_zone,
                "country": country,
                "city": city,
                "state": state,
                "viewers_must_be_team_members": viewers_must_be_team_members,
                "hidden_from_search": hidden_from_search,
                "allow_page_subscribers": allow_page_subscribers,
                "allow_incident_subscribers": allow_incident_subscribers,
                "allow_email_subscribers": allow_email_subscribers,
                "allow_sms_subscribers": allow_sms_subscribers,
                "allow_webhook_subscribers": allow_webhook_subscribers,
                "allow_rss_atom_feeds": allow_rss_atom_feeds,
                "support_url": support_url,
            }

            # 2. Filter out optional arguments that were not provided (are None)
            filtered_page_data = {k: v for k, v in page_data.items() if v is not None}

            self.logger.info(f"Creating status page: {filtered_page_data.get('name', 'Unnamed')}")

            # 3. Use the clean dictionary with your SDK
            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesApi
                from pingera.models import Page
                pages_api = StatusPagesApi(api_client)

                page_model = Page(**filtered_page_data)
                response = pages_api.v1_pages_post(page=page_model)

                page_data_result = self._convert_sdk_object_to_dict(response)
                return self._success_response(page_data_result)

        except Exception as e:
            self.logger.error(f"Error creating page: {e}")
            return self._error_response(str(e))

    async def update_page(
        self,
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
        Update an existing status page (full update).

        Args:
            page_id: ID of the page to update
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
            str: JSON string containing the updated page details
        """
        try:
            # 1. Collect all arguments into a dictionary
            page_data = {
                "name": name,
                "subdomain": subdomain,
                "domain": domain,
                "url": url,
                "language": language,
                "headline": headline,
                "page_description": page_description,
                "time_zone": time_zone,
                "country": country,
                "city": city,
                "state": state,
                "viewers_must_be_team_members": viewers_must_be_team_members,
                "hidden_from_search": hidden_from_search,
                "allow_page_subscribers": allow_page_subscribers,
                "allow_incident_subscribers": allow_incident_subscribers,
                "allow_email_subscribers": allow_email_subscribers,
                "allow_sms_subscribers": allow_sms_subscribers,
                "allow_webhook_subscribers": allow_webhook_subscribers,
                "allow_rss_atom_feeds": allow_rss_atom_feeds,
                "support_url": support_url,
            }

            # 2. Filter out optional arguments that were not provided (are None)
            filtered_page_data = {k: v for k, v in page_data.items() if v is not None}

            if not filtered_page_data:
                return self._error_response("No update data provided. Please specify at least one field to update.")

            self.logger.info(f"Updating page {page_id} with data: {filtered_page_data}")

            # 3. Use the clean dictionary with your SDK
            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesApi
                from pingera.models import Page
                pages_api = StatusPagesApi(api_client)

                page_id_int = int(page_id)
                page_model = Page(**filtered_page_data)
                response = pages_api.v1_pages_page_id_put(page_id=page_id_int, page=page_model)

                page_data_result = self._convert_sdk_object_to_dict(response)
                return self._success_response(page_data_result)

        except ValueError:
            self.logger.error(f"Invalid page ID: {page_id}")
            return self._error_response(f"Invalid page ID: {page_id}")
        except Exception as e:
            self.logger.error(f"Error updating page {page_id}: {e}")
            return self._error_response(str(e))

    async def patch_page(
        self,
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
        Partially update an existing status page.

        Args:
            page_id: ID of the page to update
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
            str: JSON string containing the updated page details
        """
        try:
            # 1. Collect all arguments into a dictionary
            patch_data = {
                "name": name,
                "subdomain": subdomain,
                "domain": domain,
                "url": url,
                "language": language,
                "headline": headline,
                "page_description": page_description,
                "time_zone": time_zone,
                "country": country,
                "city": city,
                "state": state,
                "viewers_must_be_team_members": viewers_must_be_team_members,
                "hidden_from_search": hidden_from_search,
                "allow_page_subscribers": allow_page_subscribers,
                "allow_incident_subscribers": allow_incident_subscribers,
                "allow_email_subscribers": allow_email_subscribers,
                "allow_sms_subscribers": allow_sms_subscribers,
                "allow_webhook_subscribers": allow_webhook_subscribers,
                "allow_rss_atom_feeds": allow_rss_atom_feeds,
                "support_url": support_url,
            }

            # 2. Filter out optional arguments that were not provided (are None)
            filtered_patch_data = {k: v for k, v in patch_data.items() if v is not None}

            if not filtered_patch_data:
                return self._error_response("No update data provided. Please specify at least one field to update.")

            self.logger.info(f"Patching page {page_id} with data: {filtered_patch_data}")

            # 3. Use the clean dictionary with your SDK
            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesApi
                from pingera.models import Page1
                pages_api = StatusPagesApi(api_client)

                page_id_int = int(page_id)
                patch_model = Page1(**filtered_patch_data)
                response = pages_api.v1_pages_page_id_patch(page_id=page_id_int, page1=patch_model)

                page_data_result = self._convert_sdk_object_to_dict(response)
                return self._success_response(page_data_result)

        except ValueError:
            self.logger.error(f"Invalid page ID: {page_id}")
            return self._error_response(f"Invalid page ID: {page_id}")
        except Exception as e:
            self.logger.error(f"Error patching page {page_id}: {e}")
            return self._error_response(str(e))

    async def delete_page(self, page_id: str) -> str:
        """
        Permanently delete a status page and all associated data.
        This action cannot be undone.

        Args:
            page_id: ID of the page to delete

        Returns:
            str: JSON string confirming deletion
        """
        try:
            self.logger.info(f"Deleting page: {page_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesApi
                pages_api = StatusPagesApi(api_client)

                page_id_int = int(page_id)
                pages_api.v1_pages_page_id_delete(page_id=page_id_int)

                return self._success_response({
                    "deleted": True,
                    "page_id": page_id,
                    "message": f"Page {page_id} deleted successfully"
                })

        except ValueError:
            self.logger.error(f"Invalid page ID: {page_id}")
            return self._error_response(f"Invalid page ID: {page_id}", None)
        except PingeraError as e:
            self.logger.error(f"Error deleting page {page_id}: {e}")
            return self._error_response(str(e), None)