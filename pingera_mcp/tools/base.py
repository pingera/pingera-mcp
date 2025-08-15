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
        Convert SDK object to dictionary with clean, business-relevant data only.

        Args:
            obj: SDK response object

        Returns:
            dict: Clean dictionary with only relevant business data
        """
        if obj is None:
            return {}

        # If it's already a dict, return as-is
        if isinstance(obj, dict):
            return obj

        result = {}
        
        # Strategy 1: Try to_dict() method first (preferred)
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            try:
                result = obj.to_dict()
                if isinstance(result, dict):
                    # Clean up the result by removing internal metadata
                    cleaned_result = self._clean_sdk_dict(result)
                    self.logger.debug(f"to_dict() extracted {len(cleaned_result)} clean fields")
                    return cleaned_result
            except Exception as e:
                self.logger.debug(f"to_dict() failed: {e}")

        # Strategy 2: Extract from __dict__ 
        if hasattr(obj, '__dict__'):
            for key, value in obj.__dict__.items():
                # Skip internal/metadata fields
                if key.startswith('_') or key in ['model_fields', 'model_config', 'model_computed_fields', 'model_fields_set']:
                    continue
                    
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

        # Ensure we have an ID field
        if 'id' not in result:
            # Look for alternative ID fields
            for attr in ['page_id', 'organization_id', 'check_id', 'component_id']:
                if hasattr(obj, attr):
                    value = getattr(obj, attr)
                    if value:
                        result['id'] = value
                        break

        self.logger.debug(f"Extracted {len(result)} fields: {list(result.keys())}")
        if 'id' in result:
            self.logger.debug(f"ID found: {result['id']}")

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