
"""Tool registration functions for checks domain."""

from typing import Optional, List, Dict, Any
from ..tool_registry import tool_registry


def register_checks_tools():
    """Register all checks-related tools."""
    
    @tool_registry.register("list_checks", requires_write=False)
    def register_list_checks(mcp_instance):
        @mcp_instance.tool()
        async def list_checks(
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.list_checks(page, page_size, type, status, group_id, name)
        return list_checks
    
    @tool_registry.register("get_check_details", requires_write=False)
    def register_get_check_details(mcp_instance):
        @mcp_instance.tool()
        async def get_check_details(check_id: str) -> str:
            """
            Get detailed configuration and settings for a specific monitoring check.
        
            Args:
                check_id: The unique identifier of the monitoring check
        
            Returns:
                JSON with complete check configuration including URL, intervals, timeouts,
                expected responses, notification settings, and linked components.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.get_check_details(check_id)
        return get_check_details
    
    @tool_registry.register("get_check_results", requires_write=False)
    def register_get_check_results(mcp_instance):
        @mcp_instance.tool()
        async def get_check_results(
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.get_check_results(check_id, from_date, to_date, page, page_size)
        return get_check_results
    
    @tool_registry.register("get_check_statistics", requires_write=False)
    def register_get_check_statistics(mcp_instance):
        @mcp_instance.tool()
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.get_check_statistics(check_id)
        return get_check_statistics
    
    @tool_registry.register("list_check_jobs", requires_write=False)
    def register_list_check_jobs(mcp_instance):
        @mcp_instance.tool()
        async def list_check_jobs() -> str:
            """
            List all currently running or queued check execution jobs.
        
            Shows the status of scheduled and on-demand check executions,
            useful for monitoring the execution queue and identifying any stuck jobs.
        
            Returns:
                JSON with list of active jobs including job IDs, check IDs, status, and execution times.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.list_check_jobs()
        return list_check_jobs
    
    @tool_registry.register("get_check_job_details", requires_write=False)
    def register_check_job_details(mcp_instance):
        @mcp_instance.tool()
        async def get_check_job_details(job_id: str) -> str:
            """
            Get detailed information about a specific check execution job.
        
            Args:
                job_id: The unique identifier of the check job
        
            Returns:
                JSON with job details including execution status, start/end times, results, and any errors.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.get_check_job_details(job_id)
        return get_check_job_details
    
    @tool_registry.register("get_unified_results", requires_write=False)
    def register_get_unified_results(mcp_instance):
        @mcp_instance.tool()
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.get_unified_results(check_ids, from_date, to_date, status, page, page_size)
        return get_unified_results
    
    @tool_registry.register("get_unified_statistics", requires_write=False)
    def register_get_unified_statistics(mcp_instance):
        @mcp_instance.tool()
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.get_unified_statistics(check_ids, from_date, to_date)
        return get_unified_statistics
    
    @tool_registry.register("list_on_demand_checks", requires_write=False)
    def register_list_on_demand_checks(mcp_instance):
        @mcp_instance.tool()
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.list_on_demand_checks(page, page_size)
        return list_on_demand_checks
    
    @tool_registry.register("get_on_demand_job_status", requires_write=False)
    def register_get_on_demand_job_status(mcp_instance):
        @mcp_instance.tool()
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.get_on_demand_job_status(job_id)
        return get_on_demand_job_status
    
    # Write operations
    
    @tool_registry.register("create_icmp_check", requires_write=True)
    def register_create_icmp_check(mcp_instance):
        @mcp_instance.tool()
        async def create_icmp_check(
            name: str,
            host: str,
            interval: int = 300,
            timeout: int = 30,
            active: bool = True,
            probe_count: Optional[int] = 4,
            ip_version: Optional[str] = "auto",
            probe_interval: Optional[float] = 1.0,
            probe_timeout: Optional[float] = 1.0,
            max_packet_loss: Optional[float] = None
        ) -> str:
            """
            Create a permanent ICMP (ping) monitoring check.
        
            ICMP checks monitor network connectivity and latency to hosts using ICMP echo requests (ping).
            They are useful for monitoring server availability, network latency, and packet loss.
        
            Args:
                name: A descriptive name for this ICMP check (required)
                host: Hostname or IP address to ping (required, max 255 characters)
                interval: How often to run the check in seconds (default: 300, range: 30-86400)
                timeout: Overall check timeout in seconds (default: 30, range: 1-30)
                active: Whether the check is active (default: True)
                probe_count: Number of ping probes to send (default: 4, range: 1-100)
                ip_version: IP version preference - 'v4', 'v6', or 'auto' (default: 'auto', prefers IPv6)
                probe_interval: Interval between individual probes in seconds (default: 1.0, range: 0.001-10)
                probe_timeout: Timeout for each individual probe in seconds (default: 1.0, range: 0.1-30)
                max_packet_loss: Maximum acceptable packet loss percentage (range: 0-100, optional)
        
            Returns:
                JSON with created ICMP check details including check ID and configuration.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.create_icmp_check(
                name, host, interval, timeout, active,
                probe_count, ip_version, probe_interval, probe_timeout, max_packet_loss
            )
        return create_icmp_check
    
    @tool_registry.register("create_dns_check", requires_write=True)
    def register_create_dns_check(mcp_instance):
        @mcp_instance.tool()
        async def create_dns_check(
            name: str,
            host: str,
            interval: int = 300,
            timeout: int = 10,
            active: bool = True,
            record_type: Optional[str] = "A",
            dns_servers: Optional[List[str]] = None,
            expected_answers: Optional[List[str]] = None,
            validation_mode: Optional[str] = "contains_all"
        ) -> str:
            """
            Create a permanent DNS monitoring check.
        
            DNS checks monitor DNS resolution and validate DNS records. They can verify that
            your domain resolves correctly and returns expected IP addresses or other DNS records.
        
            Args:
                name: A descriptive name for this DNS check (required)
                host: Domain name to query (required, e.g., 'example.com')
                interval: How often to run the check in seconds (default: 300, range: 30-86400)
                timeout: Check timeout in seconds (default: 10, range: 1-30)
                active: Whether the check is active (default: True)
                record_type: DNS record type to query (default: 'A')
                            Supported types: A, AAAA, MX, TXT, CNAME, NS, SOA, PTR, SRV, CAA, etc.
                dns_servers: List of custom DNS server IP addresses to use (optional)
                            If not specified, uses system default DNS servers
                expected_answers: List of expected DNS answers for validation (optional)
                                 The check will fail if actual answers don't match expectations
                validation_mode: How to validate answers (default: 'contains_all')
                                - 'contains_all': Actual answers must include all expected answers
                                - 'exact': Actual answers must exactly match expected answers
        
            Returns:
                JSON with created DNS check details including check ID and configuration.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.create_dns_check(
                name, host, interval, timeout, active,
                record_type, dns_servers, expected_answers, validation_mode
            )
        return create_dns_check
    
    @tool_registry.register("create_synthetic_check", requires_write=True)
    def register_create_synthetic_check(mcp_instance):
        @mcp_instance.tool()
        async def create_synthetic_check(
            name: str,
            url: str,
            pw_script: str,
            interval: int = 300,
            timeout: int = 60,
            active: bool = True
        ) -> str:
            """
            Create a permanent synthetic browser monitoring check using Playwright.
        
            Synthetic checks simulate real user interactions with your website using a headless
            browser. They can navigate pages, fill forms, click buttons, and verify page content.
            The check uses Playwright scripts written in JavaScript or TypeScript.
        
            IMPORTANT: You must provide a complete Playwright script in the pw_script parameter.
            The script should use the Playwright test framework and include proper assertions.
        
            Args:
                name: A descriptive name for this synthetic check (required, max 100 characters)
                url: The starting URL for the browser test (required)
                pw_script: Complete Playwright script content in JavaScript or TypeScript (required)
                interval: How often to run the check in seconds (default: 300, range: 30-86400)
                timeout: Overall check timeout in seconds (default: 60, range: 1-300)
                active: Whether the check is active (default: True)
        
            Returns:
                JSON with created synthetic check details including check ID and configuration.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            parameters = {"pw_script": pw_script}
            return await checks_tools.create_check(
                name=name,
                type="synthetic",
                url=url,
                interval=interval,
                timeout=timeout,
                active=active,
                parameters=parameters
            )
        return create_synthetic_check
    
    @tool_registry.register("create_multistep_check", requires_write=True)
    def register_create_multistep_check(mcp_instance):
        @mcp_instance.tool()
        async def create_multistep_check(
            name: str,
            url: str,
            pw_script: str,
            interval: int = 300,
            timeout: int = 60,
            active: bool = True
        ) -> str:
            """
            Create a permanent multi-step monitoring check using Playwright.
        
            Multi-step checks are similar to synthetic checks but are specifically designed for
            complex, multi-page workflows like checkout processes, login flows, or API sequences.
            They use Playwright scripts to automate and verify multi-step user journeys.
        
            IMPORTANT: You must provide a complete Playwright script in the pw_script parameter.
            The script should include all steps of your workflow with proper error handling.
        
            Args:
                name: A descriptive name for this multi-step check (required, max 100 characters)
                url: The starting URL for the workflow (required)
                pw_script: Complete Playwright script content in JavaScript or TypeScript (required)
                interval: How often to run the check in seconds (default: 300, range: 30-86400)
                timeout: Overall check timeout in seconds (default: 60, range: 1-300)
                active: Whether the check is active (default: True)
        
            Returns:
                JSON with created multi-step check details including check ID and configuration.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            parameters = {"pw_script": pw_script}
            return await checks_tools.create_check(
                name=name,
                type="multistep",
                url=url,
                interval=interval,
                timeout=timeout,
                active=active,
                parameters=parameters
            )
        return create_multistep_check
    
    @tool_registry.register("execute_custom_check", requires_write=True)
    def register_execute_custom_check(mcp_instance):
        @mcp_instance.tool()
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
                type: Type of check ('web', 'api', 'tcp', 'ssl', 'icmp', 'dns', 'multistep', 'synthetic') - REQUIRED
                name: A user-friendly name for the custom check (max 100 characters) - REQUIRED
                url: The URL to monitor (required for web/api checks). Supports international domain names.
                host: The hostname or IP address to monitor (required for TCP/SSL/ICMP/DNS checks, max 255 characters)
                port: The port number to monitor (required for TCP/SSL checks, range: 1-65535)
                timeout: Timeout in seconds (range: 1-30, default: 30)
                parameters: Additional parameters specific to the check type.
        
            Returns:
                JSON with the job id that is executed asynchronously.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.execute_custom_check(type, name, url, host, port, timeout, parameters)
        return execute_custom_check
    
    @tool_registry.register("execute_icmp_check", requires_write=True)
    def register_execute_icmp_check(mcp_instance):
        @mcp_instance.tool()
        async def execute_icmp_check(
            name: str,
            host: str,
            timeout: int = 30,
            probe_count: Optional[int] = 4,
            ip_version: Optional[str] = "auto",
            probe_interval: Optional[float] = 1.0,
            probe_timeout: Optional[float] = 1.0,
            max_packet_loss: Optional[float] = None
        ) -> str:
            """
            Execute a one-time ICMP (ping) check without creating a permanent monitor.
        
            This performs an immediate ICMP ping test to check network connectivity and latency
            to a host. Useful for quick diagnostics or testing before setting up permanent monitoring.
        
            Args:
                name: A descriptive name for this test (required, max 100 characters)
                host: Hostname or IP address to ping (required, max 255 characters)
                timeout: Overall check timeout in seconds (default: 30, range: 1-30)
                probe_count: Number of ping probes to send (default: 4, range: 1-100)
                ip_version: IP version preference - 'v4', 'v6', or 'auto' (default: 'auto', prefers IPv6)
                probe_interval: Interval between individual probes in seconds (default: 1.0, range: 0.001-10)
                probe_timeout: Timeout for each individual probe in seconds (default: 1.0, range: 0.1-30)
                max_packet_loss: Maximum acceptable packet loss percentage (range: 0-100, optional)
        
            Returns:
                JSON with job ID for tracking the asynchronous execution.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            parameters = {}
            if probe_count is not None:
                parameters["probe_count"] = probe_count
            if ip_version is not None:
                parameters["ip_version"] = ip_version
            if probe_interval is not None:
                parameters["probe_interval"] = probe_interval
            if probe_timeout is not None:
                parameters["probe_timeout"] = probe_timeout
            if max_packet_loss is not None:
                parameters["assertions"] = {"max_packet_loss": max_packet_loss}
        
            return await checks_tools.execute_custom_check(
                type="icmp",
                name=name,
                host=host,
                timeout=timeout,
                parameters=parameters if parameters else None
            )
        return execute_icmp_check
    
    @tool_registry.register("execute_dns_check", requires_write=True)
    def register_execute_dns_check(mcp_instance):
        @mcp_instance.tool()
        async def execute_dns_check(
            name: str,
            host: str,
            timeout: int = 10,
            record_type: Optional[str] = "A",
            dns_servers: Optional[List[str]] = None,
            expected_answers: Optional[List[str]] = None,
            validation_mode: Optional[str] = "contains_all"
        ) -> str:
            """
            Execute a one-time DNS resolution check without creating a permanent monitor.
        
            This performs an immediate DNS query to verify domain resolution and optionally
            validate that DNS records match expected values. Useful for troubleshooting DNS
            issues or testing DNS changes before they propagate.
        
            Args:
                name: A descriptive name for this test (required, max 100 characters)
                host: Domain name to query (required, e.g., 'example.com')
                timeout: Check timeout in seconds (default: 10, range: 1-30)
                record_type: DNS record type to query (default: 'A')
                dns_servers: List of custom DNS server IP addresses to use (optional)
                expected_answers: List of expected DNS answers for validation (optional)
                validation_mode: How to validate answers (default: 'contains_all')
        
            Returns:
                JSON with job ID for tracking the asynchronous execution.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            parameters = {}
            if record_type is not None:
                parameters["record_type"] = record_type
            if dns_servers is not None:
                parameters["dns_servers"] = dns_servers
            if expected_answers is not None:
                parameters["expected_answers"] = expected_answers
            if validation_mode is not None:
                parameters["validation_mode"] = validation_mode
        
            return await checks_tools.execute_custom_check(
                type="dns",
                name=name,
                host=host,
                timeout=timeout,
                parameters=parameters if parameters else None
            )
        return execute_dns_check
    
    @tool_registry.register("execute_synthetic_check", requires_write=True)
    def register_execute_synthetic_check(mcp_instance):
        @mcp_instance.tool()
        async def execute_synthetic_check(
            name: str,
            url: str,
            pw_script: str,
            timeout: int = 60
        ) -> str:
            """
            Execute a one-time synthetic browser check without creating a permanent monitor.
        
            This performs an immediate browser automation test using Playwright to simulate
            real user interactions. Useful for testing UI workflows, verifying page functionality,
            or troubleshooting before setting up permanent monitoring.
        
            IMPORTANT: You must provide a complete Playwright script in the pw_script parameter.
        
            Args:
                name: A descriptive name for this test (required, max 100 characters)
                url: The starting URL for the browser test (required)
                pw_script: Complete Playwright script content in JavaScript or TypeScript (required)
                timeout: Overall check timeout in seconds (default: 60, range: 1-300)
        
            Returns:
                JSON with job ID for tracking the asynchronous execution.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            parameters = {"pw_script": pw_script}
            return await checks_tools.execute_custom_check(
                type="synthetic",
                name=name,
                url=url,
                timeout=timeout,
                parameters=parameters
            )
        return execute_synthetic_check
    
    @tool_registry.register("execute_multistep_check", requires_write=True)
    def register_execute_multistep_check(mcp_instance):
        @mcp_instance.tool()
        async def execute_multistep_check(
            name: str,
            url: str,
            pw_script: str,
            timeout: int = 60
        ) -> str:
            """
            Execute a one-time multi-step workflow check without creating a permanent monitor.
        
            This performs an immediate browser automation test for complex, multi-page workflows
            using Playwright. Ideal for testing login flows, checkout processes, or multi-step
            forms before setting up permanent monitoring.
        
            IMPORTANT: You must provide a complete Playwright script in the pw_script parameter
            that covers all steps in your workflow.
        
            Args:
                name: A descriptive name for this test (required, max 100 characters)
                url: The starting URL for the workflow (required)
                pw_script: Complete Playwright script content in JavaScript or TypeScript (required)
                timeout: Overall check timeout in seconds (default: 60, range: 1-300)
        
            Returns:
                JSON with job ID for tracking the asynchronous execution.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            parameters = {"pw_script": pw_script}
            return await checks_tools.execute_custom_check(
                type="multistep",
                name=name,
                url=url,
                timeout=timeout,
                parameters=parameters
            )
        return execute_multistep_check
    
    @tool_registry.register("execute_existing_check", requires_write=True)
    def register_execute_existing_check(mcp_instance):
        @mcp_instance.tool()
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.execute_existing_check(check_id)
        return execute_existing_check
    
    @tool_registry.register("create_check", requires_write=True)
    def register_create_check(mcp_instance):
        @mcp_instance.tool()
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
            """
            Create a new monitoring check to watch a website, API, or service.
        
            Set up automated monitoring that will test your service at regular
            intervals and alert you when issues are detected.
            If name is not set, AI agent should generate it from the URL or description.
        
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.create_check(
                name=name,
                type=type,
                url=url,
                host=host,
                port=port,
                interval=interval,
                timeout=timeout,
                active=active,
                parameters=parameters,
            )
        return create_check
    
    @tool_registry.register("update_check", requires_write=True)
    def register_update_check(mcp_instance):
        @mcp_instance.tool()
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
                parameters: New additional parameters.
                secrets: List of secrets to associate with this check (replaces all existing associations).
        
            Returns:
                A JSON object with the updated check details.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
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
                secrets=secrets,
            )
        return update_check
    
    @tool_registry.register("delete_check", requires_write=True)
    def register_delete_check(mcp_instance):
        @mcp_instance.tool()
        async def delete_check(check_id: str) -> str:
            """
            Delete a monitoring check permanently.
        
            This stops all monitoring for the specified check and removes
            all historical data and results.
        
            Args:
                check_id: The unique identifier of the check to delete
        
            Returns:
                JSON confirming successful deletion.
            """
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.delete_check(check_id)
        return delete_check
    
    @tool_registry.register("pause_check", requires_write=True)
    def register_pause_check(mcp_instance):
        @mcp_instance.tool()
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.pause_check(check_id)
        return pause_check
    
    @tool_registry.register("resume_check", requires_write=True)
    def register_resume_check(mcp_instance):
        @mcp_instance.tool()
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
            from ..mcp_server import _update_tools_client, checks_tools
            _update_tools_client()
            return await checks_tools.resume_check(check_id)
        return resume_check
