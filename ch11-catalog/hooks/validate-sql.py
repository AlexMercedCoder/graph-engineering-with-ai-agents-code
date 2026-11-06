#!/usr/bin/env python3
"""PreToolUse hook: check SQL in a shell command against the catalog before it runs.

Register it for the Bash tool (see hooks/settings.example.json). It reads the hook's
JSON on stdin, pulls SQL out of quoted arguments and heredocs in any command that
mentions sqlite3, and checks each SELECT or WITH statement with Catalog.validate.
A rejection exits 2, which blocks the command and shows the agent the problems.

It's an advisory guard with known blind spots: it finds commands by the substring
"sqlite3", so it misses SQL sent through another client (Python's sqlite3 module, a
script) or read from a file (sqlite3 db < query.sql, .read); it can't see statements
built from shell variables; and the lineage check sees only columns named after a
metric. It fails closed: an internal error blocks the command. Enforcement stays
with the data platform.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from validate import Catalog  # noqa: E402

QUOTED = re.compile(r'"((?:[^"\\]|\\.)*)"' + r"|'([^']*)'", re.S)
HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?\n(.*?)\n\1\b", re.S)
STATEMENT = re.compile(r"^\s*(select|with)\b", re.I)


def statements(command):
    chunks = [body for _, body in HEREDOC.findall(command)]
    chunks += [a or b for a, b in QUOTED.findall(command)]
    for chunk in chunks:
        lines = [l for l in chunk.splitlines()
                 if not l.lstrip().startswith((".", "--"))]
        for stmt in "\n".join(lines).split(";"):
            if STATEMENT.match(stmt) and "$" not in stmt:
                yield stmt.strip()


def main():
    event = json.load(sys.stdin)
    if event.get("tool_name") != "Bash":
        return 0
    command = event.get("tool_input", {}).get("command", "")
    if "sqlite3" not in command:
        return 0
    catalog = Catalog()
    problems = []
    for stmt in statements(command):
        result = catalog.validate(stmt)
        if not result.ok:
            problems.append((stmt, result.problems))
    if not problems:
        return 0
    print("Blocked by the catalog's SQL check. Fix these and run it again:", file=sys.stderr)
    for stmt, found in problems:
        print(f"\n{' '.join(stmt.split())[:200]}", file=sys.stderr)
        for p in found:
            print(f"  - {p}", file=sys.stderr)
    return 2


try:
    sys.exit(main())
except SystemExit:
    raise
except Exception as exc:  # fail closed: a guard that crashes must not let the command through
    print(f"Blocked: the catalog's SQL check failed ({type(exc).__name__}: {exc}), "
          "so the command did not run.", file=sys.stderr)
    sys.exit(2)
