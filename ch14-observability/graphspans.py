#!/usr/bin/env python3
"""Turn exported spans back into the execution graph that produced them.

    python3 graphspans.py tree telemetry/run-1        # one tree per trace
    python3 graphspans.py nodes telemetry/run-1       # the normalized nodes as JSON lines

Claude Code, OpenCode, and the MCP Python SDK name their spans differently.
normalize() maps each one onto five kinds of node, using the GenAI convention
names where one exists:

  turn    one user prompt (claude_code.interaction, SessionPrompt.prompt)
  llm     one model request (claude_code.llm_request, ai.streamText)
  tool    one tool call (claude_code.tool, Tool.execute)
  server  the MCP server's side of a tool call (tools/call <name>)
  graph   the traversal inside it (graph.*)

Spans that are none of these (OpenCode alone exported 1,197 spans for one
question) are dropped, and their children are attached to the
nearest node that is kept.
"""
import json
import sys
from pathlib import Path


def load(folder):
    path = Path(folder) / "spans.jsonl"
    return [json.loads(l) for l in path.open()] if path.exists() else []


def _int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def kind_of(span):
    n = span["name"]
    if n in ("claude_code.interaction", "SessionPrompt.prompt"):
        return "turn"
    if n in ("claude_code.llm_request", "ai.streamText"):
        return "llm"
    if n in ("claude_code.tool", "Tool.execute"):
        return "tool"
    if n == "claude_code.hook":
        return "hook"
    if n.startswith("tools/call"):
        return "server"
    if n.startswith("graph."):
        return "graph"
    return None


def normalize(span):
    a, k = span["attributes"], kind_of(span)
    node = {"kind": k, "span_id": span["span_id"], "trace_id": span["trace_id"],
            "start_ns": span["start_ns"], "ms": (span["end_ns"] - span["start_ns"]) / 1e6,
            "service": span["resource"].get("service.name"), "error": a.get("error.type")}
    if k == "llm":
        if span["name"] == "ai.streamText":
            node.update(model=a.get("ai.model.id"), agent=a.get("session.id"),
                        input=_int(a.get("ai.usage.inputTokenDetails.noCacheTokens")),
                        cache_read=_int(a.get("ai.usage.inputTokenDetails.cacheReadTokens")),
                        cache_write=_int(a.get("ai.usage.inputTokenDetails.cacheWriteTokens")),
                        output=_int(a.get("ai.usage.outputTokens")))
        else:
            node.update(model=a.get("model"), agent=a.get("agent_id", "main"),
                        source=a.get("query_source_safe"),
                        input=_int(a.get("input_tokens")), cache_read=_int(a.get("cache_read_tokens")),
                        cache_write=_int(a.get("cache_creation_tokens")),
                        output=_int(a.get("output_tokens")))
    elif k == "tool":
        cc = span["name"] == "claude_code.tool"
        node.update(tool=a.get("tool_name") or a.get("tool.name"), skill=a.get("skill_name"),
                    agent=a.get("agent_id", "main") if cc else a.get("session.id"),
                    call_id=a.get("tool_use_id") or a.get("tool.call_id"))
    elif k == "server":
        node.update(tool=a.get("gen_ai.tool.name"), method=a.get("mcp.method.name"))
    elif k == "graph":
        node.update(op=span["name"], **{key.split(".", 1)[1].replace(".", "_"): v
                                        for key, v in a.items() if key.startswith(("graph.", "auth."))},
                    user=a.get("graph.subject", a.get("enduser.id")))
    elif k == "turn":
        node.update(agent=a.get("session.id"))
    return node


def graph(spans):
    """Return (nodes, children): kept nodes and, for each, its kept children."""
    by_id = {s["span_id"]: s for s in spans}
    kept = {s["span_id"]: normalize(s) for s in spans if kind_of(s)}
    children = {}
    for sid, node in kept.items():
        parent = by_id[sid].get("parent_span_id")
        while parent and parent not in kept:
            parent = by_id.get(parent, {}).get("parent_span_id")
        node["parent"] = parent
        children.setdefault(parent, []).append(node)
    # A harness that doesn't propagate trace context leaves the server's spans in
    # a trace of their own. Attach each one to the tool call that was running
    # when it started and has the same tool name.
    for orphan in [n for n in children.get(None, []) if n["kind"] == "server"]:
        calls = [n for n in kept.values() if n["kind"] == "tool"
                 and str(n.get("tool", "")).endswith(str(orphan.get("tool")))
                 and n["start_ns"] <= orphan["start_ns"] <= n["start_ns"] + n["ms"] * 1e6]
        if calls:
            children[None].remove(orphan)
            orphan.update(parent=calls[0]["span_id"], joined="by time")
            children.setdefault(calls[0]["span_id"], []).append(orphan)
    for kids in children.values():
        kids.sort(key=lambda n: n["start_ns"])
    return kept, children


def label(n):
    k = n["kind"]
    if k == "llm":
        who = "" if n.get("agent") in (None, "main") else f" [{str(n['agent'])[:10]}]"
        if n.get("source") not in (None, "sdk", "repl_main_thread") and not n["source"].startswith("agent."):
            who += f" ({n['source']})"
        return (f"llm {n['model']}{who}  in {n['input']:,}  cache {n['cache_read']:,} read"
                f" + {n['cache_write']:,} written  out {n['output']:,}")
    if k == "tool":
        who = "" if n.get("agent") in (None, "main") else f" [{str(n['agent'])[:10]}]"
        return f"tool {n['tool']}{who}  {n['ms']:,.0f} ms"
    if k == "server":
        joined = f"  [joined {n['joined']}]" if n.get("joined") else ""
        return f"server {n['method']} {n['tool'] or ''}  ({n['service']}){'  ERROR ' + n['error'] if n['error'] else ''}{joined}"
    if k == "graph":
        bits = [f"user {n.get('user')}"]
        if "paths_found" in n:
            bits += [f"depth {n.get('depth_used')}/{n.get('depth_cap')}", f"reached {n.get('depth_reached')}",
                     f"paths {n['paths_found']}", f"coverage {n.get('coverage')}"]
        if "decision" in n:
            bits.append(f"access {n['decision']}")
        return f"{n['op']}  " + "  ".join(bits)
    return k


def tree(folder, out=sys.stdout):
    nodes, children = graph(load(folder))

    def walk(n, depth):
        print("  " * depth + label(n), file=out)
        for c in children.get(n["span_id"], []):
            walk(c, depth + 1)

    for root in children.get(None, []):
        print(f"trace {root['trace_id'][:8]}", file=out)
        walk(root, 1)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("tree", "nodes"):
        raise SystemExit(__doc__)
    if sys.argv[1] == "tree":
        tree(sys.argv[2])
    else:
        for n in graph(load(sys.argv[2]))[0].values():
            print(json.dumps(n))
