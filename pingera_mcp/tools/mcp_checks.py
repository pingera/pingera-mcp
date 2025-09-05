
"""
MCP logic functions for check management.
"""
from typing import Optional, List, Dict, Any

from pingera_mcp import PingeraClient
from pingera_mcp.tools import ChecksTools


async def _list_checks_logic(
    client: PingeraClient,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    group_id: Optional[str] = None,
    name: Optional[str] = None
) -> str:
    """
    List all monitoring checks in your account.

    Checks are automated tests that monitor your websites, APIs, and services.
    They run at regular intervals and can trigger alerts when issues are detected.

    Args:
        page: Page number for pagination (default: 1)
        page_size: Number of items per page (default: 20, max: 100)
        type: Filter by check type ('web', 'api', 'ssl', 'tcp', 'synthetic', 'multistep')
        status: Filter by status (can specify multiple statuses separated by commas)
        group_id: Filter checks by group ID (use "ungrouped" for checks not assigned to any group)
        name: Filter checks by name using case-insensitive partial matching

    Returns:
        JSON with list of checks including names, URLs, types, intervals, and current status.
    """
    tools = ChecksTools(client)
    return await tools.list_checks(page, page_size, type, status, group_id, name)


async def _get_check_details_logic(client: PingeraClient, check_id: str) -> str:
    """
    Get detailed configuration and settings for a specific monitoring check.

    Args:
        check_id: The unique identifier of the monitoring check

    Returns:
        JSON with complete check configuration including URL, intervals, timeouts,
        expected responses, notification settings, and linked components.
    """
    tools = ChecksTools(client)
    return await tools.get_check_details(check_id)


async def _get_check_results_logic(
    client: PingeraClient,
    check_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """
    Get historical results and performance data for a monitoring check.

    This provides detailed execution history including response times, status codes,
    error messages, and uptime statistics for the specified time period.

    Args:
        check_id: The unique identifier of the monitoring check
        from_date: Start date in ISO format (e.g., '2024-01-01T00:00:00Z')
        to_date: End date in ISO format (e.g., '2024-01-31T23:59:59Z')
        page: Page number for pagination
        page_size: Number of results per page

    Returns:
        JSON with check results including timestamps, response times, status codes, and error details.
    """
    tools = ChecksTools(client)
    return await tools.get_check_results(check_id, from_date, to_date, page, page_size)


async def _execute_custom_check_logic(
    client: PingeraClient,
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

    Returns:
        JSON with the job id that is executed asynchronously.
    """
    tools = ChecksTools(client)
    return await tools.execute_custom_check(type, name, url, host, port, timeout, parameters)


async def _create_check_logic(
    client: PingeraClient,
    name: str,
    type: str,
    url: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    interval: int = 300,
    timeout: int = 10,
    active: bool = True,
    parameters: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a new monitoring check to watch a website, API, or service.

    Set up automated monitoring that will test your service at regular
    intervals and alert you when issues are detected.

    Args:
        name: A user-friendly name for the monitor check. Max 100 characters.
        type: The type of check. Valid: 'web', 'api', 'ssl', 'tcp', 'synthetic', 'multistep'.
        url: The URL to monitor (for 'web' and 'api' checks).
        host: The hostname or IP address (for 'tcp' and 'ssl' checks).
        port: The port number to monitor (for 'tcp' checks). Range: 1-65535.
        interval: Frequency of checks in seconds. Range: 30-86400. Default: 300.
        timeout: Request timeout in seconds. Range: 1-30. Default: 10.
        active: A flag to set the check as active or paused. Default: True.
        parameters: Additional parameters for 'synthetic' and 'multistep' checks.

    Returns:
        A JSON object with the created check's details.
    """
    tools = ChecksTools(client)
    return await tools.create_check(name, type, url, host, port, interval, timeout, active, parameters)


async def _delete_check_logic(client: PingeraClient, check_id: str) -> str:
    """
    Delete a monitoring check permanently.

    This stops all monitoring for the specified check and removes
    all historical data and results.

    Args:
        check_id: The unique identifier of the check to delete

    Returns:
        JSON confirming successful deletion.
    """
    tools = ChecksTools(client)
    return await tools.delete_check(check_id)
