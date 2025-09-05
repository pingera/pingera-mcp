
"""
MCP tool logic for status operations.
"""
from pingera_mcp import PingeraClient
from pingera_mcp.tools import StatusTools

async def _test_connection_logic(client: PingeraClient) -> str:
    """
    Test the connection to Pingera API and verify authentication.

    Use this tool to verify that your API key is working and the service is accessible.
    It provides connection status, API version info, and any authentication issues.

    Returns:
        JSON with connection status, API information, and authentication details.
    """
    if not client:
        raise RuntimeError("Pingera client could not be initialized for this operation.")
    status_tools = StatusTools(client)
    return await status_tools.test_pingera_connection()
