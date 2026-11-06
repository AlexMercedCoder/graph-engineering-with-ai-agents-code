#!/usr/bin/env python3
"""latency.py: time the same tool call over stdio and over the HTTP connector.

    python3 tools/latency.py [calls]        # connector must be running on 8813

Runs execute_query on one generated statement `calls` times (default 50) through
the Chapter 11 stdio server and through the connector, each in one open
session, and prints the median and 95th percentile per call. Both run on this
machine, so the HTTP figure is protocol and token-check overhead only; add your
network round trip to Anthropic's servers and back for a hosted connector.
"""
import asyncio
import statistics
import subprocess
import sys
import time
from pathlib import Path

import httpx2
from mcp.client import Client
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client

HERE = Path(__file__).resolve().parent
CH11 = HERE.parent.parent / "ch11-catalog"
CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else 50
ARGS = {"metric": "net_written_premium", "dimensions": ["region"], "time_range": "2026-Q3"}


async def timed(transport):
    async with Client(transport) as c:
        sql = "".join(p.text for p in (await c.call_tool("generate_governed_sql", ARGS)).content)
        times = []
        for _ in range(CALLS):
            start = time.perf_counter()
            await c.call_tool("execute_query", {"sql": sql})
            times.append((time.perf_counter() - start) * 1000)
        return statistics.median(times), statistics.quantiles(times, n=20)[18]


def main():
    stdio = stdio_client(StdioServerParameters(
        command=sys.executable, args=[str(CH11 / "server" / "server.py")],
        env={"CATALOG_IDENTITY": "analyst", "CATALOG_SCOPES": "catalog:read data:read"}))
    token = subprocess.run([sys.executable, str(HERE / "connector-check.py"), "--token", "analyst"],
                           capture_output=True, text=True, check=True).stdout.strip()
    http = streamable_http_client("http://127.0.0.1:8813/mcp",
                                  http_client=httpx2.AsyncClient(headers={"Authorization": f"Bearer {token}"}))
    for label, transport in (("stdio, local process", stdio), ("HTTP connector, loopback", http)):
        median, p95 = asyncio.run(timed(transport))
        print(f"{label:26} median {median:6.1f} ms   p95 {p95:6.1f} ms   ({CALLS} calls)")


if __name__ == "__main__":
    main()
