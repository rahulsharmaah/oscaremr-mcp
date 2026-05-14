$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"

$code = @"
import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(
        command=r"$python",
        args=["-m", "oscar_db_mcp.server"],
        cwd=r"$repoRoot",
        env=os.environ.copy(),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("TOOLS:", [tool.name for tool in tools.tools])
            result = await session.call_tool("health_check", arguments={})
            print("HEALTH:", result.content[0].text if result.content else result)


asyncio.run(main())
"@

$code | & $python -
