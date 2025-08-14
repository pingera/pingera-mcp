
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
        "PINGERA_MODE": "read_only",
        "PINGERA_BASE_URL": "https://api.pingera.ru/v1",
        "PINGERA_TIMEOUT": "30",
        "PINGERA_MAX_RETRIES": "3",
        "PINGERA_DEBUG": "false",
        "PINGERA_SERVER_NAME": "Pingera MCP Server"
    }
)

async def run():
    """Run simple MCP client test with Gemini."""
    
    # Simple query about monitoring checks
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
                    tool_schema = {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": tool.inputSchema.get("properties", {}),
                            "required": tool.inputSchema.get("required", [])
                        }
                    }
                    tools.append(tool_schema)
                
                print(f"🔧 Available tools: {[tool['name'] for tool in tools]}")
                print("\n" + "-"*50)
                
                # Ask Gemini to use the tools
                model = genai.GenerativeModel('gemini-2.0-flash-exp', tools=tools)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(temperature=0)
                )
                
                print("🎯 Gemini's response:")
                if response.text:
                    print(response.text)
                
                # Check if Gemini wants to call a function
                if response.candidates[0].content.parts and len(response.candidates[0].content.parts) > 0:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call'):
                            function_call = part.function_call
                            
                            print(f"\n🔧 Gemini wants to call: {function_call.name}")
                            print(f"📝 With arguments: {dict(function_call.args)}")
                            
                            # Execute the MCP tool
                            result = await session.call_tool(
                                function_call.name, 
                                arguments=dict(function_call.args)
                            )
                            
                            print(f"\n📊 Tool result:")
                            print(json.dumps(json.loads(result.content[0].text), indent=2))
                            
                            # Ask Gemini to interpret the results
                            follow_up_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                            follow_up = follow_up_model.generate_content(
                                f"Based on this monitoring data: {result.content[0].text}\n\nPlease summarize the results in a friendly way for the question: {prompt}"
                            )
                            
                            print(f"\n🤖 Gemini's summary:")
                            print(follow_up.text)
    
    except Exception as e:
        print(f"❌ Error connecting to MCP server: {e}")
        print("\nMake sure the MCP server is properly configured for stdio communication.")
        print("The server should be running via 'python main.py' and listening on stdio.")

if __name__ == "__main__":
    print("🚀 Starting simple MCP client test with Gemini...")
    print("="*60)
    asyncio.run(run())
