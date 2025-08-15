"""
Base class for MCP tools.
"""
import json
import logging
from typing import Any, Dict

from ..sdk_client import PingeraSDKClient
from ..exceptions import PingeraError


class BaseTools:
    """Base class for MCP tools with common functionality."""

    def __init__(self, client: PingeraSDKClient):
        self.client = client
        self.logger = logging.getLogger(self.__class__.__name__)

    def _success_response(self, data: Any) -> str:
        """Create a successful JSON response."""
        return json.dumps({
            "success": True,
            "data": data
        }, indent=2, default=str)

    def _error_response(self, error_message: str, data: Any = None) -> str:
        """Create standardized error response."""
        return json.dumps({
            "success": False,
            "error": error_message,
            "data": data
        }, indent=2)

    def _convert_sdk_object_to_dict(self, obj) -> dict:
        """
        Convert SDK object to dictionary, preserving all attributes including IDs.

        Args:
            obj: SDK response object

        Returns:
            dict: Dictionary representation of the object
        """
        if obj is None:
            return {}

        # If it's already a dict, return as-is
        if isinstance(obj, dict):
            return obj

        # Try to_dict() method first
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            try:
                return obj.to_dict()
            except Exception as e:
                self.logger.debug(f"Failed to use to_dict() method: {e}")

        # Fall back to extracting __dict__ attributes
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                # Skip private attributes
                if key.startswith('_'):
                    continue

                # Handle datetime objects
                if hasattr(value, 'isoformat'):
                    result[key] = value.isoformat()
                # Handle nested objects recursively
                elif hasattr(value, '__dict__'):
                    result[key] = self._convert_sdk_object_to_dict(value)
                # Handle lists of objects
                elif isinstance(value, list):
                    result[key] = [self._convert_sdk_object_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                else:
                    result[key] = value
            return result

        # If all else fails, return the object as-is
        return obj