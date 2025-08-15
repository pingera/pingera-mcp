
"""
MCP tools for alert management.
"""
import json
from typing import Optional, List
from datetime import datetime

from .base import BaseTools
from ..exceptions import PingeraError


class AlertsTools(BaseTools):
    """Tools for managing alerts and notifications."""

    async def list_alerts(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        status: Optional[str] = None
    ) -> str:
        """
        List alerts.

        Args:
            page: Page number for pagination
            page_size: Number of items per page
            status: Filter by alert status (e.g., 'active', 'inactive')

        Returns:
            JSON string containing alerts data
        """
        try:
            self.logger.info(f"Listing alerts (page={page}, page_size={page_size}, status={status})")

            with self.client._get_api_client() as api_client:
                from pingera.api import AlertsApi
                alerts_api = AlertsApi(api_client)

                # Only pass non-None parameters
                kwargs = {}
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size
                if status is not None:
                    kwargs['status'] = status

                response = alerts_api.v1_alerts_get(**kwargs)

                alerts_data = self._format_alerts_response(response)
                return self._success_response(alerts_data)

        except Exception as e:
            self.logger.error(f"Error listing alerts: {e}")
            return self._error_response(str(e))

    async def get_alert_details(self, alert_id: str) -> str:
        """
        Get detailed information about a specific alert.

        Args:
            alert_id: ID of the alert to retrieve

        Returns:
            JSON string containing alert details
        """
        try:
            self.logger.info(f"Getting alert details for ID: {alert_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import AlertsApi
                alerts_api = AlertsApi(api_client)

                response = alerts_api.v1_alerts_alert_id_get(alert_id=alert_id)

                alert_data = self._format_alert_response(response)
                return self._success_response(alert_data)

        except Exception as e:
            self.logger.error(f"Error getting alert details for {alert_id}: {e}")
            return self._error_response(str(e))

    async def create_alert(self, alert_data: dict) -> str:
        """
        Create a new alert.

        Args:
            alert_data: Dictionary containing alert configuration

        Returns:
            JSON string containing created alert data
        """
        try:
            self.logger.info(f"Creating new alert: {alert_data.get('name', 'Unnamed')}")

            with self.client._get_api_client() as api_client:
                from pingera.api import AlertsApi
                alerts_api = AlertsApi(api_client)

                response = alerts_api.v1_alerts_post(alert_data)

                created_alert = self._format_alert_response(response)
                return self._success_response(created_alert)

        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            return self._error_response(str(e))

    async def update_alert(self, alert_id: str, alert_data: dict) -> str:
        """
        Update an existing alert.

        Args:
            alert_id: ID of the alert to update
            alert_data: Dictionary containing updated alert configuration

        Returns:
            JSON string containing updated alert data
        """
        try:
            self.logger.info(f"Updating alert {alert_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import AlertsApi
                alerts_api = AlertsApi(api_client)

                response = alerts_api.v1_alerts_alert_id_put(
                    alert_id=alert_id,
                    alert_data=alert_data
                )

                updated_alert = self._format_alert_response(response)
                return self._success_response(updated_alert)

        except Exception as e:
            self.logger.error(f"Error updating alert {alert_id}: {e}")
            return self._error_response(str(e))

    async def delete_alert(self, alert_id: str) -> str:
        """
        Delete an alert.

        Args:
            alert_id: ID of the alert to delete

        Returns:
            JSON string confirming deletion
        """
        try:
            self.logger.info(f"Deleting alert {alert_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import AlertsApi
                alerts_api = AlertsApi(api_client)

                alerts_api.v1_alerts_alert_id_delete(alert_id=alert_id)

                return self._success_response({
                    "message": f"Alert {alert_id} deleted successfully",
                    "alert_id": alert_id
                })

        except Exception as e:
            self.logger.error(f"Error deleting alert {alert_id}: {e}")
            return self._error_response(str(e))

    async def get_alert_statistics(self) -> str:
        """
        Get alert statistics.

        Returns:
            JSON string containing alert statistics
        """
        try:
            self.logger.info("Getting alert statistics")

            with self.client._get_api_client() as api_client:
                from pingera.api import AlertsApi
                alerts_api = AlertsApi(api_client)

                response = alerts_api.v1_alerts_stats_get()

                stats_data = self._format_stats_response(response)
                return self._success_response(stats_data)

        except Exception as e:
            self.logger.error(f"Error getting alert statistics: {e}")
            return self._error_response(str(e))

    async def list_alert_channels(self) -> str:
        """
        Get alert channels.

        Returns:
            JSON string containing alert channels
        """
        try:
            self.logger.info("Listing alert channels")

            with self.client._get_api_client() as api_client:
                from pingera.api import AlertsApi
                alerts_api = AlertsApi(api_client)

                response = alerts_api.v1_alert_channels_get()

                channels_data = self._format_channels_response(response)
                return self._success_response(channels_data)

        except Exception as e:
            self.logger.error(f"Error listing alert channels: {e}")
            return self._error_response(str(e))

    async def list_alert_rules(self) -> str:
        """
        Get alert rules.

        Returns:
            JSON string containing alert rules
        """
        try:
            self.logger.info("Listing alert rules")

            with self.client._get_api_client() as api_client:
                from pingera.api import AlertsApi
                alerts_api = AlertsApi(api_client)

                response = alerts_api.v1_alert_rules_get()

                rules_data = self._format_rules_response(response)
                return self._success_response(rules_data)

        except Exception as e:
            self.logger.error(f"Error listing alert rules: {e}")
            return self._error_response(str(e))

    def _format_alerts_response(self, response) -> dict:
        """Format alerts list response."""
        if hasattr(response, '__dict__'):
            # Handle the actual API response structure with pagination and alerts
            alerts_data = getattr(response, 'alerts', [])
            pagination = getattr(response, 'pagination', {})
            
            # Convert model objects to dictionaries for JSON serialization
            if isinstance(alerts_data, list):
                formatted_alerts = []
                for item in alerts_data:
                    if hasattr(item, '__dict__'):
                        # Convert datetime objects to strings for JSON serialization
                        alert_dict = {}
                        for key, value in item.__dict__.items():
                            if hasattr(value, 'isoformat'):  # datetime object
                                alert_dict[key] = value.isoformat()
                            else:
                                alert_dict[key] = value
                        formatted_alerts.append(alert_dict)
                    else:
                        formatted_alerts.append(item)
            else:
                formatted_alerts = alerts_data

            # Extract pagination info
            total = pagination.get('total_items', 0) if isinstance(pagination, dict) else 0
            page = pagination.get('page', 1) if isinstance(pagination, dict) else 1
            page_size = pagination.get('page_size', 20) if isinstance(pagination, dict) else 20

            return {
                "alerts": formatted_alerts,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        return {"alerts": [], "total": 0}

    def _format_alert_response(self, response) -> dict:
        """Format single alert response."""
        if hasattr(response, '__dict__'):
            # Convert datetime objects to strings for JSON serialization
            alert_dict = {}
            for key, value in response.__dict__.items():
                if hasattr(value, 'isoformat'):  # datetime object
                    alert_dict[key] = value.isoformat()
                else:
                    alert_dict[key] = value
            return alert_dict
        return response

    def _format_stats_response(self, response) -> dict:
        """Format alert statistics response."""
        if hasattr(response, '__dict__'):
            return response.__dict__
        return response

    def _format_channels_response(self, response) -> dict:
        """Format alert channels response."""
        if hasattr(response, '__dict__'):
            # Convert model objects to dictionaries for JSON serialization
            channels_data = getattr(response, 'channels', [])
            if isinstance(channels_data, list):
                formatted_channels = []
                for item in channels_data:
                    if hasattr(item, '__dict__'):
                        formatted_channels.append(item.__dict__)
                    else:
                        formatted_channels.append(item)
            else:
                formatted_channels = channels_data

            return {
                "channels": formatted_channels,
                "total": len(formatted_channels) if isinstance(formatted_channels, list) else 0
            }
        return {"channels": [], "total": 0}

    def _format_rules_response(self, response) -> dict:
        """Format alert rules response."""
        if hasattr(response, '__dict__'):
            # Convert model objects to dictionaries for JSON serialization
            rules_data = getattr(response, 'rules', [])
            if isinstance(rules_data, list):
                formatted_rules = []
                for item in rules_data:
                    if hasattr(item, '__dict__'):
                        formatted_rules.append(item.__dict__)
                    else:
                        formatted_rules.append(item)
            else:
                formatted_rules = rules_data

            return {
                "rules": formatted_rules,
                "total": len(formatted_rules) if isinstance(formatted_rules, list) else 0
            }
        return {"rules": [], "total": 0}
