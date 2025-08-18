
#!/usr/bin/env python3
"""
Simple MCP client to test Pingera MCP Server with Gemini.
"""
import asyncio
import os
import json
import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure MCP server parameters to match README setup
server_params = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "--with",
        "pingera-mcp-server",
        "--python",
        "3.10",
        "pingera-mcp"
    ],
    env={
        "PINGERA_API_KEY": os.getenv("PINGERA_API_KEY", "your_api_key_here"),
        "PINGERA_MODE": "read_write",
        "PINGERA_BASE_URL": "https://api.pingera.ru/v1",
        "PINGERA_TIMEOUT": "30",
        "PINGERA_MAX_RETRIES": "3",
        "PINGERA_DEBUG": "false",
        "PINGERA_SERVER_NAME": "Pingera MCP Server"
    }
)

async def main():
    """Run simple MCP client test with Gemini."""
    import sys
    
    # Get prompt from command line argument, stdin, or use default
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        # Read from stdin if piped
        prompt = sys.stdin.read().strip()
    else:
        prompt = "How many monitoring checks do I have and what types are they?"
    
    if not prompt:
        prompt = "How many monitoring checks do I have and what types are they?"
    
    print(f"🤖 Query: {prompt}")
    print("\n" + "="*50)
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize MCP session
                await session.initialize()
                
                # Get available tools from MCP server
                mcp_tools = await session.list_tools()
                
                print(f"📋 Found {len(mcp_tools.tools)} MCP tools available")
                
                # Convert MCP tools to Gemini format
                tools = []
                for tool in mcp_tools.tools:
                    # Extract the input schema safely
                    input_schema = tool.inputSchema or {}
                    properties = input_schema.get("properties", {})
                    required = input_schema.get("required", [])
                    
                    # Convert MCP schema properties to Gemini format
                    gemini_properties = {}
                    for prop_name, prop_schema in properties.items():
                        # Convert MCP property schema to Gemini format
                        gemini_prop = {}
                        
                        # Handle type conversion
                        if isinstance(prop_schema, dict):
                            prop_type = prop_schema.get("type", "string")
                            if prop_type == "array":
                                gemini_prop["type"] = "ARRAY"
                                items = prop_schema.get("items", {})
                                if isinstance(items, dict) and "type" in items:
                                    item_type = items["type"]
                                    if item_type == "string":
                                        gemini_prop["items"] = {"type": "STRING"}
                                    elif item_type == "integer":
                                        gemini_prop["items"] = {"type": "INTEGER"}
                                    elif item_type == "number":
                                        gemini_prop["items"] = {"type": "NUMBER"}
                                    else:
                                        gemini_prop["items"] = {"type": "STRING"}
                            elif prop_type == "integer":
                                gemini_prop["type"] = "INTEGER"
                            elif prop_type == "number":
                                gemini_prop["type"] = "NUMBER"
                            elif prop_type == "boolean":
                                gemini_prop["type"] = "BOOLEAN"
                            else:
                                gemini_prop["type"] = "STRING"
                            
                            # Add description if available
                            if "description" in prop_schema:
                                gemini_prop["description"] = prop_schema["description"]
                        else:
                            gemini_prop["type"] = "STRING"
                        
                        gemini_properties[prop_name] = gemini_prop
                    
                    tool_schema = {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "OBJECT",
                            "properties": gemini_properties,
                            "required": required
                        }
                    }
                    tools.append(tool_schema)
                
                print(f"🔧 Available tools: {[tool['name'] for tool in tools]}")
                print("\n" + "-"*50)
                
                # Ask Gemini to use the tools
                print(f"🔧 Creating Gemini model with {len(tools)} tools...")
                try:
                    model = genai.GenerativeModel('gemini-2.5-flash', tools=tools)
                    print("✓ Gemini model created successfully")
                    
                    print(f"🤖 Generating content for prompt: {prompt}")
                    print(f"🔧 Using temperature: 0")
                    
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(temperature=0)
                    )
                    print("✓ Gemini response generated successfully")
                    print(f"📝 Response type: {type(response)}")
                    print(f"📝 Response candidates count: {len(response.candidates) if hasattr(response, 'candidates') else 'N/A'}")
                    
                except Exception as gemini_error:
                    print(f"❌ Gemini error: {gemini_error}")
                    print(f"❌ Error type: {type(gemini_error)}")
                    import traceback
                    print("❌ Full traceback:")
                    traceback.print_exc()
                    raise
                
                # Check if Gemini wants to call a function first
                function_calls_made = False
                if response.candidates[0].content.parts and len(response.candidates[0].content.parts) > 0:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call'):
                            function_call = part.function_call
                            function_calls_made = True
                            
                            # Check if function call has a valid name
                            if not function_call.name or function_call.name.strip() == "":
                                print("❌ Gemini generated an empty function call name")
                                print("🤖 Falling back to text response...")
                                function_calls_made = False
                                break
                            
                            print(f"🔧 Gemini wants to call: {function_call.name}")
                            print(f"📝 With arguments: {dict(function_call.args)}")
                            
                            # Execute the MCP tool
                            result = await session.call_tool(
                                function_call.name, 
                                arguments=dict(function_call.args)
                            )
                            
                            print(f"\n📊 Tool result:")
                            print(json.dumps(json.loads(result.content[0].text), indent=2))
                            
                            # Ask Gemini to interpret the results
                            follow_up_model = genai.GenerativeModel('gemini-2.5-flash')
                            follow_up = follow_up_model.generate_content(
                                f"Based on this monitoring data: {result.content[0].text}\n\nPlease summarize the results in a friendly way for the question: {prompt}"
                            )
                            
                            print(f"\n🤖 Gemini's summary:")
                            print(follow_up.text)
                
                # Only try to access text if no function calls were made
                if not function_calls_made:
                    print("🎯 Gemini's response:")
                    try:
                        if response.text:
                            print(response.text)
                        else:
                            print("No text response from Gemini")
                    except ValueError as e:
                        print(f"Could not get text from response: {e}")
                        print("Response likely contains function calls or other structured content")
    
    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        print("\nMake sure the MCP server is properly configured for stdio communication.")
        print("The server should be running via 'python main.py' and listening on stdio.")

asyncio.run(main())
