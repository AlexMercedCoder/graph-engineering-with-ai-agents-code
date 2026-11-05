#!/usr/bin/env python3
"""Extract entities and relationships from docs/ into the project graph.

    python3 extract.py            refresh the graph from the saved extractions
    python3 extract.py --model    also re-extract changed documents with a model
    python3 extract.py --rebuild  drop the graph and load every document again
    python3 extract.py --names    list the distinct node names, for alias review

Extraction is a model call, and model calls cost money and vary from run to
run, so every result is saved in extractions/<doc>.json with the hash of the
document it came from. A refresh re-extracts only documents whose hash changed,
then patches the graph one document at a time: delete everything that document
produced, insert what it produces now, drop nodes no document mentions. A
deleted document takes its nodes and edges with it.

The four failure modes and their guards:
  entity resolution          -> normalize() and the ALIASES table
  relationship hallucination -> span_supports(): the quoted sentence must exist
  silent staleness           -> per-document hashes, provenance on every row
  type drift                 -> validate() rejects types and signatures outside
                                the ontology, and logs what it dropped
"""
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ontology import ALIASES, ENTITY_TYPES, EXTRACTION_PROMPT, RELATIONSHIP_TYPES, SIGNATURES

HERE = Path(__file__).resolve().parent
DOCS = Path(os.environ.get("GRAPH_DOCS", HERE.parent / "docs"))
CACHE = Path(os.environ.get("GRAPH_CACHE", HERE / "extractions"))
DB = Path(os.environ.get("GRAPH_DB", HERE / "project-graph.db"))
MODEL = os.environ.get("EXTRACT_MODEL", "claude-sonnet-5-5")


