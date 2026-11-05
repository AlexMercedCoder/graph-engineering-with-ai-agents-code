#!/usr/bin/env python3
"""Call the three governed-data tools without an agent or the MCP SDK.

    python3 server/cli.py navigate "net written premium"
    python3 server/cli.py generate net_written_premium region 2026-Q3
    python3 server/cli.py ask net_written_premium region 2026-Q3      # generate, then execute
    python3 server/cli.py execute --sql "SELECT ..."                  # hand-written SQL is refused

Identity and scopes come from CATALOG_IDENTITY and CATALOG_SCOPES, as in the server.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import execute_query, generate_governed_sql, navigate_catalog  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("navigate"); n.add_argument("concept", nargs="?", default="")
    for name in ("generate", "ask"):
        g = sub.add_parser(name)
        g.add_argument("metric"); g.add_argument("dimensions"); g.add_argument("time_range")
        g.add_argument("--filter", action="append", default=[], help="dimension=value")
    e = sub.add_parser("execute"); e.add_argument("--sql", required=True)
    a = ap.parse_args()
    if a.cmd == "navigate":
        print(navigate_catalog(a.concept))
        return 0
    if a.cmd == "execute":
        out = execute_query(a.sql)
        print(out)
        return 1 if out.startswith(("Rejected", "Forbidden", "Execution failed")) else 0
    dims = [d for d in a.dimensions.split(",") if d]
    filters = dict(f.split("=", 1) for f in a.filter) or None
    sql = generate_governed_sql(a.metric, dims, a.time_range, filters)
    print(sql)
    if sql.startswith(("Rejected", "Forbidden")):
        return 1
    if a.cmd == "ask":
        out = execute_query(sql)
        print("\n" + out)
        return 1 if out.startswith(("Rejected", "Forbidden", "Execution failed")) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
