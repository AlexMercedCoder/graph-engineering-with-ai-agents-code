#!/usr/bin/env python3
"""Check the graph server's spans without a harness: call the traced tool in-process
at depth caps 4 and 1 and inspect the spans it records.

    python3 tools/check-instrumentation.py      # prints "instrumentation ok" or fails
"""
import logging
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
if "CHILD" not in os.environ:
    graph_dir = HERE.parent / "ch10-graph" / "graph"
    if not (graph_dir / "project-graph.db").exists():
        subprocess.run([sys.executable, "extract.py"], cwd=graph_dir, check=True, capture_output=True)
    for cap, coverage, paths in (("4", "complete", 7), ("1", "partial", 3)):
        env = dict(os.environ, CHILD="1", GRAPH_MAX_DEPTH=cap, COLLECTOR="http://127.0.0.1:9",
                   EXPECT=f"{coverage},{paths}")
        if subprocess.run([sys.executable, __file__], env=env).returncode:
            sys.exit(1)
    print("instrumentation ok")
    sys.exit(0)

logging.disable(logging.CRITICAL)
sys.path.insert(0, str(HERE / "server"))
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # noqa: E402
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter  # noqa: E402

import graph_server  # noqa: E402

memory = InMemorySpanExporter()
graph_server.provider.add_span_processor(SimpleSpanProcessor(memory))
reply = graph_server.traced_dependents("UserService", 4)
span = [s for s in memory.get_finished_spans() if s.name == "graph.find_dependents"][0]
coverage, paths = os.environ["EXPECT"].split(",")
a = span.attributes
assert a["graph.coverage"] == coverage, a["graph.coverage"]
assert a["graph.paths_found"] == int(paths), a["graph.paths_found"]
assert ("Coverage is partial" in reply) == (coverage == "partial"), reply
assert a["graph.subject"] == "unknown"
