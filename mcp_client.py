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
import traceback
from proto.marshal.collections.maps import MapComposite

# ADD THIS HELPER FUNCTION
def convert_proto_map_to_dict(proto_map):
    """Recursively converts a Proto MapComposite to a standard Python dict."""
    if not isinstance(proto_map, MapComposite):
        return proto_map

    py_dict = {}
    for key, value in proto_map.items():
        if isinstance(value, MapComposite):
            py_dict[key] = convert_proto_map_to_dict(value)
        else:
            py_dict[key] = value
    return py_dict


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
        "python",
        "-m",
        "pingera_mcp"
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
                    print("❌ Full traceback:")
                    traceback.print_exc()
                    raise

                # Check if Gemini wants to call a function first
                function_calls_made = False
                tool_responses = []
                
                if response.candidates[0].content.parts and len(response.candidates[0].content.parts) > 0:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call'):
                            function_call = part.function_call

                            # Check if function call has a valid name
                            if not function_call.name or function_call.name.strip() == "":
                                print("❌ Gemini generated an empty function call name")
                                print("🤖 Falling back to text response...")
                                function_calls_made = False
                                break

                            # Execute the tool call via MCP
                            print(f"🔧 Executing MCP tool: {function_call.name}")
                            print(f"📝 With arguments: {dict(function_call.args)}")

                            try:
                                # Add timeout to tool calls
                                args_dict = convert_proto_map_to_dict(function_call.args)
                                print(f"📝 With converted arguments: {args_dict}")

                                tool_task = asyncio.create_task(
                                    session.call_tool(function_call.name, args_dict) # Use the converted dict
                                )
                                result = await asyncio.wait_for(tool_task, timeout=60.0)
                                print(f"✓ Tool executed successfully")

                                # Debug result structure
                                print(f"📝 Result type: {type(result)}")
                                print(f"📝 Result attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")

                                # Handle different result types
                                if hasattr(result, 'content') and result.content:
                                    print(f"📝 Content type: {type(result.content)}")
                                    print(f"📝 Content length: {len(result.content) if result.content else 0}")

                                    if result.content and len(result.content) > 0:
                                        print(f"📝 First content item type: {type(result.content[0])}")

                                        if isinstance(result.content[0], dict):
                                            content = json.dumps(result.content[0], indent=2)
                                        elif hasattr(result.content[0], 'text'):
                                            content = result.content[0].text
                                        else:
                                            content = str(result.content[0])

                                        print(f"📊 Tool result:")
                                        # Only show first 500 chars to avoid spam
                                        if len(content) > 500:
                                            print(f"{content[:500]}... (truncated)")
                                        else:
                                            print(content)

                                        print(f"\n✅ Tool execution completed successfully!")
                                        function_calls_made = True
                                        
                                        # Store tool response for Gemini's follow-up
                                        tool_responses.append(
                                            genai.protos.Part(
                                                function_response=genai.protos.FunctionResponse(
                                                    name=function_call.name,
                                                    response={"result": content}
                                                )
                                            )
                                        )
                                    else:
                                        print("⚠️ Tool returned empty content list")
                                else:
                                    print("⚠️ Tool returned no content attribute or empty content")
                                    print(f"📝 Available result attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")

                            except asyncio.TimeoutError:
                                print(f"❌ Tool execution timed out after 60 seconds")
                            except Exception as tool_error:
                                print(f"❌ Tool execution failed: {tool_error}")
                                print(f"📝 Tool error type: {type(tool_error)}")
                                print(f"📝 Tool error details:")
                                traceback.print_exc()

                # If tools were executed, get Gemini's final response
                if function_calls_made and tool_responses:
                    print("\n🔄 Getting Gemini's final response with tool results...")
                    try:
                        # Create a new message with tool responses
                        final_response = model.generate_content(
                            [
                                {"role": "user", "parts": [prompt]},
                                {"role": "model", "parts": response.candidates[0].content.parts},
                                {"role": "user", "parts": tool_responses}
                            ],
                            generation_config=genai.types.GenerationConfig(temperature=0)
                        )
                        
                        print("🎯 Gemini's final response:")
                        if final_response.text:
                            print(final_response.text)
                        else:
                            print("No final text response from Gemini")
                            
                    except Exception as final_error:
                        print(f"❌ Error getting final response: {final_error}")
                        print("📝 Falling back to basic text response...")
                        # Fallback to basic text response
                        try:
                            if response.text:
                                print("🎯 Gemini's response:")
                                print(response.text)
                        except ValueError as e:
                            print(f"Could not get any text response: {e}")
                
                # Only try to access text if no function calls were made
                elif not function_calls_made:
                    print("🎯 Gemini's response:")
                    try:
                        if response.text:
                            print(response.text)
                        else:
                            print("No text response from Gemini")
                    except ValueError as e:
                        print(f"Could not get text from response: {e}")
                        print("Response likely contains function calls or other structured content")

    except Exception as session_error:
        print(f"❌ MCP session error: {session_error}")
        print(f"📝 Session error type: {type(session_error)}")
        traceback.print_exc()
        raise

    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        print(f"📝 Error type: {type(e)}")
        print(f"📝 Error details:")
        traceback.print_exc()
        print("\nMake sure the MCP server is properly configured for stdio communication.")
        print("The server should be running via 'python main.py' and listening on stdio.")

asyncio.run(main())