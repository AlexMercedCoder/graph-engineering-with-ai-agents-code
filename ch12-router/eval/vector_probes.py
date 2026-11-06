#!/usr/bin/env python3
"""Top-hit similarity for the probes that set search_docs' confidence thresholds.

    python3 vector_probes.py

Three questions the documents answer and two they don't. knowledge_server.py
calls a top hit of 0.75 or more high and 0.65 or more medium, between the two
groups. Rerun this with probes from your own corpus before you trust them.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ch10-graph" / "eval"))
from chunks import search  # noqa: E402

PROBES = [("answered", "What are the NotificationsAPI retry semantics?"),
          ("answered", "Which database does OrderService use?"),
          ("answered", "How often does RenewalsWorker re-bill subscriptions?"),
          ("not answered", "What was our loss ratio by region in Q3 2026?"),
          ("not answered", "Who is the CEO?")]

for kind, q in PROBES:
    hit = search(q, 1)[0]
    print(f"{hit['score']:.2f}  {kind:<13} {q}  -> {hit['id']}")
