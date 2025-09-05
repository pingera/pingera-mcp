
"""
MCP logic functions for Playwright script generation.
"""
from typing import Optional

from pingera_mcp import PingeraClient
from pingera_mcp.tools import PlaywrightGeneratorTools


async def _generate_synthetic_check_script_logic(
    client: PingeraClient,
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
    tools = PlaywrightGeneratorTools(client)
    return await tools.generate_synthetic_check_script(description, target_url, script_name)


async def _generate_api_check_script_logic(
    client: PingeraClient,
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
    tools = PlaywrightGeneratorTools(client)
    return await tools.generate_api_check_script(
        url, description, method, headers, payload, expected_status, contains_string, custom_code
    )
