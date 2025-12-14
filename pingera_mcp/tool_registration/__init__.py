
"""
Tool registration functions for MCP server.

This package contains registration functions for all MCP tools,
organized by domain (pages, checks, components, etc.).
"""

from .pages import register_pages_tools
from .components import register_components_tools
from .checks import register_checks_tools
from .alerts import register_alerts_tools
from .heartbeats import register_heartbeats_tools
from .incidents import register_incidents_tools
from .check_groups import register_check_groups_tools

__all__ = [
    'register_pages_tools',
    'register_components_tools',
    'register_checks_tools',
    'register_alerts_tools',
    'register_heartbeats_tools',
    'register_incidents_tools',
    'register_check_groups_tools',
]
