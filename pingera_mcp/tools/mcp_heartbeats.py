
"""
MCP logic functions for heartbeat management.
"""
from typing import Optional

from pingera_mcp import PingeraClient
from pingera_mcp.tools import HeartbeatsTools


async def _list_heartbeats_logic(
    client: PingeraClient,
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
    tools = HeartbeatsTools(client)
    return await tools.list_heartbeats(page, page_size, status)


async def _get_heartbeat_details_logic(client: PingeraClient, heartbeat_id: str) -> str:
    """
    Get detailed information about a specific heartbeat monitor.

    Shows configuration, recent activity, ping history, and current status
    for monitoring cron jobs and scheduled tasks.

    Args:
        heartbeat_id: The unique identifier of the heartbeat monitor

    Returns:
        JSON with heartbeat details including schedule, grace period, last ping, and history.
    """
    tools = HeartbeatsTools(client)
    return await tools.get_heartbeat_details(heartbeat_id)


async def _create_heartbeat_logic(client: PingeraClient, heartbeat_data: dict) -> str:
    """
    Create a new heartbeat monitor for cron jobs or scheduled tasks.

    Set up monitoring for background processes by creating a heartbeat that
    expects regular ping signals. Configure the expected interval and grace period.

    Args:
        heartbeat_data: Dictionary with heartbeat configuration (name, interval, grace_period, etc.)

    Returns:
        JSON with created heartbeat details including the unique ping URL to use in your scripts.
    """
    tools = HeartbeatsTools(client)
    return await tools.create_heartbeat(heartbeat_data)


async def _update_heartbeat_logic(client: PingeraClient, heartbeat_id: str, heartbeat_data: dict) -> str:
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
    tools = HeartbeatsTools(client)
    return await tools.update_heartbeat(heartbeat_id, heartbeat_data)


async def _delete_heartbeat_logic(client: PingeraClient, heartbeat_id: str) -> str:
    """
    Delete a heartbeat monitor permanently.

    This will stop monitoring the associated cron job or scheduled task.
    The heartbeat ping URL will become inactive after deletion.

    Args:
        heartbeat_id: The unique identifier of the heartbeat to delete

    Returns:
        JSON confirming successful deletion.
    """
    tools = HeartbeatsTools(client)
    return await tools.delete_heartbeat(heartbeat_id)


async def _send_heartbeat_ping_logic(client: PingeraClient, heartbeat_id: str) -> str:
    """
    Manually send a ping signal to a heartbeat monitor.

    This simulates a successful execution of the monitored process.
    Normally, your cron jobs or scripts would ping the heartbeat URL automatically.

    Args:
        heartbeat_id: The unique identifier of the heartbeat to ping

    Returns:
        JSON confirming the ping was received and recorded.
    """
    tools = HeartbeatsTools(client)
    return await tools.send_heartbeat_ping(heartbeat_id)


async def _get_heartbeat_logs_logic(
    client: PingeraClient,
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
    tools = HeartbeatsTools(client)
    return await tools.get_heartbeat_logs(heartbeat_id, from_date, to_date, page, page_size)
