#!/usr/bin/env python3
"""Compare the graph's Service nodes with the services actually deployed.

Manifest names go through the extraction pipeline's normalize() and alias table first.
Fails when the graph holds a service the manifest doesn't (retired, or never real)
or the manifest names a service the graph lacks (undocumented). Lists services
with no edges as a warning, since a refresh can leave a retired one behind.

  python3 eval/check_manifest.py [manifest] [graph.db]
"""
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "graph"))
from extract import normalize  # noqa: E402  the graph's own name resolution and aliases
manifest = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "deploy" / "services.txt"
db = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
    os.environ.get("GRAPH_DB", ROOT / "graph" / "project-graph.db"))

# Deployment tools name services their own way (billing-service, the user service);
# map each name through the same normalization and aliases extraction uses.
deployed = {normalize(line.strip()) for line in manifest.read_text().splitlines()
            if line.strip() and not line.startswith("#")}
con = sqlite3.connect(db)
in_graph = {n for (n,) in con.execute("SELECT name FROM nodes WHERE type = 'Service'")}
linked = {n for (n,) in con.execute("SELECT source FROM edges UNION SELECT target FROM edges")}
con.close()

stale = sorted(in_graph - deployed)
missing = sorted(deployed - in_graph)
orphans = sorted(in_graph - linked)
for name in stale:
    print(f"stale: {name} is in the graph but not deployed")
for name in missing:
    print(f"missing: {name} is deployed but no document describes it")
for name in orphans:
    print(f"warning: {name} has no edges")
if stale or missing:
    sys.exit(1)
print(f"graph matches the manifest: {len(in_graph)} services")
