
"""
MCP tool logic functions for heartbeat monitoring.
"""
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

async def _list_heartbeats_logic(
    client,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[str] = None
) -> str:
    """List all heartbeat monitors in your account."""
    try:
        logger.info(f"Listing heartbeats - page: {page}, page_size: {page_size}, status: {status}")
        
        with client._get_api_client() as api_client:
            from pingera.api import HeartbeatsApi
            heartbeats_api = HeartbeatsApi(api_client)
            
            heartbeats = heartbeats_api.v1_heartbeats_get(page=page, page_size=page_size, status=status)
            
            heartbeats_data = []
            if isinstance(heartbeats, list):
                for heartbeat in heartbeats:
                    if hasattr(heartbeat, '__dict__'):
                        heartbeats_data.append(heartbeat.__dict__)
                    elif hasattr(heartbeat, 'to_dict'):
                        heartbeats_data.append(heartbeat.to_dict())
                    else:
                        heartbeats_data.append({"raw_response": str(heartbeat)})
            
            return json.dumps({
                "success": True,
                "heartbeats": heartbeats_data,
                "total": len(heartbeats_data)
            })
            
    except Exception as e:
        logger.error(f"Error listing heartbeats: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "heartbeats": []
        })

async def _get_heartbeat_details_logic(client, heartbeat_id: str) -> str:
    """Get detailed information about a specific heartbeat monitor."""
    try:
        logger.info(f"Getting heartbeat details: {heartbeat_id}")
        
        with client._get_api_client() as api_client:
            from pingera.api import HeartbeatsApi
            heartbeats_api = HeartbeatsApi(api_client)
            
            heartbeat = heartbeats_api.v1_heartbeats_heartbeat_id_get(heartbeat_id=heartbeat_id)
            
            heartbeat_data = {}
            if hasattr(heartbeat, '__dict__'):
                heartbeat_data = heartbeat.__dict__
            elif hasattr(heartbeat, 'to_dict'):
                heartbeat_data = heartbeat.to_dict()
            else:
                heartbeat_data = {"raw_response": str(heartbeat)}
            
            return json.dumps({
                "success": True,
                "heartbeat_id": heartbeat_id,
                "heartbeat": heartbeat_data
            })
            
    except Exception as e:
        logger.error(f"Error getting heartbeat details for {heartbeat_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _create_heartbeat_logic(client, heartbeat_data: dict) -> str:
    """Create a new heartbeat monitor for cron jobs or scheduled tasks."""
    try:
        logger.info(f"Creating heartbeat with data: {heartbeat_data}")
        
        with client._get_api_client() as api_client:
            from pingera.api import HeartbeatsApi
            from pingera.models import Heartbeat
            heartbeats_api = HeartbeatsApi(api_client)
            
            heartbeat_model = Heartbeat(**heartbeat_data)
            result = heartbeats_api.v1_heartbeats_post(heartbeat=heartbeat_model)
            
            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}
            
            return json.dumps({
                "success": True,
                "heartbeat": result_data
            })
            
    except Exception as e:
        logger.error(f"Error creating heartbeat: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _update_heartbeat_logic(client, heartbeat_id: str, heartbeat_data: dict) -> str:
    """Update configuration for an existing heartbeat monitor."""
    try:
        logger.info(f"Updating heartbeat {heartbeat_id} with data: {heartbeat_data}")
        
        with client._get_api_client() as api_client:
            from pingera.api import HeartbeatsApi
            from pingera.models import Heartbeat
            heartbeats_api = HeartbeatsApi(api_client)
            
            heartbeat_model = Heartbeat(**heartbeat_data)
            result = heartbeats_api.v1_heartbeats_heartbeat_id_put(heartbeat_id=heartbeat_id, heartbeat=heartbeat_model)
            
            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}
            
            return json.dumps({
                "success": True,
                "heartbeat_id": heartbeat_id,
                "heartbeat": result_data
            })
            
    except Exception as e:
        logger.error(f"Error updating heartbeat {heartbeat_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _delete_heartbeat_logic(client, heartbeat_id: str) -> str:
    """Delete a heartbeat monitor permanently."""
    try:
        logger.info(f"Deleting heartbeat: {heartbeat_id}")
        
        with client._get_api_client() as api_client:
            from pingera.api import HeartbeatsApi
            heartbeats_api = HeartbeatsApi(api_client)
            
            heartbeats_api.v1_heartbeats_heartbeat_id_delete(heartbeat_id=heartbeat_id)
            
            return json.dumps({
                "success": True,
                "deleted": True,
                "heartbeat_id": heartbeat_id,
                "message": f"Heartbeat {heartbeat_id} deleted successfully"
            })
            
    except Exception as e:
        logger.error(f"Error deleting heartbeat {heartbeat_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _send_heartbeat_ping_logic(client, heartbeat_id: str) -> str:
    """Manually send a ping signal to a heartbeat monitor."""
    try:
        logger.info(f"Sending ping to heartbeat: {heartbeat_id}")
        
        with client._get_api_client() as api_client:
            from pingera.api import HeartbeatsApi
            heartbeats_api = HeartbeatsApi(api_client)
            
            result = heartbeats_api.v1_heartbeats_heartbeat_id_ping_post(heartbeat_id=heartbeat_id)
            
            result_data = {}
            if hasattr(result, '__dict__'):
                result_data = result.__dict__
            elif hasattr(result, 'to_dict'):
                result_data = result.to_dict()
            else:
                result_data = {"raw_response": str(result)}
            
            return json.dumps({
                "success": True,
                "heartbeat_id": heartbeat_id,
                "ping": result_data
            })
            
    except Exception as e:
        logger.error(f"Error sending ping to heartbeat {heartbeat_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        })

async def _get_heartbeat_logs_logic(
    client,
    heartbeat_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None
) -> str:
    """Get historical ping logs and activity for a heartbeat monitor."""
    try:
        logger.info(f"Getting heartbeat logs for: {heartbeat_id}")
        
        with client._get_api_client() as api_client:
            from pingera.api import HeartbeatsApi
            heartbeats_api = HeartbeatsApi(api_client)
            
            logs = heartbeats_api.v1_heartbeats_heartbeat_id_logs_get(
                heartbeat_id=heartbeat_id,
                var_from=from_date,
                to=to_date,
                page=page,
                page_size=page_size
            )
            
            logs_data = []
            if isinstance(logs, list):
                for log in logs:
                    if hasattr(log, '__dict__'):
                        logs_data.append(log.__dict__)
                    elif hasattr(log, 'to_dict'):
                        logs_data.append(log.to_dict())
                    else:
                        logs_data.append({"raw_response": str(log)})
            
            return json.dumps({
                "success": True,
                "heartbeat_id": heartbeat_id,
                "logs": logs_data,
                "total": len(logs_data)
            })
            
    except Exception as e:
        logger.error(f"Error getting heartbeat logs for {heartbeat_id}: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "logs": []
        })
