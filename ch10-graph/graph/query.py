#!/usr/bin/env python3
"""Command line access to the traversal tools, so Chapter 10 runs without MCP.

    python3 query.py dependents NotificationsAPI 3
    python3 query.py dependencies OrderService
    python3 query.py config PAYMENT_API_KEY
    python3 query.py edge RenewalsWorker BillingService
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from traversal import find_dependencies, find_dependents, trace_configuration



def edge(source, target):
    """Show the sentence and document behind every edge between two entities."""
    import sqlite3
    from traversal import DB
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT type, sentence, source_doc FROM edges WHERE source=? AND target=?",
                       (source, target)).fetchall()
    con.close()
    return "\n".join(f"{source} -{t}-> {target}\n  {doc}: {sentence}" for t, sentence, doc in rows) \
        or f"No edge from {source} to {target}."


OPS = {"dependents": find_dependents, "dependencies": find_dependencies,
       "config": trace_configuration, "edge": edge}

if len(sys.argv) < 3 or sys.argv[1] not in OPS:
    raise SystemExit("usage: query.py {dependents|dependencies|config|edge} NAME [DEPTH|TARGET]")
op, name = sys.argv[1], sys.argv[2]
if op == "edge":
    args = [name, sys.argv[3]]
else:
    args = [name] + ([int(sys.argv[3])] if len(sys.argv) > 3 and op != "config" else [])
print(OPS[op](*args))
