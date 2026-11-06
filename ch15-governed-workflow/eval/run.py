#!/usr/bin/env python3
"""One governed-change session, end to end.

    python3 run.py --harness claude --scenario fix-approve --run 1 --out ../runs/mine
    python3 run.py --harness opencode --scenario fix-reject --run 1 --out ../runs/mine

Seeds the deployed configurations for the scenario (scenarios.json), starts
the knowledge server (8817), the change gate (8818), the scripted reviewer,
and, for Claude Code, Chapter 14's collector (8819). Then it runs the harness
in a fresh folder with the governed-change plugin: loaded with --plugin-dir in
Claude Code, translated into opencode.json and .claude/skills for OpenCode.
Saves the transcript, report.md, the decision log, the packets the reviewer
saw, the deployed files, the audit log, the spans, and a summary.
"""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CH15 = HERE.parent
ROOT = CH15.parent
PLUGIN = CH15 / "marketplace" / "plugins" / "governed-change"
SCENARIOS = json.loads((HERE / "scenarios.json").read_text())
# The agent may write report.md in its own folder and nothing else.
CLAUDE_SETTINGS = json.dumps({"permissions": {"blockWritesOutsideWorkingDirectories": True}})
OC_PERMISSION = {"edit": {"*": "deny", "report.md": "allow"}, "external_directory": "deny",
                 **{t: "deny" for t in ("bash", "read", "grep", "glob", "list", "webfetch", "websearch",
                                        "codesearch", "todowrite", "task")}}
OTEL = {"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "CLAUDE_CODE_ENHANCED_TELEMETRY_BETA": "1",
        "OTEL_TRACES_EXPORTER": "otlp", "OTEL_LOGS_EXPORTER": "otlp", "OTEL_METRICS_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:8819", "OTEL_LOG_TOOL_DETAILS": "1",
        "OTEL_METRIC_EXPORT_INTERVAL": "2000"}


def tokens():
    env = dict(re.findall(r"^(\w+)=(.*)$", (CH15 / "config" / "test-tokens.env").read_text(), re.M))
    exp = min(v["exp"] for v in json.loads((CH15 / "config" / "test-tokens.json").read_text()).values())
    if exp < time.time() + 900:
        subprocess.run([sys.executable, CH15 / "tools" / "make-test-tokens.py"], check=True)
        return tokens()
    return env


def start(cmd, env, log, cwd=None):
    return subprocess.Popen(cmd, env={**os.environ, **env}, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL)


def opencode_config(work, client_timeout=None):
    """The plugin's servers and skills, in OpenCode's terms."""
    servers = json.loads((PLUGIN / ".mcp.json").read_text())["mcpServers"]
    mcp = {}
    for name, s in servers.items():
        headers = {k: re.sub(r"\$\{(\w+)\}", r"{env:\1}", v) for k, v in s.get("headers", {}).items()}
        mcp[name] = {"type": "remote", "url": s["url"], "oauth": False, "headers": headers}
        t = s.get("timeout") if client_timeout is None or name != "change-gate" else client_timeout
        if t:
            mcp[name]["timeout"] = t
    shutil.copytree(PLUGIN / "skills", work / ".claude" / "skills")
    (work / ".opencode" / "plugins").mkdir(parents=True)
    shutil.copy(ROOT / "ch06-hooks" / "opencode" / "guards.js", work / ".opencode" / "plugins")
    cfg = {"$schema": "https://opencode.ai/config.json", "mcp": mcp, "permission": OC_PERMISSION}
    (work / "opencode.json").write_text(json.dumps(cfg, indent=1))


def run_claude(work, task, model, env, client_timeout=None):
    servers = "mcp__plugin_governed-change_project-knowledge", "mcp__plugin_governed-change_change-gate"
    plugin = PLUGIN
    if client_timeout is not None:  # the same plugin with a different client timeout for the gate
        plugin = work.parent / "plugin"
        shutil.copytree(PLUGIN, plugin)
        cfg = json.loads((plugin / ".mcp.json").read_text())
        cfg["mcpServers"]["change-gate"].pop("timeout", None)
        if client_timeout:
            cfg["mcpServers"]["change-gate"]["timeout"] = client_timeout
        (plugin / ".mcp.json").write_text(json.dumps(cfg, indent=1))
    args = ["claude", "-p", task, "--model", model, "--plugin-dir", str(plugin),
            "--setting-sources", "project,local", "--no-session-persistence",
            "--tools", "Skill,Write", "--allowedTools", *servers, "Skill", "Edit(/report.md)",
            "--settings", CLAUDE_SETTINGS,
            "--output-format", "stream-json", "--verbose", "--max-turns", "40"]
    out = subprocess.run(args, cwd=work, capture_output=True, text=True, timeout=1500,
                         stdin=subprocess.DEVNULL,
                         env={**os.environ, **env, **OTEL, "ENABLE_CLAUDEAI_MCP_SERVERS": "false"})
    events = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    calls, reqs, seen, cost = [], [], set(), None
    for e in events:
        if e.get("type") == "assistant":
            m = e["message"]
            if m.get("id") not in seen:
                seen.add(m.get("id"))
                u = m.get("usage", {})
                reqs.append(u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                            + u.get("cache_creation_input_tokens", 0))
            calls += [{"tool": c["name"], "input": c["input"]} for c in m["content"]
                      if c.get("type") == "tool_use"]
        if e.get("type") == "result":
            cost = e.get("total_cost_usd")
    return events, calls, reqs, cost


