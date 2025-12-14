
"""Tool registration functions for heartbeats domain."""

from typing import Optional
from ..tool_registry import tool_registry


def register_heartbeats_tools():
    """Register all heartbeats-related tools."""
    
    @tool_registry.register("list_heartbeats", requires_write=False)
    def register_list_heartbeats(mcp_instance):
        @mcp_instance.tool()
        async def list_heartbeats(
            page: Optional[int] = None,
            page_size: Optional[int] = None,
            status: Optional[str] = None
        ) -> str:
            """
            List all heartbeat monitors in your account.
        
            Heartbeats are passive monitoring checks where your cron jobs, scheduled
            tasks, or backup processes ping Pingera to confirm they ran successfully.
            If a ping is not received within the expected interval, an alert is triggered.
        
            Args:
                page: Page number for pagination (default: 1)
                page_size: Number of items per page (default: 20, max: 100)
                status: Filter by heartbeat status
        
            Returns:
                JSON with list of heartbeats including names, expected intervals, and last ping times.
            """
            from ..mcp_server import _update_tools_client, heartbeats_tools
            _update_tools_client()
            return await heartbeats_tools.list_heartbeats(page, page_size, status)
        return list_heartbeats
    
    @tool_registry.register("get_heartbeat_details", requires_write=False)
    def register_get_heartbeat_details(mcp_instance):
        @mcp_instance.tool()
        async def get_heartbeat_details(heartbeat_id: str) -> str:
            """
            Get detailed information about a specific heartbeat monitor.
        
            Shows complete heartbeat configuration including expected ping interval,
            grace period, alert settings, and recent ping history.
        
            Args:
                heartbeat_id: The unique identifier of the heartbeat monitor
        
            Returns:
                JSON with heartbeat details including interval settings, grace period, and ping history.
            """
            from ..mcp_server import _update_tools_client, heartbeats_tools
            _update_tools_client()
            return await heartbeats_tools.get_heartbeat_details(heartbeat_id)
        return get_heartbeat_details
    
    @tool_registry.register("create_heartbeat", requires_write=True)
    def register_create_heartbeat(mcp_instance):
        @mcp_instance.tool()
        async def create_heartbeat(heartbeat_data: dict) -> str:
            """
            Create a new heartbeat monitor for passive monitoring.
        
            Set up monitoring for scheduled tasks, cron jobs, or backup processes
            that should run at regular intervals. You'll receive a unique ping URL
            that your process should hit to confirm successful execution.
        
            Args:
                heartbeat_data: Dictionary with heartbeat configuration including:
                    - name: Heartbeat monitor name
                    - interval: Expected time between pings (e.g., "1h", "1d")
                    - grace_period: Additional time to wait before alerting
                    - alert_channels: Notification channels for missed pings
        
            Returns:
                JSON with created heartbeat details including the unique ping URL.
            """
            from ..mcp_server import _update_tools_client, heartbeats_tools
            _update_tools_client()
            return await heartbeats_tools.create_heartbeat(heartbeat_data)
        return create_heartbeat
    
    @tool_registry.register("update_heartbeat", requires_write=True)
    def register_update_heartbeat(mcp_instance):
        @mcp_instance.tool()
        async def update_heartbeat(heartbeat_id: str, heartbeat_data: dict) -> str:
            """
            Update configuration for an existing heartbeat monitor.
        
            Modify the expected interval, grace period, alert settings, or other
            heartbeat configuration without changing the ping URL.
        
            Args:
                heartbeat_id: The unique identifier of the heartbeat to update
                heartbeat_data: Dictionary with updated heartbeat configuration
        
            Returns:
                JSON with updated heartbeat details.
            """
            from ..mcp_server import _update_tools_client, heartbeats_tools
            _update_tools_client()
            return await heartbeats_tools.update_heartbeat(heartbeat_id, heartbeat_data)
        return update_heartbeat
    
    @tool_registry.register("delete_heartbeat", requires_write=True)
    def register_delete_heartbeat(mcp_instance):
        @mcp_instance.tool()
        async def delete_heartbeat(heartbeat_id: str) -> str:
            """
            Delete a heartbeat monitor permanently.
        
            This stops monitoring for missed pings and removes the heartbeat configuration.
            The ping URL will no longer accept pings.
        
            Args:
                heartbeat_id: The unique identifier of the heartbeat to delete
        
            Returns:
                JSON confirming successful deletion.
            """
            from ..mcp_server import _update_tools_client, heartbeats_tools
            _update_tools_client()
            return await heartbeats_tools.delete_heartbeat(heartbeat_id)
        return delete_heartbeat
    
    @tool_registry.register("send_heartbeat_ping", requires_write=True)
    def register_send_heartbeat_ping(mcp_instance):
        @mcp_instance.tool()
        async def send_heartbeat_ping(heartbeat_id: str) -> str:
            """
            Manually send a ping to a heartbeat monitor.
        
            Useful for testing heartbeat configuration or manually confirming
            a task completed when normal automated pinging isn't possible.
        
            Args:
                heartbeat_id: The unique identifier of the heartbeat to ping
        
            Returns:
                JSON confirming the ping was received and recorded.
            """
            from ..mcp_server import _update_tools_client, heartbeats_tools
            _update_tools_client()
            return await heartbeats_tools.send_heartbeat_ping(heartbeat_id)
        return send_heartbeat_ping
    
    @tool_registry.register("get_heartbeat_logs", requires_write=False)
    def register_get_heartbeat_logs(mcp_instance):
        @mcp_instance.tool()
        async def get_heartbeat_logs(
            heartbeat_id: str,
            from_date: Optional[str] = None,
            to_date: Optional[str] = None,
            page: Optional[int] = None,
            page_size: Optional[int] = None
        ) -> str:
            """
            Get historical ping logs for a heartbeat monitor.
        
            View when pings were received, missed pings, and any alerts that were triggered.
        
            Args:
                heartbeat_id: The unique identifier of the heartbeat
                from_date: Start date for log retrieval (ISO format)
                to_date: End date for log retrieval (ISO format)
                page: Page number for pagination
                page_size: Number of log entries per page
        
            Returns:
                JSON with ping history including timestamps, statuses, and any gaps/missed pings.
            """
            from ..mcp_server import _update_tools_client, heartbeats_tools
            _update_tools_client()
            return await heartbeats_tools.get_heartbeat_logs(
                heartbeat_id, from_date, to_date, page, page_size
            )
        return get_heartbeat_logs
