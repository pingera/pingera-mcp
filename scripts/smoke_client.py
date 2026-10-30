"""Quick smoke client: python scripts/smoke_client.py URL [tool] [json-args]. Credentials from PINGERA_API_KEY."""
import asyncio, json, os, sys

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client


async def main():
    url = sys.argv[1]
    tool = sys.argv[2] if len(sys.argv) > 2 else None
    args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    headers = {"Authorization": f"Bearer {os.environ['PINGERA_API_KEY']}"}
    headers.update(json.loads(os.environ.get("EXTRA_HEADERS", "{}")))
    mode = os.environ.get("MCP_CLIENT_MODE", "auto")
    async with httpx2.AsyncClient(headers=headers, timeout=60) as http:
        async with Client(streamable_http_client(url, http_client=http), mode=mode) as client:
            tools = await client.list_tools()
            print("tools:", len(tools.tools))
            if tool:
                result = await client.call_tool(tool, args)
                print("is_error:", result.is_error)
                for block in result.content:
                    print(getattr(block, "text", block)[:3000])


asyncio.run(main())
