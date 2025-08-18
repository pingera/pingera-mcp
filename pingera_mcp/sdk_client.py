
"""
Simple SDK client for Pingera API.
"""
import logging
from typing import List, Optional, Any
import pingera


class PingeraSDKClient:
    """Simple Pingera SDK client wrapper."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.pingera.ru", timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        
        # Initialize the SDK client
        self._client = pingera.Client(api_key=api_key)
    
    def test_connection(self) -> bool:
        """Test API connection."""
        try:
            # Try to get pages as a connection test
            self._client.status_pages.get_pages()
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_api_info(self) -> dict:
        """Get API connection info."""
        return {
            "base_url": self.base_url,
            "connected": self.test_connection(),
            "timeout": self.timeout
        }
    
    def list_components(self, page_id: str) -> List[Any]:
        """List all components for a page."""
        try:
            # Get components directly from the SDK
            components = self._client.status_pages.get_components(page_id)
            return components
        except Exception as e:
            self.logger.error(f"Error listing components: {e}")
            return []
    
    def list_pages(self) -> List[Any]:
        """List all pages."""
        try:
            pages = self._client.status_pages.get_pages()
            return pages
        except Exception as e:
            self.logger.error(f"Error listing pages: {e}")
            return []
