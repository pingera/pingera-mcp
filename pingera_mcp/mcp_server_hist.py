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
async def execute_custom_check(
    type: str,
    name: str,
    url: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    timeout: Optional[int] = 30,
    parameters: Optional[dict] = None
) -> str:
    """
    Execute a one-time custom monitoring check on any URL or service.

    This allows you to test connectivity and performance to any endpoint
    without creating a permanent monitoring check. Useful for troubleshooting
    or testing new services before setting up regular monitoring.

    Args:
        type: Type of check ('web', 'api', 'tcp', 'ssl', 'multistep', 'synthetic') - REQUIRED
        name: A user-friendly name for the custom check (max 100 characters) - REQUIRED
        url: The URL to monitor (required for web/api checks). Supports international domain names.
        host: The hostname or IP address to monitor (required for TCP/SSL checks, max 255 characters)
        port: The port number to monitor (required for TCP/SSL checks, range: 1-65535)
        timeout: Timeout in seconds (range: 1-30, default: 30)
        parameters: Additional parameters specific to the check type.

        For 'synthetic' or 'multistep' checks, the 'parameters' dictionary must contain a 'pw_script' key. The value of this key should be the full Playwright script in Javascript or Typescript content as a string.

        Example for a 'synthetic' check:
        {
          "type": "synthetic",
          "name": "Login Test",
          "url": "https://pingera.ru",
          "parameters": {
            "pw_script": "Playwright script content as a string"
          }
        }

        Example for a 'tcp' check:
        {
          "type": "tcp",
          "name": "Database Connection",
          "host": "db.example.com",
          "port": 5432
        }

    Returns:
        JSON with the job id that is executed asynchronously.
    """
    return await checks_tools.execute_custom_check(type, name, url, host, port, timeout, parameters)

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

