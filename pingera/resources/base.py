
"""
Base class for MCP resources.
"""
import json
import logging
from typing import Any

from pingera import PingeraClient, PingeraError


class BaseResources:
    """Base class for MCP resources with common functionality."""
    
    def __init__(self, client: PingeraClient):
        self.client = client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _json_response(self, data: Any) -> str:
        """Create a JSON response."""
        return json.dumps(data, indent=2, default=str)
    
    def _error_response(self, error: str, fallback_data: Any = None) -> str:
        """Create an error response with fallback data."""
        response_data = {"error": error}
        if fallback_data:
            response_data.update(fallback_data)
        return self._json_response(response_data)
