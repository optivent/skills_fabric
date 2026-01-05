import asyncio
import json
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

async def run_with_timeout(coro, timeout=30):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return "ERROR: Sensor Timeout"

class SovereignOrchestrator:
    def __init__(self, local_repo_path):
        self.local_repo_path = local_repo_path
        self.context7_api_key = "05-708d097ae494"
        self.context7_url = "https://mcp.context7.com/mcp"

    async def call_forensic(self, tool_name, arguments):
        params = StdioServerParameters(
            command="/home/aig/play/skills_factory/forensic_mcp/.venv/bin/python3",
            args=["/home/aig/play/skills_factory/forensic_mcp/forensic_server.py"],
            env=None
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result.content

    async def call_context7(self, tool_name, arguments):
        headers = {
            "X-API-Key": self.context7_api_key,
            "Accept": "application/json, text/event-stream"
        }
        async with sse_client(url=self.context7_url, headers=headers) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result.content

    async def verify_library_truth(self, library_name, sample_symbol, sample_file):
        print(f"\n--- [TRUTH LOOP]: Verifying {library_name} ---")
        
        # 1. Pattern (Context7)
        print(f"[1/3] Fetching Patterns from Context7...")
        c7_data = await run_with_timeout(self.call_context7("get_library_docs", {"name": library_name}))
        if isinstance(c7_data, str) and "ERROR" in c7_data:
            print(f"      ⚠ Context7: {c7_data}")
        else:
            print(f"      ✓ Patterns retrieved.")

        # 2. Reality (Forensic)
        print(f"[2/3] Fetching Bedrock Reality from Forensic (Local AST)...")
        try:
            full_path = str(Path(self.local_repo_path) / sample_file)
            ast_data = await run_with_timeout(self.call_forensic("get_file_symbols", {"file_path": full_path}))
            
            if isinstance(ast_data, str) and "ERROR" in ast_data:
                print(f"      ❌ Forensic: {ast_data}")
            else:
                symbols = json.loads(ast_data[0].text) if hasattr(ast_data[0], "text") else []
                exists = any(s["name"] == sample_symbol for s in symbols)
                if exists:
                    print(f"      ✓ Physical verification: \"{sample_symbol}\" exists in {sample_file}.")
                else:
                    print(f"      ❌ DRIFT DETECTED: \"{sample_symbol}\" NOT found in {sample_file}!")
        except Exception as e:
            print(f"      ❌ Forensic Failure: {e}")

        print(f"--- [TRUTH LOOP COMPLETE] ---\n")

async def main():
    orch = SovereignOrchestrator("/home/aig/play/skills_factory/loguru_poc/loguru")
    await orch.verify_library_truth("loguru", "Logger", "loguru/_logger.py")
    await orch.verify_library_truth("loguru", "NonExistentClass", "loguru/_logger.py")

if __name__ == "__main__":
    asyncio.run(main())
