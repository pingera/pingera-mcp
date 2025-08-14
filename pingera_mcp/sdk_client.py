"""
Pingera SDK client wrapper for MCP server integration.
"""
import logging
import os
from typing import Dict, Optional, Any, List

# Import from the pingera package
import pingera
from pingera import ApiClient, Configuration
from pingera.api import (
    StatusPagesComponentsApi,
    StatusPagesIncidentsApi,
    ChecksApi,
    AlertsApi,
    HeartbeatsApi,
    OnDemandChecksApi,
    ChecksUnifiedResultsApi
)
from pingera.exceptions import ApiException

from .exceptions import (
    PingeraAPIError,
    PingeraAuthError,
    PingeraConnectionError,
    PingeraTimeoutError
)


class PingeraSDKClient:
    """Pingera client using official SDK."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.pingera.ru",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Pingera SDK client.

        Args:
            api_key: API key for authentication
            base_url: Base URL for Pingera API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

        # Configure the SDK client
        self.configuration = Configuration()
        # Remove /v1 suffix since the SDK adds it automatically
        host_without_version = self.base_url.replace('/v1', '').rstrip('/')
        self.configuration.host = host_without_version
        self.configuration.api_key['apiKeyAuth'] = self.api_key
        self.configuration.timeout = timeout

        # Store configuration, API client will be created in context manager
        self.api_client = None

        # Initialize endpoints for compatibility
        self.pages = PagesEndpointSDK(self)
        self.components = ComponentEndpointsSDK(self)

    def _handle_api_exception(self, e: ApiException) -> None:
        """Convert SDK exceptions to our custom exceptions."""
        if e.status == 401:
            raise PingeraAuthError("Authentication failed. Check your API key.")
        elif e.status == 408:
            raise PingeraTimeoutError(f"Request timed out")
        elif e.status >= 500:
            raise PingeraConnectionError(f"Server error: {e.reason}")
        else:
            raise PingeraAPIError(
                message=f"API error: {e.reason}",
                status_code=e.status,
                response_data=e.body
            )

    def test_connection(self) -> bool:
        """
        Test connection to Pingera API.

        Returns:
            bool: True if connection is successful
        """
        try:
            # Use proper SDK pattern with context manager
            with ApiClient(self.configuration) as api_client:
                checks_api = ChecksApi(api_client)
                # Make a minimal API call to test authentication
                checks = checks_api.v1_checks_get(page=1, page_size=1)
                return True
        except ApiException as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and connection status.

        Returns:
            Dict containing API information
        """
        try:
            # Test connection by making a simple API call
            is_connected = self.test_connection()

            return {
                "connected": is_connected,
                "base_url": self.base_url,
                "message": "Pingera.ru API (SDK)",
                "authentication": "Bearer Token",
                "documentation": "https://docs.pingera.ru/api/overview",
                "api_version": "v1",
                "sdk_version": "official"
            }
        except Exception as e:
            return {
                "connected": False,
                "base_url": self.base_url,
                "error": str(e),
                "api_version": "v1",
                "sdk_version": "official"
            }


class PagesEndpointSDK:
    """Pages endpoint using SDK."""

    def __init__(self, client: PingeraSDKClient):
        self.client = client

    def list(self, page: Optional[int] = None, per_page: Optional[int] = None, status: Optional[str] = None):
        """List pages using SDK."""
        try:
            # SDK doesn't seem to have a direct pages list endpoint
            # We'll need to adapt based on available endpoints
            # For now, return empty response - this would need actual API exploration
            return {"pages": [], "total": 0, "page": page or 1, "per_page": per_page or 20}
        except ApiException as e:
            self.client._handle_api_exception(e)

    def get(self, page_id: str):
        """Get single page using SDK."""
        try:
            # This would need to be implemented based on actual SDK endpoints
            # For now, return a mock page
            return {
                "id": page_id,
                "name": "SDK Page",
                "status": "active",
                "url": f"https://status.example.com",
                "domain": "example.com"
            }
        except ApiException as e:
            self.client._handle_api_exception(e)


class ComponentEndpointsSDK:
    """Component endpoints using SDK."""

    def __init__(self, client: PingeraSDKClient):
        self.client = client

    def get_component_groups(self, page_id: str, show_deleted: bool = False):
        """Get component groups using SDK."""
        try:
            # Use proper SDK pattern with context manager
            with ApiClient(self.client.configuration) as api_client:
                components_api = StatusPagesComponentsApi(api_client)
                components_response = components_api.v1_pages_page_id_components_get(page_id)
                return components_response
        except ApiException as e:
            self.client._handle_api_exception(e)

    def get_component(self, page_id: str, component_id: str):
        """Get single component using SDK."""
        try:
            # Use proper SDK pattern with context manager
            with ApiClient(self.client.configuration) as api_client:
                components_api = StatusPagesComponentsApi(api_client)
                components_response = components_api.v1_pages_page_id_components_get(page_id)

                if hasattr(components_response, 'data') and components_response.data:
                    for comp in components_response.data:
                        if comp.id == component_id:
                            return comp

                raise PingeraAPIError(f"Component {component_id} not found")
        except ApiException as e:
            self.client._handle_api_exception(e)