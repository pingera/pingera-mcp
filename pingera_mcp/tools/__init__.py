
"""
MCP tools for Pingera monitoring service.
This module serves as the central registry for all MCP tools.
"""

from .status import StatusTools
from .pages import PagesTools
from .components import ComponentTools
from .checks import ChecksTools
from .check_groups import CheckGroupsTools
from .alerts import AlertsTools
from .heartbeats import HeartbeatsTools
from .incidents import IncidentsTools
from .playwright_generator import PlaywrightGeneratorTools

# Import MCP tool logic functions
from .mcp_status import _test_connection_logic
from .mcp_pages import (
    _list_pages_logic,
    _get_page_details_logic,
    _create_page_logic,
    _patch_page_logic,
    _delete_page_logic,
)
from .mcp_components import (
    _list_component_groups_logic,
    _list_components_logic,
    _get_component_details_logic,
    _create_component_logic,
    _patch_component_logic,
    _delete_component_logic,
)

# Define the registry for read-only tools
READ_ONLY_TOOLS = [
    ("test_pingera_connection", _test_connection_logic),
    ("list_pages", _list_pages_logic),
    ("get_page_details", _get_page_details_logic),
    ("list_component_groups", _list_component_groups_logic),
    ("list_components", _list_components_logic),
    ("get_component_details", _get_component_details_logic),
]

# Define the registry for write tools
WRITE_TOOLS = [
    ("create_page", _create_page_logic),
    ("patch_page", _patch_page_logic),
    ("delete_page", _delete_page_logic),
    ("create_component", _create_component_logic),
    ("patch_component", _patch_component_logic),
    ("delete_component", _delete_component_logic),
]

# Combined registry for convenience
ALL_TOOLS = READ_ONLY_TOOLS + WRITE_TOOLS

__all__ = [
    "StatusTools",
    "PagesTools", 
    "ComponentTools",
    "ChecksTools",
    "CheckGroupsTools",
    "AlertsTools",
    "HeartbeatsTools",
    "IncidentsTools",
    "PlaywrightGeneratorTools",
    "READ_ONLY_TOOLS",
    "WRITE_TOOLS",
    "ALL_TOOLS",
]
