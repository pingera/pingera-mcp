
#!/usr/bin/env python3
"""
Simple MCP client to test Pingera MCP Server with Gemini.
"""
import asyncio
import os
import json
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Configure MCP server parameters
server_params = StdioServerParameters(
    command="python",
    args=["main.py"],
    env={}
)

async def run():
    """Run simple MCP client test with Gemini."""
    
    # Simple query about monitoring checks
    prompt = "How many monitoring checks do I have and what types are they?"
    
    print(f"🤖 Query: {prompt}")
    print("\n" + "="*50)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize MCP session
            await session.initialize()
            
            # Get available tools from MCP server
            mcp_tools = await session.list_tools()
            
            print(f"📋 Found {len(mcp_tools.tools)} MCP tools available")
            
            # Convert MCP tools to Gemini format
            tools = [
                types.Tool(
                    function_declarations=[
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                k: v
                                for k, v in tool.inputSchema.items()
                                if k not in ["additionalProperties", "$schema"]
                            },
                        }
                    ]
                )
                for tool in mcp_tools.tools
            ]
            
            print(f"🔧 Available tools: {[tool.function_declarations[0]['name'] for tool in tools]}")
            print("\n" + "-"*50)
            
            # Ask Gemini to use the tools
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    tools=tools,
                ),
            )
            
            print("🎯 Gemini's response:")
            print(response.candidates[0].content.parts[0].text if response.candidates[0].content.parts[0].text else "No text response")
            
            # Check if Gemini wants to call a function
            if response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                
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
                follow_up = client.models.generate_content(
                    model="gemini-2.0-flash-exp",
                    contents=[
                        {"role": "user", "parts": [{"text": prompt}]},
                        {"role": "model", "parts": [{"function_call": function_call}]},
                        {"role": "function", "parts": [{"function_response": {"name": function_call.name, "response": json.loads(result.content[0].text)}}]},
                        {"role": "user", "parts": [{"text": "Please summarize the results in a friendly way"}]}
                    ],
                    config=types.GenerateContentConfig(temperature=0),
                )
                
                print(f"\n🤖 Gemini's summary:")
                print(follow_up.candidates[0].content.parts[0].text)

if __name__ == "__main__":
    print("🚀 Starting simple MCP client test with Gemini...")
    print("="*60)
    asyncio.run(run())
