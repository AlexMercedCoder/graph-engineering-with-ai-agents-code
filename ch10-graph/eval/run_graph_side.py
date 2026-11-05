#!/usr/bin/env python3
"""Run the multi-hop half of the benchmark through the graph tools and grade it.

Each multi-hop question has one tool call that a correct traversal would make.
A question passes when the tool's results are exactly the expected entities:
every one of them, and nothing else.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUERY = HERE.parent / "graph" / "query.py"
CALLS = {11: "dependents NotificationsAPI 2", 12: "dependents BillingService 2",
         13: "dependencies OrderService 2", 14: "dependents NotificationsService 1",
         15: "dependents UserService 2", 16: "dependents PaymentsAPI 1",
         17: "dependents OrderService 2", 18: "dependencies ReportingService 2",
         19: "dependents PaymentsService 1", 20: "dependencies BillingService 2"}

rows = [json.loads(l) for l in (HERE / "questions.jsonl").read_text().splitlines() if l.strip()]
passed = 0
for r in (r for r in rows if r["id"] in CALLS):
    out = subprocess.run([sys.executable, str(QUERY), *CALLS[r["id"]].split()],
                         capture_output=True, text=True).stdout
    results = [l.split(" via ")[0] for l in out.splitlines() if " via " in l]
    hits = [any(re.fullmatch(p, name, re.I) or re.search(p, name, re.I) for name in results)
            for p in r["expect"]]
    extra = [n for n in results if not any(re.search(p, n, re.I) for p in r["expect"])]
    ok = all(hits) and not extra
    passed += ok
    note = f"  extra: {', '.join(extra)}" if extra else ""
    print(f"[{r['id']:>2}] {'PASS' if ok else 'MISS'} {sum(hits)}/{len(hits)}  "
          f"{CALLS[r['id']]:<34}{note}")
print(f"\ngraph tools answered {passed}/{len(CALLS)} multi-hop questions exactly")
