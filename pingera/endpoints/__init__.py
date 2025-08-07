
"""
Pingera API endpoints package.
"""

from .pages import PagesEndpoint
from .checks import ChecksEndpoint
from .on_demand import OnDemandEndpoint

__all__ = [
    "PagesEndpoint",
    "ChecksEndpoint", 
    "OnDemandEndpoint",
]
