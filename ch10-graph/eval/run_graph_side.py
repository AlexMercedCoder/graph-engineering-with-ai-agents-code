#!/usr/bin/env python3
"""Run the multi-hop half of the Chapter 10 benchmark through the graph tools.

This scores the graph side automatically. The vector side is the reader's own
retriever, so record its answers by hand and compare. The point of the exercise
is the gap between the two on the multi-hop half, not the absolute numbers.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUERY = HERE.parent / "graph" / "query.py"

rows = [json.loads(l) for l in (HERE / "questions.jsonl").read_text().splitlines() if l.strip()]
multi = [r for r in rows if r["hops"] == "multi" and r.get("tool")]
print(f"{len(multi)} multi-hop questions with a graph tool call\n")
answered = 0
for r in multi:
    out = subprocess.run([sys.executable, str(QUERY), *r["tool"].split()],
                         capture_output=True, text=True).stdout.strip()
    ok = bool(out) and "No " not in out.split("\n")[0] and "Nothing" not in out
    answered += ok
    print(f"[{r['id']:>2}] {'ANSWERED' if ok else 'EMPTY   '}  {r['q']}")
    print(f"      tool: {r['tool']}")
    print(f"      -> {out.splitlines()[0] if out else '(no output)'}")
print(f"\ngraph answered {answered}/{len(multi)} multi-hop questions with a non-empty traversal")
print("A vector retriever over docs/ typically returns plausible passages for these")
print("and the connecting fact for very few. Score both and compare by question shape.")
