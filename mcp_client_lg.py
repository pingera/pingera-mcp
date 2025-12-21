"""
An example MCP client that connects to the Pingera MCP server,
discovers its tools, and integrates them into a LangGraph ReAct agent
powered by Google's Gemini model.

** This version is updated to use SSE transport. **
"""
import asyncio
import os
import traceback
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

# --- Configuration ---
SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:5000/sse")
PINGERA_API_KEY = os.getenv("PINGERA_API_KEY")

async def main():
    """Main function to set up the client, agent, and run a query."""
    print("--- Starting Pingera MCP Client (Debug Mode) ---")

    # 1. Input Validation
    if not PINGERA_API_KEY:
        raise ValueError("The 'PINGERA_API_KEY' environment variable is not set. Please set it to your key.")
    if not os.getenv("GOOGLE_API_KEY"):
        print("\nWarning: 'GOOGLE_API_KEY' environment variable is not set. The script may fail.")
        print("You can set it with: export GOOGLE_API_KEY='your-google-api-key'")

    if "127.0.0.1" in SERVER_URL or "localhost" in SERVER_URL:
        print(f"\nWarning: Connecting to localhost ({SERVER_URL}).")
        print("If your server is hosted (e.g., on Replit), set the 'MCP_SERVER_URL' environment variable.")
        print("Example: export MCP_SERVER_URL='https://your-replit-url'")

    # 2. Set up the MCP Client
    # Use 'sse' transport which is compatible with FastMCP's SSE implementation
    client = MultiServerMCPClient(
        {
            "pingera": {
                "url": SERVER_URL,
                "transport": "sse",
                "headers": {
                    "Authorization": PINGERA_API_KEY
                },
            }
        }
    )

    print(f"\nConnecting to MCP server at {SERVER_URL}...")

    # 3. Fetch the available tools from the server
    try:
        # We can now use the tools directly, as the header is handled by the client.
        tools = await client.get_tools()
        print(f"✅ Successfully discovered {len(tools)} tools.")

    except Exception as e:
        print(f"❌ An error occurred during tool setup.")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Details: {e}")
        print("\n--- Full Traceback ---")
        traceback.print_exc()
        print("\n--- End Traceback ---")
        return

    # 4. Set up the Gemini LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    print("\nInitialized Google Gemini LLM.")

    # 5. Create the LangGraph ReAct Agent
    agent_executor = create_react_agent(llm, tools)
    print("✅ LangGraph agent created successfully.")

    # 6. Get user input
    print("\n" + "="*50)
    prompt = input("Enter your request (or press Enter for default): ").strip()

    if not prompt:
        prompt = "Show me the status?"
        print(f"Using default prompt: '{prompt}'")

    print(f"\nInvoking agent with prompt: '{prompt}'")
    print("--- [START] Agent Execution Stream ---")

    messages = [("user", prompt)]

    final_answer = ""
    async for chunk in agent_executor.astream({"messages": messages}):
        print(f"\n[CHUNK]: {chunk}\n")
        if 'agent' in chunk:
            agent_messages = chunk['agent'].get('messages', [])
            for msg in agent_messages:
                if msg.content:
                    print(f"🕵️ [AGENT THOUGHT]:\n{msg.content}\n")
        if 'tool' in chunk:
             tool_messages = chunk['tool'].get('messages', [])
             for msg in tool_messages:
                 print(f"🛠️ [TOOL OBSERVATION/ERROR]:\n{msg.content}\n")
        if chunk.get('messages'):
            last_message = chunk['messages'][-1]
            if isinstance(last_message, BaseMessage):
                final_answer = last_message.content

    # 7. Print the final response
    print("\n--- [END] Agent Execution Stream ---")
    print("\n✅ Agent execution finished.")
    print("\n--- Final Agent Response ---")
    print(final_answer)


if __name__ == "__main__":
    asyncio.run(main())