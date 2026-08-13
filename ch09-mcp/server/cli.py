#!/usr/bin/env python3
"""project-kb: the same three operations as a command line program.

This is the "If your harness lacks this" substitute from Chapter 9. Grant the
agent shell access to this one command and the boundary holds for the same
reason it holds over MCP: no operation takes a path or a query.

    python3 cli.py error-code E4021
    python3 cli.py config-schema payments
    python3 cli.py architecture "soft deletes"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import find_architecture_docs, get_config_schema, lookup_error_code

USAGE = "usage: cli.py {error-code CODE | config-schema SERVICE | architecture TOPIC [N]}"


def main(argv):
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2
    op, args = argv[0], argv[1:]
    if op == "error-code":
        print(lookup_error_code(args[0]))
    elif op == "config-schema":
        print(get_config_schema(args[0]))
    elif op == "architecture":
        n = int(args[1]) if len(args) > 1 else 3
        print(find_architecture_docs(args[0], n))
    else:
        print(USAGE, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
