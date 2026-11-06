#!/usr/bin/env python3
"""Replay the shell commands from recorded raw-schema sessions through the SQL hook.

Shows what hooks/validate-sql.py would have blocked, without running an agent.

  python3 eval/replay_hook.py runs/2026-11-03-governed-access/*raw*.jsonl
"""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "validate-sql.py"


def commands(path):
    for line in open(path, encoding="utf-8"):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "assistant":  # Claude Code stream-json
            for c in event["message"].get("content", []):
                if c.get("type") == "tool_use" and c.get("name") == "Bash":
                    yield c["input"].get("command", "")
        part = event.get("part", {})  # OpenCode run --format json
        if part.get("type") == "tool" and part.get("tool") == "bash":
            yield part.get("state", {}).get("input", {}).get("command", "")


for path in sys.argv[1:]:
    sql_cmds = blocked = 0
    reasons = set()
    for cmd in commands(path):
        if "sqlite3" not in cmd:
            continue
        sql_cmds += 1
        event = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
        out = subprocess.run([sys.executable, str(HOOK)], input=event, text=True,
                             capture_output=True)
        if out.returncode == 2:
            blocked += 1
            reasons.update(l.strip("- ").split(".")[0] for l in out.stderr.splitlines()
                           if l.startswith("  - "))
    print(f"{Path(path).name}: {blocked} of {sql_cmds} sqlite3 commands blocked")
    for r in sorted(reasons):
        print(f"    {r}")
