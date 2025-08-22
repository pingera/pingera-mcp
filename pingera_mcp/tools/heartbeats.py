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
        """
        Create a new heartbeat.

        Args:
            heartbeat_data: Heartbeat configuration data

        Returns:
            JSON string with created heartbeat data
        """
        try:
            self.logger.info(f"Creating heartbeat with data: {heartbeat_data}")

            with self.client._get_api_client() as api_client:
                from pingera.api import HeartbeatsApi
                heartbeats_api = HeartbeatsApi(api_client)

                response = heartbeats_api.v1_heartbeats_post(heartbeat_data)

                created_heartbeat = self._format_heartbeat_response(response)
                return self._success_response(created_heartbeat)

        except Exception as e:
            self.logger.error(f"Error creating heartbeat: {e}")
            return self._error_response(str(e))

    async def update_heartbeat(self, heartbeat_id: str, heartbeat_data: dict) -> str:
        """
        Update an existing heartbeat.

        Args:
            heartbeat_id: ID of the heartbeat to update
            heartbeat_data: Updated heartbeat data

        Returns:
            JSON string with updated heartbeat data
        """
        try:
            self.logger.info(f"Updating heartbeat {heartbeat_id} with data: {heartbeat_data}")

            with self.client._get_api_client() as api_client:
                from pingera.api import HeartbeatsApi
                heartbeats_api = HeartbeatsApi(api_client)

                response = heartbeats_api.v1_heartbeats_heartbeat_id_put(
                    heartbeat_id=heartbeat_id,
                    heartbeat_data=heartbeat_data
                )

                updated_heartbeat = self._format_heartbeat_response(response)
                return self._success_response(updated_heartbeat)

        except Exception as e:
            self.logger.error(f"Error updating heartbeat {heartbeat_id}: {e}")
            return self._error_response(str(e))

    async def delete_heartbeat(self, heartbeat_id: str) -> str:
        """
        Delete a heartbeat.

        Args:
            heartbeat_id: ID of the heartbeat to delete

        Returns:
            JSON string with deletion status
        """
        try:
            self.logger.info(f"Deleting heartbeat {heartbeat_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import HeartbeatsApi
                heartbeats_api = HeartbeatsApi(api_client)

                heartbeats_api.v1_heartbeats_heartbeat_id_delete(heartbeat_id=heartbeat_id)

                return self._success_response({"deleted": True, "heartbeat_id": heartbeat_id})

        except Exception as e:
            self.logger.error(f"Error deleting heartbeat {heartbeat_id}: {e}")
            return self._error_response(str(e))

    async def send_heartbeat_ping(self, heartbeat_id: str) -> str:
        """
        Send a ping to a heartbeat.

        Args:
            heartbeat_id: ID of the heartbeat to ping

        Returns:
            JSON string with ping status
        """
        try:
            self.logger.info(f"Sending ping to heartbeat {heartbeat_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import HeartbeatsApi
                heartbeats_api = HeartbeatsApi(api_client)

                response = heartbeats_api.v1_heartbeats_heartbeat_id_ping_post(heartbeat_id=heartbeat_id)

                ping_data = self._format_ping_response(response)
                return self._success_response(ping_data)

        except Exception as e:
            self.logger.error(f"Error sending ping to heartbeat {heartbeat_id}: {e}")
            return self._error_response(str(e))

    async def get_heartbeat_logs(
        self,
        heartbeat_id: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """Get historical ping logs for a heartbeat monitor."""
        try:
            self.logger.info(f"Getting logs for heartbeat {heartbeat_id}")

            # Filter out None values
            kwargs = {"heartbeat_id": heartbeat_id}
            if from_date is not None:
                kwargs["from_date"] = from_date
            if to_date is not None:
                kwargs["to_date"] = to_date
            if page is not None:
                kwargs["page"] = page
            if page_size is not None:
                kwargs["page_size"] = page_size

            # Call the SDK method
            logs = await self.client.get_heartbeat_logs(**kwargs)

            logs_data = self._format_logs_response(logs)
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