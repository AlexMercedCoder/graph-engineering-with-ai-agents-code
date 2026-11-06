"""Fail when a tool is renamed or removed, or a parameter is removed or retyped.

Run from ch09-mcp/: python3 tools/check-interface.py
After an intended change, record it: python3 tools/check-interface.py --update
Adding a tool or an optional parameter passes; skills and clients don't break on additions.
"""
import asyncio
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "server"))
import server  # noqa: E402

SNAPSHOT = HERE / "tools" / "interface.json"


def current():
    tools = asyncio.run(server.mcp.list_tools())
    out = {}
    for t in tools:
        schema = t.input_schema if hasattr(t, "input_schema") else t.inputSchema
        props = schema.get("properties", {})
        out[t.name] = {"params": {k: v.get("type", "any") for k, v in props.items()},
                       "required": sorted(schema.get("required", []))}
    return out


def main():
    now = current()
    if "--update" in sys.argv:
        SNAPSHOT.write_text(json.dumps(now, indent=2, sort_keys=True) + "\n")
        print(f"recorded {len(now)} tools in {SNAPSHOT.name}")
        return 0
    before = json.loads(SNAPSHOT.read_text())
    problems = []
    for name, spec in before.items():
        if name not in now:
            problems.append(f"tool {name} was removed or renamed")
            continue
        for param, kind in spec["params"].items():
            if param not in now[name]["params"]:
                problems.append(f"{name}: parameter {param} was removed or renamed")
            elif now[name]["params"][param] != kind:
                problems.append(f"{name}: parameter {param} changed type from {kind} "
                                f"to {now[name]['params'][param]}")
        for param in now[name]["required"]:
            if param not in spec["required"]:
                problems.append(f"{name}: parameter {param} became required")
    if problems:
        print("interface broken:")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"interface holds: {len(before)} tools, no removals or type changes")
    return 0


sys.exit(main())
