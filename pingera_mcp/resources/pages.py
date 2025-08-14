
"""
MCP resources for page data access.
"""
from .base import BaseResources
from ..exceptions import PingeraError


class PagesResources(BaseResources):
    """Resources for accessing page data."""
    
    async def get_pages_resource(self) -> str:
        """
        Resource providing access to all monitored pages.
        
        Returns:
            str: JSON string containing all pages
        """
        try:
            self.logger.info("Fetching pages resource")
            pages = self.client.get_pages()
            
            # Convert to dict for JSON serialization
            pages_data = {
                "pages": [page.dict() for page in pages.pages],
                "total": pages.total,
                "page": pages.page,
                "per_page": pages.per_page
            }
            
            return self._json_response(pages_data)
            
        except PingeraError as e:
            self.logger.error(f"Error fetching pages resource: {e}")
            return self._error_response(str(e), {
                "pages": [],
                "total": 0
            })
    
    async def get_page_resource(self, page_id: str) -> str:
        """
        Resource providing access to a specific page.
        
        Args:
            page_id: ID of the page to retrieve
            
        Returns:
            str: JSON string containing page details
        """
        try:
            self.logger.info(f"Fetching page resource for ID: {page_id}")
            page_id_int = int(page_id)
            page = self.client.get_page(page_id_int)
            
            return self._json_response(page.dict())
            
        except ValueError:
            self.logger.error(f"Invalid page ID: {page_id}")
            return self._error_response(f"Invalid page ID: {page_id}", {
                "page": None
            })
        except PingeraError as e:
            self.logger.error(f"Error fetching page resource {page_id}: {e}")
            return self._error_response(str(e), {
                "page": None
            })
