"""
MCP logic functions for alert management.
"""
from typing import Optional

from pingera_mcp import PingeraClient
from pingera_mcp.tools import AlertsTools


async def _list_alerts_logic(
    client: PingeraClient,
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
    tools = AlertsTools(client)
    return await tools.list_alerts(page, page_size, status)


async def _get_alert_details_logic(client: PingeraClient, alert_id: str) -> str:
    """
    Get detailed configuration for a specific alert rule.

    Shows complete alert setup including trigger conditions, notification
    channels, escalation rules, and recent activity.

    Args:
        alert_id: The unique identifier of the alert rule

    Returns:
        JSON with alert details including conditions, channels, thresholds, and escalation settings.
    """
    tools = AlertsTools(client)
    return await tools.get_alert_details(alert_id)


async def _get_alert_statistics_logic(client: PingeraClient) -> str:
    """
    Get statistical overview of all alert activity.

    Provides summary of alert triggers, resolution times, most frequently
    triggered alerts, and overall notification volume.

    Returns:
        JSON with alert statistics including trigger counts, avg resolution time, and trends.
    """
    tools = AlertsTools(client)
    return await tools.get_alert_statistics()


async def _list_alert_channels_logic(client: PingeraClient) -> str:
    """
    List all configured notification channels for alerts.

    Shows available notification methods like email, SMS, webhooks,
    and their configuration status. These channels are used by alert rules
    to deliver notifications when issues are detected.

    Returns:
        JSON with list of notification channels including types, names, and status.
    """
    tools = AlertsTools(client)
    return await tools.list_alert_channels()


async def _list_alert_rules_logic(client: PingeraClient) -> str:
    """
    List all alert rules and their trigger conditions.

    Shows the specific conditions and thresholds that will trigger each alert,
    including response time thresholds, uptime requirements, and error conditions.

    Returns:
        JSON with list of alert rules including conditions, thresholds, and linked checks.
    """
    tools = AlertsTools(client)
    return await tools.list_alert_rules()