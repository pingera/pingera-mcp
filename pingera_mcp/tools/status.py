"""
MCP tools for status and connection management.
"""
from .base import BaseTools
from ..exceptions import PingeraError


class StatusTools(BaseTools):
    """Tools for status and connection management."""

    async def test_pingera_connection(self) -> str:
        """
        Test connection to Pingera API.

        Returns:
            str: JSON string containing connection test results
        """
        try:
            self.logger.info("Testing Pingera connection")
            is_connected = self.client.test_connection()
            api_info = self.client.get_api_info()

            data = {
                "connected": is_connected,
                "api_info": api_info
            }

            return self._success_response(data)

        except Exception as e:
            self.logger.error(f"Error testing connection: {e}")
            return self._error_response(str(e), {"connected": False})