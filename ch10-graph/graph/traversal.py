"""Traversal tools over the project graph. These are the Chapter 10 MCP tools.

Every helper the book's listings call is defined here: resolve_entity,
traverse_incoming, traverse_outgoing, nearest_entities, and a Path object with
describe(). Depth and result counts are capped in code rather than requested in
a docstring, because a docstring is advice and a min() is a guarantee.
"""
import difflib
import os
import sqlite3
from pathlib import Path as FsPath

DB = FsPath(os.environ.get("GRAPH_DB", FsPath(__file__).resolve().parent / "project-graph.db"))
MAX_DEPTH = 4
MAX_RESULTS = 25
ALL_TYPES = ("Service", "APIEndpoint", "Database", "Configuration")


class GraphMissing(Exception):
    pass


def _con():
    if not DB.exists():
        raise GraphMissing(f"The graph file {DB.name} doesn't exist yet. Run: python3 extract.py")
    return sqlite3.connect(DB)


class Node:
    def __init__(self, name, type_):
        self.name, self.type = name, type_


class Hop:
    """One edge walked. `via` names the service that exposes the endpoint, when
    the hop reached a service through the API it serves."""
    def __init__(self, source, target, rel, reached, via=None, sentence=None):
        self.source, self.target, self.rel = source, target, rel
        self.reached, self.via, self.sentence = reached, via, sentence

    def text(self):
        owner = f" (exposed by {self.via})" if self.via else ""
        return f"{self.source} -{self.rel}-> {self.target}{owner}"


class Path:
    """One traversal result: the entity reached and the hops that reached it."""
    def __init__(self, hops):
        self.hops = hops

    @property
    def target(self):
        return Node(self.hops[-1].reached, None)

    def describe(self):
        return " then ".join(h.text() for h in reversed(self.hops))


def _like(text):
    escaped = text.lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def resolve_entity(name, types=ALL_TYPES):
    """Find the entity a name refers to. Returns (node, note, candidates).

    An exact match (ignoring case) wins. Otherwise a substring match is used if
    it is unique, or if exactly one of the matches is a service, and the note
    says what the name resolved to. Anything else is ambiguous, and the
    candidates come back for the caller to report.
    """
    con = _con()
    marks = ",".join("?" * len(types))
    exact = con.execute(f"SELECT name, type FROM nodes WHERE lower(name)=lower(?) "
                        f"AND type IN ({marks})", (name, *types)).fetchone()
    if exact:
        con.close()
        return Node(*exact), None, []
    rows = con.execute(
        f"SELECT name, type FROM nodes WHERE lower(name) LIKE ? ESCAPE '\\' "
        f"AND type IN ({marks}) ORDER BY type != 'Service', length(name), name",
        (_like(name), *types)).fetchall()
    con.close()
    services = [r for r in rows if r[1] == "Service"]
    if len(rows) == 1 or len(services) == 1:
        pick = rows[0] if len(rows) == 1 else services[0]
        others = [r[0] for r in rows if r[0] != pick[0]]
        also = f" (also matched: {', '.join(others)})" if others else ""
        return Node(*pick), f"Resolved {name!r} to {pick[0]}{also}.", []
    return None, None, [r[0] for r in rows]


def nearest_entities(name, types=ALL_TYPES, limit=5):
    """The known names closest to `name`, for a helpful miss."""
    con = _con()
    marks = ",".join("?" * len(types))
    names = [r[0] for r in con.execute(f"SELECT name FROM nodes WHERE type IN ({marks})", types)]
    con.close()
    lower = {n.lower(): n for n in names}
    close = difflib.get_close_matches(name.lower(), list(lower), n=limit, cutoff=0.3)
    return [lower[c] for c in close] or sorted(names)[:limit]


def _miss(name, candidates, types, what):
    if candidates:
        return f"{name!r} matches more than one {what}: {', '.join(candidates)}. Ask again with one of them."
    return f"No {what} named {name!r}. Closest known: {', '.join(nearest_entities(name, types))}."


def _neighbors_backward(con, node, rel_types):
    """Who is affected when `node` changes: the sources of its incoming edges,
    and the callers of any API it exposes. EXPOSES is a free hop, so a service
    and the API it serves count as one place and only services come back."""
    marks = ",".join("?" * len(rel_types))
    exposed = [r[0] for r in con.execute(
        "SELECT target FROM edges WHERE source=? AND type='EXPOSES'", (node,))]
    for target in [node] + exposed:
        for src, rel, sentence in con.execute(
                f"SELECT source, type, sentence FROM edges WHERE target=? AND type IN ({marks})",
                (target, *rel_types)):
            yield Hop(src, target, rel, src, via=node if target != node else None, sentence=sentence)


