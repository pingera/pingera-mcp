
"""
Check management tool decorators.
"""
from typing import Optional, List, Dict, Any


def register_checks_tools(mcp, config, checks_tools, update_tools_client_func):
    """Register all check-related MCP tools."""
    
    @mcp.tool()
    async def list_checks(
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
        group_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> str:
        """List all monitoring checks in your account."""
        update_tools_client_func()
        return await checks_tools.list_checks(page, page_size, type, status, group_id, name)

    @mcp.tool()
    async def get_check_details(check_id: str) -> str:
        """Get detailed configuration and settings for a specific monitoring check."""
        update_tools_client_func()
        return await checks_tools.get_check_details(check_id)

    @mcp.tool()
    async def get_check_results(
        check_id: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """Get historical results and performance data for a monitoring check."""
        update_tools_client_func()
        return await checks_tools.get_check_results(check_id, from_date, to_date, page, page_size)

    @mcp.tool()
    async def get_check_statistics(check_id: str) -> str:
        """Get statistical summary and performance metrics for a monitoring check."""
        update_tools_client_func()
        return await checks_tools.get_check_statistics(check_id)

    @mcp.tool()
    async def list_check_jobs() -> str:
        """List all currently running or queued check execution jobs."""
        update_tools_client_func()
        return await checks_tools.list_check_jobs()

    @mcp.tool()
    async def get_check_job_details(job_id: str) -> str:
        """Get detailed information about a specific check execution job."""
        update_tools_client_func()
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
        """Get combined results from multiple checks in a unified format."""
        update_tools_client_func()
        return await checks_tools.get_unified_results(check_ids, from_date, to_date, status, page, page_size)

    @mcp.tool()
    async def get_unified_statistics(
        check_ids: Optional[List[str]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> str:
        """Get combined statistical summary across multiple monitoring checks."""
        update_tools_client_func()
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
        """Execute a one-time custom monitoring check on any URL or service."""
        update_tools_client_func()
        return await checks_tools.execute_custom_check(type, name, url, host, port, timeout, parameters)

    @mcp.tool()
    async def execute_existing_check(check_id: str) -> str:
        """Manually trigger an existing monitoring check to run immediately."""
        update_tools_client_func()
        return await checks_tools.execute_existing_check(check_id)

    @mcp.tool()
    async def get_on_demand_job_status(job_id: str) -> str:
        """Check the status and results of an on-demand check execution job."""
        update_tools_client_func()
        return await checks_tools.get_on_demand_job_status(job_id)

    @mcp.tool()
    async def list_on_demand_checks(
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """List on-demand checks."""
        update_tools_client_func()
        return await checks_tools.list_on_demand_checks(page, page_size)

    if config.is_read_write():
        @mcp.tool()
        async def create_check(
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
            """Create a new monitoring check to watch a website, API, or service."""
            update_tools_client_func()
            return await checks_tools.create_check(
                name=name, type=type, url=url, host=host, port=port,
                interval=interval, timeout=timeout, active=active,
                parameters=parameters,
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
            secrets: Optional[List[dict]] = None,
        ) -> str:
            """Update configuration for an existing monitoring check."""
            update_tools_client_func()
            return await checks_tools.update_check(
                check_id=check_id, name=name, url=url, host=host, port=port,
                interval=interval, timeout=timeout, active=active,
                parameters=parameters, secrets=secrets,
            )

        @mcp.tool()
        async def delete_check(check_id: str) -> str:
            """Delete a monitoring check permanently."""
            update_tools_client_func()
            return await checks_tools.delete_check(check_id)

        @mcp.tool()
        async def pause_check(check_id: str) -> str:
            """Temporarily pause a monitoring check without deleting it."""
            update_tools_client_func()
            return await checks_tools.pause_check(check_id)

        @mcp.tool()
        async def resume_check(check_id: str) -> str:
            """Resume a previously paused monitoring check."""
            update_tools_client_func()
            return await checks_tools.resume_check(check_id)
