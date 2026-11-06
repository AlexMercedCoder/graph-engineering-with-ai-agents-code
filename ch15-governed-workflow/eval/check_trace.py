#!/usr/bin/env python3
"""Check that one Claude Code session left a complete trace.

    python3 check_trace.py ../runs/<date>/claude-fix-approve-run1

Complete means: in the trace of the session's turn there is a span for every
tool call, a server span from project-knowledge and from change-gate under
those calls, and, if the session proposed a change, the gate's own span with
its outcome. A component missing from the trace is a component that isn't
wired in, or isn't instrumented.
"""
import json
import sys
from pathlib import Path


def check(run):
    spans = [json.loads(l) for l in (Path(run) / "telemetry" / "spans.jsonl").open()]
    turns = [s for s in spans if s["name"] == "claude_code.interaction"]
    if not turns:
        return ["no claude_code.interaction span"]
    tid = turns[0]["trace_id"]
    mine = [s for s in spans if s["trace_id"] == tid]
    by_service = {}
    for s in mine:
        by_service.setdefault(s["resource"].get("service.name"), []).append(s["name"])
    tools = [s for s in mine if s["name"] == "claude_code.tool"]
    calls = [json.loads(l) for l in (Path(run) / "transcript.jsonl").open() if l.strip()]
    called = sum(1 for e in calls if e.get("type") == "assistant"
                 for c in e["message"]["content"] if c.get("type") == "tool_use")
    problems = []
    if len(tools) != called:
        problems.append(f"{called} tool calls in the transcript, {len(tools)} tool spans in the trace")
    for service in ("project-knowledge", "change-gate"):
        if not any(n.startswith("tools/call") for n in by_service.get(service, [])):
            problems.append(f"no tools/call span from {service} in the session's trace")
    proposed = any(n == "tools/call propose_change" for n in by_service.get("change-gate", []))
    gate = [s for s in mine if s["name"] == "gate.propose_change"]
    if proposed and not (gate and gate[0]["attributes"].get("gate.outcome")):
        problems.append("propose_change was called but no gate span with an outcome")
    return problems


if __name__ == "__main__":
    bad = 0
    for run in sys.argv[1:]:
        problems = check(run)
        bad += bool(problems)
        print(f"{Path(run).name}: " + ("complete" if not problems else "; ".join(problems)))
    sys.exit(1 if bad else 0)
