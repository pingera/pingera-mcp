"""
MCP tools for heartbeat monitoring.
"""
import json
from typing import Optional, Dict, Any
from datetime import datetime

from .base import BaseTools
from ..exceptions import PingeraError


class HeartbeatsTools(BaseTools):
    """Tools for managing heartbeat monitoring."""

    async def list_heartbeats(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        status: Optional[str] = None
    ) -> str:
        """
        List all heartbeats with optional filtering.

        Args:
            page: Page number for pagination
            page_size: Number of items per page
            status: Filter by heartbeat status

        Returns:
            JSON string with heartbeats data
        """
        try:
            self.logger.info(f"Listing heartbeats (page={page}, page_size={page_size}, status={status})")

            with self.client._get_api_client() as api_client:
                from pingera.api import HeartbeatsApi
                heartbeats_api = HeartbeatsApi(api_client)

                kwargs = {}
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size
                # Note: HeartbeatsApi.v1_heartbeats_get does not support status filtering
                # Status filtering will be handled client-side if needed

                response = heartbeats_api.v1_heartbeats_get(**kwargs)

                heartbeats_data = self._format_heartbeats_response(response)
                return self._success_response(heartbeats_data)

        except Exception as e:
            self.logger.error(f"Error listing heartbeats: {e}")
            return self._error_response(str(e))

    async def get_heartbeat_details(self, heartbeat_id: str) -> str:
        """
        Get details for a specific heartbeat.

        Args:
            heartbeat_id: ID of the heartbeat to retrieve

        Returns:
            JSON string with heartbeat details
        """
        try:
            self.logger.info(f"Getting heartbeat details for ID: {heartbeat_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import HeartbeatsApi
                heartbeats_api = HeartbeatsApi(api_client)

                response = heartbeats_api.v1_heartbeats_heartbeat_id_get(heartbeat_id=heartbeat_id)

                heartbeat_data = self._format_heartbeat_response(response)
                return self._success_response(heartbeat_data)

        except Exception as e:
            self.logger.error(f"Error getting heartbeat details for {heartbeat_id}: {e}")
            return self._error_response(str(e))

    async def create_heartbeat(self, heartbeat_data: dict) -> str:
        """Create a new heartbeat monitor."""
        try:
            return json.dumps({
                "success": False,
                "error": "Heartbeat creation not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to create heartbeat: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "Failed to create heartbeat monitor"
            }, indent=2)

    async def update_heartbeat(self, heartbeat_id: str, heartbeat_data: dict) -> str:
        """Update an existing heartbeat monitor."""
        try:
            return json.dumps({
                "success": False,
                "error": "Heartbeat update not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to update heartbeat: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to update heartbeat: {heartbeat_id}"
            }, indent=2)

    async def delete_heartbeat(self, heartbeat_id: str) -> str:
        """Delete a heartbeat monitor."""
        try:
            return json.dumps({
                "success": False,
                "error": "Heartbeat deletion not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to delete heartbeat: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to delete heartbeat: {heartbeat_id}"
            }, indent=2)

    async def send_heartbeat_ping(self, heartbeat_id: str) -> str:
        """Send a ping signal to a heartbeat monitor."""
        try:
            return json.dumps({
                "success": False,
                "error": "Heartbeat ping not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to send heartbeat ping: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to ping heartbeat: {heartbeat_id}"
            }, indent=2)

    async def get_heartbeat_logs(
        self,
        heartbeat_id: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """
        Get logs for a heartbeat.

        Args:
            heartbeat_id: ID of the heartbeat
            from_date: Start date for log filtering (ISO 8601 format)
            to_date: End date for log filtering (ISO 8601 format)
            page: Page number for pagination
            page_size: Number of items per page

        Returns:
            JSON string with heartbeat logs
        """
        try:
            self.logger.info(f"Getting logs for heartbeat {heartbeat_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import HeartbeatsApi
                heartbeats_api = HeartbeatsApi(api_client)

                kwargs = {}
                if from_date is not None:
                    kwargs['from_date'] = from_date
                if to_date is not None:
                    kwargs['to_date'] = to_date
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size

                response = heartbeats_api.v1_heartbeats_heartbeat_id_logs_get(
                    heartbeat_id=heartbeat_id,
                    **kwargs
                )

                logs_data = self._format_logs_response(response)
                return self._success_response(logs_data)

        except Exception as e:
            self.logger.error(f"Error getting logs for heartbeat {heartbeat_id}: {e}")
            return self._error_response(str(e))

    def _format_heartbeats_response(self, response) -> Dict[str, Any]:
        """Format heartbeats list response."""
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        elif hasattr(response, '__dict__'):
            return response.__dict__
        else:
            return {"heartbeats": response if isinstance(response, list) else [response]}

    def _format_heartbeat_response(self, response) -> Dict[str, Any]:
        """Format single heartbeat response."""
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        elif hasattr(response, '__dict__'):
            return response.__dict__
        else:
            return response

    def _format_ping_response(self, response) -> Dict[str, Any]:
        """Format ping response."""
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        elif hasattr(response, '__dict__'):
            return response.__dict__
        else:
            return {"ping_sent": True, "timestamp": datetime.utcnow().isoformat()}

    def _format_logs_response(self, response) -> Dict[str, Any]:
        """Format logs response."""
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        elif hasattr(response, '__dict__'):
            return response.__dict__
        else:
            return {"logs": response if isinstance(response, list) else [response]}