def _neighbors_forward(con, node, rel_types):
    """What `node` needs: the targets of its outgoing edges, plus the service
    that serves any API it calls."""
    marks = ",".join("?" * len(rel_types))
    for tgt, rel, sentence in con.execute(
            f"SELECT target, type, sentence FROM edges WHERE source=? AND type IN ({marks})",
            (node, *rel_types)):
        yield Hop(node, tgt, rel, tgt, sentence=sentence)
        if rel == "CALLS":
            for (owner,) in con.execute(
                    "SELECT source FROM edges WHERE target=? AND type='EXPOSES'", (tgt,)):
                yield Hop(node, tgt, rel, owner, via=owner, sentence=sentence)


def _walk(root, rel_types, depth, step):
    depth = min(max(depth, 1), MAX_DEPTH)
    con = _con()
    found, frontier, seen = [], [(root.name, [])], {root.name}
    for _ in range(depth):
        nxt = []
        for node, hops in frontier:
            for hop in step(con, node, rel_types):
                if hop.reached in seen:
                    continue
                seen.add(hop.reached)
                path = hops + [hop]
                found.append(Path(path))
                nxt.append((hop.reached, path))
        frontier = nxt
    con.close()
    return found


def traverse_incoming(root, rel_types, depth):
    """Walk backward from root, up to depth hops. Returns Path objects."""
    return _walk(root, rel_types, depth, _neighbors_backward)


def traverse_outgoing(root, rel_types, depth):
    """Walk forward from root, up to depth hops. Returns Path objects."""
    return _walk(root, rel_types, depth, _neighbors_forward)


def _capped(lines):
    if len(lines) <= MAX_RESULTS:
        return lines
    return lines[:MAX_RESULTS] + [f"... and {len(lines) - MAX_RESULTS} more; ask with a smaller max_depth."]


# --- the three tools -------------------------------------------------------

def find_dependents(service_or_endpoint: str, max_depth: int = 2) -> str:
    """Return the services affected by a change to a named service or API,
    following CALLS and DEPENDS_ON relationships backward. A service and the
    API it exposes count as one place. Use when assessing the blast radius of
    a change. Depth defaults to 2 and is capped at 4; at most 25 results.
    Returns each affected service and the path that connects it."""
    depth = min(max(max_depth, 1), MAX_DEPTH)
    types = ("Service", "APIEndpoint")
    try:
        root, note, candidates = resolve_entity(service_or_endpoint, types)
        if root is None:
            return _miss(service_or_endpoint, candidates, types, "service or API")
        paths = traverse_incoming(root, ["CALLS", "DEPENDS_ON"], depth)
    except GraphMissing as e:
        return str(e)
    head = [note] if note else []
    if not paths:
        return "\n".join(head + [f"Nothing depends on {root.name} within {depth} hops."])
    lines = [f"{p.target.name} via {p.describe()}" for p in paths]
    return "\n".join(head + [f"{len(paths)} affected within {depth} hops:"] + _capped(lines))


def find_dependencies(service: str, max_depth: int = 2) -> str:
    """Return what a named service needs in order to run, following CALLS,
    DEPENDS_ON, and STORES relationships forward, and from each API it calls
    to the service that serves it. Use when assessing what must exist for a
    service to run. Depth defaults to 2 and is capped at 4; at most 25
    results. Returns each entity and the path that connects it."""
    depth = min(max(max_depth, 1), MAX_DEPTH)
    try:
        root, note, candidates = resolve_entity(service, ("Service",))
        if root is None:
            return _miss(service, candidates, ("Service",), "service")
        paths = traverse_outgoing(root, ["CALLS", "DEPENDS_ON", "STORES"], depth)
    except GraphMissing as e:
        return str(e)
    head = [note] if note else []
    if not paths:
        return "\n".join(head + [f"{root.name} depends on nothing within {depth} hops."])
    return "\n".join(head + _capped([f"{p.target.name} via {p.describe()}" for p in paths]))


def trace_configuration(key_or_service: str) -> str:
    """Given a configuration key, return every service it configures; given a
    service, return the configuration keys that configure it. Follows
    CONFIGURES relationships. Use before changing a configuration value, or to
    find a service's keys. Returns each pair with the sentence that states it."""
    types = ("Configuration", "Service")
    try:
        root, note, candidates = resolve_entity(key_or_service, types)
        if root is None:
            return _miss(key_or_service, candidates, types, "configuration key or service")
        con = _con()
        if root.type == "Configuration":
            rows = con.execute("SELECT target, sentence FROM edges WHERE source=? AND type='CONFIGURES'",
                               (root.name,)).fetchall()
        else:
            rows = con.execute("SELECT source, sentence FROM edges WHERE target=? AND type='CONFIGURES'",
                               (root.name,)).fetchall()
        con.close()
    except GraphMissing as e:
        return str(e)
    head = [note] if note else []
    if not rows:
        return "\n".join(head + [f"No CONFIGURES relationship recorded for {root.name}."])
    return "\n".join(head + _capped([f"{name}: {sentence}" for name, sentence in rows]))
