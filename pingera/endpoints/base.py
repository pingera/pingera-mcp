
"""
Base endpoint class for Pingera API endpoints.
"""
from typing import Any, Dict, Optional
from abc import ABC


class BaseEndpoint(ABC):
    """Base class for API endpoints."""
    
    def __init__(self, client):
        """
        Initialize endpoint with client reference.
        
        Args:
            client: PingeraClient instance
        """
        self.client = client
        self._base_path = ""
    
    def _make_request(
        self, 
        method: str, 
        path: str = "", 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Make HTTP request using the client.
        
        Args:
            method: HTTP method
            path: Endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            requests.Response: Response object
        """
        return self.client._make_request(method, path, params, data)
