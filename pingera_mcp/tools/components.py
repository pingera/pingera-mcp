
"""
MCP tools for component management.
"""
import json
from typing import Optional

from .base import BaseTools


class ComponentTools(BaseTools):
    """Tools for managing status page components."""

    async def list_components(self, page_id: str) -> str:
        """
        List all components for a status page.
        
        Args:
            page_id: ID of the status page
            
        Returns:
            JSON string with components data
        """
        try:
            self.logger.info(f"Listing components for page {page_id}")
            
            # Use the simple SDK method
            components = self.client.list_components(page_id)
            
            # Format the response
            formatted_components = []
            for component in components:
                if hasattr(component, '__dict__'):
                    comp_dict = {}
                    for key, value in component.__dict__.items():
                        if hasattr(value, 'isoformat'):  # datetime object
                            comp_dict[key] = value.isoformat()
                        else:
                            comp_dict[key] = value
                    formatted_components.append(comp_dict)
                else:
                    formatted_components.append(component)
            
            return self._success_response({
                "components": formatted_components,
                "total": len(formatted_components),
                "page_id": page_id
            })

        except Exception as e:
            self.logger.error(f"Error listing components for page {page_id}: {e}")
            return self._error_response(str(e))

    async def list_component_groups(self, page_id: str, show_deleted: bool = False) -> str:
        """
        List component groups for a status page.
        
        Args:
            page_id: ID of the status page
            show_deleted: Whether to include deleted components
            
        Returns:
            JSON string with component groups data
        """
        try:
            self.logger.info(f"Listing component groups for page {page_id}")
            
            # For now, just return components since groups are less commonly used
            components = self.client.list_components(page_id)
            
            return self._success_response({
                "component_groups": [],
                "components": len(components),
                "page_id": page_id,
                "message": "Use list_components to get individual components"
            })

        except Exception as e:
            self.logger.error(f"Error listing component groups for page {page_id}: {e}")
            return self._error_response(str(e))

    async def get_component_details(self, page_id: str, component_id: str) -> str:
        """
        Get details for a specific component.
        
        Args:
            page_id: ID of the status page
            component_id: ID of the component to retrieve
            
        Returns:
            JSON string with component details
        """
        try:
            self.logger.info(f"Getting component details for {component_id} on page {page_id}")
            
            # Get all components and find the specific one
            components = self.client.list_components(page_id)
            
            for component in components:
                comp_id = getattr(component, 'id', None) or getattr(component, 'component_id', None)
                if str(comp_id) == str(component_id):
                    if hasattr(component, '__dict__'):
                        comp_dict = {}
                        for key, value in component.__dict__.items():
                            if hasattr(value, 'isoformat'):  # datetime object
                                comp_dict[key] = value.isoformat()
                            else:
                                comp_dict[key] = value
                        return self._success_response(comp_dict)
                    else:
                        return self._success_response(component)
            
            return self._error_response(f"Component {component_id} not found on page {page_id}")

        except Exception as e:
            self.logger.error(f"Error getting component details for {component_id}: {e}")
            return self._error_response(str(e))
