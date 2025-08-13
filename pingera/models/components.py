
"""
Component models for Pingera API.
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


class ComponentStatus(str, Enum):
    """Component operational status."""
    OPERATIONAL = "operational"
    UNDER_MAINTENANCE = "under_maintenance"
    DEGRADED_PERFORMANCE = "degraded_performance"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"


class Component(BaseModel):
    """Component model matching Pingera API schema."""
    
    # Required fields
    name: str
    
    # Read-only fields
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    page_id: Optional[str] = None
    
    # Optional fields
    description: Optional[str] = None
    group: bool = False
    group_id: Optional[str] = None
    only_show_if_degraded: Optional[bool] = None
    position: Optional[int] = None
    showcase: Optional[bool] = None
    start_date: Optional[datetime] = None
    status: Optional[ComponentStatus] = None

    class Config:
        use_enum_values = True


class ComponentList(BaseModel):
    """Model representing a list of components from Pingera API."""
    
    component_groups: List[Component] = Field(default_factory=list, description="List of component groups")
    total: Optional[int] = Field(None, description="Total number of components")
    page_id: Optional[str] = Field(None, description="Page ID these components belong to")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
