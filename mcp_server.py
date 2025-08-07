"""
MCP Server implementation for Pingera monitoring service.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, Tool, TextContent

from config import Config
from pingera import PingeraClient, PingeraError, Page, PageList


def create_mcp_server(config: Config) -> FastMCP:
    """
    Create and configure the MCP server for Pingera.
    
    Args:
        config: Configuration object
        
    Returns:
        FastMCP: Configured MCP server
    """
    logger = logging.getLogger(__name__)
    
    # Initialize Pingera client
    pingera_client = PingeraClient(
        api_key=config.api_key,
        base_url=config.base_url,
        timeout=config.timeout,
        max_retries=config.max_retries
    )
    
    # Create MCP server
    mcp = FastMCP(config.server_name)
    
    @mcp.resource("pingera://pages")
    async def get_pages_resource() -> str:
        """
        Resource providing access to all monitored pages.
        
        Returns:
            str: JSON string containing all pages
        """
        try:
            logger.info("Fetching pages resource")
            pages = pingera_client.get_pages()
            
            # Convert to dict for JSON serialization
            pages_data = {
                "pages": [page.dict() for page in pages.pages],
                "total": pages.total,
                "page": pages.page,
                "per_page": pages.per_page
            }
            
            return json.dumps(pages_data, indent=2, default=str)
            
        except PingeraError as e:
            logger.error(f"Error fetching pages resource: {e}")
            return json.dumps({
                "error": str(e),
                "pages": [],
                "total": 0
            }, indent=2)
    
    @mcp.resource("pingera://pages/{page_id}")
    async def get_page_resource(page_id: str) -> str:
        """
        Resource providing access to a specific page.
        
        Args:
            page_id: ID of the page to retrieve
            
        Returns:
            str: JSON string containing page details
        """
        try:
            logger.info(f"Fetching page resource for ID: {page_id}")
            page_id_int = int(page_id)
            page = pingera_client.get_page(page_id_int)
            
            return json.dumps(page.dict(), indent=2, default=str)
            
        except ValueError:
            logger.error(f"Invalid page ID: {page_id}")
            return json.dumps({
                "error": f"Invalid page ID: {page_id}",
                "page": None
            }, indent=2)
        except PingeraError as e:
            logger.error(f"Error fetching page resource {page_id}: {e}")
            return json.dumps({
                "error": str(e),
                "page": None
            }, indent=2)
    
    @mcp.resource("pingera://status")
    async def get_status_resource() -> str:
        """
        Resource providing Pingera API connection status.
        
        Returns:
            str: JSON string containing status information
        """
        try:
            logger.info("Fetching status resource")
            api_info = pingera_client.get_api_info()
            
            return json.dumps({
                "mode": config.mode.value,
                "api_info": api_info,
                "features": {
                    "read_operations": True,
                    "write_operations": config.is_read_write()
                }
            }, indent=2)
            
        except Exception as e:
            logger.error(f"Error fetching status resource: {e}")
            return json.dumps({
                "mode": config.mode.value,
                "error": str(e),
                "features": {
                    "read_operations": False,
                    "write_operations": False
                }
            }, indent=2)
    
    @mcp.tool()
    async def list_pages(
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        status: Optional[str] = None
    ) -> str:
        """
        List monitored pages from Pingera.
        
        Args:
            page: Page number for pagination
            per_page: Number of items per page (max 100)
            status: Filter by page status
            
        Returns:
            str: JSON string containing list of pages
        """
        try:
            logger.info(f"Listing pages - page: {page}, per_page: {per_page}, status: {status}")
            
            # Validate parameters
            if per_page is not None and per_page > 100:
                per_page = 100
            
            pages = pingera_client.get_pages(
                page=page,
                per_page=per_page,
                status=status
            )
            
            result = {
                "success": True,
                "data": {
                    "pages": [page.dict() for page in pages.pages],
                    "total": pages.total,
                    "page": pages.page,
                    "per_page": pages.per_page
                }
            }
            
            return json.dumps(result, indent=2, default=str)
            
        except PingeraError as e:
            logger.error(f"Error listing pages: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "data": {"pages": [], "total": 0}
            }, indent=2)
    
    @mcp.tool()
    async def get_page_details(page_id: int) -> str:
        """
        Get detailed information about a specific page.
        
        Args:
            page_id: ID of the page to retrieve
            
        Returns:
            str: JSON string containing page details
        """
        try:
            logger.info(f"Getting page details for ID: {page_id}")
            page = pingera_client.get_page(page_id)
            
            result = {
                "success": True,
                "data": page.dict()
            }
            
            return json.dumps(result, indent=2, default=str)
            
        except PingeraError as e:
            logger.error(f"Error getting page details for {page_id}: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "data": None
            }, indent=2)
    
    @mcp.tool()
    async def test_pingera_connection() -> str:
        """
        Test connection to Pingera API.
        
        Returns:
            str: JSON string containing connection test results
        """
        try:
            logger.info("Testing Pingera connection")
            is_connected = pingera_client.test_connection()
            api_info = pingera_client.get_api_info()
            
            result = {
                "success": True,
                "data": {
                    "connected": is_connected,
                    "api_info": api_info,
                    "server_mode": config.mode.value
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "data": {"connected": False}
            }, indent=2)
    
    # Add write operations only if in read-write mode
    if config.is_read_write():
        logger.info("Read-write mode enabled - write operations will be available when implemented")
        
        @mcp.tool()
        async def placeholder_write_operation() -> str:
            """
            Placeholder for future write operations.
            
            Returns:
                str: Information about write operations
            """
            return json.dumps({
                "success": True,
                "message": "Write operations are available in this mode but not yet implemented. Future features will include creating, updating, and deleting monitored pages.",
                "mode": "read_write"
            }, indent=2)
    
    return mcp
