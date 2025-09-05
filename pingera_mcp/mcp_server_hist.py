"""
MCP Server implementation for Pingera monitoring service.
"""
import logging
import json
from typing import Optional, Dict, Any, List

from mcp.server.fastmcp import FastMCP

from .config import Config
from pingera_mcp import PingeraClient
from pingera_mcp.tools import (
        StatusTools,
        PagesTools,
        ComponentTools,
        ChecksTools,
        AlertsTools,
        HeartbeatsTools,
        IncidentsTools,
        PlaywrightGeneratorTools,
        CheckGroupsTools, # Import CheckGroupsTools
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pingera-mcp-server")

def create_mcp_server(config: Config) -> FastMCP:
    """Create and configure MCP server with the given configuration."""
    # Validate API key
    if not config.api_key:
        logger.error("PINGERA_API_KEY environment variable is required")
        raise ValueError("PINGERA_API_KEY is required")

    logger.info(f"Starting Pingera MCP Server in {config.mode} mode")

    # Create MCP server
    mcp_server = FastMCP(config.server_name)

    # Initialize Pingera client - moved here so tests can mock it
    pingera_client = PingeraClient(
        api_key=config.api_key,
        base_url=config.base_url,
        timeout=config.timeout,
        max_retries=config.max_retries
    )

    return mcp_server

# Load configuration
config = Config()

# Create MCP server
mcp = create_mcp_server(config)

# Initialize Pingera client (for module-level usage)
pingera_client = PingeraClient(
    api_key=config.api_key,
    base_url=config.base_url,
    timeout=config.timeout,
    max_retries=config.max_retries
)
logger.info("Using Pingera SDK client")

# Initialize tool instances
status_tools = StatusTools(pingera_client)
pages_tools = PagesTools(pingera_client)
component_tools = ComponentTools(pingera_client)
checks_tools = ChecksTools(pingera_client)
alerts_tools = AlertsTools(pingera_client)
heartbeats_tools = HeartbeatsTools(pingera_client)
incidents_tools = IncidentsTools(pingera_client)
playwright_tools = PlaywrightGeneratorTools(pingera_client)
check_groups_tools = CheckGroupsTools(pingera_client) # Initialize CheckGroupsTools



@mcp.tool()
async def get_check_statistics(check_id: str) -> str:
    """
    Get statistical summary and performance metrics for a monitoring check.

    Provides uptime percentage, average response time, total executions,
    and other key performance indicators for the check.

    Args:
        check_id: The unique identifier of the monitoring check

    Returns:
        JSON with statistics including uptime %, avg response time, success rate, and error counts.
    """
    return await checks_tools.get_check_statistics(check_id)

@mcp.tool()
async def list_check_jobs() -> str:
    """
    List all currently running or queued check execution jobs.

    Shows the status of scheduled and on-demand check executions,
    useful for monitoring the execution queue and identifying any stuck jobs.

    Returns:
        JSON with list of active jobs including job IDs, check IDs, status, and execution times.
    """
    return await checks_tools.list_check_jobs()

@mcp.tool()
async def get_check_job_details(job_id: str) -> str:
    """
    Get detailed information about a specific check execution job.

    Args:
        job_id: The unique identifier of the check job

    Returns:
        JSON with job details including execution status, start/end times, results, and any errors.
    """
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
    """
    Get combined results from multiple checks in a unified format.

    Useful for analyzing performance across multiple services or getting
    an overview of all your monitoring data in a single request.

    Args:
        check_ids: List of check IDs to include (if None, includes all checks)
        from_date: Start date in ISO format
        to_date: End date in ISO format
        status: Filter by result status ('success', 'failure', 'timeout')
        page: Page number for pagination
        page_size: Number of results per page

    Returns:
        JSON with unified results from multiple checks including timestamps and performance data.
    """
    return await checks_tools.get_unified_results(check_ids, from_date, to_date, status, page, page_size)

@mcp.tool()
async def get_unified_statistics(
    check_ids: Optional[List[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> str:
    """
    Get combined statistical summary across multiple monitoring checks.

    Provides aggregated uptime, performance metrics, and trends across
    your entire monitoring infrastructure or a subset of checks.

    Args:
        check_ids: List of check IDs to analyze (if None, includes all checks)
        from_date: Start date for statistics calculation
        to_date: End date for statistics calculation

    Returns:
        JSON with aggregated statistics including overall uptime, avg response times, and trends.
    """
    return await checks_tools.get_unified_statistics(check_ids, from_date, to_date)

@mcp.tool()
async def execute_existing_check(check_id: str) -> str:
    """
    Manually trigger an existing monitoring check to run immediately.

    Forces an immediate execution of a configured check, bypassing the normal
    scheduled interval. Useful for testing after configuration changes or
    getting fresh data on demand.

    Args:
        check_id: The unique identifier of the check to execute

    Returns:
        JSON with execution job details and immediate results if available.
    """
    return await checks_tools.execute_existing_check(check_id)

@mcp.tool()
async def get_on_demand_job_status(job_id: str) -> str:
    """
    Check the status and results of an on-demand check execution job.

    After triggering a manual check execution, use this to monitor the job
    progress and retrieve results once the execution completes.

    Args:
        job_id: The job ID returned from execute_existing_check or execute_custom_check

    Returns:
        JSON with job status, execution progress, and results if completed.
    """
    return await checks_tools.get_on_demand_job_status(job_id)







# Register write tools only if in read-write mode
if config.is_read_write():
    logger.info("Read-write mode enabled - adding write operations")

    
  

    

    

    @mcp.tool()
    async def create_incident(
        page_id: str,
        name: str,
        status: str,
        body: Optional[str] = None,
        impact: Optional[str] = None,
        deliver_notifications: Optional[bool] = True,
        components: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create a new incident on a status page to communicate issues to users.

        Post an incident when you need to inform users about service outages,
        maintenance, or other events affecting your services.

        Args:
            page_id: The ID of the status page to post the incident on
            name: The name/title of the incident (1-200 characters, required)
            status: Current status of the incident (required, e.g., 'investigating', 'identified', 'monitoring', 'resolved')
            body: The initial update body content for the incident
            impact: Impact level ('none', 'minor', 'major', 'critical')
            deliver_notifications: Whether to send notifications when creating this incident (default: True)
            components: A dictionary mapping component IDs to their status during incident creation

        Returns:
            JSON with created incident details including ID and public URL.
        """
        return await incidents_tools.create_incident(
            page_id=page_id,
            name=name,
            status=status,
            body=body,
            impact=impact,
            deliver_notifications=deliver_notifications,
            components=components
        )

    @mcp.tool()
    async def update_incident(
        page_id: str,
        incident_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        body: Optional[str] = None,
        impact: Optional[str] = None,
        deliver_notifications: Optional[bool] = None,
        components: Optional[Dict[str, str]] = None,
        auto_transition_to_maintenance_state: Optional[bool] = None,
        auto_transition_to_operational_state: Optional[bool] = None,
        auto_transition_deliver_notifications_at_start: Optional[bool] = None,
        auto_transition_deliver_notifications_at_end: Optional[bool] = None,
        scheduled_for: Optional[str] = None,
        scheduled_until: Optional[str] = None,
        scheduled_remind_prior: Optional[bool] = None,
        scheduled_auto_in_progress: Optional[bool] = None,
        scheduled_auto_completed: Optional[bool] = None,
        reminder_intervals: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        FULL UPDATE: Replace all incident configuration (PUT method). Requires many fields to be specified.

        WARNING: This is a full replacement operation. For simple changes like updating just the name or status, 
        use patch_incident instead which is designed for partial updates.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident
            name: The name/title of the incident
            status: The current status of the incident
            body: The main description/body content of the incident
            impact: The impact level of the incident
            deliver_notifications: Whether to send notifications when updating this incident
            components: Dictionary mapping component IDs to their status
            auto_transition_to_maintenance_state: Whether to auto transition components to maintenance
            auto_transition_to_operational_state: Whether to auto transition components to operational
            auto_transition_deliver_notifications_at_start: Whether to deliver notifications at start
            auto_transition_deliver_notifications_at_end: Whether to deliver notifications at end
            scheduled_for: For scheduled maintenance, when maintenance starts (ISO format)
            scheduled_until: For scheduled maintenance, when maintenance ends (ISO format)
            scheduled_remind_prior: Whether to send reminder notifications before scheduled maintenance
            scheduled_auto_in_progress: Whether scheduled maintenance should auto be marked in progress
            scheduled_auto_completed: Whether scheduled maintenance should auto be marked completed
            reminder_intervals: Intervals for reminder notifications
            metadata: Additional metadata associated with the incident

        Returns:
            JSON with updated incident details.
        """
        return await incidents_tools.update_incident(
            page_id=page_id,
            incident_id=incident_id,
            name=name,
            status=status,
            body=body,
            impact=impact,
            deliver_notifications=deliver_notifications,
            components=components,
            auto_transition_to_maintenance_state=auto_transition_to_maintenance_state,
            auto_transition_to_operational_state=auto_transition_to_operational_state,
            auto_transition_deliver_notifications_at_start=auto_transition_deliver_notifications_at_start,
            auto_transition_deliver_notifications_at_end=auto_transition_deliver_notifications_at_end,
            scheduled_for=scheduled_for,
            scheduled_until=scheduled_until,
            scheduled_remind_prior=scheduled_remind_prior,
            scheduled_auto_in_progress=scheduled_auto_in_progress,
            scheduled_auto_completed=scheduled_auto_completed,
            reminder_intervals=reminder_intervals,
            metadata=metadata
        )

    @mcp.tool()
    async def patch_incident(
        page_id: str,
        incident_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
        body: Optional[str] = None,
        impact: Optional[str] = None,
        deliver_notifications: Optional[bool] = None,
        components: Optional[Dict[str, str]] = None,
        auto_transition_to_maintenance_state: Optional[bool] = None,
        auto_transition_to_operational_state: Optional[bool] = None,
        auto_transition_deliver_notifications_at_start: Optional[bool] = None,
        auto_transition_deliver_notifications_at_end: Optional[bool] = None,
        scheduled_for: Optional[str] = None,
        scheduled_until: Optional[str] = None,
        scheduled_remind_prior: Optional[bool] = None,
        scheduled_auto_in_progress: Optional[bool] = None,
        scheduled_auto_completed: Optional[bool] = None,
        reminder_intervals: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        RECOMMENDED: Partially update specific fields of an incident (PATCH method).

        Use this for simple updates like changing the name, status, description, or other individual fields.
        Only the fields you specify will be updated, leaving other settings unchanged.
        This is the preferred method for most incident updates.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident
            name: The name/title of the incident
            status: The current status of the incident
            body: The main description/body content of the incident
            impact: The impact level of the incident
            deliver_notifications: Whether to send notifications when updating this incident
            components: Dictionary mapping component IDs to their status
            auto_transition_to_maintenance_state: Whether to auto transition components to maintenance
            auto_transition_to_operational_state: Whether to auto transition components to operational
            auto_transition_deliver_notifications_at_start: Whether to deliver notifications at start
            auto_transition_deliver_notifications_at_end: Whether to deliver notifications at end
            scheduled_for: For scheduled maintenance, when maintenance starts (ISO format)
            scheduled_until: For scheduled maintenance, when maintenance ends (ISO format)
            scheduled_remind_prior: Whether to send reminder notifications before scheduled maintenance
            scheduled_auto_in_progress: Whether scheduled maintenance should auto be marked in progress
            scheduled_auto_completed: Whether scheduled maintenance should auto be marked completed
            reminder_intervals: Intervals for reminder notifications
            metadata: Additional metadata associated with the incident

        Returns:
            JSON with updated incident configuration.
        """
        return await incidents_tools.patch_incident(
            page_id=page_id,
            incident_id=incident_id,
            name=name,
            status=status,
            body=body,
            impact=impact,
            deliver_notifications=deliver_notifications,
            components=components,
            auto_transition_to_maintenance_state=auto_transition_to_maintenance_state,
            auto_transition_to_operational_state=auto_transition_to_operational_state,
            auto_transition_deliver_notifications_at_start=auto_transition_deliver_notifications_at_start,
            auto_transition_deliver_notifications_at_end=auto_transition_deliver_notifications_at_end,
            scheduled_for=scheduled_for,
            scheduled_until=scheduled_until,
            scheduled_remind_prior=scheduled_remind_prior,
            scheduled_auto_in_progress=scheduled_auto_in_progress,
            scheduled_auto_completed=scheduled_auto_completed,
            reminder_intervals=reminder_intervals,
            metadata=metadata
        )

    @mcp.tool()
    async def delete_incident(page_id: str, incident_id: str) -> str:
        """
        Delete an incident from a status page permanently.

        This removes the incident and all its updates from the status page.
        Use with caution as this action cannot be undone.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident to delete

        Returns:
            JSON confirming successful deletion.
        """
        return await incidents_tools.delete_incident(page_id, incident_id)

    @mcp.tool()
    async def add_incident_update(page_id: str, incident_id: str, update_data: dict) -> str:
        """
        Add a new status update to an existing incident.

        Post updates to keep users informed about incident progress,
        investigation findings, or resolution steps.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident
            update_data: Dictionary with update details including:
                - body: The update message text
                - status: New incident status if changed
                - deliver_notifications: Whether to notify subscribers

        Returns:
            JSON with created update details including timestamp and content.
        """
        return await incidents_tools.add_incident_update(page_id, incident_id, update_data)

    @mcp.tool()
    async def update_incident_update(page_id: str, incident_id: str, update_id: str, update_data: dict) -> str:
        """
        Edit an existing incident status update.

        Modify the content or status of a previously posted incident update.
        Useful for correcting typos or adding additional information.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident
            update_id: The unique identifier of the update to modify
            update_data: Dictionary with updated content and settings

        Returns:
            JSON with updated incident update details.
        """
        return await incidents_tools.update_incident_update(page_id, incident_id, update_id, update_data)

    @mcp.tool()
    async def delete_incident_update(page_id: str, incident_id: str, update_id: str) -> str:
        """
        Delete a specific incident status update.

        Remove an incident update from the timeline. This action cannot
        be undone and may confuse users if the update was already public.

        Args:
            page_id: The ID of the status page
            incident_id: The unique identifier of the incident
            update_id: The unique identifier of the update to delete

        Returns:
            JSON confirming successful deletion.
        """
        return await incidents_tools.delete_incident_update(page_id, incident_id, update_id)

# Register Playwright script generation tools (always available)
@mcp.tool()
async def generate_synthetic_check_script(
    description: str,
    target_url: str,
    script_name: Optional[str] = None
) -> str:
    """
    Generate a Playwright script for synthetic browser monitoring.

    This tool creates a complete Playwright test script based on your description
    of what should be tested. The script will include proper error handling,
    screenshots, and basic validation.

    Args:
        description: Natural language description of what the test should do
        target_url: The URL to test
        script_name: Optional name for the test (auto-generated if not provided)

    Returns:
        JSON with the generated Playwright script and usage instructions
    """
    return await playwright_tools.generate_synthetic_check_script(
        description=description,
        target_url=target_url,
        script_name=script_name
    )

@mcp.tool()
async def generate_api_check_script(
    url: str,
    description: str,
    method: str = "GET",
    headers: Optional[dict] = None,
    payload: Optional[dict] = None,
    expected_status: Optional[int] = None,
    contains_string: Optional[str] = None,
    custom_code: Optional[str] = None
) -> str:
    """
    Generates a Playwright script for an API check.

    This tool creates automated API tests that can validate endpoint responses,
    check status codes, and verify response content. It supports various HTTP methods
    and allows for custom request payloads and response assertions.

    Args:
        url: The API endpoint URL to check.
        description: A clear description of the API endpoint and what it verifies.
        method: The HTTP method to use (e.g., GET, POST, PUT, DELETE) (default: GET).
        headers: A dictionary of HTTP headers to include in the request.
        payload: A dictionary representing the request body (for POST, PUT, etc.).
        expected_status: The expected HTTP status code for the response.
        contains_string: A string that is expected to be present in the response body.
        custom_code: A string containing custom JavaScript code to execute for more complex assertions.

    Returns:
        A string containing the generated Playwright script in TypeScript.
    """
    return await playwright_tools.generate_api_check_script(
        url=url,
        description=description,
        method=method,
        headers=headers,
        payload=payload,
        expected_status=expected_status,
        contains_string=contains_string,
        custom_code=custom_code
    )
    