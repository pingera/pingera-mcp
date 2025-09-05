
"""
MCP tool logic functions for alert management.
"""
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

async def _list_alerts_logic(
    client,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """List all alert configurations in your account."""
    try:
        logger.info(f"Listing alerts - page: {page}, page_size: {page_size}, status: {status}")
        
        with client._get_api_client() as api_client:
            from pingera.api import AlertsApi
            alerts_api = AlertsApi(api_client)
            
            alerts = alerts_api.v1_alerts_get(page=page, page_size=page_size, status=status)
            
            alerts_data = []
            if isinstance(alerts, list):
                for alert in alerts:
                    if hasattr(alert, '__dict__'):
                        alerts_data.append(alert.__dict__)
                    elif hasattr(alert, 'to_dict'):
                        alerts_data.append(alert.to_dict())
                    else:
                        alerts_data.append({"raw_response": str(alert)})
            
            return json.dumps({
                "success": True,
                "alerts": alerts_data,
                "total": len(alerts_data)
            })
            
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "alerts": []
        })

async def _get_alert_details_logic(client, alert_id: str) -> str:
    """Get detailed configuration for a specific alert rule."""
    try:
        logger.info(f"Getting alert details: {alert_id}")
        
        with client._get_api_client() as api_client:
            from pingera.api import AlertsApi
            alerts_api = AlertsApi(api_client)
            
            alert = alerts_api.v1_alerts_alert_id_get(alert_id=alert_id)
            
            alert_data = {}
            if hasattr(alert, '__dict__'):
                alert_data = alert.__dict__
            elif hasattr(alert, 'to_dict'):
                alert_data = alert.to_dict()
            else:
                alert_data = {"raw_response": str(alert)}
            
            return json.dumps({
                "success": True,
                "alert_id": alert_id,
                "alert": alert_data
            })
            
    except Exception as e:
        logger.error(f"Error getting alert details for {alert_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _get_alert_statistics_logic(client) -> str:
    """Get statistical overview of all alert activity."""
    try:
        logger.info("Getting alert statistics")
        
        with client._get_api_client() as api_client:
            from pingera.api import AlertsApi
            alerts_api = AlertsApi(api_client)
            
            stats = alerts_api.v1_alerts_statistics_get()
            
            stats_data = {}
            if hasattr(stats, '__dict__'):
                stats_data = stats.__dict__
            elif hasattr(stats, 'to_dict'):
                stats_data = stats.to_dict()
            else:
                stats_data = {"raw_response": str(stats)}
            
            return json.dumps({
                "success": True,
                "statistics": stats_data
            })
            
    except Exception as e:
        logger.error(f"Error getting alert statistics: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _list_alert_channels_logic(client) -> str:
    """List all configured notification channels for alerts."""
    try:
        logger.info("Listing alert channels")
        
        with client._get_api_client() as api_client:
            from pingera.api import AlertsApi
            alerts_api = AlertsApi(api_client)
            
            channels = alerts_api.v1_alerts_channels_get()
            
            channels_data = []
            if isinstance(channels, list):
                for channel in channels:
                    if hasattr(channel, '__dict__'):
                        channels_data.append(channel.__dict__)
                    elif hasattr(channel, 'to_dict'):
                        channels_data.append(channel.to_dict())
                    else:
                        channels_data.append({"raw_response": str(channel)})
            
            return json.dumps({
                "success": True,
                "channels": channels_data,
                "total": len(channels_data)
            })
            
    except Exception as e:
        logger.error(f"Error listing alert channels: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "channels": []
        })

async def _list_alert_rules_logic(client) -> str:
    """List all alert rules and their trigger conditions."""
    try:
        logger.info("Listing alert rules")
        
        with client._get_api_client() as api_client:
            from pingera.api import AlertsApi
            alerts_api = AlertsApi(api_client)
            
            rules = alerts_api.v1_alerts_rules_get()
            
            rules_data = []
            if isinstance(rules, list):
                for rule in rules:
                    if hasattr(rule, '__dict__'):
                        rules_data.append(rule.__dict__)
                    elif hasattr(rule, 'to_dict'):
                        rules_data.append(rule.to_dict())
                    else:
                        rules_data.append({"raw_response": str(rule)})
            
            return json.dumps({
                "success": True,
                "rules": rules_data,
                "total": len(rules_data)
            })
            
    except Exception as e:
        logger.error(f"Error listing alert rules: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "rules": []
        })

async def _create_alert_logic(client, alert_data: dict) -> str:
    """Create a new alert rule to get notified when issues are detected."""
    try:
        logger.info(f"Creating alert with data: {alert_data}")
        
        with client._get_api_client() as api_client:
            from pingera.api import AlertsApi
            from pingera.models import Alert
            alerts_api = AlertsApi(api_client)
            
            alert_model = Alert(**alert_data)
            result = alerts_api.v1_alerts_post(alert=alert_model)
            
            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}
            
            return json.dumps({
                "success": True,
                "alert": result_data
            })
            
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _update_alert_logic(client, alert_id: str, alert_data: dict) -> str:
    """Update configuration for an existing alert rule."""
    try:
        logger.info(f"Updating alert {alert_id} with data: {alert_data}")
        
        with client._get_api_client() as api_client:
            from pingera.api import AlertsApi
            from pingera.models import Alert
            alerts_api = AlertsApi(api_client)
            
            alert_model = Alert(**alert_data)
            result = alerts_api.v1_alerts_alert_id_put(alert_id=alert_id, alert=alert_model)
            
            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}
            
            return json.dumps({
                "success": True,
                "alert_id": alert_id,
                "alert": result_data
            })
            
    except Exception as e:
        logger.error(f"Error updating alert {alert_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _delete_alert_logic(client, alert_id: str) -> str:
    """Delete an alert rule permanently."""
    try:
        logger.info(f"Deleting alert: {alert_id}")
        
        with client._get_api_client() as api_client:
            from pingera.api import AlertsApi
            alerts_api = AlertsApi(api_client)
            
            alerts_api.v1_alerts_alert_id_delete(alert_id=alert_id)
            
            return json.dumps({
                "success": True,
                "deleted": True,
                "alert_id": alert_id,
                "message": f"Alert {alert_id} deleted successfully"
            })
            
    except Exception as e:
        logger.error(f"Error deleting alert {alert_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })
