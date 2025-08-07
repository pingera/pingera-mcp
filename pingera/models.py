"""
Pydantic models for Pingera API responses.
"""
from datetime import datetime
from typing import List, Optional, Any, Dict

from pydantic import BaseModel, Field


class Page(BaseModel):
    """Model representing a monitored page in Pingera."""
    
    id: str = Field(..., description="Unique identifier for the page")
    name: str = Field(..., description="Name of the monitored page") 
    url: str = Field(..., description="URL being monitored")
    created_at: str = Field(..., description="When the page was created")
    updated_at: str = Field(..., description="When the page was last updated")
    subdomain: Optional[str] = Field(None, description="Subdomain for the status page")
    domain: Optional[str] = Field(None, description="Custom domain for the status page")
    organization_id: str = Field(..., description="Organization ID")
    language: Optional[str] = Field(None, description="Page language")
    time_zone: Optional[str] = Field(None, description="Timezone setting")
    template: Optional[str] = Field(None, description="Template used")
    template_id: Optional[str] = Field(None, description="Template identifier")
    
    # Status page configuration
    allow_email_subscribers: Optional[bool] = Field(None, description="Allow email subscriptions")
    allow_sms_subscribers: Optional[bool] = Field(None, description="Allow SMS subscriptions")
    allow_webhook_subscribers: Optional[bool] = Field(None, description="Allow webhook subscriptions")
    allow_rss_atom_feeds: Optional[bool] = Field(None, description="Allow RSS/Atom feeds")
    allow_page_subscribers: Optional[bool] = Field(None, description="Allow page subscriptions")
    allow_incident_subscribers: Optional[bool] = Field(None, description="Allow incident subscriptions")
    
    # Visual customization
    company_logo: Optional[str] = Field(None, description="Company logo URL")
    favicon_logo: Optional[str] = Field(None, description="Favicon URL")
    page_description: Optional[str] = Field(None, description="Page description")
    headline: Optional[str] = Field(None, description="Page headline")
    hero_cover: Optional[str] = Field(None, description="Hero cover image")
    support_url: Optional[str] = Field(None, description="Support URL")
    
    # CSS styling
    css_body_background_color: Optional[str] = Field(None, description="Body background color")
    css_font_color: Optional[str] = Field(None, description="Font color")
    css_light_font_color: Optional[str] = Field(None, description="Light font color")
    css_link_color: Optional[str] = Field(None, description="Link color")
    css_button_color: Optional[str] = Field(None, description="Button color")
    css_button_hover_color: Optional[str] = Field(None, description="Button hover color")
    css_button_border_color: Optional[str] = Field(None, description="Button border color")
    css_button_text_color: Optional[str] = Field(None, description="Button text color")
    css_greens: Optional[str] = Field(None, description="Green color for status")
    css_reds: Optional[str] = Field(None, description="Red color for status")
    css_yellows: Optional[str] = Field(None, description="Yellow color for status")
    css_blues: Optional[str] = Field(None, description="Blue color for status") 
    css_oranges: Optional[str] = Field(None, description="Orange color for status")
    css_border_color: Optional[str] = Field(None, description="Border color")
    css_graph_color: Optional[str] = Field(None, description="Graph color")
    css_spinner_color: Optional[str] = Field(None, description="Spinner color")
    css_no_data: Optional[str] = Field(None, description="No data color")
    
    # Additional configuration
    hidden_from_search: Optional[bool] = Field(None, description="Hidden from search engines")
    viewers_must_be_team_members: Optional[bool] = Field(None, description="Restrict viewers to team members")
    ip_restrictions: Optional[str] = Field(None, description="IP restrictions")
    activity_score: Optional[int] = Field(None, description="Activity score")
    state: Optional[str] = Field(None, description="Page state")
    city: Optional[str] = Field(None, description="City location")
    country: Optional[str] = Field(None, description="Country location")
    
    # Email configuration
    notifications_from_email: Optional[str] = Field(None, description="From email for notifications")
    notifications_email_footer: Optional[str] = Field(None, description="Email footer for notifications")
    email_logo: Optional[str] = Field(None, description="Email logo URL")
    transactional_logo: Optional[str] = Field(None, description="Transactional email logo URL")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class PageList(BaseModel):
    """Model representing a list of pages from Pingera API."""
    
    pages: List[Page] = Field(default_factory=list, description="List of monitored pages")
    total: Optional[int] = Field(None, description="Total number of pages")
    page: Optional[int] = Field(None, description="Current page number")
    per_page: Optional[int] = Field(None, description="Items per page")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class APIResponse(BaseModel):
    """Generic API response model."""
    
    success: bool = Field(True, description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(default_factory=list, description="List of errors")
