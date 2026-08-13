#!/usr/bin/env python3
"""Command line access to the traversal tools, so Chapter 10 runs without MCP.

    python3 query.py dependents NotificationsAPI 3
    python3 query.py dependencies OrderService
    python3 query.py config PAYMENT_API_KEY
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from traversal import find_dependencies, find_dependents, trace_configuration

OPS = {"dependents": find_dependents, "dependencies": find_dependencies, "config": trace_configuration}

if len(sys.argv) < 3 or sys.argv[1] not in OPS:
    raise SystemExit("usage: query.py {dependents|dependencies|config} NAME [DEPTH]")
op, name = sys.argv[1], sys.argv[2]
args = [name] + ([int(sys.argv[3])] if len(sys.argv) > 3 and op != "config" else [])
print(OPS[op](*args))
