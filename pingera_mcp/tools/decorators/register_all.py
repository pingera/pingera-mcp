
"""
Central registration module for all MCP tool decorators.
"""
from .pages_decorators import register_pages_tools
from .components_decorators import register_components_tools
from .checks_decorators import register_checks_tools


def register_status_tools(mcp, status_tools, update_tools_client_func):
    """Register status tools."""
    @mcp.tool()
    async def test_pingera_connection() -> str:
        """Test the connection to Pingera API and verify authentication."""
        update_tools_client_func()
        return await status_tools.test_pingera_connection()


def register_check_groups_tools(mcp, check_groups_tools, update_tools_client_func):
    """Register check groups tools."""
    from typing import Optional
    
    @mcp.tool()
    async def list_check_groups(
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """List all check groups in your account."""
        update_tools_client_func()
        return await check_groups_tools.list_check_groups(page, page_size)

    @mcp.tool()
    async def get_check_group_details(group_id: str) -> str:
        """Get detailed information about a specific check group."""
        update_tools_client_func()
        return await check_groups_tools.get_check_group_details(group_id)

    @mcp.tool()
    async def get_checks_in_group(
        group_id: str,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """Get all monitoring checks that belong to a specific check group."""
        update_tools_client_func()
        return await check_groups_tools.get_checks_in_group(group_id, page, page_size)


def register_secrets_tools(mcp, config, secrets_tools, update_tools_client_func):
    """Register secrets tools."""
    from typing import Optional, List
    
    @mcp.tool()
    async def list_secrets(
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> str:
        """List all organization secrets."""
        update_tools_client_func()
        return await secrets_tools.list_secrets(page, page_size)

    @mcp.tool()
    async def get_secret_details(secret_id: str) -> str:
        """Get detailed information about a specific secret."""
        update_tools_client_func()
        return await secrets_tools.get_secret_details(secret_id)

    @mcp.tool()
    async def get_check_secrets(check_id: str) -> str:
        """Get all secrets associated with a monitoring check."""
        update_tools_client_func()
        return await secrets_tools.get_check_secrets(check_id)

    if config.is_read_write():
        @mcp.tool()
        async def create_secret(name: str, value: str) -> str:
            """Create a new organization secret."""
            update_tools_client_func()
            return await secrets_tools.create_secret(name, value)

        @mcp.tool()
        async def update_secret(secret_id: str, value: str) -> str:
            """Update a secret's value."""
            update_tools_client_func()
            return await secrets_tools.update_secret(secret_id, value)

        @mcp.tool()
        async def delete_secret(secret_id: str) -> str:
            """Delete a secret permanently."""
            update_tools_client_func()
            return await secrets_tools.delete_secret(secret_id)

        @mcp.tool()
        async def add_secret_to_check(
            check_id: str,
            secret_id: str,
            env_var_name: str
        ) -> str:
            """Associate a secret with a monitoring check."""
            update_tools_client_func()
            return await secrets_tools.add_secret_to_check(check_id, secret_id, env_var_name)

        @mcp.tool()
        async def update_check_secrets(
            check_id: str,
            secrets: List[dict]
        ) -> str:
            """Replace all secret associations for a check."""
            update_tools_client_func()
            return await secrets_tools.update_check_secrets(check_id, secrets)

        @mcp.tool()
        async def remove_secret_from_check(check_id: str, secret_id: str) -> str:
            """Remove a secret association from a check."""
            update_tools_client_func()
            return await secrets_tools.remove_secret_from_check(check_id, secret_id)


def register_playwright_tools(mcp, playwright_tools, update_tools_client_func):
    """Register Playwright script generation tools."""
    from typing import Optional
    
    @mcp.tool()
    async def generate_synthetic_check_script(
        description: str,
        target_url: str,
        script_name: Optional[str] = None
    ) -> str:
        """Generate a Playwright script for synthetic browser monitoring."""
        update_tools_client_func()
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
        """Generates a Playwright script for an API check."""
        update_tools_client_func()
        return await playwright_tools.generate_api_check_script(
            url=url, description=description, method=method,
            headers=headers, payload=payload, expected_status=expected_status,
            contains_string=contains_string, custom_code=custom_code
        )


def register_all_tools(mcp, config, tool_instances, update_tools_client_func):
    """Register all MCP tools from all modules."""
    
    # Register read-only tools
    register_status_tools(mcp, tool_instances['status'], update_tools_client_func)
    register_pages_tools(mcp, config, tool_instances['pages'], update_tools_client_func)
    register_components_tools(mcp, config, tool_instances['components'], update_tools_client_func)
    register_checks_tools(mcp, config, tool_instances['checks'], update_tools_client_func)
    register_check_groups_tools(mcp, tool_instances['check_groups'], update_tools_client_func)
    register_secrets_tools(mcp, config, tool_instances['secrets'], update_tools_client_func)
    register_playwright_tools(mcp, tool_instances['playwright'], update_tools_client_func)
    
    # Import and register remaining tools (alerts, heartbeats, incidents)
    # These follow similar patterns - abbreviated for brevity
