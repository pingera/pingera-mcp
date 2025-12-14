
"""Tool registration functions for Playwright generator domain."""

from typing import Optional
from ..tool_registry import tool_registry


def register_playwright_tools():
    """Register all Playwright generator-related tools."""
    
    @tool_registry.register("generate_synthetic_check_script", requires_write=False)
    def register_generate_synthetic_check_script(mcp_instance):
        @mcp_instance.tool()
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
            from ..mcp_server import _update_tools_client, playwright_tools
            _update_tools_client()
            return await playwright_tools.generate_synthetic_check_script(
                description=description,
                target_url=target_url,
                script_name=script_name
            )
        return generate_synthetic_check_script
    
    @tool_registry.register("generate_api_check_script", requires_write=False)
    def register_generate_api_check_script(mcp_instance):
        @mcp_instance.tool()
        async def generate_api_check_script(
            description: str,
            base_url: str,
            script_name: Optional[str] = None
        ) -> str:
            """
            Generate a Playwright script for multi-step API monitoring.
            
            Args:
                description: Natural language description of the API test flow
                base_url: The base API URL to test
                script_name: Optional name for the test (auto-generated if not provided)
            
            Returns:
                JSON with the generated Playwright script and usage instructions
            """
            from ..mcp_server import _update_tools_client, playwright_tools
            _update_tools_client()
            return await playwright_tools.generate_api_check_script(
                description=description,
                base_url=base_url,
                script_name=script_name
            )
        return generate_api_check_script
