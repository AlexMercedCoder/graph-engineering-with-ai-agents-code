#!/usr/bin/env python3
"""run-bundle.py: launch a packed .mcpb the way Claude Desktop does, and ask it questions.

    python3 bundle/run-bundle.py bundle/governed-data-local.mcpb analyst
    python3 bundle/run-bundle.py bundle/governed-data-local.mcpb finance

Unpacks the bundle into a temporary folder, reads manifest.json, substitutes
${__dirname} and ${user_config.identity} into mcp_config, and starts the server
over stdio, which is the transport Desktop uses for a local extension. Then it
asks for net written premium and for commission paid, the restricted metric.

The identity argument is the value a person types into the extension's Identity
setting. Nothing checks it.
"""
import asyncio
import json
import sys
import tempfile
import zipfile
from pathlib import Path

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters, stdio_client


def substitute(value, dirname, user_config):
    value = value.replace("${__dirname}", dirname)
    for key, v in user_config.items():
        value = value.replace("${user_config." + key + "}", v)
    return value


async def ask(params):
    async with Client(stdio_client(params)) as c:
        tools = [t.name for t in (await c.list_tools()).tools]
        print("tools:", ", ".join(tools))
        for metric in ("net_written_premium", "commission_paid"):
            sql = await c.call_tool("generate_governed_sql", {
                "metric": metric, "dimensions": [], "time_range": "2026-Q3"})
            sql = "".join(getattr(p, "text", "") for p in sql.content)
            if "-- governed:" not in sql:
                print(f"{metric}: {sql.splitlines()[0]}")
                continue
            rows = await c.call_tool("execute_query", {"sql": sql})
            print(f"{metric}: {' / '.join(''.join(getattr(p, 'text', '') for p in rows.content).splitlines())}")


def main():
    bundle, identity = Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "analyst"
    with tempfile.TemporaryDirectory() as d:
        zipfile.ZipFile(bundle).extractall(d)
        manifest = json.loads((Path(d) / "manifest.json").read_text())
        cfg = manifest["server"]["mcp_config"]
        user_config = {"identity": identity}
        params = StdioServerParameters(
            command=cfg["command"],
            args=[substitute(a, d, user_config) for a in cfg["args"]],
            env={k: substitute(v, d, user_config) for k, v in cfg.get("env", {}).items()})
        print(f"{manifest['name']} {manifest['version']}, Identity setting = {identity}")
        asyncio.run(ask(params))


if __name__ == "__main__":
    main()
