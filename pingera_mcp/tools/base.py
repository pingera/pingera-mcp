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

        # Log object details for debugging
        self.logger.debug(f"Converting SDK object: {type(obj)}")
        self.logger.debug(f"Object dir: {dir(obj)}")

        # Try to_dict() method first
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            try:
                result = obj.to_dict()
                self.logger.debug(f"to_dict() result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                return result
            except Exception as e:
                self.logger.debug(f"Failed to use to_dict() method: {e}")

        # Try attribute_map if available (OpenAPI generated clients often have this)
        if hasattr(obj, 'attribute_map'):
            result = {}
            for python_name, api_name in obj.attribute_map.items():
                if hasattr(obj, python_name):
                    value = getattr(obj, python_name)
                    if hasattr(value, 'isoformat'):
                        result[api_name] = value.isoformat()
                    elif hasattr(value, '__dict__'):
                        result[api_name] = self._convert_sdk_object_to_dict(value)
                    elif isinstance(value, list):
                        result[api_name] = [self._convert_sdk_object_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                    else:
                        result[api_name] = value
            self.logger.debug(f"attribute_map result keys: {list(result.keys())}")
            return result

        # Fall back to extracting all public attributes
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                # Skip private attributes but keep everything else
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
            
            # Enhanced ID extraction - check for common ID attributes directly on the object
            # Try to extract IDs using getattr and also check all attributes
            for id_attr in ['id', 'page_id', 'organization_id', 'uuid', 'pk', 'created_at', 'updated_at']:
                try:
                    if hasattr(obj, id_attr):
                        value = getattr(obj, id_attr)
                        if value is not None and id_attr not in result:
                            # Handle datetime objects for timestamps
                            if hasattr(value, 'isoformat'):
                                result[id_attr] = value.isoformat()
                            else:
                                result[id_attr] = value
                            self.logger.info(f"Added missing {id_attr}: {value}")
                except Exception as e:
                    self.logger.warning(f"Failed to extract {id_attr}: {e}")
            
            # Also try to get all attributes from dir() that look like IDs
            for attr_name in dir(obj):
                if not attr_name.startswith('_') and ('id' in attr_name.lower() or attr_name in ['created_at', 'updated_at']):
                    try:
                        if attr_name not in result and hasattr(obj, attr_name):
                            value = getattr(obj, attr_name)
                            if value is not None and callable(value) == False:  # Skip methods
                                # Handle datetime objects
                                if hasattr(value, 'isoformat'):
                                    result[attr_name] = value.isoformat()
                                else:
                                    result[attr_name] = value
                                self.logger.info(f"Found ID-like attribute {attr_name}: {value}")
                    except Exception as e:
                        self.logger.warning(f"Failed to extract {attr_name}: {e}")
            
            self.logger.debug(f"Final extraction result keys: {list(result.keys())}")
            if 'id' in result:
                self.logger.info(f"Successfully extracted ID: {result['id']}")
            else:
                self.logger.warning("No 'id' field found in extracted data")
            
            return result

        # If all else fails, try to convert object directly to dict using vars()
        try:
            result = vars(obj)
            self.logger.debug(f"vars() result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            return result
        except:
            pass

        # Last resort: return the object as-is and log
        self.logger.warning(f"Could not convert SDK object {type(obj)} to dict, returning as-is")
        return obj