@mcp.tool()
async def list_on_demand_checks(
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """
    List on-demand checks.

    Args:
        page: Page number for pagination
        page_size: Number of items per page

    Returns:
        JSON string containing on-demand checks data
    """
    return await checks_tools.list_on_demand_checks(page, page_size)


@mcp.tool()
async def list_alerts(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """
    List all alert configurations in your account.

    Alerts are rules that trigger notifications when monitoring checks fail
    or meet specific conditions. Each alert can be configured with different
    channels, thresholds, and escalation rules.

    Args:
        page: Page number for pagination
        page_size: Number of alerts per page
        status: Filter by alert status ('active', 'paused', 'disabled')

    Returns:
        JSON with list of alerts including names, conditions, notification channels, and status.
    """
    return await alerts_tools.list_alerts(page, page_size, status)

@mcp.tool()
async def get_alert_details(alert_id: str) -> str:
    """
    Get detailed configuration for a specific alert rule.

    Shows complete alert setup including trigger conditions, notification
    channels, escalation rules, and recent activity.

    Args:
        alert_id: The unique identifier of the alert rule

    Returns:
        JSON with alert details including conditions, channels, thresholds, and escalation settings.
    """
    return await alerts_tools.get_alert_details(alert_id)

@mcp.tool()
async def get_alert_statistics() -> str:
    """
    Get statistical overview of all alert activity.

    Provides summary of alert triggers, resolution times, most frequently
    triggered alerts, and overall notification volume.

    Returns:
        JSON with alert statistics including trigger counts, avg resolution time, and trends.
    """
    return await alerts_tools.get_alert_statistics()

@mcp.tool()
async def list_alert_channels() -> str:
    """
    List all configured notification channels for alerts.

    Shows available notification methods like email, SMS, webhooks,
    and their configuration status. These channels are used by alert rules
    to deliver notifications when issues are detected.

    Returns:
        JSON with list of notification channels including types, names, and status.
    """
    return await alerts_tools.list_alert_channels()

@mcp.tool()
async def list_alert_rules() -> str:
    """
    List all alert rules and their trigger conditions.

    Shows the specific conditions and thresholds that will trigger each alert,
    including response time thresholds, uptime requirements, and error conditions.

    Returns:
        JSON with list of alert rules including conditions, thresholds, and linked checks.
    """
    return await alerts_tools.list_alert_rules()

# Register heartbeat tools
@mcp.tool()
async def list_heartbeats(
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """
    List all heartbeat monitors in your account.

    Heartbeats monitor cron jobs, scheduled tasks, and background processes
    by expecting regular "ping" signals. If a ping is missed, it indicates
    the monitored process may have failed or stopped running.

    Args:
        page: Page number for pagination
        page_size: Number of heartbeats per page
        status: Filter by status ('active', 'inactive', 'grace_period', 'down')

    Returns:
        JSON with list of heartbeats including names, URLs, intervals, and last ping times.
    """
    return await heartbeats_tools.list_heartbeats(page, page_size, status)

@mcp.tool()
async def get_heartbeat_details(heartbeat_id: str) -> str:
    """
    Get detailed information about a specific heartbeat monitor.

    Shows configuration, recent activity, ping history, and current status
    for monitoring cron jobs and scheduled tasks.

    Args:
        heartbeat_id: The unique identifier of the heartbeat monitor

    Returns:
        JSON with heartbeat details including schedule, grace period, last ping, and history.
    """
    return await heartbeats_tools.get_heartbeat_details(heartbeat_id)

@mcp.tool()
async def create_heartbeat(heartbeat_data: dict) -> str:
    """
    Create a new heartbeat monitor for cron jobs or scheduled tasks.

    Set up monitoring for background processes by creating a heartbeat that
    expects regular ping signals. Configure the expected interval and grace period.

    Args:
        heartbeat_data: Dictionary with heartbeat configuration (name, interval, grace_period, etc.)

    Returns:
        JSON with created heartbeat details including the unique ping URL to use in your scripts.
    """
    return await heartbeats_tools.create_heartbeat(heartbeat_data)

@mcp.tool()
async def update_heartbeat(heartbeat_id: str, heartbeat_data: dict) -> str:
    """
    Update configuration for an existing heartbeat monitor.

    Modify settings like expected interval, grace period, notification rules,
    or other heartbeat configuration parameters.

    Args:
        heartbeat_id: The unique identifier of the heartbeat to update
        heartbeat_data: Dictionary with updated heartbeat configuration

    Returns:
        JSON with updated heartbeat details and configuration.
    """
    return await heartbeats_tools.update_heartbeat(heartbeat_id, heartbeat_data)

@mcp.tool()
async def delete_heartbeat(heartbeat_id: str) -> str:
    """
    Delete a heartbeat monitor permanently.

    This will stop monitoring the associated cron job or scheduled task.
    The heartbeat ping URL will become inactive after deletion.

    Args:
        heartbeat_id: The unique identifier of the heartbeat to delete

    Returns:
        JSON confirming successful deletion.
    """
    return await heartbeats_tools.delete_heartbeat(heartbeat_id)

@mcp.tool()
async def send_heartbeat_ping(heartbeat_id: str) -> str:
    """
    Manually send a ping signal to a heartbeat monitor.

    This simulates a successful execution of the monitored process.
    Normally, your cron jobs or scripts would ping the heartbeat URL automatically.

    Args:
        heartbeat_id: The unique identifier of the heartbeat to ping

    Returns:
        JSON confirming the ping was received and recorded.
    """
    return await heartbeats_tools.send_heartbeat_ping(heartbeat_id)

@mcp.tool()
async def get_heartbeat_logs(
    heartbeat_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """
    Get historical ping logs and activity for a heartbeat monitor.

    Shows when pings were received, missed pings that triggered alerts,
    and the overall reliability pattern of the monitored process.

    Args:
        heartbeat_id: The unique identifier of the heartbeat
        from_date: Start date in ISO format for log retrieval
        to_date: End date in ISO format for log retrieval
        page: Page number for pagination
        page_size: Number of log entries per page

    Returns:
        JSON with ping history including timestamps, status, and any alert triggers.
    """
    return await heartbeats_tools.get_heartbeat_logs(heartbeat_id, from_date, to_date, page, page_size)



@mcp.tool()
async def get_incident_details(page_id: str, incident_id: str) -> str:
    """
    Get detailed information about a specific incident.

    Shows complete incident details including description, affected components,
    impact level, timeline, and all status updates posted during the incident.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident

    Returns:
        JSON with incident details including description, components, updates, and resolution timeline.
    """
    return await incidents_tools.get_incident_details(page_id, incident_id)

@mcp.tool()
async def get_incident_updates(page_id: str, incident_id: str) -> str:
    """
    Get all status updates posted during an incident.

    Shows chronological list of updates that were posted to keep users
    informed about the incident progress, investigation, and resolution.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident

    Returns:
        JSON with list of incident updates including timestamps, status changes, and messages.
    """
    return await incidents_tools.get_incident_updates(page_id, incident_id)

@mcp.tool()
async def get_incident_update_details(page_id: str, incident_id: str, update_id: str) -> str:
    """
    Get detailed information about a specific incident update.

    Shows the complete content of a specific status update that was posted
    during an incident, including the message, timestamp, and status change.

    Args:
        page_id: The ID of the status page
        incident_id: The unique identifier of the incident
        update_id: The unique identifier of the specific update

    Returns:
        JSON with update details including message content, timestamp, and status information.
    """
    return await incidents_tools.get_incident_update_details(page_id, incident_id, update_id)


# Register write tools only if in read-write mode
if config.is_read_write():
    logger.info("Read-write mode enabled - adding write operations")

    

    @mcp.tool()
    async def update_page(
        page_id: str,
        name: Optional[str] = None,
        subdomain: Optional[str] = None,
        domain: Optional[str] = None,
        url: Optional[str] = None,
        language: Optional[str] = None,
        headline: Optional[str] = None,
        page_description: Optional[str] = None,
        time_zone: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        viewers_must_be_team_members: Optional[bool] = None,
        hidden_from_search: Optional[bool] = None,
        allow_page_subscribers: Optional[bool] = None,
        allow_incident_subscribers: Optional[bool] = None,
        allow_email_subscribers: Optional[bool] = None,
        allow_sms_subscribers: Optional[bool] = None,
        allow_webhook_subscribers: Optional[bool] = None,
        allow_rss_atom_feeds: Optional[bool] = None,
        support_url: Optional[str] = None,
    ) -> str:
        """
        FULL UPDATE: Replace all page configuration (PUT method). Requires many fields to be specified.

        WARNING: This is a full replacement operation. For simple changes like updating just the name, 
        use patch_page instead which is designed for partial updates.

        Args:
            page_id: The unique identifier of the page to update
            name: New name/title for the status page
            subdomain: New subdomain setting
            domain: New custom domain
            url: Updated company/service URL
            language: New language setting
            headline: Headline text displayed on the status page
            page_description: Brief description of what this status page monitors
            time_zone: Timezone for displaying dates and times on the status page
            country: Country where your organization is located
            city: City where your organization is located
            state: State/region where your organization is located
            viewers_must_be_team_members: Whether only team members can view this page
            hidden_from_search: Whether to hide this page from search engines
            allow_page_subscribers: Whether to allow users to subscribe to page updates
            allow_incident_subscribers: Whether to allow users to subscribe to incident updates
            allow_email_subscribers: Whether to allow email subscriptions
            allow_sms_subscribers: Whether to allow SMS subscriptions
            allow_webhook_subscribers: Whether to allow webhook subscriptions
            allow_rss_atom_feeds: Whether to provide RSS/Atom feeds
            support_url: URL to your support or contact page

        Returns:
            JSON with updated page details and configuration.
        """
        return await pages_tools.update_page(
            page_id=page_id,
            name=name,
            subdomain=subdomain,
            domain=domain,
            url=url,
            language=language,
            headline=headline,
            page_description=page_description,
            time_zone=time_zone,
            country=country,
            city=city,
            state=state,
            viewers_must_be_team_members=viewers_must_be_team_members,
            hidden_from_search=hidden_from_search,
            allow_page_subscribers=allow_page_subscribers,
            allow_incident_subscribers=allow_incident_subscribers,
            allow_email_subscribers=allow_email_subscribers,
            allow_sms_subscribers=allow_sms_subscribers,
            allow_webhook_subscribers=allow_webhook_subscribers,
            allow_rss_atom_feeds=allow_rss_atom_feeds,
            support_url=support_url,
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
        """
        FULL UPDATE: Replace all component configuration (PUT method). Requires many fields to be specified.

        WARNING: This is a full replacement operation. For simple changes like updating just the name or status, 
        use patch_component instead which is designed for partial updates.

        Args:
            page_id: The ID of the status page
            component_id: The unique identifier of the component to update
            name: New display name
            description: Updated description
            group: Whether this should be a group or individual component
            group_id: New parent group ID
            only_show_if_degraded: Updated visibility setting
            position: New display position
            showcase: Whether to highlight prominently
            status: New status setting
            **kwargs: Additional configuration updates

        Returns:
            JSON with updated component details and configuration.
        """
        return await component_tools.update_component(
            page_id, component_id, name, description, group, group_id,
            only_show_if_degraded, position, showcase, status, **kwargs
        )

    


    @mcp.tool()
    async def update_check(
        check_id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        interval: Optional[int] = None,
        timeout: Optional[int] = None,
        active: Optional[bool] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Update configuration for an existing monitoring check.

        Modify check settings like its name, URL, interval, or active status.
        Only include the parameters you wish to change.

        Args:
            check_id: The unique identifier of the check to update. (Required)
            name: A new user-friendly name for the monitor check.
            url: The new URL to monitor.
            host: The new hostname or IP address.
            port: The new port number to monitor.
            interval: The new frequency of checks in seconds.
            timeout: The new request timeout in seconds.
            active: A new flag to set the check as active (true) or paused (false).
            parameters: New additional parameters. For synthetic or multistep checks, the 'parameters' dictionary must contain a 'pw_script' key. The value of this key should be the full Playwright script in Javascript or Typescript content as a string.

        Returns:
            A JSON object with the updated check details.
        """
        return await checks_tools.update_check(
            check_id=check_id,
            name=name,
            url=url,
            host=host,
            port=port,
            interval=interval,
            timeout=timeout,
            active=active,
            parameters=parameters,
        )

    

    @mcp.tool()
    async def pause_check(check_id: str) -> str:
        """
        Temporarily pause a monitoring check without deleting it.

        The check will stop running but all configuration and historical
        data will be preserved. Can be resumed later.

        Args:
            check_id: The unique identifier of the check to pause

        Returns:
            JSON confirming the check has been paused.
        """
        return await checks_tools.pause_check(check_id)

    @mcp.tool()
    async def resume_check(check_id: str) -> str:
        """
        Resume a previously paused monitoring check.

        The check will start running again at its configured interval
        with all previous settings intact.

        Args:
            check_id: The unique identifier of the check to resume

        Returns:
            JSON confirming the check has been resumed.
        """
        return await checks_tools.resume_check(check_id)

    @mcp.tool()
    async def create_alert(alert_data: dict) -> str:
        """
        Create a new alert rule to get notified when issues are detected.

        Set up notifications that will be sent when monitoring checks fail
        or meet specific conditions like response time thresholds.

        Args:
            alert_data: Dictionary with alert configuration including:
                - name: Alert rule name
                - check_ids: List of checks this alert applies to
                - conditions: Trigger conditions (failures, response time, etc.)
                - channels: Notification channels (email, SMS, webhook, etc.)
                - escalation: Escalation rules and delays

        Returns:
            JSON with created alert rule details and configuration.
        """
        return await alerts_tools.create_alert(alert_data)

    @mcp.tool()
    async def update_alert(alert_id: str, alert_data: dict) -> str:
        """
        Update configuration for an existing alert rule.

        Modify alert conditions, notification channels, escalation rules,
        or which checks the alert applies to.

        Args:
            alert_id: The unique identifier of the alert rule to update
            alert_data: Dictionary with updated alert configuration

        Returns:
            JSON with updated alert rule details and configuration.
        """
        return await alerts_tools.update_alert(alert_id, alert_data)

    @mcp.tool()
    async def delete_alert(alert_id: str) -> str:
        """
        Delete an alert rule permanently.

        This stops all notifications from this alert rule and removes
        the configuration. Historical alert activity may be preserved.

        Args:
            alert_id: The unique identifier of the alert rule to delete

        Returns:
            JSON confirming successful deletion.
        """
        return await alerts_tools.delete_alert(alert_id)

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


    