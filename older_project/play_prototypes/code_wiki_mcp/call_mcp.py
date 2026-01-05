import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command="/home/aig/play/skills_factory/code_wiki_mcp/.venv/bin/python3",
        args=["/home/aig/play/skills_factory/code_wiki_mcp/server.py"],
        env=None
    )
    
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("--- CALLING search_code_wiki ---")
            result = await session.call_tool("search_code_wiki", {
                "repo_url": "https://github.com/Delgan/loguru",
                "query": "Give me the complete overview and core documentation for Loguru."
            })
            
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
                else:
                    print(content)

if __name__ == "__main__":
    asyncio.run(main())
