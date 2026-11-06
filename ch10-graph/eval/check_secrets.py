#!/usr/bin/env python3
"""Check that extraction refuses a folder holding credentials, before any model call.

Works on temporary copies of docs/ and the saved extractions. The planted values are fake.
  python3 eval/check_secrets.py
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GRAPH = Path(__file__).resolve().parent.parent / "graph"
CASES = {
    "an .env file beside the documents": ("payments.env", "PAYMENT_API_KEY=not-a-real-key-0000\n"),
    "a private key pasted into a document": (
        "runbook.md", "# Runbook\n\n-----BEGIN OPENSSH PRIVATE KEY-----\nfake\n"),
    "an assignment of a password": ("deploy.md", "# Deploy\n\nSet password = fake-pass-123456 first.\n"),
}

failed = 0
for label, (name, text) in CASES.items():
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        shutil.copytree(GRAPH.parent / "docs", tmp / "docs")
        shutil.copytree(GRAPH / "extractions", tmp / "extractions")
        (tmp / "docs" / name).write_text(text)
        env = dict(os.environ, GRAPH_DOCS=str(tmp / "docs"), GRAPH_CACHE=str(tmp / "extractions"),
                   GRAPH_DB=str(tmp / "g.db"))
        out = subprocess.run([sys.executable, str(GRAPH / "extract.py"), "--rebuild"],
                             env=env, capture_output=True, text=True)
        refused = out.returncode != 0 and "Refusing to extract" in out.stderr + out.stdout
        print(f"{'refused' if refused else 'NOT REFUSED'}: {label}")
        failed += not refused
with tempfile.TemporaryDirectory() as t:
    tmp = Path(t)
    shutil.copytree(GRAPH.parent / "docs", tmp / "docs")
    shutil.copytree(GRAPH / "extractions", tmp / "extractions")
    env = dict(os.environ, GRAPH_DOCS=str(tmp / "docs"), GRAPH_CACHE=str(tmp / "extractions"),
               GRAPH_DB=str(tmp / "g.db"))
    ok = subprocess.run([sys.executable, str(GRAPH / "extract.py"), "--rebuild"],
                        env=env, capture_output=True, text=True).returncode == 0
    print(f"{'extracted' if ok else 'WRONGLY REFUSED'}: the clean documents")
    failed += not ok
sys.exit(1 if failed else 0)
