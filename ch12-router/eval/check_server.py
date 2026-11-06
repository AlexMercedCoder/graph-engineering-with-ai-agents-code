#!/usr/bin/env python3
"""Check the knowledge server's evidence envelopes without an agent.

    python3 check_server.py

Needs the MCP Python SDK, numpy, and PyYAML, the Chapter 10 graph
(ch10-graph/graph/extract.py), and the Chapter 11 warehouse
(ch11-catalog/warehouse/seed.py). Skips search_docs, which loads an
embedding model.
"""
import asyncio
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
os.environ.update({"CATALOG_IDENTITY": "analyst", "CATALOG_SCOPES": "catalog:read data:read"})
import knowledge_server as k  # noqa: E402

failed = []


def env(text):
    return json.loads(text)["evidence"]


def expect(name, ok):
    print(f"{'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        failed.append(name)


names = [t.name for t in asyncio.run(k.mcp.list_tools())]
expect("server lists eleven tools", len(names) == 11)
expect("error code found", env(k.lookup_error_code("E4021"))["status"] == "found")
expect("unknown error code not_found", env(k.lookup_error_code("E4023"))["status"] == "not_found")
e = env(k.find_dependents("NotificationsAPI", 2))
expect("traversal found, complete, high", (e["status"], e["coverage"], e["confidence"]) == ("found", "complete", "high"))
expect("loose name lowers confidence", env(k.find_dependents("Notifications", 2))["confidence"] == "medium")
expect("loss ratio refused", env(k.navigate_catalog("loss ratio"))["status"] == "refused")
expect("analyst refused commission", env(k.navigate_catalog("commission"))["status"] == "refused")
sql = json.loads(k.generate_governed_sql("net_written_premium", ["region"], "2026-Q3"))["result"]
rows = json.loads(k.execute_query(sql))
expect("governed query found with catalog revision",
       rows["evidence"]["status"] == "found" and rows["evidence"]["source"]["revision"].startswith("catalog")
       and "343269.84" in rows["result"])
expect("hand-written SQL refused", env(k.execute_query("SELECT 1"))["status"] == "refused")
doc = dict(env(k.lookup_error_code("E4021")), claim="E4021 is not retryable.")
expect("check_evidence accepts an envelope plus a claim", k.check_evidence(json.dumps([doc])).startswith("All 1"))
expect("check_evidence names a missing field",
       "missing cost_tokens" in k.check_evidence(json.dumps([{x: doc[x] for x in doc if x != "cost_tokens"}])))

print(f"{'all server checks passed' if not failed else f'{len(failed)} failed'}")
sys.exit(1 if failed else 0)
