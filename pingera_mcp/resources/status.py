
"""
MCP resources for status information.
"""
from config import Config
from .base import BaseResources


class StatusResources(BaseResources):
    """Resources for status information."""
    
    def __init__(self, client, config: Config):
        super().__init__(client)
        self.config = config
    
    async def get_status_resource(self) -> str:
        """
        Resource providing Pingera API connection status.
        
        Returns:
            str: JSON string containing status information
        """
        try:
            self.logger.info("Fetching status resource")
            api_info = self.client.get_api_info()
            
            status_data = {
                "mode": self.config.mode.value,
                "api_info": api_info,
                "features": {
                    "read_operations": True,
                    "write_operations": self.config.is_read_write()
                }
            }
            
            return self._json_response(status_data)
            
        except Exception as e:
            self.logger.error(f"Error fetching status resource: {e}")
            return self._error_response(str(e), {
                "mode": self.config.mode.value,
                "features": {
                    "read_operations": False,
                    "write_operations": False
                }
            })
