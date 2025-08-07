
"""
Base class for MCP tools.
"""
import json
import logging
from typing import Any, Dict

from pingera import PingeraClient, PingeraError


class BaseTools:
    """Base class for MCP tools with common functionality."""
    
    def __init__(self, client: PingeraClient):
        self.client = client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _success_response(self, data: Any) -> str:
        """Create a successful JSON response."""
        return json.dumps({
            "success": True,
            "data": data
        }, indent=2, default=str)
    
    def _error_response(self, error: str, data: Any = None) -> str:
        """Create an error JSON response."""
        return json.dumps({
            "success": False,
            "error": error,
            "data": data
        }, indent=2)
