
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
from .mcp_checks import (
    _list_checks_logic,
    _get_check_details_logic,
    _get_check_results_logic,
    _execute_custom_check_logic,
    _create_check_logic,
    _delete_check_logic,
)
from .mcp_check_groups import (
    _list_check_groups_logic,
    _get_check_group_details_logic,
    _get_checks_in_group_logic,
)
from .mcp_incidents import (
    _list_incidents_logic,
    _create_incident_logic,
    _patch_incident_logic,
    _delete_incident_logic,
)
from .mcp_playwright import (
    _generate_synthetic_check_script_logic,
    _generate_api_check_script_logic,
)

# Define the registry for read-only tools
READ_ONLY_TOOLS = [
    ("test_pingera_connection", _test_connection_logic),
    ("list_pages", _list_pages_logic),
    ("get_page_details", _get_page_details_logic),
    ("list_component_groups", _list_component_groups_logic),
    ("list_components", _list_components_logic),
    ("get_component_details", _get_component_details_logic),
    ("list_checks", _list_checks_logic),
    ("get_check_details", _get_check_details_logic),
    ("get_check_results", _get_check_results_logic),
    ("list_check_groups", _list_check_groups_logic),
    ("get_check_group_details", _get_check_group_details_logic),
    ("get_checks_in_group", _get_checks_in_group_logic),
    ("list_incidents", _list_incidents_logic),
    ("generate_synthetic_check_script", _generate_synthetic_check_script_logic),
    ("generate_api_check_script", _generate_api_check_script_logic),
]

# Define the registry for write tools
WRITE_TOOLS = [
    ("create_page", _create_page_logic),
    ("patch_page", _patch_page_logic),
    ("delete_page", _delete_page_logic),
    ("create_component", _create_component_logic),
    ("patch_component", _patch_component_logic),
    ("delete_component", _delete_component_logic),
    ("create_check", _create_check_logic),
    ("delete_check", _delete_check_logic),
    ("create_incident", _create_incident_logic),
    ("patch_incident", _patch_incident_logic),
    ("delete_incident", _delete_incident_logic),
    ("execute_custom_check", _execute_custom_check_logic),
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
