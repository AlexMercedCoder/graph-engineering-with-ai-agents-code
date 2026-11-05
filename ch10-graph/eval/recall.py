#!/usr/bin/env python3
"""How much of each answer the flat retriever puts in front of the agent.

For every benchmark question, take the top-k sections by similarity and check
how many of the sections that state the answer's facts are among them.

    python3 recall.py          k = 3 and 5
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from chunks import search

rows = [json.loads(l) for l in (HERE / "questions.jsonl").read_text().splitlines() if l.strip()]
for k in (3, 5):
    print(f"top-{k} sections")
    for shape in ("single", "multi"):
        qs = [r for r in rows if r["hops"] == shape]
        full, frac = 0, 0.0
        for r in qs:
            got = {h["id"] for h in search(r["q"], k)}
            hit = len(set(r["support"]) & got) / len(r["support"])
            frac += hit
            full += hit == 1
            if "-v" in sys.argv:
                print(f"  [{r['id']:>2}] {hit:4.0%}  missing: {sorted(set(r['support']) - got)}")
        print(f"  {shape:<6} all supporting sections retrieved for {full}/{len(qs)} questions; "
              f"mean share retrieved {frac / len(qs):.0%}")
