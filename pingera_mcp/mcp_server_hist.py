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
    