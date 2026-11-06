#!/usr/bin/env python3
"""Rerun the triage over the published runs and compare each verdict with the one
recorded when the runs were published (runs/2026-11-05-triage/verdicts.json).

    python3 eval/check-saved-runs.py            # prints "N verdicts match" or the differences
    python3 eval/check-saved-runs.py --record   # rewrite verdicts.json from the current triage

No model and no network: this tests triage.py, graphspans.py, and expected.json
against traces that don't change.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from triage import triage  # noqa: E402

RUNS = HERE.parent / "runs" / "2026-11-05-triage"
current = {p.name: (lambda t: {"verdict": t["verdict"], "answer_correct": t["answer_correct"]})(triage(p))
           for p in sorted(RUNS.iterdir()) if (p / "transcript.jsonl").exists()}
if "--record" in sys.argv:
    (RUNS / "verdicts.json").write_text(json.dumps(current, indent=1) + "\n")
    print(f"recorded {len(current)} verdicts")
    sys.exit(0)
recorded = json.loads((RUNS / "verdicts.json").read_text())
diff = {k: (recorded.get(k), current.get(k)) for k in set(recorded) | set(current)
        if recorded.get(k) != current.get(k)}
for k, (was, now) in sorted(diff.items()):
    print(f"{k}: recorded {was}, now {now}")
print(f"{len(current) - len(diff)} of {len(recorded)} verdicts match")
sys.exit(1 if diff else 0)
