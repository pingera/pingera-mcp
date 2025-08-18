"""
MCP tools for component management.
"""
import json
from typing import Optional

from .base import BaseTools
from ..exceptions import PingeraError


class ComponentTools(BaseTools):
    """Tools for managing status page components."""

    async def list_component_groups(self, page_id: str, show_deleted: Optional[bool] = False) -> str:
        """List all component groups for a page."""
        try:
            components_response = self.client.components.get_component_groups(page_id, show_deleted)
            components_dict = self._convert_sdk_object_to_dict(components_response)

            return json.dumps({
                "success": True,
                "data": components_dict,
                "message": f"Retrieved component groups for page {page_id}"
            }, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to list component groups: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve component groups for page {page_id}"
            }, indent=2)

    async def get_component_details(self, page_id: str, component_id: str) -> str:
        """Get details for a specific component."""
        try:
            component_response = self.client.components.get_component(page_id, component_id)
            component_dict = self._convert_sdk_object_to_dict(component_response)

            return json.dumps({
                "success": True,
                "data": component_dict,
                "message": f"Retrieved details for component {component_id}"
            }, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to get component details: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve details for component {component_id}"
            }, indent=2)

    async def create_component(self, page_id: str, name: str, description: Optional[str] = None, group: Optional[bool] = False, group_id: Optional[str] = None, only_show_if_degraded: Optional[bool] = None, position: Optional[int] = None, showcase: Optional[bool] = None, status: Optional[str] = None, **kwargs) -> str:
        """Create a new component."""
        try:
            component_data = {
                "name": name,
                "description": description,
                "group": group,
                "group_id": group_id,
                "only_show_if_degraded": only_show_if_degraded,
                "position": position,
                "showcase": showcase,
                "status": status,
                **kwargs
            }
            # Remove None values
            component_data = {k: v for k, v in component_data.items() if v is not None}

            return json.dumps({
                "success": False,
                "error": "Component creation not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to create component: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to create component: {name}"
            }, indent=2)

    async def update_component(self, page_id: str, component_id: str, name: Optional[str] = None, description: Optional[str] = None, group: Optional[bool] = None, group_id: Optional[str] = None, only_show_if_degraded: Optional[bool] = None, position: Optional[int] = None, showcase: Optional[bool] = None, status: Optional[str] = None, **kwargs) -> str:
        """Update an existing component."""
        try:
            return json.dumps({
                "success": False,
                "error": "Component update not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to update component: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to update component: {component_id}"
            }, indent=2)

    async def patch_component(self, page_id: str, component_id: str, **kwargs) -> str:
        """Partially update a component."""
        try:
            return json.dumps({
                "success": False,
                "error": "Component patch not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to patch component: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to patch component: {component_id}"
            }, indent=2)

    async def delete_component(self, page_id: str, component_id: str) -> str:
        """Delete a component."""
        try:
            return json.dumps({
                "success": False,
                "error": "Component deletion not yet implemented in SDK",
                "message": "Write operations require SDK method implementation"
            }, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to delete component: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "message": f"Failed to delete component: {component_id}"
            }, indent=2)