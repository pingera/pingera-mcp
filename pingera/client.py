"""
Pingera API client for interacting with the monitoring service.
"""
import logging
from typing import Dict, Optional, Any, List
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    PingeraAPIError, 
    PingeraAuthError, 
    PingeraConnectionError,
    PingeraTimeoutError
)
from .models import Page, PageList, APIResponse


class PingeraClient:
    """Client for interacting with Pingera monitoring API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.pingera.ru/v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Pingera API client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for Pingera API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Setup requests session with retries
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "Pingera-MCP-Server/0.1.0"
        })
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Make HTTP request to Pingera API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data
            
        Returns:
            requests.Response: Response object
            
        Raises:
            PingeraConnectionError: If connection fails
            PingeraTimeoutError: If request times out
            PingeraAuthError: If authentication fails
            PingeraAPIError: If API returns error
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))
        
        try:
            self.logger.debug(f"Making {method} request to {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout
            )
            
            self.logger.debug(f"Response status: {response.status_code}")
            
            # Handle authentication errors
            if response.status_code == 401:
                raise PingeraAuthError("Authentication failed. Check your API key.")
            
            # Handle other client errors
            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                    message = error_data.get("message", f"API error: {response.status_code}")
                except ValueError:
                    message = f"API error: {response.status_code}"
                
                raise PingeraAPIError(
                    message=message,
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            return response
            
        except requests.exceptions.ConnectTimeout:
            raise PingeraTimeoutError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise PingeraConnectionError(f"Connection error: {e}")
        except requests.exceptions.RequestException as e:
            raise PingeraAPIError(f"Request failed: {e}")
    
    def get_pages(
        self, 
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        status: Optional[str] = None
    ) -> PageList:
        """
        Get list of monitored pages.
        
        Args:
            page: Page number for pagination
            per_page: Number of items per page
            status: Filter by page status
            
        Returns:
            PageList: List of monitored pages
            
        Raises:
            PingeraAPIError: If API request fails
        """
        params = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if status is not None:
            params["status"] = status
        
        try:
            response = self._make_request("GET", "/pages", params=params)
            data = response.json()
            
            # Handle different possible response structures
            if isinstance(data, list):
                # Direct list of pages
                pages = [Page(**page_data) for page_data in data]
                return PageList(pages=pages, total=len(pages))
            elif isinstance(data, dict):
                if "pages" in data:
                    # Response with pages key
                    pages = [Page(**page_data) for page_data in data["pages"]]
                    return PageList(
                        pages=pages,
                        total=data.get("total"),
                        page=data.get("page"),
                        per_page=data.get("per_page")
                    )
                elif "data" in data:
                    # Response with data key
                    page_data = data["data"]
                    if isinstance(page_data, list):
                        pages = [Page(**item) for item in page_data]
                        return PageList(pages=pages, total=len(pages))
                    else:
                        # Single page wrapped in data
                        pages = [Page(**page_data)]
                        return PageList(pages=pages, total=1)
                else:
                    # Assume the dict itself contains page data
                    pages = [Page(**data)]
                    return PageList(pages=pages, total=1)
            else:
                self.logger.warning(f"Unexpected response format: {type(data)}")
                return PageList(pages=[], total=0)
                
        except Exception as e:
            self.logger.error(f"Error getting pages: {e}")
            raise
    
    def get_page(self, page_id: int) -> Page:
        """
        Get a specific page by ID.
        
        Args:
            page_id: ID of the page to retrieve
            
        Returns:
            Page: Page details
            
        Raises:
            PingeraAPIError: If API request fails
        """
        try:
            response = self._make_request("GET", f"/pages/{page_id}")
            data = response.json()
            
            # Handle different response structures
            if "data" in data:
                return Page(**data["data"])
            else:
                return Page(**data)
                
        except Exception as e:
            self.logger.error(f"Error getting page {page_id}: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test connection to Pingera API.
        
        Returns:
            bool: True if connection is successful
        """
        try:
            # Use the root endpoint for a lightweight connection test
            response = self._make_request("GET", "/")
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and connection status.
        
        Returns:
            Dict containing API information
        """
        try:
            # Query the root endpoint to get API status
            response = self._make_request("GET", "/")
            api_data = response.json()
            
            return {
                "connected": True,
                "base_url": self.base_url,
                "message": api_data.get("message", "Pingera.ru API"),
                "authentication": api_data.get("authentication"),
                "documentation": api_data.get("documentation"),
                "api_version": "v1"
            }
        except Exception as e:
            return {
                "connected": False,
                "base_url": self.base_url,
                "error": str(e),
                "api_version": "v1"
            }
