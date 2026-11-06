#!/usr/bin/env python3
"""Time one call of each retrieval tool, without a model, to compare their overhead.

  python3 eval/time_tools.py [calls]
"""
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "graph"), str(ROOT / "eval")]
import chunks  # noqa: E402
from traversal import find_dependents  # noqa: E402

CALLS = int(sys.argv[1]) if len(sys.argv) > 1 else 50
QUESTION = "Which services break if the NotificationsAPI changes its retry semantics?"

t = time.perf_counter()
chunks.search(QUESTION, 3)
print(f"vector search, first call (loads the model and embeds 41 sections): "
      f"{(time.perf_counter() - t) * 1000:.0f} ms")
for label, fn in [("vector search", lambda: chunks.search(QUESTION, 3)),
                  ("graph traversal, 2 hops", lambda: find_dependents("NotificationsAPI", 2)),
                  ("graph traversal, 4 hops", lambda: find_dependents("NotificationsAPI", 4))]:
    samples = []
    for _ in range(CALLS):
        t = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t) * 1000)
    print(f"{label}: median {statistics.median(samples):.2f} ms over {CALLS} calls")
