"""
MCP Server implementation for Pingera monitoring service.
"""
import logging
from typing import Optional, List

from mcp.server.fastmcp import FastMCP

from config import Config
from pingera_mcp import PingeraClient
from pingera_mcp.tools import PagesTools, StatusTools, ComponentTools, ChecksTools, AlertsTools, HeartbeatsTools, IncidentsTools
from pingera_mcp.resources import PagesResources, StatusResources, ComponentResources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pingera-mcp-server")

# Load configuration
config = Config()

# Validate API key
if not config.api_key:
    logger.error("PINGERA_API_KEY environment variable is required")
    raise ValueError("PINGERA_API_KEY is required")

logger.info(f"Starting Pingera MCP Server in {config.mode} mode")

# Create MCP server
mcp = FastMCP(config.server_name)

# Initialize Pingera client
pingera_client = PingeraClient(
    api_key=config.api_key,
    base_url=config.base_url,
    timeout=config.timeout,
    max_retries=config.max_retries
)
logger.info("Using Pingera SDK client")

# Initialize tool and resource handlers
pages_tools = PagesTools(pingera_client)
status_tools = StatusTools(pingera_client)
component_tools = ComponentTools(pingera_client)
checks_tools = ChecksTools(pingera_client)
alerts_tools = AlertsTools(pingera_client)
heartbeats_tools = HeartbeatsTools(pingera_client)
incidents_tools = IncidentsTools(pingera_client)
pages_resources = PagesResources(pingera_client)
status_resources = StatusResources(pingera_client, config)
component_resources = ComponentResources(pingera_client)

# Register resources
@mcp.resource("pingera://pages")
async def get_pages_resource() -> str:
    return await pages_resources.get_pages_resource()

@mcp.resource("pingera://pages/{page_id}")
async def get_page_resource(page_id: str) -> str:
    return await pages_resources.get_page_resource(page_id)

@mcp.resource("pingera://status")
async def get_status_resource() -> str:
    return await status_resources.get_status_resource()

