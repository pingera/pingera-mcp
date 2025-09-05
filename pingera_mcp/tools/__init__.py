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
    _get_check_statistics_logic,
    _list_check_jobs_logic,
    _get_check_job_details_logic,
    _get_unified_results_logic,
    _get_unified_statistics_logic,
    _execute_existing_check_logic,
    _get_on_demand_job_status_logic,
    _list_on_demand_checks_logic,
)
from .mcp_alerts import (
    _list_alerts_logic,
    _get_alert_details_logic,
    _get_alert_statistics_logic,
    _list_alert_channels_logic,
    _list_alert_rules_logic,
    _create_alert_logic,
    _update_alert_logic,
    _delete_alert_logic,
)
from .mcp_check_groups import (
    _list_check_groups_logic,
    _get_check_group_details_logic,
    _get_checks_in_group_logic,
)
from .mcp_heartbeats import (
    _list_heartbeats_logic,
    _get_heartbeat_details_logic,
    _create_heartbeat_logic,
    _update_heartbeat_logic,
    _delete_heartbeat_logic,
    _send_heartbeat_ping_logic,
    _get_heartbeat_logs_logic,
)
from .mcp_incidents import (
    _list_incidents_logic,
    _get_incident_details_logic,
    _get_incident_updates_logic,
    _get_incident_update_details_logic,
    _create_incident_logic,
    _patch_incident_logic,
    _delete_incident_logic,
    _add_incident_update_logic,
    _update_incident_update_logic,
    _delete_incident_update_logic,
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
    ("execute_custom_check", _execute_custom_check_logic),
    ("get_check_statistics", _get_check_statistics_logic),
    ("list_check_jobs", _list_check_jobs_logic),
    ("get_check_job_details", _get_check_job_details_logic),
    ("get_unified_results", _get_unified_results_logic),
    ("get_unified_statistics", _get_unified_statistics_logic),
    ("execute_existing_check", _execute_existing_check_logic),
    ("get_on_demand_job_status", _get_on_demand_job_status_logic),
    ("list_on_demand_checks", _list_on_demand_checks_logic),
    ("list_alerts", _list_alerts_logic),
    ("get_alert_details", _get_alert_details_logic),
    ("get_alert_statistics", _get_alert_statistics_logic),
    ("list_alert_channels", _list_alert_channels_logic),
    ("list_alert_rules", _list_alert_rules_logic),
    ("list_check_groups", _list_check_groups_logic),
    ("get_check_group_details", _get_check_group_details_logic),
    ("get_checks_in_group", _get_checks_in_group_logic),
    ("list_heartbeats", _list_heartbeats_logic),
    ("get_heartbeat_details", _get_heartbeat_details_logic),
    ("send_heartbeat_ping", _send_heartbeat_ping_logic),
    ("get_heartbeat_logs", _get_heartbeat_logs_logic),
    ("list_incidents", _list_incidents_logic),
    ("get_incident_details", _get_incident_details_logic),
    ("get_incident_updates", _get_incident_updates_logic),
    ("get_incident_update_details", _get_incident_update_details_logic),
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
    ("create_alert", _create_alert_logic),
    ("update_alert", _update_alert_logic),
    ("delete_alert", _delete_alert_logic),
    ("create_heartbeat", _create_heartbeat_logic),
    ("update_heartbeat", _update_heartbeat_logic),
    ("delete_heartbeat", _delete_heartbeat_logic),
    ("create_incident", _create_incident_logic),
    ("patch_incident", _patch_incident_logic),
    ("delete_incident", _delete_incident_logic),
    ("add_incident_update", _add_incident_update_logic),
    ("update_incident_update", _update_incident_update_logic),
    ("delete_incident_update", _delete_incident_update_logic),
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