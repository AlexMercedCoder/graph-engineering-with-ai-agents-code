"""Time what the stdio server costs: startup to a tool list, and each tool call.

Run from ch09-mcp/: python3 tools/time-calls.py [calls]
Compare with the file route, timed the same way: one grep for the error code.
"""
import asyncio
import statistics
import subprocess
import sys
import time
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent.parent
CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else 50


async def main():
    params = StdioServerParameters(command=sys.executable,
                                   args=[str(HERE / "server" / "server.py")],
                                   env={"KB_IDENTITY": "engineer"})
    start = time.perf_counter()
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            ready = time.perf_counter() - start
            timings = {}
            for name, args in [("lookup_error_code", {"code": "E4021"}),
                               ("get_config_schema", {"service": "payments"}),
                               ("find_architecture_docs", {"topic": "capture worker"})]:
                samples = []
                for _ in range(CALLS):
                    t = time.perf_counter()
                    await session.call_tool(name, args)
                    samples.append((time.perf_counter() - t) * 1000)
                timings[name] = samples
    print(f"startup to tool list ({len(tools.tools)} tools): {ready * 1000:.0f} ms")
    for name, samples in timings.items():
        print(f"{name}: median {statistics.median(samples):.2f} ms, "
              f"max {max(samples):.2f} ms over {CALLS} calls")
    docs = HERE / "knowledge"
    samples = []
    for _ in range(CALLS):
        t = time.perf_counter()
        subprocess.run(["grep", "-rn", "E4021", str(docs)], capture_output=True)
        samples.append((time.perf_counter() - t) * 1000)
    print(f"grep for comparison: median {statistics.median(samples):.2f} ms")


asyncio.run(main())
