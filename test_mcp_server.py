
#!/usr/bin/env python3
"""
Test script to demonstrate Pingera MCP Server functionality.
"""
import asyncio
import json
import os
from mcp.server import Server
from mcp.types import (
    ReadResourceRequest, 
    CallToolRequest, 
    ListResourcesRequest,
    ListToolsRequest
)

async def test_mcp_server():
    """Test the MCP server functionality."""
    print("🔧 Testing Pingera MCP Server functionality...")
    
    # Import and create server
    from config import Config
    from mcp_server import create_mcp_server
    
    config = Config()
    mcp_app = create_mcp_server(config)
    
    print(f"✓ Server created in {config.mode.value} mode")
    
    # Get the actual MCP server instance from FastMCP
    server = mcp_app._mcp_server
    
    try:
        # Test listing available resources
        print("\n📚 Testing available resources...")
        resources_result = await server.list_resources()
        resources = resources_result.resources
        print(f"✓ Found {len(resources)} available resources:")
        for resource in resources:
            print(f"  - {resource.uri}: {resource.description or 'No description'}")
        
        # Test listing available tools
        print("\n🔧 Testing available tools...")
        tools_result = await server.list_tools()
        tools = tools_result.tools
        print(f"✓ Found {len(tools)} available tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description or 'No description'}")
        
        # Test reading a resource (if available)
        if resources:
            print("\n📖 Testing resource reading...")
            test_resource = resources[0]  # Test the first available resource
            try:
                read_result = await server.read_resource(
                    ReadResourceRequest(uri=test_resource.uri)
                )
                if read_result.contents:
                    content = read_result.contents[0]
                    if hasattr(content, 'text'):
                        print(f"✓ Resource read successfully - content length: {len(content.text)} chars")
                        # Try to parse as JSON to show some data
                        try:
                            data = json.loads(content.text)
                            if isinstance(data, dict):
                                print(f"  Resource contains: {list(data.keys())}")
                        except json.JSONDecodeError:
                            print("  Resource contains non-JSON text data")
                    else:
                        print(f"✓ Resource read successfully - content type: {type(content)}")
                else:
                    print("⚠ Resource read returned empty content")
            except Exception as e:
                print(f"❌ Failed to read resource {test_resource.uri}: {e}")
        
        # Test calling a tool (if available)
        if tools:
            print("\n🛠 Testing tool execution...")
            # Find a simple tool to test
            test_tools = ['test_pingera_connection', 'list_pages']
            tool_to_test = None
            
            for tool_name in test_tools:
                if any(tool.name == tool_name for tool in tools):
                    tool_to_test = tool_name
                    break
            
            if tool_to_test:
                try:
                    if tool_to_test == 'list_pages':
                        call_result = await server.call_tool(
                            CallToolRequest(name=tool_to_test, arguments={"per_page": 5})
                        )
                    else:
                        call_result = await server.call_tool(
                            CallToolRequest(name=tool_to_test, arguments={})
                        )
                    
                    if call_result.content:
                        content = call_result.content[0]
                        if hasattr(content, 'text'):
                            print(f"✓ Tool '{tool_to_test}' executed successfully")
                            # Try to parse and show result
                            try:
                                result = json.loads(content.text)
                                if result.get('success'):
                                    print(f"  Tool result: {result.get('data', 'No data')}")
                                else:
                                    print(f"  Tool error: {result.get('error', 'Unknown error')}")
                            except json.JSONDecodeError:
                                print(f"  Tool returned: {content.text[:100]}...")
                        else:
                            print(f"✓ Tool '{tool_to_test}' executed - content type: {type(content)}")
                    else:
                        print(f"⚠ Tool '{tool_to_test}' returned empty content")
                except Exception as e:
                    print(f"❌ Failed to call tool '{tool_to_test}': {e}")
            else:
                print("⚠ No suitable test tools found")
        
        # Show operation mode capabilities
        print(f"\n⚙️ Operation Mode: {config.mode.value}")
        if config.is_read_write():
            print("✓ Read-write mode: Write operations are available")
            write_tools = [tool.name for tool in tools if any(
                op in tool.name for op in ['create', 'update', 'delete', 'patch']
            )]
            if write_tools:
                print(f"  Write tools available: {', '.join(write_tools[:5])}")
        else:
            print("✓ Read-only mode: Only read operations available")
        
    except Exception as e:
        print(f"❌ Server testing failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 MCP Server testing completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
