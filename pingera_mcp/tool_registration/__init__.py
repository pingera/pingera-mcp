
"""
Tool registration functions for MCP server.

This package contains registration functions for all MCP tools,
organized by domain (pages, checks, components, etc.).
"""

from .pages import register_pages_tools
from .components import register_components_tools
from .checks import register_checks_tools

__all__ = [
    'register_pages_tools',
    'register_components_tools',
    'register_checks_tools',
]