def call_model(text):
    """The one provider-specific function. Swap in your own client here."""
    with tempfile.TemporaryDirectory() as empty:
        out = subprocess.run(
            ["claude", "-p", EXTRACTION_PROMPT + "\n---\n" + text, "--model", MODEL,
             "--tools", "", "--strict-mcp-config", "--setting-sources", "project",
             "--output-format", "json", "--no-session-persistence"],
            cwd=empty, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    reply = json.loads(out.stdout)
    body = reply["result"]
    raw = json.loads(body[body.index("{"):body.rindex("}") + 1])
    u = reply.get("usage", {})
    usage = {"input_tokens": u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
             + u.get("cache_creation_input_tokens", 0),
             "output_tokens": u.get("output_tokens", 0),
             "cost_usd": reply.get("total_cost_usd")}
    return raw, usage


def canonical_case(key):
    return "".join(part[:1].upper() + part[1:] for part in key.split())


def normalize(name):
    # Configuration keys are identifiers, not prose. Keep them verbatim.
    if re.fullmatch(r"[A-Z][A-Z0-9_]{3,}", name.strip()):
        return name.strip()
    key = re.sub(r"[-_]+", " ", name).strip().lower()
    key = re.sub(r"^the\s+", "", key)
    return ALIASES.get(key, canonical_case(key) if " " in key else name.strip())


def span_supports(text, edge):
    """Keep an edge only if its quoted sentence appears verbatim in the source."""
    quote = " ".join(edge.get("sentence", "").split())
    return bool(quote) and quote in " ".join(text.split())


def validate(result, log):
    types = {e["name"]: e["type"] for e in result["entities"]}
    kept_entities = []
    for e in result["entities"]:
        if e["type"] in ENTITY_TYPES:
            kept_entities.append(e)
        else:
            log.append(f"{result['doc']}: dropped entity type {e['type']} ({e['name']})")
    kept_edges = []
    for r in result["edges"]:
        sig = SIGNATURES.get(r["type"])
        got = (types.get(r["source"]), types.get(r["target"]))
        if sig is None:
            log.append(f"{result['doc']}: dropped relationship type {r['type']} "
                       f"({r['source']} -> {r['target']})")
        elif got != sig:
            log.append(f"{result['doc']}: dropped {r['source']} -{r['type']}-> {r['target']}, "
                       f"types {got[0]} -> {got[1]} break the signature {sig[0]} -> {sig[1]}")
        else:
            kept_edges.append(r)
    result["entities"], result["edges"] = kept_entities, kept_edges
    return result


def extract_document(path, raw, log):
    """Turn one raw model reply into validated, normalized, span-checked rows."""
    text = path.read_text(encoding="utf-8")
    entities = [{"name": normalize(e["name"]), "type": e["type"]} for e in raw.get("entities", [])]
    edges = []
    for r in raw.get("relationships", []):
        edge = {"source": normalize(r["source"]), "type": r["type"],
                "target": normalize(r["target"]), "sentence": r.get("sentence", "")}
        if span_supports(text, edge):
            edges.append(edge)
        else:
            log.append(f"{path.name}: dropped {edge['source']} -{edge['type']}-> "
                       f"{edge['target']}, quote not found in the document")
    return validate({"doc": path.name, "entities": entities, "edges": edges}, log)


def doc_hash(path):
    """Hash the document together with the prompt: a schema change re-extracts all."""
    return hashlib.sha256(EXTRACTION_PROMPT.encode() + path.read_bytes()).hexdigest()


def load_or_extract(path, use_model, spent):
    cached = CACHE / (path.stem + ".json")
    h = doc_hash(path)
    if cached.exists():
        saved = json.loads(cached.read_text())
        if saved["sha256"] == h:
            return saved
    if not use_model:
        raise SystemExit(f"{path.name} or the extraction prompt changed since the last "
                         f"extraction. Run: python3 extract.py --model")
    raw, usage = call_model(path.read_text(encoding="utf-8"))
    spent.append(usage)
    saved = {"doc": path.name, "sha256": h, "model": MODEL,
             "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "usage": usage, "raw": raw}
    CACHE.mkdir(exist_ok=True)
    cached.write_text(json.dumps(saved, indent=1) + "\n")
    return saved


SCHEMA = """
CREATE TABLE IF NOT EXISTS docs (name TEXT PRIMARY KEY, sha256 TEXT, extracted_at TEXT);
CREATE TABLE IF NOT EXISTS nodes (name TEXT PRIMARY KEY, type TEXT);
CREATE TABLE IF NOT EXISTS mentions (name TEXT, source_doc TEXT, UNIQUE(name, source_doc));
CREATE TABLE IF NOT EXISTS edges (source TEXT, target TEXT, type TEXT, sentence TEXT,
                                  source_doc TEXT, extracted_at TEXT,
                                  UNIQUE(source, target, type, source_doc));
"""


def forget(con, doc):
    for table, col in (("edges", "source_doc"), ("mentions", "source_doc"), ("docs", "name")):
        con.execute(f"DELETE FROM {table} WHERE {col}=?", (doc,))


def insert(con, doc, res, saved):
    for e in res["entities"]:
        con.execute("INSERT OR IGNORE INTO nodes VALUES (?,?)", (e["name"], e["type"]))
        con.execute("INSERT OR IGNORE INTO mentions VALUES (?,?)", (e["name"], doc))
    for r in res["edges"]:
        con.execute("INSERT OR IGNORE INTO edges VALUES (?,?,?,?,?,?)",
                    (r["source"], r["target"], r["type"], r["sentence"], doc,
                     saved["extracted_at"]))
    con.execute("INSERT INTO docs VALUES (?,?,?)", (doc, saved["sha256"], saved["extracted_at"]))


def refresh(use_model=False, rebuild=False):
    if rebuild and DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    stored = dict(con.execute("SELECT name, sha256 FROM docs"))
    current = {p.name: p for p in sorted(DOCS.glob("*.md"))}
    log, spent, changed = [], [], []
    for name in set(stored) - set(current):
        forget(con, name)
        changed.append(f"removed {name}")
    for name, path in current.items():
        if stored.get(name) == doc_hash(path):
            continue
        saved = load_or_extract(path, use_model, spent)
        res = extract_document(path, saved["raw"], log)
        forget(con, name)
        insert(con, name, res, saved)
        changed.append(f"{'added' if name not in stored else 'updated'} {name}")
    con.execute("DELETE FROM nodes WHERE name NOT IN (SELECT name FROM mentions)")
    con.commit()
    nodes = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edges = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    con.close()
    for line in log:
        print("  " + line, file=sys.stderr)
    cost = sum(u.get("cost_usd") or 0 for u in spent)
    calls = f"{len(spent)} model call{'' if len(spent) == 1 else 's'}"
    counts = {kind: sum(c.startswith(kind) for c in changed) for kind in ("added", "updated", "removed")}
    summary = ", ".join(f"{n} {kind}" for kind, n in counts.items() if n)
    unchanged = len(current) - counts["added"] - counts["updated"]
    print(f"{summary or 'nothing changed'}, {unchanged} unchanged ({calls}, ${cost:.4f}); "
          f"graph has {nodes} nodes, {edges} edges")
    for c in changed if len(changed) < len(current) else []:
        print("  " + c)

if __name__ == "__main__":
    if "--names" in sys.argv:
        con = sqlite3.connect(DB)
        for name, typ in con.execute("SELECT name, type FROM nodes ORDER BY lower(name)"):
            print(f"{typ:<14}{name}")
    else:
        refresh(use_model="--model" in sys.argv, rebuild="--rebuild" in sys.argv)
