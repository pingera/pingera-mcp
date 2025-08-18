"""
MCP tools for component management.
"""
import json
from typing import Optional

from .base import BaseTools
from ..exceptions import PingeraError


class ComponentTools(BaseTools):
    """Tools for managing status page components."""

    async def list_component_groups(
        self,
        page_id: str,
        show_deleted: bool = False
    ) -> str:
        """
        Get all component groups for a specific status page.

        Args:
            page_id: The ID of the status page
            show_deleted: Include deleted component groups in the response

        Returns:
            str: JSON string containing list of component groups
        """
        try:
            self.logger.info(f"Listing component groups for page {page_id}")

            component_groups = self.client.components.get_component_groups(
                page_id=page_id,
                show_deleted=show_deleted
            )

            data = {
                "page_id": page_id,
                "component_groups": [group.dict() for group in component_groups],
                "total": len(component_groups),
                "show_deleted": show_deleted
            }

            return self._success_response(data)

        except PingeraError as e:
            self.logger.error(f"Error listing component groups for page {page_id}: {e}")
            return self._error_response(str(e), {"component_groups": [], "total": 0})

    async def get_component_details(self, page_id: str, component_id: str) -> str:
        """
        Get detailed information about a specific component.

        Args:
            page_id: The ID of the status page
            component_id: The ID of the component

        Returns:
            str: JSON string containing component details
        """
        try:
            self.logger.info(f"Getting component details for {component_id} on page {page_id}")
            # Use the SDK client properly - components should be an attribute
            if hasattr(self.client, 'components'):
                component = self.client.components.get_component(
                    page_id=page_id,
                    component_id=component_id
                )
            else:
                # Fallback for direct client method
                component = self.client.get_component(
                    page_id=page_id,
                    component_id=component_id
                )

            # Handle SDK response format properly
            if hasattr(component, 'to_dict'):
                component_dict = component.to_dict()
            elif hasattr(component, '__dict__'):
                component_dict = component.__dict__
            else:
                # If it's already a dict or simple type
                component_dict = component if component is not None else {}

            return self._success_response(component_dict)

        except PingeraError as e:
            self.logger.error(f"Error getting component {component_id} details: {e}")
            return self._error_response(str(e), None)

    async def create_component(
        self,
        page_id: str,
        name: str,
        description: Optional[str] = None,
        group: bool = False,
        group_id: Optional[str] = None,
        only_show_if_degraded: Optional[bool] = None,
        position: Optional[int] = None,
        showcase: Optional[bool] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Create a new component for a status page.

        Args:
            page_id: The ID of the status page
            name: Display name of the component (required)
            description: Detailed description of the component
            group: Whether this component is a group container
            group_id: ID of the group this component belongs to
            only_show_if_degraded: Whether to show only when not operational
            position: Display order position on the status page
            showcase: Whether to prominently display this component
            status: Current operational status of the component
            **kwargs: Additional component configuration options

        Returns:
            str: JSON string containing the created component details
        """
        try:
            self.logger.info(f"Creating new component '{name}' for page {page_id}")

            component_data = {"name": name}
            if description:
                component_data["description"] = description
            if group is not None:
                component_data["group"] = group
            if group_id:
                component_data["group_id"] = group_id
            if only_show_if_degraded is not None:
                component_data["only_show_if_degraded"] = only_show_if_degraded
            if position is not None:
                component_data["position"] = position
            if showcase is not None:
                component_data["showcase"] = showcase
            if status:
                component_data["status"] = status

            # Add any additional configuration
            component_data.update(kwargs)

            component = self.client.components.create_component(page_id, component_data)

            return self._success_response(component.dict())

        except PingeraError as e:
            self.logger.error(f"Error creating component: {e}")
            return self._error_response(str(e), None)

    async def update_component(
        self,
        page_id: str,
        component_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        group: Optional[bool] = None,
        group_id: Optional[str] = None,
        only_show_if_degraded: Optional[bool] = None,
        position: Optional[int] = None,
        showcase: Optional[bool] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Update an existing component (full update).

        Args:
            page_id: The ID of the status page
            component_id: The ID of the component to update
            name: Display name of the component
            description: Detailed description of the component
            group: Whether this component is a group container
            group_id: ID of the group this component belongs to
            only_show_if_degraded: Whether to show only when not operational
            position: Display order position on the status page
            showcase: Whether to prominently display this component
            status: Current operational status of the component
            **kwargs: Additional component configuration options

        Returns:
            str: JSON string containing the updated component details
        """
        try:
            self.logger.info(f"Updating component {component_id} on page {page_id}")

            component_data = {}
            if name:
                component_data["name"] = name
            if description:
                component_data["description"] = description
            if group is not None:
                component_data["group"] = group
            if group_id:
                component_data["group_id"] = group_id
            if only_show_if_degraded is not None:
                component_data["only_show_if_degraded"] = only_show_if_degraded
            if position is not None:
                component_data["position"] = position
            if showcase is not None:
                component_data["showcase"] = showcase
            if status:
                component_data["status"] = status

            # Add any additional configuration
            component_data.update(kwargs)

            component = self.client.components.update_component(page_id, component_id, component_data)

            return self._success_response(component.dict())

        except PingeraError as e:
            self.logger.error(f"Error updating component {component_id}: {e}")
            return self._error_response(str(e), None)

    async def patch_component(self, page_id: str, component_id: str, **kwargs) -> str:
        """
        Partially update an existing component.

        Args:
            page_id: The ID of the status page
            component_id: The ID of the component to update
            **kwargs: Component fields to update (only provided fields will be updated)

        Returns:
            str: JSON string containing the updated component details
        """
        try:
            self.logger.info(f"Patching component {component_id} on page {page_id}")

            if not kwargs:
                return self._error_response("No fields provided for update", None)

            component = self.client.components.patch_component(page_id, component_id, kwargs)

            return self._success_response(component.dict())

        except PingeraError as e:
            self.logger.error(f"Error patching component {component_id}: {e}")
            return self._error_response(str(e), None)

    async def delete_component(self, page_id: str, component_id: str) -> str:
        """
        Permanently delete a component.
        This action cannot be undone.

        Args:
            page_id: The ID of the status page
            component_id: The ID of the component to delete

        Returns:
            str: JSON string confirming deletion
        """
        try:
            self.logger.info(f"Deleting component {component_id} from page {page_id}")

            success = self.client.components.delete_component(page_id, component_id)

            if success:
                return json.dumps({
                    "success": True,
                    "message": f"Component {component_id} deleted successfully",
                    "data": {"page_id": page_id, "component_id": component_id}
                }, indent=2)
            else:
                return self._error_response("Failed to delete component", None)

        except PingeraError as e:
            self.logger.error(f"Error deleting component {component_id}: {e}")
            return self._error_response(str(e), None)