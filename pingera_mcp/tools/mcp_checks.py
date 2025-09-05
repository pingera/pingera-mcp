"""
MCP logic functions for check management.
"""
from typing import Optional, List, Dict, Any

from pingera_mcp import PingeraClient
from pingera_mcp.tools import ChecksTools
import json
import logging

logger = logging.getLogger(__name__)


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
    """Delete a monitoring check permanently."""
    try:
        logger.info(f"Deleting check: {check_id}")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            checks_api.v1_checks_check_id_delete(check_id=check_id)

            return json.dumps({
                "success": True,
                "deleted": True,
                "check_id": check_id,
                "message": f"Check {check_id} deleted successfully"
            })

    except Exception as e:
        logger.error(f"Error deleting check {check_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _get_check_statistics_logic(client, check_id: str) -> str:
    """Get statistical summary and performance metrics for a monitoring check."""
    try:
        logger.info(f"Getting statistics for check: {check_id}")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            stats = checks_api.v1_checks_check_id_statistics_get(check_id=check_id)

            stats_data = {}
            if hasattr(stats, '__dict__'):
                stats_data = stats.__dict__
            elif hasattr(stats, 'to_dict'):
                stats_data = stats.to_dict()
            else:
                stats_data = {"raw_response": str(stats)}

            return json.dumps({
                "success": True,
                "check_id": check_id,
                "statistics": stats_data
            })

    except Exception as e:
        logger.error(f"Error getting statistics for check {check_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _list_check_jobs_logic(client) -> str:
    """List all currently running or queued check execution jobs."""
    try:
        logger.info("Listing check jobs")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            jobs = checks_api.v1_checks_jobs_get()

            jobs_data = []
            if isinstance(jobs, list):
                for job in jobs:
                    if hasattr(job, '__dict__'):
                        jobs_data.append(job.__dict__)
                    elif hasattr(job, 'to_dict'):
                        jobs_data.append(job.to_dict())
                    else:
                        jobs_data.append({"raw_response": str(job)})

            return json.dumps({
                "success": True,
                "jobs": jobs_data,
                "total": len(jobs_data)
            })

    except Exception as e:
        logger.error(f"Error listing check jobs: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "jobs": []
        })


async def _get_check_job_details_logic(client, job_id: str) -> str:
    """Get detailed information about a specific check execution job."""
    try:
        logger.info(f"Getting job details for: {job_id}")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            job = checks_api.v1_checks_jobs_job_id_get(job_id=job_id)

            job_data = {}
            if hasattr(job, '__dict__'):
                job_data = job.__dict__
            elif hasattr(job, 'to_dict'):
                job_data = job.to_dict()
            else:
                job_data = {"raw_response": str(job)}

            return json.dumps({
                "success": True,
                "job_id": job_id,
                "job": job_data
            })

    except Exception as e:
        logger.error(f"Error getting job details for {job_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _get_unified_results_logic(
    client,
    check_ids: Optional[List[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    status: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """Get combined results from multiple checks in a unified format."""
    try:
        logger.info("Getting unified results")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            results = checks_api.v1_checks_unified_results_get(
                check_ids=check_ids,
                var_from=from_date,
                to=to_date,
                status=status,
                page=page,
                page_size=page_size
            )

            results_data = {}
            if hasattr(results, '__dict__'):
                results_data = results.__dict__
            elif hasattr(results, 'to_dict'):
                results_data = results.to_dict()
            else:
                results_data = {"raw_response": str(results)}

            return json.dumps({
                "success": True,
                "results": results_data
            })

    except Exception as e:
        logger.error(f"Error getting unified results: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _get_unified_statistics_logic(
    client,
    check_ids: Optional[List[str]] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> str:
    """Get combined statistical summary across multiple monitoring checks."""
    try:
        logger.info("Getting unified statistics")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            stats = checks_api.v1_checks_unified_statistics_get(
                check_ids=check_ids,
                var_from=from_date,
                to=to_date
            )

            stats_data = {}
            if hasattr(stats, '__dict__'):
                stats_data = stats.__dict__
            elif hasattr(stats, 'to_dict'):
                stats_data = stats.to_dict()
            else:
                stats_data = {"raw_response": str(stats)}

            return json.dumps({
                "success": True,
                "statistics": stats_data
            })

    except Exception as e:
        logger.error(f"Error getting unified statistics: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _execute_existing_check_logic(client, check_id: str) -> str:
    """Manually trigger an existing monitoring check to run immediately."""
    try:
        logger.info(f"Executing existing check: {check_id}")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            result = checks_api.v1_checks_check_id_execute_post(check_id=check_id)

            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}

            return json.dumps({
                "success": True,
                "check_id": check_id,
                "execution": result_data
            })

    except Exception as e:
        logger.error(f"Error executing check {check_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _get_on_demand_job_status_logic(client, job_id: str) -> str:
    """Check the status and results of an on-demand check execution job."""
    try:
        logger.info(f"Getting on-demand job status: {job_id}")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            status = checks_api.v1_checks_on_demand_job_id_get(job_id=job_id)

            status_data = {}
            if hasattr(status, '__dict__'):
                status_data = status.__dict__
            elif hasattr(status, 'to_dict'):
                status_data = status.to_dict()
            else:
                status_data = {"raw_response": str(status)}

            return json.dumps({
                "success": True,
                "job_id": job_id,
                "status": status_data
            })

    except Exception as e:
        logger.error(f"Error getting job status for {job_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _list_on_demand_checks_logic(
    client,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """List on-demand checks."""
    try:
        logger.info("Listing on-demand checks")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            checks = checks_api.v1_checks_on_demand_get(page=page, page_size=page_size)

            checks_data = []
            if isinstance(checks, list):
                for check in checks:
                    if hasattr(check, '__dict__'):
                        checks_data.append(check.__dict__)
                    elif hasattr(check, 'to_dict'):
                        checks_data.append(check.to_dict())
                    else:
                        checks_data.append({"raw_response": str(check)})

            return json.dumps({
                "success": True,
                "checks": checks_data,
                "total": len(checks_data)
            })

    except Exception as e:
        logger.error(f"Error listing on-demand checks: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "checks": []
        })


async def _update_check_logic(
    client,
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
    """Update configuration for an existing monitoring check."""
    try:
        check_data = {
            "name": name,
            "url": url,
            "host": host,
            "port": port,
            "interval": interval,
            "timeout": timeout,
            "active": active,
            "parameters": parameters,
        }

        # Filter out None values
        filtered_data = {k: v for k, v in check_data.items() if v is not None}

        if not filtered_data:
            return json.dumps({
                "success": False,
                "error": "No update data provided"
            })

        logger.info(f"Updating check {check_id} with data: {filtered_data}")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            from pingera.models import Check
            checks_api = MonitoringChecksApi(api_client)

            check_model = Check(**filtered_data)
            result = checks_api.v1_checks_check_id_put(check_id=check_id, check=check_model)

            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}

            return json.dumps({
                "success": True,
                "check_id": check_id,
                "check": result_data
            })

    except Exception as e:
        logger.error(f"Error updating check {check_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _pause_check_logic(client, check_id: str) -> str:
    """Temporarily pause a monitoring check without deleting it."""
    try:
        logger.info(f"Pausing check: {check_id}")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            result = checks_api.v1_checks_check_id_pause_post(check_id=check_id)

            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}

            return json.dumps({
                "success": True,
                "check_id": check_id,
                "status": "paused",
                "result": result_data
            })

    except Exception as e:
        logger.error(f"Error pausing check {check_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def _resume_check_logic(client, check_id: str) -> str:
    """Resume a previously paused monitoring check."""
    try:
        logger.info(f"Resuming check: {check_id}")

        with client._get_api_client() as api_client:
            from pingera.api import MonitoringChecksApi
            checks_api = MonitoringChecksApi(api_client)

            result = checks_api.v1_checks_check_id_resume_post(check_id=check_id)

            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}

            return json.dumps({
                "success": True,
                "check_id": check_id,
                "status": "resumed",
                "result": result_data
            })

    except Exception as e:
        logger.error(f"Error resuming check {check_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })