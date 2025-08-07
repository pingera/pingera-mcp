
"""
Component endpoints for Pingera API.
"""
from typing import Optional, List

from .base import BaseEndpoint
from ..models import Component


class ComponentEndpoints(BaseEndpoint):
    """Component-related API endpoints."""

    def get_component_groups(self, page_id: str, show_deleted: bool = False) -> List[Component]:
        """
        Get all component groups for a specific status page.
        
        Args:
            page_id: The ID of the status page
            show_deleted: Include deleted component groups in the response
            
        Returns:
            List[Component]: List of component groups
        """
        params = {}
        if show_deleted:
            params["show_deleted"] = show_deleted
            
        response = self._make_request(
            "GET",
            f"pages/{page_id}/component-groups",
            params=params
        )
        
        return [Component(**component) for component in response]

    def create_component(self, page_id: str, component_data: dict) -> Component:
        """
        Create a new component for a status page.
        
        Args:
            page_id: The ID of the status page
            component_data: Component configuration data
            
        Returns:
            Component: The created component
        """
        response = self._make_request(
            "POST",
            f"pages/{page_id}/components",
            data=component_data
        )
        
        return Component(**response.json())

    def get_component(self, page_id: str, component_id: str) -> Component:
        """
        Get a specific component by ID.
        
        Args:
            page_id: The ID of the status page
            component_id: The ID of the component
            
        Returns:
            Component: The component details
        """
        response = self._make_request(
            "GET",
            f"pages/{page_id}/components/{component_id}"
        )
        
        return Component(**response.json())

    def update_component(self, page_id: str, component_id: str, component_data: dict) -> Component:
        """
        Update an existing component.
        
        Args:
            page_id: The ID of the status page
            component_id: The ID of the component to update
            component_data: Updated component data
            
        Returns:
            Component: The updated component
        """
        response = self._make_request(
            "PUT",
            f"pages/{page_id}/components/{component_id}",
            data=component_data
        )
        
        return Component(**response.json())

    def patch_component(self, page_id: str, component_id: str, component_data: dict) -> Component:
        """
        Partially update an existing component.
        
        Args:
            page_id: The ID of the status page
            component_id: The ID of the component to update
            component_data: Partial component data to update
            
        Returns:
            Component: The updated component
        """
        response = self._make_request(
            "PATCH",
            f"pages/{page_id}/components/{component_id}",
            data=component_data
        )
        
        return Component(**response.json())

    def delete_component(self, page_id: str, component_id: str) -> bool:
        """
        Delete a component.
        
        Args:
            page_id: The ID of the status page
            component_id: The ID of the component to delete
            
        Returns:
            bool: True if deletion was successful
        """
        self._make_request(
            "DELETE",
            f"pages/{page_id}/components/{component_id}"
        )
        
        return True
