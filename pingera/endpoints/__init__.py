"""
API endpoints for Pingera client.
"""

from .pages import PagesEndpoint
from .components import ComponentEndpoints

__all__ = [
    "PagesEndpoint",
    "ComponentEndpoints",
]