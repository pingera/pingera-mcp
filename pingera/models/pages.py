
"""
Pydantic models for pages.
"""
from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class Page(BaseModel):
    """Model representing a monitored page in Pingera."""
    
    # Required fields
    name: str = Field(..., min_length=1, max_length=100, description="Display name of the status page")
    
    # Read-only fields
    id: Optional[str] = Field(None, description="Unique identifier for the status page")
    created_at: Optional[str] = Field(None, description="Timestamp when the page was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when the page was last updated")
    organization_id: Optional[str] = Field(None, description="ID of the organization this page belongs to")
    template: Optional[str] = Field(None, description="Name of the template used for this page")
    
    # Core configuration
    subdomain: Optional[str] = Field(None, max_length=100, description="Subdomain for accessing the status page (e.g., 'mycompany' for mycompany.pingera.ru)")
    domain: Optional[str] = Field(None, max_length=100, description="Custom domain for the status page")
    url: Optional[str] = Field(None, max_length=200, description="Company URL - users will be redirected there when clicking on the logo")
    language: Optional[Literal["ru", "en"]] = Field(None, description="Language for the status page interface")
    time_zone: Optional[str] = Field(None, description="Timezone for displaying dates and times on the status page")
    template_id: Optional[str] = Field(None, max_length=12, description="ID of the template used for this page")
    
    # Location information
    city: Optional[str] = Field(None, max_length=100, description="City where your organization is located")
    state: Optional[str] = Field(None, max_length=100, description="State/region where your organization is located")
    country: Optional[str] = Field(None, max_length=100, description="Country where your organization is located")
    
    # Page content and branding
    page_description: Optional[str] = Field(None, description="Brief description of what this status page monitors")
    headline: Optional[str] = Field(None, max_length=200, description="Headline text displayed on the status page")
    company_logo: Optional[str] = Field(None, max_length=200, description="URL to the company logo")
    favicon_logo: Optional[str] = Field(None, max_length=200, description="URL to the favicon image")
    hero_cover: Optional[str] = Field(None, max_length=200, description="URL to the hero cover image")
    support_url: Optional[str] = Field(None, max_length=200, description="URL to your support or contact page")
    
    # Access control
    viewers_must_be_team_members: Optional[bool] = Field(None, description="Whether only team members can view this page. In other words if page is public or not.")
    hidden_from_search: Optional[bool] = Field(None, description="Whether to hide this page from search engines")
    ip_restrictions: Optional[str] = Field(None, max_length=200, description="IP address restrictions for viewing the page")
    activity_score: Optional[int] = Field(None, description="Internal activity score for the page")
    
    # Subscription settings
    allow_email_subscribers: Optional[bool] = Field(None, description="Whether to allow email subscriptions")
    allow_sms_subscribers: Optional[bool] = Field(None, description="Whether to allow SMS subscriptions")
    allow_webhook_subscribers: Optional[bool] = Field(None, description="Whether to allow webhook subscriptions")
    allow_rss_atom_feeds: Optional[bool] = Field(None, description="Whether to provide RSS/Atom feeds")
    allow_page_subscribers: Optional[bool] = Field(None, description="Whether to allow users to subscribe to page updates")
    allow_incident_subscribers: Optional[bool] = Field(None, description="Whether to allow users to subscribe to incident updates")
    
    # Email configuration
    notifications_from_email: Optional[str] = Field(None, max_length=100, description="Email address used as sender for notifications")
    notifications_email_footer: Optional[str] = Field(None, description="Footer text included in notification emails")
    email_logo: Optional[str] = Field(None, max_length=200, description="URL to the logo used in email notifications")
    transactional_logo: Optional[str] = Field(None, max_length=200, description="URL to the logo used in transactional emails")
    
    # CSS styling (HEX color format)
    css_body_background_color: Optional[str] = Field(None, description="Background color for the page body in HEX format")
    css_font_color: Optional[str] = Field(None, description="Primary font color in HEX format")
    css_light_font_color: Optional[str] = Field(None, description="Light font color for secondary text in HEX format")
    css_link_color: Optional[str] = Field(None, description="Color for links in HEX format")
    css_button_color: Optional[str] = Field(None, description="Button background color in HEX format")
    css_button_hover_color: Optional[str] = Field(None, description="Button color on hover in HEX format")
    css_button_border_color: Optional[str] = Field(None, description="Button border color in HEX format")
    css_button_text_color: Optional[str] = Field(None, description="Button text color in HEX format")
    css_greens: Optional[str] = Field(None, description="Green color used for operational status in HEX format")
    css_reds: Optional[str] = Field(None, description="Red color used for major outage status in HEX format")
    css_yellows: Optional[str] = Field(None, description="Yellow color used for degraded status in HEX format")
    css_blues: Optional[str] = Field(None, description="Blue color used for maintenance status in HEX format") 
    css_oranges: Optional[str] = Field(None, description="Orange color used for partial outage status in HEX format")
    css_border_color: Optional[str] = Field(None, description="Border color for page elements in HEX format")
    css_graph_color: Optional[str] = Field(None, description="Color used for graphs and charts in HEX format")
    css_spinner_color: Optional[str] = Field(None, description="Loading spinner color in HEX format")
    css_no_data: Optional[str] = Field(None, description="Color used when no data is available in HEX format")
    
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
