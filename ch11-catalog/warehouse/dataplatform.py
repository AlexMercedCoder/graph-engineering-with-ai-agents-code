"""A stand-in for the data platform under the semantic layer.

The executor hands this module SQL and an identity. It returns rows the identity
may see, within a row cap and a timeout. Enforcement happens here, not in the
MCP server: an identity's connection holds only the tables, columns, and rows its
policy grants, so a query cannot read past the policy whatever SQL it contains.

A real platform does this with grants, row access policies, and column masks.
SQLite has none of those, so this module builds each identity an in-memory copy
of what it may read, attached under the schema name `analytics`.
"""
import sqlite3
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
WAREHOUSE = HERE / "warehouse.db"
POLICIES = HERE / "policies.yaml"


class PolicyError(Exception):
    pass


def _policy(identity):
    doc = yaml.safe_load(POLICIES.read_text(encoding="utf-8"))
    pol = doc["identities"].get(identity)
    if pol is None:
        raise PolicyError(f"Unknown identity {identity!r}: no tables are visible.")
    return pol or {}


def connect(identity):
    if not WAREHOUSE.exists():
        raise PolicyError("warehouse/warehouse.db is missing. Run: python3 warehouse/seed.py")
    pol = _policy(identity)
    con = sqlite3.connect("file::memory:", uri=True)
    con.execute("ATTACH DATABASE ? AS src", (f"file:{WAREHOUSE}?mode=ro",))
    con.execute("ATTACH DATABASE ':memory:' AS analytics")
    deny_t = set(pol.get("deny_tables", []))
    deny_c = set(pol.get("deny_columns", []))
    filters = pol.get("row_filters", {})
    for (table,) in con.execute("SELECT name FROM src.sqlite_master WHERE type='table'").fetchall():
        if table in deny_t:
            continue
        cols = [r[1] for r in con.execute(f"PRAGMA src.table_info({table})")
                if f"{table}.{r[1]}" not in deny_c]
        where = filters.get(table)
        if where:
            where = where.replace(" FROM ", " FROM src.")
        con.execute(f"CREATE TABLE analytics.{table} AS SELECT {', '.join(cols)} FROM src.{table}"
                    + (f" WHERE {where}" if where else ""))
    con.execute("DETACH DATABASE src")

    def read_only(action, *_):
        return sqlite3.SQLITE_OK if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ,
                                               sqlite3.SQLITE_FUNCTION) else sqlite3.SQLITE_DENY
    con.set_authorizer(read_only)
    return con


def run(sql, identity, max_rows=1000, timeout_s=30):
    """Run one SELECT for an identity. Returns (columns, rows, truncated)."""
    con = connect(identity)
    deadline = time.monotonic() + timeout_s
    con.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10_000)
    try:
        cur = con.execute(sql)
        rows = cur.fetchmany(max_rows + 1)
        cols = [c[0] for c in cur.description or []]
    except sqlite3.OperationalError as e:
        if "interrupted" in str(e):
            raise PolicyError(f"Query exceeded the {timeout_s}s limit and was stopped.") from e
        raise
    finally:
        con.close()
    return cols, rows[:max_rows], len(rows) > max_rows
