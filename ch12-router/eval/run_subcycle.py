#!/usr/bin/env python3
"""The brief task (brief_task.md), with retrieval inline or in a worker.

    python3 run_subcycle.py --harness claude --setup inline --run 1 --out results/
    python3 run_subcycle.py --harness claude --setup worker --run 1 --out results/
    python3 run_subcycle.py --harness claude --setup worker --task act_fix.md --act --run 1 --out results/

inline: the main session has the project-knowledge tools and loads the
retrieve-evidence and act-on-evidence skills.
worker: the main session has only the worker tool and Write, and loads
act-on-evidence; the retrieval-worker (agents/retrieval-worker.md) has
the project-knowledge tools, which only it can see.

--act copies Chapter 9's exercise configuration into config/ and gives the
main session Read and Edit, for the tasks that change a file (act_fix.md,
act_refuse.md); the edited payments.conf is saved with the transcript.

Each session runs in a fresh folder as the analyst identity. The script saves
the transcript, brief.md, and a summary of the main session's requests, so
grade_brief.py can score answers and the context each setup carried.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "agents"))
import build_agents_json  # noqa: E402
SERVER = ROOT / "knowledge_server.py"
ENV = {"CATALOG_IDENTITY": "analyst", "CATALOG_SCOPES": "catalog:read data:read"}
OC_OFF = ["bash", "read", "grep", "glob", "list", "webfetch",
          "websearch", "todowrite", "todoread"]


def worker_definition():
    text = (ROOT / "agents" / "retrieval-worker.md").read_text()
    _, front, body = text.split("---", 2)
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", front, re.M))
    return meta, body.strip()


def copy_skills(work, names):
    for n in names:
        shutil.copytree(ROOT / "skills" / n, work / ".claude" / "skills" / n)


def server_cfg():
    return {"command": sys.executable, "args": [str(SERVER)], "env": ENV}


def run_claude(work, setup, model, task, act):
    meta, body = worker_definition()
    extra = ["Read", "Edit"] if act else []
    args = ["claude", "-p", task, "--model", model, "--strict-mcp-config",
            "--setting-sources", "project,local", "--no-session-persistence",
            "--output-format", "stream-json", "--verbose"]
    if setup == "inline":
        copy_skills(work, ["retrieve-evidence", "act-on-evidence"])
        (work / "mcp.json").write_text(json.dumps({"mcpServers": {"project-knowledge": server_cfg()}}))
        args += ["--mcp-config", str(work / "mcp.json"), "--tools", ",".join(["Write", "Skill"] + extra),
                 "--allowedTools", "mcp__project-knowledge", "Write", "Skill", *extra]
    else:
        copy_skills(work, ["act-on-evidence"])
        (work / "mcp.json").write_text(json.dumps({"mcpServers": {}}))
        (work / "agents.json").write_text(json.dumps(build_agents_json.definition()))
        args += ["--agents", (work / "agents.json").read_text(), "--mcp-config", str(work / "mcp.json"),
                 "--tools", ",".join(["Agent", "Write", "Skill"] + extra),
                 "--allowedTools", "mcp__project-knowledge", "Agent", "Write", "Skill", *extra]
    out = subprocess.run(args, cwd=work, capture_output=True, text=True, timeout=1200,
                         stdin=subprocess.DEVNULL)
    events = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    main_reqs, sub_reqs, calls, seen = [], [], [], set()
    cost = None
    for e in events:
        if e.get("type") == "assistant":
            m = e["message"]
            sub = e.get("parent_tool_use_id") is not None
            if m.get("id") not in seen:      # one request can span several events
                seen.add(m.get("id"))
                u = m.get("usage", {})
                ctx = (u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                       + u.get("cache_creation_input_tokens", 0))
                (sub_reqs if sub else main_reqs).append(ctx)
            for c in m["content"]:
                if c.get("type") == "tool_use":
                    calls.append({"by": "worker" if sub else "main", "tool": c["name"],
                                  "input": c["input"]})
        if e.get("type") == "result":
            cost = e.get("total_cost_usd")
    return events, main_reqs, sub_reqs, calls, cost


def run_opencode(work, setup, model, task, act):
    meta, body = worker_definition()
    tools = {t: False for t in OC_OFF if not (act and t == "read")}
    cfg = {"$schema": "https://opencode.ai/config.json",
           "mcp": {"project-knowledge": {"type": "local", "command": [sys.executable, str(SERVER)],
                                         "environment": ENV}}}
    if setup == "inline":
        copy_skills(work, ["retrieve-evidence", "act-on-evidence"])
        tools.update({"task": False})
    else:
        copy_skills(work, ["act-on-evidence"])
        tools.update({"project-knowledge_*": False})
        cfg["agent"] = {meta["name"]: {
            "mode": "subagent", "description": meta["description"], "prompt": body,
            "tools": {"project-knowledge_*": True, "write": False, "skill": False}}}
    cfg["tools"] = tools
    (work / "opencode.json").write_text(json.dumps(cfg))
    out = subprocess.run(["opencode", "run", "--dir", str(work), "--format", "json", "-m", model, task],
                         cwd=work, capture_output=True, text=True, timeout=1200,
                         stdin=subprocess.DEVNULL)
    events = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    main_reqs, sub_reqs, calls = [], [], []
    for e in events:
        p = e.get("part") or {}
        if p.get("type") == "tool":
            state = p.get("state") or {}
            calls.append({"by": "main", "tool": p.get("tool"), "input": state.get("input")})
            child = (state.get("metadata") or {}).get("sessionId")
            if p.get("tool") == "task" and child:
                # the worker runs in a child session that `opencode run` doesn't stream
                exp = subprocess.run(["opencode", "export", child], capture_output=True, text=True,
                                     timeout=120, stdin=subprocess.DEVNULL)
                doc = json.loads(exp.stdout[exp.stdout.index("{"):])
                for m in doc.get("messages", []):
                    for q in m.get("parts", []):
                        if q.get("type") == "tool":
                            calls.append({"by": "worker", "tool": q.get("tool"),
                                          "input": (q.get("state") or {}).get("input")})
                        if q.get("type") == "step-finish":
                            sub_reqs.append(_oc_tokens(q))
        if p.get("type") == "step-finish":
            main_reqs.append(_oc_tokens(p))
    return events, main_reqs, sub_reqs, calls, None


def _oc_tokens(part):
    t = part.get("tokens") or {}
    c = t.get("cache") or {}
    return t.get("input", 0) + c.get("read", 0) + c.get("write", 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", choices=["claude", "opencode"], required=True)
    ap.add_argument("--setup", choices=["inline", "worker"], required=True)
    ap.add_argument("--run", type=int, default=1)
    ap.add_argument("--model")
    ap.add_argument("--task", default="brief_task.md")
    ap.add_argument("--act", action="store_true")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    task = (HERE / a.task).read_text()
    label = "" if a.task == "brief_task.md" else Path(a.task).stem + "-"
    model = a.model or {"claude": "claude-opus-5-5", "opencode": "openai/gpt-6.1-sol"}[a.harness]
    a.out.mkdir(parents=True, exist_ok=True)
    stem = a.out / f"{label}{a.harness}-{a.setup}-run{a.run}"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=work)
        if a.act:
            shutil.copytree(ROOT.parent / "ch09-mcp" / "exercise" / "config", work / "config")
        t = time.time()
        run = run_claude if a.harness == "claude" else run_opencode
        events, main_reqs, sub_reqs, calls, cost = run(work, a.setup, model, task, a.act)
        secs = time.time() - t
        brief = work / "brief.md"
        stem.with_suffix(".brief.md").write_text(brief.read_text() if brief.exists() else "")
        if a.act:
            conf = work / "config" / "staging" / "payments.conf"
            stem.with_suffix(".payments.conf").write_text(conf.read_text() if conf.exists() else "")
    stem.with_suffix(".jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
    summary = {"harness": a.harness, "model": model, "setup": a.setup, "run": a.run,
               "seconds": round(secs), "main_requests": len(main_reqs),
               "main_input_tokens": sum(main_reqs), "main_last_context": max(main_reqs, default=0),
               "worker_requests": len(sub_reqs), "worker_input_tokens": sum(sub_reqs),
               "tool_calls": calls, "cost_usd": cost}
    stem.with_suffix(".json").write_text(json.dumps(summary, indent=1))
    print(f"{stem.name}: main {len(main_reqs)} requests, {sum(main_reqs)} input tokens, "
          f"largest {max(main_reqs, default=0)}; worker {sum(sub_reqs)}; {secs:.0f} s; cost {cost}")


if __name__ == "__main__":
    main()
