
"""Tool registration functions for alerts domain."""

from typing import Optional
from ..tool_registry import tool_registry


def register_alerts_tools():
    """Register all alerts-related tools."""
    
    @tool_registry.register("list_alerts", requires_write=False)
    def register_list_alerts(mcp_instance):
        @mcp_instance.tool()
        async def list_alerts(
            page: Optional[int] = None,
            page_size: Optional[int] = None,
            status: Optional[str] = None
        ) -> str:
            """
            List all alert configurations in your account.
        
            Alerts are rules that trigger notifications when monitoring checks fail
            or meet specific conditions. Each alert can be configured with different
            channels, thresholds, and escalation rules.
        
            Args:
                page: Page number for pagination
                page_size: Number of alerts per page
                status: Filter by alert status ('active', 'paused', 'disabled')
        
            Returns:
                JSON with list of alerts including names, conditions, notification channels, and status.
            """
            from ..mcp_server import _update_tools_client, alerts_tools
            _update_tools_client()
            return await alerts_tools.list_alerts(page, page_size, status)
        return list_alerts
    
    @tool_registry.register("get_alert_details", requires_write=False)
    def register_get_alert_details(mcp_instance):
        @mcp_instance.tool()
        async def get_alert_details(alert_id: str) -> str:
            """
            Get detailed configuration for a specific alert rule.
        
            Shows complete alert setup including trigger conditions, notification
            channels, escalation rules, and recent activity.
        
            Args:
                alert_id: The unique identifier of the alert rule
        
            Returns:
                JSON with alert details including conditions, channels, thresholds, and escalation settings.
            """
            from ..mcp_server import _update_tools_client, alerts_tools
            _update_tools_client()
            return await alerts_tools.get_alert_details(alert_id)
        return get_alert_details
    
    @tool_registry.register("get_alert_statistics", requires_write=False)
    def register_get_alert_statistics(mcp_instance):
        @mcp_instance.tool()
        async def get_alert_statistics() -> str:
            """
            Get statistical overview of all alert activity.
        
            Provides summary of alert triggers, resolution times, most frequently
            triggered alerts, and overall notification volume.
        
            Returns:
                JSON with alert statistics including trigger counts, avg resolution time, and trends.
            """
            from ..mcp_server import _update_tools_client, alerts_tools
            _update_tools_client()
            return await alerts_tools.get_alert_statistics()
        return get_alert_statistics
    
    @tool_registry.register("list_alert_channels", requires_write=False)
    def register_list_alert_channels(mcp_instance):
        @mcp_instance.tool()
        async def list_alert_channels() -> str:
            """
            List all configured notification channels for alerts.
        
            Shows available notification methods like email, SMS, webhooks,
            and their configuration status. These channels are used by alert rules
            to deliver notifications when issues are detected.
        
            Returns:
                JSON with list of notification channels including types, names, and status.
            """
            from ..mcp_server import _update_tools_client, alerts_tools
            _update_tools_client()
            return await alerts_tools.list_alert_channels()
        return list_alert_channels
    
    @tool_registry.register("list_alert_rules", requires_write=False)
    def register_list_alert_rules(mcp_instance):
        @mcp_instance.tool()
        async def list_alert_rules() -> str:
            """
            List all alert rules and their trigger conditions.
        
            Shows the specific conditions and thresholds that will trigger each alert,
            including response time requirements, uptime requirements, and error conditions.
        
            Returns:
                JSON with list of alert rules including conditions, thresholds, and linked checks.
            """
            from ..mcp_server import _update_tools_client, alerts_tools
            _update_tools_client()
            return await alerts_tools.list_alert_rules()
        return list_alert_rules
    
    @tool_registry.register("create_alert", requires_write=True)
    def register_create_alert(mcp_instance):
        @mcp_instance.tool()
        async def create_alert(alert_data: dict) -> str:
            """
            Create a new alert rule to get notified when issues are detected.
        
            Set up notifications that will be sent when monitoring checks fail
            or meet specific conditions like response time thresholds.
        
            Args:
                alert_data: Dictionary with alert configuration including:
                    - name: Alert rule name
                    - check_ids: List of checks this alert applies to
                    - conditions: Trigger conditions (failures, response time, etc.)
                    - channels: Notification channels (email, SMS, webhook, etc.)
                    - escalation: Escalation rules and delays
        
            Returns:
                JSON with created alert rule details and configuration.
            """
            from ..mcp_server import _update_tools_client, alerts_tools
            _update_tools_client()
            return await alerts_tools.create_alert(alert_data)
        return create_alert
    
    @tool_registry.register("update_alert", requires_write=True)
    def register_update_alert(mcp_instance):
        @mcp_instance.tool()
        async def update_alert(alert_id: str, alert_data: dict) -> str:
            """
            Update configuration for an existing alert rule.
        
            Modify alert conditions, notification channels, escalation rules,
            or which checks the alert applies to.
        
            Args:
                alert_id: The unique identifier of the alert rule to update
                alert_data: Dictionary with updated alert configuration
        
            Returns:
                JSON with updated alert rule details and configuration.
            """
            from ..mcp_server import _update_tools_client, alerts_tools
            _update_tools_client()
            return await alerts_tools.update_alert(alert_id, alert_data)
        return update_alert
    
    @tool_registry.register("delete_alert", requires_write=True)
    def register_delete_alert(mcp_instance):
        @mcp_instance.tool()
        async def delete_alert(alert_id: str) -> str:
            """
            Delete an alert rule permanently.
        
            This stops all notifications from this alert rule and removes
            the configuration. Historical alert activity may be preserved.
        
            Args:
                alert_id: The unique identifier of the alert rule to delete
        
            Returns:
                JSON confirming successful deletion.
            """
            from ..mcp_server import _update_tools_client, alerts_tools
            _update_tools_client()
            return await alerts_tools.delete_alert(alert_id)
        return delete_alert
