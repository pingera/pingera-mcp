#!/usr/bin/env python3
"""
Test script to demonstrate Pingera MCP Server functionality.
"""
import asyncio
import json
import os
from mcp import ServerSession
from mcp.types import ReadResourceRequest, CallToolRequest

async def test_mcp_server():
    """Test the MCP server functionality."""
    print("🔧 Testing Pingera MCP Server functionality...")
    
    # Import and create server
    from config import Config
    from mcp_server import create_mcp_server
    
    config = Config()
    server = create_mcp_server(config)
    
    print(f"✓ Server created in {config.mode.value} mode")
    
    # Test resource access
    try:
        # Test pages resource
        pages_resource = await server._read_resource(ReadResourceRequest(uri="pingera://pages"))
        print(f"✓ Pages resource accessible - content length: {len(pages_resource.contents[0].text)} chars")
        
        # Parse and show summary
        pages_data = json.loads(pages_resource.contents[0].text)
        if 'pages' in pages_data:
            print(f"✓ Found {len(pages_data['pages'])} monitored pages")
            for i, page in enumerate(pages_data['pages'][:3]):  # Show first 3
                print(f"  - {page['name']} ({page['id']})")
        
        # Test status resource
        status_resource = await server._read_resource(ReadResourceRequest(uri="pingera://status"))
        status_data = json.loads(status_resource.contents[0].text)
        print(f"✓ Status resource: {status_data['mode']}, API connected: {status_data['api_info']['connected']}")
        
        # Test specific page resource
        if pages_data.get('pages'):
            first_page_id = pages_data['pages'][0]['id']
            page_resource = await server._read_resource(ReadResourceRequest(uri=f"pingera://pages/{first_page_id}"))
            page_data = json.loads(page_resource.contents[0].text)
            print(f"✓ Individual page resource: {page_data['name']}")
        
    except Exception as e:
        print(f"❌ Resource test failed: {e}")
    
    # Test tool functionality
    try:
        # Test list_pages tool
        list_result = await server._call_tool(CallToolRequest(name="list_pages", arguments={"per_page": 5}))
        list_data = json.loads(list_result.content[0].text)
        print(f"✓ list_pages tool: {len(list_data['data']['pages'])} pages returned")
        
        # Test connection test tool
        conn_result = await server._call_tool(CallToolRequest(name="test_pingera_connection", arguments={}))
        conn_data = json.loads(conn_result.content[0].text)
        print(f"✓ Connection test: {conn_data['data']['connected']}")
        
        # Test get_page_details tool
        if pages_data.get('pages'):
            first_page_id = pages_data['pages'][0]['id']
            # Convert string ID to what the API expects
            try:
                detail_result = await server._call_tool(CallToolRequest(
                    name="get_page_details", 
                    arguments={"page_id": first_page_id}  # Try with string ID
                ))
                detail_data = json.loads(detail_result.content[0].text)
                if detail_data.get('success'):
                    print(f"✓ Page details tool: {detail_data['data']['name']}")
                else:
                    print(f"⚠ Page details tool returned error: {detail_data.get('error')}")
            except Exception as e:
                print(f"⚠ Page details tool error: {e}")
        
        # Show available features based on mode
        if config.is_read_write():
            print("✓ Read-write mode: Write operations would be available")
        else:
            print("✓ Read-only mode: Only read operations available")
        
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 MCP Server testing completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())