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
        Convert SDK object to dictionary preserving ALL data including IDs.
        Simple and comprehensive approach.
        """
        if obj is None:
            return {}

        # If it's already a dict, return as-is
        if isinstance(obj, dict):
            return obj

        result = {}
        
        # Get ALL attributes from the object - don't be selective
        if hasattr(obj, '__dict__'):
            for key, value in obj.__dict__.items():
                # Only skip truly internal Python attributes
                if key.startswith('__'):
                    continue
                    
                # Convert all values
                if value is not None:
                    # Handle datetime objects
                    if hasattr(value, 'isoformat'):
                        result[key] = value.isoformat()
                    # Handle nested objects
                    elif hasattr(value, '__dict__'):
                        result[key] = self._convert_sdk_object_to_dict(value)
                    # Handle lists
                    elif isinstance(value, list):
                        result[key] = [self._convert_sdk_object_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                    else:
                        result[key] = value
                else:
                    # Include None values too for completeness
                    result[key] = value

        self.logger.debug(f"Extracted {len(result)} fields: {list(result.keys())}")
        return result

    def _clean_sdk_dict(self, data: dict) -> dict:
        """Remove internal SDK metadata from dictionary."""
        cleaned = {}
        skip_keys = ['model_fields', 'model_config', 'model_computed_fields', 'model_fields_set']
        
        for key, value in data.items():
            if key in skip_keys or key.startswith('_'):
                continue
                
            if isinstance(value, dict):
                cleaned[key] = self._clean_sdk_dict(value)
            elif isinstance(value, list):
                cleaned[key] = [self._clean_sdk_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                cleaned[key] = value
                
        return cleaned