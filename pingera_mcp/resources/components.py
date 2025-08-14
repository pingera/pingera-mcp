
"""
MCP resources for component data access.
"""
from .base import BaseResources
from ..exceptions import PingeraError


class ComponentResources(BaseResources):
    """Resources for accessing component data."""
    
    async def get_component_groups_resource(self, page_id: str) -> str:
        """
        Resource providing access to component groups for a specific page.
        
        Args:
            page_id: ID of the page to get component groups for
            
        Returns:
            str: JSON string containing component groups
        """
        try:
            self.logger.info(f"Fetching component groups resource for page ID: {page_id}")
            components = self.client.components.get_component_groups(page_id)
            
            # Convert to dict for JSON serialization
            components_data = [component.dict() for component in components]
            
            return self._json_response({
                "page_id": page_id,
                "component_groups": components_data,
                "total": len(components_data)
            })
            
        except PingeraError as e:
            self.logger.error(f"Error fetching component groups resource: {e}")
            return self._error_response(str(e), {
                "page_id": page_id,
                "component_groups": [],
                "total": 0
            })
    
    async def get_component_resource(self, page_id: str, component_id: str) -> str:
        """
        Resource providing access to a specific component.
        
        Args:
            page_id: ID of the page
            component_id: ID of the component to retrieve
            
        Returns:
            str: JSON string containing component details
        """
        try:
            self.logger.info(f"Fetching component resource for page ID: {page_id}, component ID: {component_id}")
            component = self.client.components.get_component(page_id, component_id)
            
            return self._json_response({
                "page_id": page_id,
                "component": component.dict()
            })
            
        except PingeraError as e:
            self.logger.error(f"Error fetching component resource: {e}")
            return self._error_response(str(e))
