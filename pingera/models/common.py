
"""
Common Pydantic models used across the API.
"""
from typing import List, Optional, Any

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """Generic API response model."""
    
    success: bool = Field(True, description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(default_factory=list, description="List of errors")
