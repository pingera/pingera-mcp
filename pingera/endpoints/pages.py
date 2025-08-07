
"""
Pages endpoint for Pingera API.
"""
from typing import Optional
from ..models.pages import Page, PageList
from .base import BaseEndpoint


class PagesEndpoint(BaseEndpoint):
    """Pages endpoint handler."""
    
    def __init__(self, client):
        super().__init__(client)
        self._base_path = "pages"
    
    def list(
        self, 
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        status: Optional[str] = None
    ) -> PageList:
        """
        Get list of statuspages.
        
        Args:
            page: Page number for pagination
            per_page: Number of items per page
            status: Filter by page status
            
        Returns:
            PageList: List of statuspages
        """
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if status is not None:
            params["status"] = status
        
        try:
            response = self._make_request("GET", "", params=params)
            data = response.json()
            
            # Handle different possible response structures
            if isinstance(data, list):
                pages = [Page(**page_data) for page_data in data]
                return PageList(pages=pages, total=len(pages))
            elif isinstance(data, dict):
                if "pages" in data:
                    pages = [Page(**page_data) for page_data in data["pages"]]
                    return PageList(
                        pages=pages,
                        total=data.get("total"),
                        page=data.get("page"),
                        per_page=data.get("per_page")
                    )
                elif "data" in data:
                    page_data = data["data"]
                    if isinstance(page_data, list):
                        pages = [Page(**item) for item in page_data]
                        return PageList(pages=pages, total=len(pages))
                    else:
                        pages = [Page(**page_data)]
                        return PageList(pages=pages, total=1)
                else:
                    pages = [Page(**data)]
                    return PageList(pages=pages, total=1)
            else:
                return PageList(pages=[], total=0)
                
        except Exception as e:
            self.client.logger.error(f"Error getting pages: {e}")
            raise
    
    def get(self, page_id: str) -> Page:
        """
        Get a specific page by ID.
        
        Args:
            page_id: ID of the page to retrieve
            
        Returns:
            Page: Page details
        """
        try:
            response = self._make_request("GET", str(page_id))
            data = response.json()
            
            if "data" in data:
                return Page(**data["data"])
            else:
                return Page(**data)
                
        except Exception as e:
            self.client.logger.error(f"Error getting page {page_id}: {e}")
            raise
    
    def create(self, page_data: dict) -> Page:
        """
        Create a new status page.
        
        Args:
            page_data: Page configuration data
            
        Returns:
            Page: Created page
        """
        try:
            response = self._make_request("POST", "", data=page_data)
            data = response.json()
            
            if "data" in data:
                return Page(**data["data"])
            else:
                return Page(**data)
                
        except Exception as e:
            self.client.logger.error(f"Error creating page: {e}")
            raise
    
    def patch(self, page_id: str, page_data: dict) -> Page:
        """
        Partially update an existing page.
        
        Args:
            page_id: ID of the page to update
            page_data: Partial page data to update
            
        Returns:
            Page: Updated page
        """
        try:
            response = self._make_request("PATCH", str(page_id), data=page_data)
            data = response.json()
            
            if "data" in data:
                return Page(**data["data"])
            else:
                return Page(**data)
                
        except Exception as e:
            self.client.logger.error(f"Error patching page {page_id}: {e}")
            raise
    
    def update(self, page_id: str, page_data: dict) -> Page:
        """
        Update an existing page.
        
        Args:
            page_id: ID of the page to update
            page_data: Updated page data
            
        Returns:
            Page: Updated page
        """
        try:
            response = self._make_request("PUT", str(page_id), data=page_data)
            data = response.json()
            
            if "data" in data:
                return Page(**data["data"])
            else:
                return Page(**data)
                
        except Exception as e:
            self.client.logger.error(f"Error updating page {page_id}: {e}")
            raise
    
    def delete(self, page_id: str) -> bool:
        """
        Delete a page.
        
        Args:
            page_id: ID of the page to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            response = self._make_request("DELETE", str(page_id))
            return response.status_code in [200, 204]
                
        except Exception as e:
            self.client.logger.error(f"Error deleting page {page_id}: {e}")
            raise
