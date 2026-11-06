#!/usr/bin/env python3
"""Check exported telemetry against policy.json: spend, access, and regression.

    python3 policy.py spend  <run-dir>...        cost and tokens per node, against the budget
    python3 policy.py access <run-dir>...        who called which graph tool, and the decision
    python3 policy.py baseline <run-dir>... > baseline.json
    python3 policy.py regress baseline.json <run-dir>...

Each run-dir holds telemetry/ from collector.py (and triage.json, for regress).
Exits 1 when any run breaks the policy, so the same command works in CI.
"""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from graphspans import graph, load  # noqa: E402

POLICY = json.loads((HERE / "policy.json").read_text())


def records(run, name):
    path = Path(run) / "telemetry" / name
    return [json.loads(l) for l in path.open()] if path.exists() else []


def node_of(attrs):
    """Which node of the execution graph a request belongs to."""
    source = attrs.get("query_source_safe") or attrs.get("query_source")
    if attrs.get("agent_id"):
        return f"subagent {attrs.get('agent.name') or attrs['agent_id'][:8]}"
    if source in (None, "sdk", "repl_main_thread", "main"):
        return "main"
    return f"auxiliary {source}"


def spend(runs):
    budget, broken = POLICY["budget"], 0
    for run in runs:
        nodes, _ = graph(load(Path(run) / "telemetry"))
        by_node = defaultdict(lambda: {"usd": 0.0, "requests": 0, "max_context": 0})
        for e in records(run, "logs.jsonl"):
            if e["event"] in ("api_request", "claude_code.api_request"):
                a = e["attributes"]
                n = by_node[node_of(a)]
                n["usd"] += float(a.get("cost_usd", 0))
        for n in nodes.values():
            if n["kind"] != "llm":
                continue
            key = "main" if n.get("agent") in (None, "main") else n["agent"]
            if n.get("source") and n["source"] not in ("sdk", "repl_main_thread") \
                    and not n["source"].startswith("agent."):
                key = f"auxiliary {n['source']}"
            elif n.get("source", "").startswith("agent."):
                key = f"subagent {n['source'].split('.')[-1]}"
            elif key != "main" and not str(key).startswith("ses_"):
                key = f"subagent {key[:8]}"
            elif str(key).startswith("ses_"):
                key = "session " + key[-6:]
            ctx = n["input"] + n["cache_read"] + n["cache_write"]
            by_node[key]["requests"] += 1
            by_node[key]["max_context"] = max(by_node[key]["max_context"], ctx)
        total = sum(v["usd"] for v in by_node.values())
        tokens = sum(n["input"] + n["cache_read"] + n["cache_write"] + n["output"]
                     for n in nodes.values() if n["kind"] == "llm")
        cost = f"${total:.4f} reported" if total else "no cost reported"
        print(f"{Path(run).name}: {cost}, {tokens:,} tokens")
        for k, v in sorted(by_node.items()):
            flag = "  OVER" if v["max_context"] > budget["max_request_context_tokens"] else ""
            broken += bool(flag)
            print(f"  {k:32} {v['requests']:2} requests  largest context {v['max_context']:7,}"
                  f"  ${v['usd']:.4f}{flag}")
        if total > budget["max_session_usd"]:
            broken += 1
            print(f"  session over budget: ${total:.4f} > ${budget['max_session_usd']}")
        if tokens > budget["max_session_tokens"]:
            broken += 1
            print(f"  session over budget: {tokens:,} tokens > {budget['max_session_tokens']:,}")
    return broken


def access(runs):
    """One row per graph tool call. `holders` is compared with the token subject
    in graph.subject by exact string."""
    restricted, broken = POLICY["access"]["restricted_tools"], 0
    print("| Run | User | Tool | Decision |")
    print("|---|---|---|---|")
    for run in runs:
        nodes, _ = graph(load(Path(run) / "telemetry"))
        for n in sorted((n for n in nodes.values() if n["kind"] == "graph"), key=lambda n: n["start_ns"]):
            tool = n["op"].split(".", 1)[1]
            decision = n.get("decision", "allow")
            if tool in restricted and decision != "deny" and n.get("user") not in POLICY["access"]["holders"]:
                broken += 1
                decision += "  POLICY BREACH"
            print(f"| {Path(run).name} | {n.get('user')} | {tool} | {decision} |")
    return broken


def tokens_of(run):
    t = json.loads((Path(run) / "triage.json").read_text())
    return t, t["tokens"]["input"] + t["tokens"]["cache_read"] + t["tokens"]["cache_write"]


def baseline(runs):
    by_h = defaultdict(list)
    for run in runs:
        t, tok = tokens_of(run)
        by_h[t["harness"]].append({"tokens": tok, "requests": t["tokens"]["requests"],
                                   "paths": t["evidence"]["paths"], "tools": t["route"]["tools"]})
    out = {h: {"median_tokens": statistics.median(r["tokens"] for r in rs),
               "median_requests": statistics.median(r["requests"] for r in rs),
               "paths": sorted({r["paths"] for r in rs}),
               "tools": sorted({str(x) for r in rs for x in r["tools"]}), "runs": len(rs)}
           for h, rs in by_h.items()}
    print(json.dumps(out, indent=1))
    return 0


def regress(base_file, runs):
    base, band, broken = json.loads(Path(base_file).read_text()), POLICY["regression"]["token_band"], 0
    for run in runs:
        t, tok = tokens_of(run)
        b = base[t["harness"]]
        problems = []
        if t["verdict"] != "pass":
            problems.append(f"triage: {t['verdict']}")
        if tok > b["median_tokens"] * band:
            problems.append(f"context tokens {tok:,} > {band}x baseline {b['median_tokens']:,.0f}")
        if t["evidence"]["paths"] not in b["paths"]:
            problems.append(f"paths {t['evidence']['paths']} not in baseline {b['paths']}")
        used = {str(x) for x in t["route"]["tools"]}
        if sorted(used - set(b["tools"])):
            problems.append(f"new tools {sorted(used - set(b['tools']))}")
        if sorted(set(b["tools"]) - used):
            problems.append(f"missing tools {sorted(set(b['tools']) - used)}")
        broken += bool(problems)
        print(f"{Path(run).name}: {'; '.join(problems) if problems else 'within baseline'}")
    return broken


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    cmd, rest = sys.argv[1], sys.argv[2:]
    result = {"spend": spend, "access": access, "baseline": baseline}.get(cmd)
    if cmd == "regress":
        sys.exit(1 if regress(rest[0], rest[1:]) else 0)
    if result is None:
        raise SystemExit(__doc__)
    sys.exit(1 if result(rest) else 0)
