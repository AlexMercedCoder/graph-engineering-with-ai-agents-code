#!/usr/bin/env python3
"""Ask an agent each benchmark question with one MCP server and nothing else.

    python3 run_agents.py --harness claude --side chunks --runs 2 --out results/
    python3 run_agents.py --harness opencode --side graph --runs 2 --out results/

--side chunks gives the agent search_docs (eval/chunk_server.py); --side graph
gives it the three traversal tools (graph/server.py). Built-in tools are turned
off, so the agent can't read docs/ directly. Each session runs in an empty
temporary folder. Run this with a Python that has mcp and fastembed installed,
because the servers are started with the same interpreter. Grade with grade.py.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVERS = {"chunks": ("docs", HERE / "chunk_server.py"),
           "graph": ("graph", HERE.parent / "graph" / "server.py")}
PROMPT = ("Answer this question about our system's architecture using the tools you have. "
          "Name every service, API, database, or configuration key the answer involves.\n\n"
          "Question: {q}")
OFF = ["bash", "edit", "write", "read", "grep", "glob", "list", "patch", "webfetch",
       "websearch", "todowrite", "todoread", "task", "skill"]


def run_claude(work, name, server, prompt, model):
    cfg = work / "mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {name: {
        "command": sys.executable, "args": [str(server)]}}}))
    out = subprocess.run(
        ["claude", "-p", prompt, "--model", model, "--tools", "", "--strict-mcp-config",
         "--mcp-config", str(cfg), "--allowedTools", f"mcp__{name}",
         "--setting-sources", "project,local", "--no-session-persistence",
         "--output-format", "stream-json", "--verbose"],
        cwd=work, capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
    events = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    answer, calls, tin, tout, cost = "", [], 0, 0, None
    for e in events:
        if e.get("type") == "assistant":
            for c in e["message"]["content"]:
                if c.get("type") == "tool_use":
                    calls.append({"tool": c["name"], "input": c["input"]})
        if e.get("type") == "result":
            answer = e.get("result", "")
            u = e.get("usage", {})
            tin = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                   + u.get("cache_creation_input_tokens", 0))
            tout = u.get("output_tokens", 0)
            cost = e.get("total_cost_usd")
    return answer, calls, tin, tout, cost, events


def run_opencode(work, name, server, prompt, model):
    (work / "opencode.json").write_text(json.dumps({
        "$schema": "https://opencode.ai/config.json",
        "mcp": {name: {"type": "local", "command": [sys.executable, str(server)]}},
        "tools": {t: False for t in OFF}}))
    out = subprocess.run(["opencode", "run", "--dir", str(work), "--format", "json",
                          "-m", model, prompt],
                         cwd=work, capture_output=True, text=True, timeout=600,
                         stdin=subprocess.DEVNULL)
    events = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    texts, calls, tin, tout = [], [], 0, 0
    for e in events:
        p = e.get("part") or {}
        if p.get("type") == "text":
            texts.append(p.get("text", ""))
        if p.get("type") == "tool":
            calls.append({"tool": p.get("tool"), "input": (p.get("state") or {}).get("input")})
        if p.get("type") == "step-finish":
            t = p.get("tokens") or {}
            c = t.get("cache") or {}
            tin += t.get("input", 0) + c.get("read", 0) + c.get("write", 0)
            tout += t.get("output", 0)
    return (texts[-1] if texts else ""), calls, tin, tout, None, events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", choices=["claude", "opencode"], required=True)
    ap.add_argument("--side", choices=list(SERVERS), required=True)
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--ids", type=int, nargs="*")
    ap.add_argument("--model")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    model = a.model or {"claude": "claude-opus-5-5", "opencode": "openai/gpt-6.1-sol"}[a.harness]
    run = run_claude if a.harness == "claude" else run_opencode
    name, server = SERVERS[a.side]
    a.out.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in (HERE / "questions.jsonl").read_text().splitlines() if l.strip()]
    for n in range(1, a.runs + 1):
        for r in rows:
            if a.ids and r["id"] not in a.ids:
                continue
            stem = a.out / f"{a.harness}-{a.side}-q{r['id']:02d}-run{n}"
            with tempfile.TemporaryDirectory() as tmp:
                answer, calls, tin, tout, cost, events = run(Path(tmp), name, server,
                                                       PROMPT.format(q=r["q"]), model)
            stem.with_suffix(".jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
            stem.with_suffix(".json").write_text(json.dumps({
                "harness": a.harness, "model": model, "side": a.side, "id": r["id"], "run": n,
                "answer": answer, "tool_calls": calls, "input_tokens": tin,
                "output_tokens": tout, "cost_usd": cost}, indent=1))
            print(f"{stem.name}: {len(calls)} tool calls, {tin} input tokens", flush=True)


if __name__ == "__main__":
    main()
