
"""
Tests for MCP server functionality.
"""
import json
import pytest
from unittest.mock import Mock, patch, AsyncMock

from mcp_server import create_mcp_server
from pingera import PingeraError


class TestMCPServer:
    """Test cases for MCP server."""
    
    @pytest.fixture
    def server(self, mock_config):
        """Create MCP server for testing."""
        with patch('mcp_server.PingeraClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            return create_mcp_server(mock_config), mock_client
    
    @pytest.mark.asyncio
    async def test_pages_resource_success(self, server, mock_page_list):
        """Test successful pages resource retrieval."""
        mcp_server, mock_client = server
        mock_client.get_pages.return_value = mock_page_list
        
        # Get the resource function
        resource_func = None
        for resource in mcp_server._resources:
            if resource.uri == "pingera://pages":
                resource_func = resource.read
                break
        
        assert resource_func is not None
        result = await resource_func()
        
        # Parse and verify the result
        data = json.loads(result)
        assert "pages" in data
        assert len(data["pages"]) == 1
        assert data["pages"][0]["name"] == "Test Page"
        assert data["total"] == 1
    
    @pytest.mark.asyncio
    async def test_pages_resource_error(self, server):
        """Test pages resource with API error."""
        mcp_server, mock_client = server
        mock_client.get_pages.side_effect = PingeraError("API Error")
        
        # Get the resource function
        resource_func = None
        for resource in mcp_server._resources:
            if resource.uri == "pingera://pages":
                resource_func = resource.read
                break
        
        assert resource_func is not None
        result = await resource_func()
        
        # Parse and verify error handling
        data = json.loads(result)
        assert "error" in data
        assert data["error"] == "API Error"
        assert data["pages"] == []
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_status_resource(self, server):
        """Test status resource."""
        mcp_server, mock_client = server
        mock_client.get_api_info.return_value = {
            "connected": True,
            "message": "Pingera.ru API",
            "authentication": "Create API token at https://app.pingera.ru to authorize and use this API",
            "documentation": "https://docs.pingera.ru/api/overview",
            "api_version": "v1"
        }
        
        # Get the resource function
        resource_func = None
        for resource in mcp_server._resources:
            if resource.uri == "pingera://status":
                resource_func = resource.read
                break
        
        assert resource_func is not None
        result = await resource_func()
        
        # Parse and verify the result
        data = json.loads(result)
        assert data["mode"] == "read_only"
        assert data["api_info"]["connected"] is True
        assert data["api_info"]["message"] == "Pingera.ru API"
        assert data["features"]["read_operations"] is True
        assert data["features"]["write_operations"] is False
    
    @pytest.mark.asyncio
    async def test_list_pages_tool(self, server, mock_page_list):
        """Test list_pages tool."""
        mcp_server, mock_client = server
        mock_client.get_pages.return_value = mock_page_list
        
        # Find the list_pages tool
        list_pages_tool = None
        for tool in mcp_server._tools:
            if tool.name == "list_pages":
                list_pages_tool = tool.handler
                break
        
        assert list_pages_tool is not None
        result = await list_pages_tool(page=1, per_page=10)
        
        # Parse and verify the result
        data = json.loads(result)
        assert data["success"] is True
        assert len(data["data"]["pages"]) == 1
        assert data["data"]["pages"][0]["name"] == "Test Page"
    
    @pytest.mark.asyncio
    async def test_test_connection_tool(self, server):
        """Test connection test tool."""
        mcp_server, mock_client = server
        mock_client.test_connection.return_value = True
        mock_client.get_api_info.return_value = {
            "connected": True,
            "message": "Pingera.ru API",
            "api_version": "v1"
        }
        
        # Find the test_pingera_connection tool
        test_conn_tool = None
        for tool in mcp_server._tools:
            if tool.name == "test_pingera_connection":
                test_conn_tool = tool.handler
                break
        
        assert test_conn_tool is not None
        result = await test_conn_tool()
        
        # Parse and verify the result
        data = json.loads(result)
        assert data["success"] is True
        assert data["data"]["connected"] is True
        assert data["data"]["api_info"]["message"] == "Pingera.ru API"
    
    def test_read_write_mode_adds_write_tools(self, mock_config):
        """Test that read-write mode adds write operation tools."""
        mock_config.mode = mock_config.mode.READ_WRITE
        
        with patch('mcp_server.PingeraClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            server = create_mcp_server(mock_config)
            
            # Check that placeholder write operation tool is added
            tool_names = [tool.name for tool in server._tools]
            assert "placeholder_write_operation" in tool_names