# Register read-only tools
@mcp.tool()
async def list_pages(
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    return await pages_tools.list_pages(page, per_page, status)

@mcp.tool()
async def get_page_details(page_id: int) -> str:
    return await pages_tools.get_page_details(page_id)

@mcp.tool()
async def test_pingera_connection() -> str:
    return await status_tools.test_pingera_connection()

@mcp.tool()
async def list_component_groups(
    page_id: str,
    show_deleted: Optional[bool] = False
) -> str:
    return await component_tools.list_component_groups(page_id, show_deleted)

@mcp.tool()
async def get_component_details(page_id: str, component_id: str) -> str:
    return await component_tools.get_component_details(page_id, component_id)

@mcp.tool()
async def list_checks(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    check_type: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    return await checks_tools.list_checks(page, page_size, check_type, status)

@mcp.tool()
async def get_check_details(check_id: str) -> str:
    return await checks_tools.get_check_details(check_id)

@mcp.tool()
async def get_check_results(
    check_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    return await checks_tools.get_check_results(check_id, from_date, to_date, page, page_size)

@mcp.tool()
async def get_check_statistics(check_id: str) -> str:
    return await checks_tools.get_check_statistics(check_id)

@mcp.tool()
async def list_check_jobs() -> str:
    return await checks_tools.list_check_jobs()

@mcp.tool()
async def get_check_job_details(job_id: str) -> str:
    return await checks_tools.get_check_job_details(job_id)

@mcp.tool()
async def get_unified_results(
    check_ids: Optional[List[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    status: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    return await checks_tools.get_unified_results(check_ids, from_date, to_date, status, page, page_size)

@mcp.tool()
async def get_unified_statistics(
    check_ids: Optional[List[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> str:
    return await checks_tools.get_unified_statistics(check_ids, from_date, to_date)

@mcp.tool()
async def execute_custom_check(
    url: str,
    check_type: str = "web",
    timeout: Optional[int] = 30,
    name: Optional[str] = None,
    parameters: Optional[dict] = None
) -> str:
    return await checks_tools.execute_custom_check(url, check_type, timeout, name, parameters)

@mcp.tool()
async def execute_existing_check(check_id: str) -> str:
    return await checks_tools.execute_existing_check(check_id)

@mcp.tool()
async def get_on_demand_job_status(job_id: str) -> str:
    return await checks_tools.get_on_demand_job_status(job_id)

@mcp.tool()
async def list_on_demand_checks(
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    return await checks_tools.list_on_demand_checks(page, page_size)

@mcp.tool()
async def list_alerts(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    return await alerts_tools.list_alerts(page, page_size, status)

@mcp.tool()
async def get_alert_details(alert_id: str) -> str:
    return await alerts_tools.get_alert_details(alert_id)

@mcp.tool()
async def get_alert_statistics() -> str:
    return await alerts_tools.get_alert_statistics()

@mcp.tool()
async def list_alert_channels() -> str:
    return await alerts_tools.list_alert_channels()

@mcp.tool()
async def list_alert_rules() -> str:
    return await alerts_tools.list_alert_rules()

# Register heartbeat tools
@mcp.tool()
async def list_heartbeats(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    return await heartbeats_tools.list_heartbeats(page, page_size, status)

@mcp.tool()
async def get_heartbeat_details(heartbeat_id: str) -> str:
    return await heartbeats_tools.get_heartbeat_details(heartbeat_id)

@mcp.tool()
async def create_heartbeat(heartbeat_data: dict) -> str:
    return await heartbeats_tools.create_heartbeat(heartbeat_data)

@mcp.tool()
async def update_heartbeat(heartbeat_id: str, heartbeat_data: dict) -> str:
    return await heartbeats_tools.update_heartbeat(heartbeat_id, heartbeat_data)

@mcp.tool()
async def delete_heartbeat(heartbeat_id: str) -> str:
    return await heartbeats_tools.delete_heartbeat(heartbeat_id)

@mcp.tool()
async def send_heartbeat_ping(heartbeat_id: str) -> str:
    return await heartbeats_tools.send_heartbeat_ping(heartbeat_id)

@mcp.tool()
async def get_heartbeat_logs(
    heartbeat_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    return await heartbeats_tools.get_heartbeat_logs(heartbeat_id, from_date, to_date, page, page_size)

@mcp.tool()
async def list_incidents(
    page_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    return await incidents_tools.list_incidents(page_id, page, page_size, status)

@mcp.tool()
async def get_incident_details(page_id: str, incident_id: str) -> str:
    return await incidents_tools.get_incident_details(page_id, incident_id)

@mcp.tool()
async def get_incident_updates(page_id: str, incident_id: str) -> str:
    return await incidents_tools.get_incident_updates(page_id, incident_id)

@mcp.tool()
async def get_incident_update_details(page_id: str, incident_id: str, update_id: str) -> str:
    return await incidents_tools.get_incident_update_details(page_id, incident_id, update_id)


# Register write tools only if in read-write mode
if config.is_read_write():
    logger.info("Read-write mode enabled - adding write operations")

    @mcp.tool()
    async def create_page(
        name: str,
        subdomain: Optional[str] = None,
        domain: Optional[str] = None,
        url: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> str:
        return await pages_tools.create_page(name, subdomain, domain, url, language, **kwargs)

    @mcp.tool()
    async def update_page(
        page_id: str,
        name: Optional[str] = None,
        subdomain: Optional[str] = None,
        domain: Optional[str] = None,
        url: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> str:
        return await pages_tools.update_page(page_id, name, subdomain, domain, url, language, **kwargs)

    @mcp.tool()
    async def patch_page(page_id: str, **kwargs) -> str:
        return await pages_tools.patch_page(page_id, **kwargs)

    @mcp.tool()
    async def delete_page(page_id: str) -> str:
        return await pages_tools.delete_page(page_id)

    @mcp.tool()
    async def create_component(
        page_id: str,
        name: str,
        description: Optional[str] = None,
        group: Optional[bool] = False,
        group_id: Optional[str] = None,
        only_show_if_degraded: Optional[bool] = None,
        position: Optional[int] = None,
        showcase: Optional[bool] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> str:
        return await component_tools.create_component(
            page_id, name, description, group, group_id, 
            only_show_if_degraded, position, showcase, status, **kwargs
        )

    @mcp.tool()
    async def update_component(
        page_id: str,
        component_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        group: Optional[bool] = None,
        group_id: Optional[str] = None,
        only_show_if_degraded: Optional[bool] = None,
        position: Optional[int] = None,
        showcase: Optional[bool] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> str:
        return await component_tools.update_component(
            page_id, component_id, name, description, group, group_id,
            only_show_if_degraded, position, showcase, status, **kwargs
        )

    @mcp.tool()
    async def patch_component(page_id: str, component_id: str, **kwargs) -> str:
        return await component_tools.patch_component(page_id, component_id, **kwargs)

    @mcp.tool()
    async def delete_component(page_id: str, component_id: str) -> str:
        return await component_tools.delete_component(page_id, component_id)

    @mcp.tool()
    async def create_check(check_data: dict) -> str:
        return await checks_tools.create_check(check_data)

    @mcp.tool()
    async def update_check(check_id: str, check_data: dict) -> str:
        return await checks_tools.update_check(check_id, check_data)

    @mcp.tool()
    async def delete_check(check_id: str) -> str:
        return await checks_tools.delete_check(check_id)

    @mcp.tool()
    async def pause_check(check_id: str) -> str:
        return await checks_tools.pause_check(check_id)

    @mcp.tool()
    async def resume_check(check_id: str) -> str:
        return await checks_tools.resume_check(check_id)

    @mcp.tool()
    async def create_alert(alert_data: dict) -> str:
        return await alerts_tools.create_alert(alert_data)

    @mcp.tool()
    async def update_alert(alert_id: str, alert_data: dict) -> str:
        return await alerts_tools.update_alert(alert_id, alert_data)

    @mcp.tool()
    async def delete_alert(alert_id: str) -> str:
        return await alerts_tools.delete_alert(alert_id)

    @mcp.tool()
    async def create_incident(page_id: str, incident_data: dict) -> str:
        return await incidents_tools.create_incident(page_id, incident_data)

    @mcp.tool()
    async def update_incident(page_id: str, incident_id: str, incident_data: dict) -> str:
        return await incidents_tools.update_incident(page_id, incident_id, incident_data)

    @mcp.tool()
    async def delete_incident(page_id: str, incident_id: str) -> str:
        return await incidents_tools.delete_incident(page_id, incident_id)

    @mcp.tool()
    async def add_incident_update(page_id: str, incident_id: str, update_data: dict) -> str:
        return await incidents_tools.add_incident_update(page_id, incident_id, update_data)

    @mcp.tool()
    async def update_incident_update(page_id: str, incident_id: str, update_id: str, update_data: dict) -> str:
        return await incidents_tools.update_incident_update(page_id, incident_id, update_id, update_data)

    @mcp.tool()
    async def delete_incident_update(page_id: str, incident_id: str, update_id: str) -> str:
        return await incidents_tools.delete_incident_update(page_id, incident_id, update_id)