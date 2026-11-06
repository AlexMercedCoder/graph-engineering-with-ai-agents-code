#!/usr/bin/env python3
"""What the instrumentation costs per tool call: find_dependents with and without
the traced wrapper, in-process, N calls each (default 3,000), then the pieces
the wrapper adds: resolving the name, walking the graph, and the one-hop probe.

    python3 collector.py &                  # spans go somewhere real
    python3 tools/bench-overhead.py [N]

The traced version also runs the traversal one hop deeper to decide coverage,
so most of its overhead is that second query, not the span.
"""
import logging
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("COLLECTOR", "http://127.0.0.1:8814")   # start collector.py first
logging.disable(logging.CRITICAL)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))
import graph_server  # noqa: E402
import traversal  # noqa: E402

n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
for name, fn in (("plain", traversal.find_dependents), ("traced", graph_server.traced_dependents)):
    fn("UserService", 4)
    start = time.perf_counter()
    for _ in range(n):
        fn("UserService", 4)
    print(f"{name:7} {(time.perf_counter() - start) / n * 1000:.3f} ms per call ({n} calls)")

root, _, _ = graph_server.resolve_entity("UserService", ("Service", "APIEndpoint"))
for name, fn in (("resolve", lambda: graph_server.resolve_entity("UserService", ("Service", "APIEndpoint"))),
                 ("walk", lambda: graph_server.traverse_incoming(root, ["CALLS", "DEPENDS_ON"], 4)),
                 ("probe", lambda: graph_server.one_hop_further(root, 4))):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    print(f"{name:7} {(time.perf_counter() - start) / n * 1000:.3f} ms per call")
