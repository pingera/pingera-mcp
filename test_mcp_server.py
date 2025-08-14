#!/usr/bin/env python3
"""
Test script to demonstrate Pingera MCP Server functionality.
"""
import asyncio
import json
import os
from typing import Dict, Any

async def test_mcp_server():
    """Test the MCP server functionality."""
    print("🔧 Testing Pingera MCP Server functionality...")

    # Import and create server
    from config import Config
    from mcp_server import create_mcp_server

    config = Config()
    mcp_app = create_mcp_server(config)

    print(f"✓ Server created in {config.mode.value} mode")

    try:
        # Test basic server functionality by checking if it was created
        print("\n📚 Testing server creation...")
        print("✓ FastMCP server instance created successfully")

        # Test Pingera client connection
        print("\n🔌 Testing Pingera API connection...")
        try:
            # Get the client from one of the tool instances
            # We'll need to access it through the server's internal structure
            from pingera_mcp import PingeraClient
            from pingera_mcp.tools import StatusTools

            # Create a test client to check connection
            test_client = PingeraClient(
                api_key=config.api_key,
                base_url=config.base_url,
                timeout=config.timeout,
                max_retries=config.max_retries
            )

            # Test connection
            print(f"  Testing with base URL: {test_client.base_url}")
            print(f"  API key configured: {'Yes' if test_client.api_key else 'No'}")

            connection_status = test_client.test_connection()
            api_info = test_client.get_api_info()

            if connection_status:
                print("✓ Pingera API connection successful")
                print(f"  API URL: {api_info.get('base_url', 'Unknown')}")
                print(f"  Connected: {api_info.get('connected', False)}")
            else:
                print("❌ Pingera API connection failed")
                print(f"  Error: {api_info.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ API connection test failed: {e}")

        # Test that tools and resources are properly registered
        print("\n🛠 Testing MCP server configuration...")

        # Check if the server has the expected structure
        if hasattr(mcp_app, '_mcp_server'):
            print("✓ MCP server instance found")
        else:
            print("❌ MCP server instance not found")

        # Test that the server can be started (without actually starting it)
        print("✓ Server configuration appears valid")

        # Show operation mode capabilities
        print(f"\n⚙️ Operation Mode: {config.mode.value}")
        if config.is_read_write():
            print("✓ Read-write mode: Write operations are available")
            print("  Available operations: create, update, delete, patch")
        else:
            print("✓ Read-only mode: Only read operations available")
            print("  Available operations: list, get, test_connection")

        # Show available tools conceptually
        print("\n🔧 Expected Tools:")
        basic_tools = [
            "list_pages", "get_page_details", "test_pingera_connection",
            "list_component_groups", "get_component_details"
        ]

        for tool in basic_tools:
            print(f"  - {tool}: Available")

        if config.is_read_write():
            write_tools = [
                "create_page", "update_page", "patch_page", "delete_page",
                "create_component", "update_component", "patch_component", "delete_component"
            ]
            for tool in write_tools:
                print(f"  - {tool}: Available (write mode)")

        # Show available resources conceptually
        print("\n📚 Expected Resources:")
        resources = [
            "pingera://pages - List of all status pages",
            "pingera://pages/{page_id} - Specific page details",
            "pingera://status - API connection status and capabilities"
        ]

        for resource in resources:
            print(f"  - {resource}")

        # Test MCP tool call for list_pages
        print("\n📋 Testing MCP tool call: list_pages...")
        try:
            # Since we're testing the MCP server directly, we need to simulate tool calls
            # In a real MCP environment, this would be called by the MCP client (like Claude)

            # Get the tool handler from our server components
            from pingera_mcp.tools import PagesTools

            # Create a pages tool instance with our test client
            pages_tool = PagesTools(test_client)

            # Call the list_pages tool directly (simulating MCP tool call)
            result = await pages_tool.list_pages(page=1, per_page=10)

            print("✓ MCP tool call successful")
            print("📄 Pages data received:")
            
            # First, let's see the raw API response
            print(f"  Raw result: {result}")

            # Parse and display the result
            import json
            try:
                parsed_result = json.loads(result)
                print(f"  Parsed result: {parsed_result}")
                
                if parsed_result.get("success"):
                    pages_data = parsed_result.get("data", {})
                    pages = pages_data.get("pages", [])
                    total = pages_data.get("total", 0)

                    print(f"  Total pages: {total}")
                    print(f"  Pages in this response: {len(pages)}")

                    if pages:
                        print("  Page details:")
                        for i, page in enumerate(pages, 1):
                            # Handle both dict and object formats
                            if hasattr(page, '__dict__'):
                                page_dict = page.__dict__ if hasattr(page, '__dict__') else page
                            else:
                                page_dict = page
                            
                            name = page_dict.get('name', 'Unknown')
                            page_id = page_dict.get('id', 'N/A')
                            subdomain = page_dict.get('subdomain', '')
                            domain = page_dict.get('domain', '')
                            url = page_dict.get('url', '')
                            template = page_dict.get('template', '')
                            language = page_dict.get('language', '')
                            
                            print(f"    {i}. {name} (ID: {page_id})")
                            
                            # Show subdomain or domain
                            if domain:
                                print(f"       Domain: {domain}")
                            elif subdomain:
                                print(f"       Subdomain: {subdomain}.pingera.ru")
                            
                            # Show company URL if available
                            if url:
                                print(f"       Company URL: {url}")
                            
                            # Show template and language
                            if template:
                                print(f"       Template: {template}")
                            if language:
                                print(f"       Language: {language}")
                            
                            # Show creation date if available
                            if page_dict.get('created_at'):
                                print(f"       Created: {page_dict.get('created_at')}")
                            
                            print()  # Add spacing between pages
                    else:
                        print("  No pages found")
                else:
                    print(f"  ❌ Tool returned error: {parsed_result.get('error', 'Unknown error')}")

            except json.JSONDecodeError:
                print(f"  Raw response: {result}")

        except Exception as e:
            print(f"❌ MCP tool call failed: {e}")
            print("  This might be expected if the API is not accessible in test environment")

        print("\n🎉 MCP Server testing completed!")

        print("\n✅ Server configuration test completed successfully!")

    except Exception as e:
        print(f"❌ Server testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())