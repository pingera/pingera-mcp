
"""Tool registration functions for status domain."""

from ..tool_registry import tool_registry


def register_status_tools():
    """Register all status-related tools."""
    
    @tool_registry.register("test_pingera_connection", requires_write=False)
    def register_test_pingera_connection(mcp_instance):
        @mcp_instance.tool()
        async def test_pingera_connection() -> str:
            """
            Test connection to Pingera API.
            
            Returns:
                JSON string containing connection test results
            """
            from ..mcp_server import _update_tools_client, status_tools
            _update_tools_client()
            return await status_tools.test_pingera_connection()
        return test_pingera_connection
