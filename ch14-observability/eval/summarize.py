#!/usr/bin/env python3
"""Tabulate triage.json from every run folder under <runs-dir>.

    python3 eval/summarize.py <runs-dir>
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

rows = defaultdict(list)
for f in sorted(Path(sys.argv[1]).glob("*/triage.json")):
    t = json.loads(f.read_text())
    rows[(t["harness"], t["condition"])].append(t)
print("| Harness | Condition | Runs | Verdicts | Answer correct | Mean tokens (in / cache read / out) |")
print("|---|---|---|---|---|---|")
for (h, c), ts in sorted(rows.items(), key=lambda kv: (kv[0][0], ["baseline", "bad-description", "depth-cap-silent", "depth-cap", "soft-body", "stale-rule"].index(kv[0][1]))):
    verdicts = defaultdict(int)
    for t in ts:
        verdicts[t["verdict"]] += 1
    tok = {k: sum(t["tokens"][k] for t in ts) / len(ts) for k in ("input", "cache_read", "output")}
    print(f"| {h} | {c} | {len(ts)} | {', '.join(f'{v} {k}' for k, v in verdicts.items())} | "
          f"{sum(t['answer_correct'] for t in ts)} of {len(ts)} | "
          f"{tok['input']:,.0f} / {tok['cache_read']:,.0f} / {tok['output']:,.0f} |")