def run_opencode(work, task, model, env, client_timeout=None):
    opencode_config(work, client_timeout)
    out = subprocess.run(["opencode", "run", "--dir", str(work), "--format", "json", "-m", model, task],
                         cwd=work, capture_output=True, text=True, timeout=1500,
                         stdin=subprocess.DEVNULL, env={**os.environ, **env})
    events = [json.loads(l) for l in out.stdout.splitlines() if l.startswith("{")]
    calls, reqs = [], []
    for e in events:
        p = e.get("part") or {}
        if p.get("type") == "tool":
            calls.append({"tool": p.get("tool"), "input": (p.get("state") or {}).get("input")})
        if p.get("type") == "step-finish":
            t = p.get("tokens") or {}
            c = t.get("cache") or {}
            reqs.append(t.get("input", 0) + c.get("read", 0) + c.get("write", 0))
    return events, calls, reqs, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", choices=["claude", "opencode"], required=True)
    ap.add_argument("--scenario", choices=list(SCENARIOS), required=True)
    ap.add_argument("--run", type=int, default=1)
    ap.add_argument("--model")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--review-delay", type=float, default=5,
                    help="seconds the scripted reviewer reads before deciding")
    ap.add_argument("--client-timeout", type=int,
                    help="change-gate tool timeout in ms for the client; 0 leaves it out (default: the plugin's)")
    ap.add_argument("--graph", type=Path,
                    help="a folder with project-graph.db and docs/ to serve instead of Chapter 10's (scale/build)")
    a = ap.parse_args()
    sc = SCENARIOS[a.scenario]
    model = a.model or {"claude": "claude-opus-5-5", "opencode": "openai/gpt-6.1-sol"}[a.harness]
    out = (a.out / f"{a.harness}-{a.scenario}-run{a.run}").resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = tokens()
    procs = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        state, work = tmp / "state", tmp / "work"
        work.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=work)
        senv = {"GOVERNED_STATE": str(state), "GATE_TIMEOUT": str(sc.get("timeout", 120)),
                "REVIEW_DELAY": str(a.review_delay)}
        if a.graph:
            senv["GRAPH_DB"] = str((a.graph / "project-graph.db").resolve())
            senv["GRAPH_DOCS"] = str((a.graph / "docs").resolve())
        subprocess.run([sys.executable, CH15 / "tools" / "seed-deploy.py", "--fault", sc["fault"]],
                       env={**os.environ, **senv}, check=True, capture_output=True)
        seed = {e: (state / "deploy" / e / "payments.conf").read_text() for e in ("staging", "production")}
        logs = open(out / "servers.log", "w")
        try:
            if a.harness == "claude":
                procs.append(start([sys.executable, ROOT / "ch14-observability" / "collector.py",
                                    "--port", "8819", "--out", str(out / "telemetry")], {}, logs))
                senv["COLLECTOR"] = "http://127.0.0.1:8819"
            procs.append(start([sys.executable, "knowledge_http.py"], senv, logs, CH15 / "servers"))
            procs.append(start([sys.executable, "gate_server.py"], senv, logs, CH15 / "servers"))
            procs.append(start([sys.executable, "reviewer.py", *sc["review"]], senv, logs, CH15 / "gate"))
            time.sleep(5)
            t = time.time()
            run = run_claude if a.harness == "claude" else run_opencode
            task = sc["task"].replace("{deploy}", str(state / "deploy"))
            events, calls, reqs, cost = run(work, task, model, env, a.client_timeout)
            secs = round(time.time() - t)
            time.sleep(3)          # let the last spans export
        finally:
            for p in procs:
                p.send_signal(signal.SIGTERM)
            for p in procs:
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    p.kill()
            logs.close()
        for name in ("decisions.jsonl", "seen-packets.jsonl"):
            src = state / name
            (out / name).write_text(src.read_text() if src.exists() else "")
        for e in ("staging", "production"):
            (out / f"{e}.seed.conf").write_text(seed[e])
            (out / f"{e}.conf").write_text((state / "deploy" / e / "payments.conf").read_text())
        for src, name in ((work / "report.md", "report.md"), (work / ".agent-work" / "audit.jsonl", "audit.jsonl")):
            (out / name).write_text(src.read_text() if src.exists() else "")
    (out / "transcript.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
    summary = {"harness": a.harness, "model": model, "scenario": a.scenario, "run": a.run,
               "date": time.strftime("%Y-%m-%d"), "seconds": secs, "requests": len(reqs),
               "input_tokens": sum(reqs), "largest_request": max(reqs, default=0),
               "cost_usd": cost, "tool_calls": calls}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(f"{out.name}: {len(calls)} calls, {sum(reqs)} input tokens, {secs} s, cost {cost}")


if __name__ == "__main__":
    main()
