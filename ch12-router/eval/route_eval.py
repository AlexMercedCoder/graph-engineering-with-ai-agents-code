#!/usr/bin/env python3
"""Measure the router on a labeled question set without retrieving anything.

    python3 route_eval.py                  rules, unmatched questions take the default path
    python3 route_eval.py --model          rules, unmatched questions go to the model
    python3 route_eval.py --model-only     every question goes to the model

A mis-route is scored by what it costs. Sending a graph question to vector
search costs extra searches but still answers it (Chapter 10's agents answered
multi-hop questions from search alone, with about twice the calls). Every other
mis-route sends the question to a path that can't answer it. A question's
"accept" list names other paths that answer it correctly, from the earlier
chapters' runs.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import router  # noqa: E402

COST_ONLY = {("graph", "vector")}     # (expected, got) pairs that still answer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, default=HERE / "routing.jsonl")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--model", action="store_true")
    g.add_argument("--model-only", action="store_true")
    ap.add_argument("--json", type=Path, help="write per-question results here")
    a = ap.parse_args()
    if a.model or a.model_only:
        os.environ.setdefault("ROUTER_MODEL", "claude-haiku-5-5")

    rows = [json.loads(l) for l in a.file.read_text().splitlines() if l.strip()]
    results, cost, secs = [], 0.0, 0.0
    for r in rows:
        t = time.time()
        if a.model_only:
            ans = router.classify_with_model(r["q"])
            got, by = (ans[0] if ans else ()), "model"
            cost += (ans[1] or 0) if ans else 0
        else:
            rt = router.route(r["q"])
            got, by = rt.paths, rt.matched_by
            cost += rt.cost_usd
        secs += time.time() - t
        want = tuple(r["expected"])
        ok = set(got) == set(want) or (len(got) == 1 and got[0] in r.get("accept", []))
        kind = "" if ok else ("cost only" if (want[0], got[0] if got else "") in COST_ONLY
                              and len(want) == 1 else "wrong path")
        results.append({**r, "got": list(got), "by": by, "ok": ok, "miss": kind})

    n = len(results)
    ok = sum(x["ok"] for x in results)
    fell = sum(x["by"] != "rule" for x in results)
    print(f"routing accuracy: {ok}/{n}")
    if not a.model_only:
        print(f"unmatched by rules: {fell}/{n}")
    print(f"mis-routes that only cost more: {sum(x['miss'] == 'cost only' for x in results)}")
    print(f"mis-routes to a path that can't answer: {sum(x['miss'] == 'wrong path' for x in results)}")
    if a.model or a.model_only:
        print(f"model calls: {fell if a.model else n}, {secs:.0f} s, ${cost:.4f}")
    for x in results:
        if not x["ok"]:
            print(f"  {x['miss']:>10}  {x['q'][:70]!r}\n              expected {'+'.join(x['expected'])}, "
                  f"got {'+'.join(x['got']) or 'nothing'} ({x['by']})")
    if a.json:
        a.json.write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
