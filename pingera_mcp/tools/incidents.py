
"""
MCP tools for incident management.
"""
import json
from typing import Optional, Dict, Any
from datetime import datetime

from .base import BaseTools
from ..exceptions import PingeraError


class IncidentsTools(BaseTools):
    """Tools for managing status page incidents."""

    async def list_incidents(
        self,
        page_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        status: Optional[str] = None
    ) -> str:
        """
        List incidents for a status page.
        
        Args:
            page_id: ID of the status page
            page: Page number for pagination
            page_size: Number of items per page
            status: Filter by incident status (e.g., 'open', 'investigating', 'resolved')
            
        Returns:
            JSON string with incidents data
        """
        try:
            self.logger.info(f"Listing incidents for page {page_id} (page={page}, page_size={page_size}, status={status})")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                kwargs = {}
                if page is not None:
                    kwargs['page'] = page
                if page_size is not None:
                    kwargs['page_size'] = page_size
                if status is not None:
                    kwargs['status'] = status

                response = incidents_api.v1_pages_page_id_incidents_get(
                    page_id=page_id,
                    **kwargs
                )

                incidents_data = self._format_incidents_response(response)
                return self._success_response(incidents_data)

        except Exception as e:
            self.logger.error(f"Error listing incidents for page {page_id}: {e}")
            return self._error_response(str(e))

    async def get_incident_details(self, page_id: str, incident_id: str) -> str:
        """
        Get details for a specific incident.
        
        Args:
            page_id: ID of the status page
            incident_id: ID of the incident to retrieve
            
        Returns:
            JSON string with incident details
        """
        try:
            self.logger.info(f"Getting incident details for {incident_id} on page {page_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                response = incidents_api.v1_pages_page_id_incidents_incident_id_get(
                    page_id=page_id,
                    incident_id=incident_id
                )

                incident_data = self._format_incident_response(response)
                return self._success_response(incident_data)

        except Exception as e:
            self.logger.error(f"Error getting incident details for {incident_id}: {e}")
            return self._error_response(str(e))

    async def create_incident(self, page_id: str, incident_data: dict) -> str:
        """
        Create a new incident.
        
        Args:
            page_id: ID of the status page
            incident_data: Incident configuration data
            
        Returns:
            JSON string with created incident data
        """
        try:
            self.logger.info(f"Creating incident on page {page_id}: {incident_data.get('name', 'Unnamed')}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                response = incidents_api.v1_pages_page_id_incidents_post(
                    page_id=page_id,
                    incident=incident_data
                )

                created_incident = self._format_incident_response(response)
                return self._success_response(created_incident)

        except Exception as e:
            self.logger.error(f"Error creating incident on page {page_id}: {e}")
            return self._error_response(str(e))

    async def update_incident(self, page_id: str, incident_id: str, incident_data: dict) -> str:
        """
        Update an existing incident.
        
        Args:
            page_id: ID of the status page
            incident_id: ID of the incident to update
            incident_data: Updated incident data
            
        Returns:
            JSON string with updated incident data
        """
        try:
            self.logger.info(f"Updating incident {incident_id} on page {page_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                response = incidents_api.v1_pages_page_id_incidents_incident_id_put(
                    page_id=page_id,
                    incident_id=incident_id,
                    incident=incident_data
                )

                updated_incident = self._format_incident_response(response)
                return self._success_response(updated_incident)

        except Exception as e:
            self.logger.error(f"Error updating incident {incident_id}: {e}")
            return self._error_response(str(e))

    async def delete_incident(self, page_id: str, incident_id: str) -> str:
        """
        Delete an incident.
        
        Args:
            page_id: ID of the status page
            incident_id: ID of the incident to delete
            
        Returns:
            JSON string with deletion status
        """
        try:
            self.logger.info(f"Deleting incident {incident_id} on page {page_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                incidents_api.v1_pages_page_id_incidents_incident_id_delete(
                    page_id=page_id,
                    incident_id=incident_id
                )

                return self._success_response({
                    "deleted": True,
                    "incident_id": incident_id,
                    "page_id": page_id
                })

        except Exception as e:
            self.logger.error(f"Error deleting incident {incident_id}: {e}")
            return self._error_response(str(e))

    async def add_incident_update(self, page_id: str, incident_id: str, update_data: dict) -> str:
        """
        Add an update to an incident.
        
        Args:
            page_id: ID of the status page
            incident_id: ID of the incident
            update_data: Incident update data
            
        Returns:
            JSON string with created update data
        """
        try:
            self.logger.info(f"Adding update to incident {incident_id} on page {page_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                response = incidents_api.v1_pages_page_id_incidents_incident_id_updates_post(
                    page_id=page_id,
                    incident_id=incident_id,
                    update=update_data
                )

                update_response = self._format_update_response(response)
                return self._success_response(update_response)

        except Exception as e:
            self.logger.error(f"Error adding update to incident {incident_id}: {e}")
            return self._error_response(str(e))

    async def get_incident_updates(self, page_id: str, incident_id: str) -> str:
        """
        Get all updates for an incident.
        
        Args:
            page_id: ID of the status page
            incident_id: ID of the incident
            
        Returns:
            JSON string with incident updates
        """
        try:
            self.logger.info(f"Getting updates for incident {incident_id} on page {page_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                response = incidents_api.v1_pages_page_id_incidents_incident_id_updates_get(
                    page_id=page_id,
                    incident_id=incident_id
                )

                updates_data = self._format_updates_response(response)
                return self._success_response(updates_data)

        except Exception as e:
            self.logger.error(f"Error getting updates for incident {incident_id}: {e}")
            return self._error_response(str(e))

    async def create_incident(self, page_id: str, incident_data: dict) -> str:
        """Create a new incident."""
        try:
            return json.dumps({
                "success": False,
                "error": "Incident creation not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to create incident: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": "Failed to create incident"
            }, indent=2)

    async def update_incident(self, page_id: str, incident_id: str, incident_data: dict) -> str:
        """Update an existing incident."""
        try:
            return json.dumps({
                "success": False,
                "error": "Incident update not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to update incident: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to update incident: {incident_id}"
            }, indent=2)

    async def delete_incident(self, page_id: str, incident_id: str) -> str:
        """Delete an incident."""
        try:
            return json.dumps({
                "success": False,
                "error": "Incident deletion not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to delete incident: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to delete incident: {incident_id}"
            }, indent=2)

    async def add_incident_update(self, page_id: str, incident_id: str, update_data: dict) -> str:
        """Add a new status update to an incident."""
        try:
            return json.dumps({
                "success": False,
                "error": "Incident update creation not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to add incident update: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to add update to incident: {incident_id}"
            }, indent=2)

    async def update_incident_update(self, page_id: str, incident_id: str, update_id: str, update_data: dict) -> str:
        """Update an existing incident status update."""
        try:
            return json.dumps({
                "success": False,
                "error": "Incident update modification not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to update incident update: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to update incident update: {update_id}"
            }, indent=2)

    async def delete_incident_update(self, page_id: str, incident_id: str, update_id: str) -> str:
        """Delete an incident status update."""
        try:
            return json.dumps({
                "success": False,
                "error": "Incident update deletion not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to delete incident update: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to delete incident update: {update_id}"
            }, indent=2)

    async def get_incident_update_details(self, page_id: str, incident_id: str, update_id: str) -> str:
        """
        Get details for a specific incident update.
        
        Args:
            page_id: ID of the status page
            incident_id: ID of the incident
            update_id: ID of the update
            
        Returns:
            JSON string with update details
        """
        try:
            self.logger.info(f"Getting update {update_id} for incident {incident_id} on page {page_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                response = incidents_api.v1_pages_page_id_incidents_incident_id_updates_update_id_get(
                    page_id=page_id,
                    incident_id=incident_id,
                    update_id=update_id
                )

                update_data = self._format_update_response(response)
                return self._success_response(update_data)

        except Exception as e:
            self.logger.error(f"Error getting update {update_id}: {e}")
            return self._error_response(str(e))

    async def update_incident_update(self, page_id: str, incident_id: str, update_id: str, update_data: dict) -> str:
        """
        Update an existing incident update.
        
        Args:
            page_id: ID of the status page
            incident_id: ID of the incident
            update_id: ID of the update to modify
            update_data: Updated update data
            
        Returns:
            JSON string with updated update data
        """
        try:
            self.logger.info(f"Updating update {update_id} for incident {incident_id} on page {page_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                response = incidents_api.v1_pages_page_id_incidents_incident_id_updates_update_id_put(
                    page_id=page_id,
                    incident_id=incident_id,
                    update_id=update_id,
                    update=update_data
                )

                updated_update = self._format_update_response(response)
                return self._success_response(updated_update)

        except Exception as e:
            self.logger.error(f"Error updating update {update_id}: {e}")
            return self._error_response(str(e))

    async def delete_incident_update(self, page_id: str, incident_id: str, update_id: str) -> str:
        """
        Delete an incident update.
        
        Args:
            page_id: ID of the status page
            incident_id: ID of the incident
            update_id: ID of the update to delete
            
        Returns:
            JSON string with deletion status
        """
        try:
            self.logger.info(f"Deleting update {update_id} for incident {incident_id} on page {page_id}")

            with self.client._get_api_client() as api_client:
                from pingera.api import StatusPagesIncidentsApi
                incidents_api = StatusPagesIncidentsApi(api_client)

                incidents_api.v1_pages_page_id_incidents_incident_id_updates_update_id_delete(
                    page_id=page_id,
                    incident_id=incident_id,
                    update_id=update_id
                )

                return self._success_response({
                    "deleted": True,
                    "update_id": update_id,
                    "incident_id": incident_id,
                    "page_id": page_id
                })

        except Exception as e:
            self.logger.error(f"Error deleting update {update_id}: {e}")
            return self._error_response(str(e))

    def _format_incidents_response(self, response) -> Dict[str, Any]:
        """Format incidents list response."""
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        elif hasattr(response, '__dict__'):
            incidents_data = getattr(response, 'incidents', [])
            pagination = getattr(response, 'pagination', {})
            
            # Convert model objects to dictionaries for JSON serialization
            if isinstance(incidents_data, list):
                formatted_incidents = []
                for item in incidents_data:
                    if hasattr(item, '__dict__'):
                        # Convert datetime objects to strings for JSON serialization
                        incident_dict = {}
                        for key, value in item.__dict__.items():
                            if hasattr(value, 'isoformat'):  # datetime object
                                incident_dict[key] = value.isoformat()
                            else:
                                incident_dict[key] = value
                        formatted_incidents.append(incident_dict)
                    else:
                        formatted_incidents.append(item)
            else:
                formatted_incidents = incidents_data

            return {
                "incidents": formatted_incidents,
                "total": pagination.get('total_items', 0) if isinstance(pagination, dict) else len(formatted_incidents),
                "page": pagination.get('page', 1) if isinstance(pagination, dict) else 1,
                "page_size": pagination.get('page_size', 20) if isinstance(pagination, dict) else 20
            }
        else:
            return {"incidents": response if isinstance(response, list) else [response]}

    def _format_incident_response(self, response) -> Dict[str, Any]:
        """Format single incident response."""
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        elif hasattr(response, '__dict__'):
            # Convert datetime objects to strings for JSON serialization
            incident_dict = {}
            for key, value in response.__dict__.items():
                if hasattr(value, 'isoformat'):  # datetime object
                    incident_dict[key] = value.isoformat()
                else:
                    incident_dict[key] = value
            return incident_dict
        else:
            return response

    def _format_updates_response(self, response) -> Dict[str, Any]:
        """Format incident updates response."""
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        elif hasattr(response, '__dict__'):
            updates_data = getattr(response, 'updates', [])
            
            # Convert model objects to dictionaries for JSON serialization
            if isinstance(updates_data, list):
                formatted_updates = []
                for item in updates_data:
                    if hasattr(item, '__dict__'):
                        # Convert datetime objects to strings for JSON serialization
                        update_dict = {}
                        for key, value in item.__dict__.items():
                            if hasattr(value, 'isoformat'):  # datetime object
                                update_dict[key] = value.isoformat()
                            else:
                                update_dict[key] = value
                        formatted_updates.append(update_dict)
                    else:
                        formatted_updates.append(item)
            else:
                formatted_updates = updates_data

            return {
                "updates": formatted_updates,
                "total": len(formatted_updates) if isinstance(formatted_updates, list) else 0
            }
        else:
            return {"updates": response if isinstance(response, list) else [response]}

    def _format_update_response(self, response) -> Dict[str, Any]:
        """Format single update response."""
        if hasattr(response, 'to_dict'):
            return response.to_dict()
        elif hasattr(response, '__dict__'):
            # Convert datetime objects to strings for JSON serialization
            update_dict = {}
            for key, value in response.__dict__.items():
                if hasattr(value, 'isoformat'):  # datetime object
                    update_dict[key] = value.isoformat()
                else:
                    update_dict[key] = value
            return update_dict
        else:
            return response
