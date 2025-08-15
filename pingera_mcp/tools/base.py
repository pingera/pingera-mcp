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
        Convert SDK object to dictionary - AGGRESSIVE EXTRACTION of ALL data.
        We cannot afford to miss ANY data, especially IDs.

        Args:
            obj: SDK response object

        Returns:
            dict: Dictionary representation with ALL possible data extracted
        """
        if obj is None:
            return {}

        # If it's already a dict, return as-is
        if isinstance(obj, dict):
            return obj

        # Start with an empty result and extract EVERYTHING
        result = {}
        
        self.logger.info(f"Converting SDK object: {type(obj)}")

        # STRATEGY 1: Try to_dict() method first
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            try:
                to_dict_result = obj.to_dict()
                if isinstance(to_dict_result, dict):
                    result.update(to_dict_result)
                    self.logger.info(f"to_dict() extracted {len(to_dict_result)} fields: {list(to_dict_result.keys())}")
            except Exception as e:
                self.logger.warning(f"to_dict() failed: {e}")

        # STRATEGY 2: Extract from attribute_map (OpenAPI clients)
        if hasattr(obj, 'attribute_map'):
            try:
                for python_name, api_name in obj.attribute_map.items():
                    if hasattr(obj, python_name):
                        value = getattr(obj, python_name)
                        if value is not None:
                            # Handle datetime objects
                            if hasattr(value, 'isoformat'):
                                result[api_name] = value.isoformat()
                            # Handle nested objects
                            elif hasattr(value, '__dict__'):
                                result[api_name] = self._convert_sdk_object_to_dict(value)
                            # Handle lists
                            elif isinstance(value, list):
                                result[api_name] = [self._convert_sdk_object_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                            else:
                                result[api_name] = value
                            
                            # Also store with python name as backup
                            if python_name != api_name:
                                result[python_name] = result[api_name]
                                
                self.logger.info(f"attribute_map extracted {len(obj.attribute_map)} mappings")
            except Exception as e:
                self.logger.warning(f"attribute_map extraction failed: {e}")

        # STRATEGY 3: Extract from __dict__ (all instance attributes)
        if hasattr(obj, '__dict__'):
            try:
                for key, value in obj.__dict__.items():
                    if value is not None:  # Keep everything that has a value
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
                            
                self.logger.info(f"__dict__ extracted {len(obj.__dict__)} attributes")
            except Exception as e:
                self.logger.warning(f"__dict__ extraction failed: {e}")

        # STRATEGY 4: Extract from dir() - get ALL possible attributes
        try:
            all_attrs = [attr for attr in dir(obj) if not attr.startswith('_') and not callable(getattr(obj, attr, None))]
            for attr_name in all_attrs:
                try:
                    if not hasattr(obj, attr_name):
                        continue
                        
                    value = getattr(obj, attr_name)
                    if value is None:
                        continue
                        
                    # Skip if we already have this attribute
                    if attr_name in result:
                        continue
                        
                    # Handle datetime objects
                    if hasattr(value, 'isoformat'):
                        result[attr_name] = value.isoformat()
                    # Handle nested objects  
                    elif hasattr(value, '__dict__'):
                        result[attr_name] = self._convert_sdk_object_to_dict(value)
                    # Handle lists
                    elif isinstance(value, list):
                        result[attr_name] = [self._convert_sdk_object_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                    # Store primitive values
                    else:
                        result[attr_name] = value
                        
                except Exception as e:
                    self.logger.debug(f"Failed to extract {attr_name}: {e}")
                    
            self.logger.info(f"dir() scan found {len(all_attrs)} non-private attributes")
        except Exception as e:
            self.logger.warning(f"dir() scan failed: {e}")

        # STRATEGY 5: Use vars() as additional fallback
        try:
            vars_result = vars(obj)
            for key, value in vars_result.items():
                if key not in result and value is not None:
                    if hasattr(value, 'isoformat'):
                        result[key] = value.isoformat()
                    elif hasattr(value, '__dict__'):
                        result[key] = self._convert_sdk_object_to_dict(value)
                    elif isinstance(value, list):
                        result[key] = [self._convert_sdk_object_to_dict(item) if hasattr(item, '__dict__') else item for item in value]
                    else:
                        result[key] = value
            self.logger.info(f"vars() extracted {len(vars_result)} additional fields")
        except Exception as e:
            self.logger.debug(f"vars() extraction failed: {e}")

        # LOG RESULTS
        self.logger.info(f"TOTAL EXTRACTED FIELDS: {len(result)}")
        self.logger.info(f"All extracted keys: {sorted(result.keys())}")
        
        # Special logging for ID fields
        id_fields = [k for k in result.keys() if 'id' in k.lower()]
        if id_fields:
            self.logger.info(f"ID FIELDS FOUND: {id_fields}")
            for id_field in id_fields:
                self.logger.info(f"  {id_field}: {result[id_field]}")
        else:
            self.logger.error("NO ID FIELDS FOUND! This is a problem!")

        # If we still have no data, return the object as-is with warning
        if not result:
            self.logger.error(f"FAILED to extract ANY data from {type(obj)}")
            return {"_raw_object_type": str(type(obj)), "_extraction_failed": True}

        return result