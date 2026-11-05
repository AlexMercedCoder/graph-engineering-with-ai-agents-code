#!/usr/bin/env python3
"""Check that an incremental refresh leaves the same graph a full rebuild would.

Works on a temporary copy of docs/ and the saved extractions, so it needs no
model: it removes a document, refreshes, compares against a rebuild of the
smaller set, then restores the document and compares against the original.
"""
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

GRAPH = Path(__file__).resolve().parent.parent / "graph"


def run(tmp, db, *args):
    env = dict(os.environ, GRAPH_DOCS=str(tmp / "docs"), GRAPH_CACHE=str(tmp / "extractions"),
               GRAPH_DB=str(tmp / db))
    out = subprocess.run([sys.executable, str(GRAPH / "extract.py"), *args],
                         env=env, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def rows(tmp, db):
    con = sqlite3.connect(tmp / db)
    got = (sorted(con.execute("SELECT name, type FROM nodes")),
           sorted(con.execute("SELECT source, type, target, source_doc FROM edges")))
    con.close()
    return got


with tempfile.TemporaryDirectory() as t:
    tmp = Path(t)
    shutil.copytree(GRAPH.parent / "docs", tmp / "docs")
    shutil.copytree(GRAPH / "extractions", tmp / "extractions")
    print(run(tmp, "live.db", "--rebuild").splitlines()[0])
    original = rows(tmp, "live.db")

    doc = tmp / "docs" / "search-service.md"
    saved = doc.read_text()
    doc.unlink()
    print(run(tmp, "live.db"))
    run(tmp, "fresh.db", "--rebuild")
    ok_remove = rows(tmp, "live.db") == rows(tmp, "fresh.db")
    print(f"after removing {doc.name}: patched graph {'matches' if ok_remove else 'DIFFERS FROM'} a full rebuild")

    doc.write_text(saved)
    print(run(tmp, "live.db"))
    ok_restore = rows(tmp, "live.db") == original
    print(f"after restoring it: patched graph {'matches' if ok_restore else 'DIFFERS FROM'} the original")
sys.exit(0 if ok_remove and ok_restore else 1)
