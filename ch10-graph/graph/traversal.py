"""Traversal tools over the project graph. These are the Chapter 10 MCP tools.

Every helper the book's listings call is defined here: resolve_entity,
traverse_incoming, sample_entities, and a Path object with describe().
Depth is capped in code rather than requested in a docstring, because a
docstring is advice and a min() is a guarantee.
"""
import sqlite3
from pathlib import Path as FsPath

DB = FsPath(__file__).resolve().parent / "project-graph.db"
MAX_DEPTH = 4


def _con():
    if not DB.exists():
        raise SystemExit(f"{DB.name} not found. Run: python3 extract.py")
    return sqlite3.connect(DB)


class Hop:
    def __init__(self, source, target, rel, sentence):
        self.source, self.target, self.rel, self.sentence = source, target, rel, sentence


class Path:
    """One traversal result: the entity reached and the hops that reached it."""
    def __init__(self, hops):
        self.hops = hops

    @property
    def target(self):
        return type("Node", (), {"name": self.hops[-1].source})()

    @property
    def length(self):
        return len(self.hops)

    def describe(self):
        parts = []
        for h in reversed(self.hops):
            parts.append(f"{h.source} -{h.rel}-> {h.target}")
        return " then ".join(parts)


def resolve_entity(name):
    con = _con()
    row = con.execute("SELECT name, type FROM nodes WHERE lower(name)=lower(?)", (name,)).fetchone()
    if row is None:
        row = con.execute("SELECT name, type FROM nodes WHERE lower(name) LIKE ?",
                          (f"%{name.lower()}%",)).fetchone()
    con.close()
    return type("Node", (), {"name": row[0], "type": row[1]})() if row else None


def sample_entities(limit=6):
    con = _con()
    rows = [r[0] for r in con.execute("SELECT name FROM nodes ORDER BY name LIMIT ?", (limit,))]
    con.close()
    return rows


def traverse_incoming(root, rel_types, depth):
    """Walk edges backward from root, up to depth hops. Returns Path objects."""
    depth = min(max(depth, 1), MAX_DEPTH)
    con = _con()
    placeholders = ",".join("?" * len(rel_types))
    found, frontier, seen = [], [(root.name, [])], {root.name}
    for _ in range(depth):
        nxt = []
        for node, hops in frontier:
            rows = con.execute(
                f"SELECT source, type, sentence FROM edges WHERE target=? AND type IN ({placeholders})",
                (node, *rel_types)).fetchall()
            for src, rel, sentence in rows:
                if src in seen:
                    continue
                seen.add(src)
                new_hops = hops + [Hop(src, node, rel, sentence)]
                found.append(Path(new_hops))
                nxt.append((src, new_hops))
        frontier = nxt
        if not frontier:
            break
    con.close()
    return found


def traverse_outgoing(root, rel_types, depth):
    depth = min(max(depth, 1), MAX_DEPTH)
    con = _con()
    placeholders = ",".join("?" * len(rel_types))
    out, frontier, seen = [], [root.name], {root.name}
    for _ in range(depth):
        nxt = []
        for node in frontier:
            for tgt, rel in con.execute(
                f"SELECT target, type FROM edges WHERE source=? AND type IN ({placeholders})",
                    (node, *rel_types)):
                if tgt in seen:
                    continue
                seen.add(tgt)
                out.append((tgt, rel))
                nxt.append(tgt)
        frontier = nxt
    con.close()
    return out


# --- the three tools -------------------------------------------------------

def find_dependents(service_or_endpoint: str, max_depth: int = 2) -> str:
    """Return the services affected by a change to a named service or API
    endpoint, following CALLS and DEPENDS_ON relationships backward. Use when
    assessing the blast radius of a change. Depth defaults to 2 and is capped
    at 4. Returns services and the path that connects each one."""
    depth = min(max(max_depth, 1), MAX_DEPTH)
    root = resolve_entity(service_or_endpoint)
    if root is None:
        return (f"No service or endpoint named {service_or_endpoint!r}. "
                f"Known: {', '.join(sample_entities())}.")
    paths = traverse_incoming(root, ["CALLS", "DEPENDS_ON"], depth)
    if not paths:
        return f"Nothing depends on {root.name} within {depth} hops."
    lines = [f"{p.target.name} via {p.describe()}" for p in paths]
    return f"{len(paths)} affected within {depth} hops:\n" + "\n".join(lines)


def find_dependencies(service: str, max_depth: int = 2) -> str:
    """Return what a named service depends on, following CALLS, DEPENDS_ON, and
    STORES relationships forward. Use when assessing what must exist for a
    service to run, or what a deployment requires. Returns entities with the
    relationship type that connects each one."""
    root = resolve_entity(service)
    if root is None:
        return f"No service named {service!r}. Known: {', '.join(sample_entities())}."
    out = traverse_outgoing(root, ["CALLS", "DEPENDS_ON", "STORES"], max_depth)
    if not out:
        return f"{root.name} depends on nothing within {max_depth} hops."
    return "\n".join(f"{name} ({rel})" for name, rel in out)


def trace_configuration(config_key: str) -> str:
    """Return every service that a named configuration key affects, following
    CONFIGURES relationships. Use before changing a configuration value, to find
    out what it touches. Returns services and how each one uses the key."""
    root = resolve_entity(config_key)
    if root is None:
        return f"No configuration key named {config_key!r}."
    con = _con()
    rows = con.execute("SELECT source, sentence FROM edges WHERE target=? AND type='CONFIGURES'",
                       (root.name,)).fetchall()
    con.close()
    if not rows:
        return f"{root.name} configures nothing recorded in the graph."
    return "\n".join(f"{svc}: {sent}" for svc, sent in rows)
