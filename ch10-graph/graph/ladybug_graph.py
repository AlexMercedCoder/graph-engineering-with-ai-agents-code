#!/usr/bin/env python3
"""Load the project graph into LadybugDB, an embedded graph database, and query it in Cypher.

    pip install ladybug
    python3 ladybug_graph.py

Reads the SQLite graph that extract.py builds, so both stores hold the same
nodes and edges, then runs the Cypher version of find_dependents for the
NotificationsAPI at two hops and prints the services it returns.
"""
import shutil
import sqlite3
from pathlib import Path

import ladybug

HERE = Path(__file__).resolve().parent
SQLITE = HERE / "project-graph.db"
LADYBUG = HERE / "project-graph-ladybug.db"
RELS = ["CALLS", "EXPOSES", "STORES", "DEPENDS_ON", "CONFIGURES"]

DEPENDENTS = """
MATCH (s:Entity)-[:CALLS|DEPENDS_ON]->(:Entity {name: $root})
RETURN s.name AS name, 1 AS hops
UNION
MATCH (s:Entity)-[:CALLS|DEPENDS_ON]->(:Entity)-[:CALLS|DEPENDS_ON]->(:Entity {name: $root})
RETURN s.name AS name, 2 AS hops
UNION
MATCH (s:Entity)-[:CALLS]->(:Entity)<-[:EXPOSES]-(:Entity)-[:CALLS|DEPENDS_ON]->(:Entity {name: $root})
RETURN s.name AS name, 2 AS hops
"""


def load():
    if LADYBUG.exists():
        shutil.rmtree(LADYBUG) if LADYBUG.is_dir() else LADYBUG.unlink()
    db = ladybug.Database(str(LADYBUG))
    con = ladybug.Connection(db)
    con.execute("CREATE NODE TABLE Entity(name STRING, type STRING, PRIMARY KEY(name))")
    for rel in RELS:
        con.execute(f"CREATE REL TABLE {rel}(FROM Entity TO Entity, sentence STRING, source_doc STRING)")
    src = sqlite3.connect(SQLITE)
    for name, typ in src.execute("SELECT name, type FROM nodes"):
        con.execute("CREATE (:Entity {name: $n, type: $t})", {"n": name, "t": typ})
    for s, t, rel, sentence, doc in src.execute(
            "SELECT source, target, type, sentence, source_doc FROM edges"):
        con.execute(f"MATCH (a:Entity {{name: $s}}), (b:Entity {{name: $t}}) "
                    f"CREATE (a)-[:{rel} {{sentence: $sen, source_doc: $doc}}]->(b)",
                    {"s": s, "t": t, "sen": sentence, "doc": doc})
    src.close()
    return con


if __name__ == "__main__":
    con = load()
    res = con.execute(DEPENDENTS, {"root": "NotificationsAPI"})
    best = {}
    while res.has_next():
        name, hops = res.get_next()
        best[name] = min(hops, best.get(name, hops))
    for name, hops in sorted(best.items(), key=lambda x: (x[1], x[0])):
        print(f"{hops}  {name}")
