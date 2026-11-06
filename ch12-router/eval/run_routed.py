#!/usr/bin/env python3
"""Chapter 10's twenty questions, routed or left to the agent.

    python3 run_routed.py --harness claude --setup routed --runs 2 --out results/
    python3 run_routed.py --harness opencode --setup free --runs 2 --out results/

--setup routed classifies each question with router.route() (rules only) and
starts the session with only the chosen path's server: Chapter 10's
chunk_server.py for vector, its graph/server.py for graph, and both_server.py
when the route fans out to both. --setup free starts both_server.py, which
offers all four tools, and lets the agent choose. --setup vector or graph
starts one path's server regardless of the question. --questions combined.jsonl
runs the four questions that ask for a relationship and a description at once.
The prompt, the harness settings, and the transcripts match Chapter 10's
run_agents.py, so ../../ch10-graph/eval/grade.py grades the results and
Chapter 10's vector-only and graph-only runs are the baselines.
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CH10 = HERE.parents[1] / "ch10-graph"
sys.path[:0] = [str(HERE.parent), str(CH10 / "eval")]
import router  # noqa: E402
from run_agents import PROMPT, run_claude, run_opencode  # noqa: E402

PATH_SERVER = {"vector": ("docs", CH10 / "eval" / "chunk_server.py"),
               "graph": ("graph", CH10 / "graph" / "server.py")}
BOTH = ("knowledge", HERE / "both_server.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", choices=["claude", "opencode"], required=True)
    ap.add_argument("--setup", choices=["routed", "free", "vector", "graph"], required=True)
    ap.add_argument("--questions", type=Path, default=CH10 / "eval" / "questions.jsonl")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--ids", type=int, nargs="*")
    ap.add_argument("--model")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    model = a.model or {"claude": "claude-opus-5-5", "opencode": "openai/gpt-6.1-sol"}[a.harness]
    run = run_claude if a.harness == "claude" else run_opencode
    a.out.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in a.questions.read_text().splitlines() if l.strip()]
    for n in range(1, a.runs + 1):
        for r in rows:
            if a.ids and r["id"] not in a.ids:
                continue
            if a.setup == "routed":
                paths = router.route(r["q"]).paths
                chosen = "+".join(paths)
                if set(paths) == {"vector", "graph"}:
                    name, server = BOTH          # a fan-out route gets both paths' tools
                else:
                    name, server = PATH_SERVER.get(paths[0], PATH_SERVER["vector"])
            elif a.setup in PATH_SERVER:
                chosen, (name, server) = a.setup, PATH_SERVER[a.setup]
            else:
                chosen, (name, server) = "agent", BOTH
            stem = a.out / f"{a.harness}-{a.setup}-q{r['id']:02d}-run{n}"
            with tempfile.TemporaryDirectory() as tmp:
                answer, calls, tin, tout, cost, events = run(Path(tmp), name, server,
                                                             PROMPT.format(q=r["q"]), model)
            stem.with_suffix(".jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n")
            stem.with_suffix(".json").write_text(json.dumps({
                "harness": a.harness, "model": model, "side": a.setup, "route": chosen,
                "id": r["id"], "run": n, "answer": answer, "tool_calls": calls,
                "input_tokens": tin, "output_tokens": tout, "cost_usd": cost}, indent=1))
            print(f"{stem.name}: {chosen}, {len(calls)} tool calls, {tin} input tokens", flush=True)


if __name__ == "__main__":
    main()
