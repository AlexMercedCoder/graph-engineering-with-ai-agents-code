#!/usr/bin/env python3
"""Build the project graph from docs/ into a SQLite file.

The book frames extraction as a model call. This implementation uses a
deterministic rule-based extractor instead, for one reason: a reader running it
twice gets the same graph, so the benchmark in eval/ is reproducible and costs
nothing. The four failure modes the chapter names are all still present and all
still guarded, which is the part worth practising:

  entity resolution        -> normalize() plus the ALIASES table
  relationship hallucination -> every edge stores the sentence that produced it
  silent staleness         -> every node stores its source document
  type drift               -> validate() rejects types outside the ontology

To run the model-based version instead, replace extract_document() with a call
to your provider using EXTRACTION_PROMPT. Everything downstream is unchanged.
"""
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ontology import ALIASES, ENTITY_TYPES, RELATIONSHIP_TYPES

HERE = Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"
DB = HERE / "project-graph.db"

VERB_MAP = [
    (r"\bcalls the (\w+)", "CALLS", "APIEndpoint"),
    (r"\bcalls (\w+API)", "CALLS", "APIEndpoint"),
    (r"\bdepends on (\w+)", "DEPENDS_ON", "Service"),
    (r"\bstores .*? in the (\w+) ", "STORES", "Database"),
    (r"\bconfigured by ([A-Z][A-Z0-9_]{3,})", "CONFIGURES", "Configuration"),
    # "configured by X and Y" states two relationships, not one.
    (r"\bconfigured by [A-Z][A-Z0-9_]{3,} and ([A-Z][A-Z0-9_]{3,})", "CONFIGURES", "Configuration"),
]


def canonical_case(name):
    return "".join(part[:1].upper() + part[1:] for part in name.split())


def normalize(name):
    # Configuration keys are identifiers, not prose. Preserve them verbatim.
    if re.fullmatch(r"[A-Z][A-Z0-9_]{3,}", name):
        return name
    key = re.sub(r"[-_]+", " ", name).strip().lower()
    return ALIASES.get(key, canonical_case(key) if " " in key else name)


def span_supports(text, sentence):
    """Drop any edge whose quoted sentence is not present verbatim."""
    return sentence.strip() and sentence.strip() in text


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if s.strip()]


def extract_document(path):
    text = path.read_text(encoding="utf-8")
    subject = normalize(re.search(r"^#\s*(\w+)", text, re.M).group(1))
    entities = [{"name": subject, "type": "Service", "source": path.name}]
    edges = []
    for sent in sentences(text):
        for pattern, rel, target_type in VERB_MAP:
            for m in re.finditer(pattern, sent, re.I):
                target = normalize(m.group(1))
                entities.append({"name": target, "type": target_type, "source": path.name})
                edges.append({
                    "source": subject, "target": target, "type": rel,
                    "sentence": sent, "source_doc": path.name,
                })
    edges = [e for e in edges if span_supports(text.replace("\n", " "), e["sentence"])]
    return validate({"path": path.name, "entities": entities, "edges": edges})


def validate(result):
    bad_e = {e["type"] for e in result["entities"]} - ENTITY_TYPES
    bad_r = {e["type"] for e in result["edges"]} - RELATIONSHIP_TYPES
    if bad_e or bad_r:
        print(f"  {result['path']}: dropping unknown types {bad_e or ''} {bad_r or ''}", file=sys.stderr)
    result["entities"] = [e for e in result["entities"] if e["type"] in ENTITY_TYPES]
    result["edges"] = [e for e in result["edges"] if e["type"] in RELATIONSHIP_TYPES]
    return result


def build():
    if DB.exists():
        DB.unlink()  # rebuild rather than patch: patching accumulates staleness
    con = sqlite3.connect(DB)
    con.executescript("""
        CREATE TABLE nodes (name TEXT PRIMARY KEY, type TEXT, source_doc TEXT);
        CREATE TABLE edges (source TEXT, target TEXT, type TEXT, sentence TEXT,
                            source_doc TEXT, UNIQUE(source,target,type));
    """)
    n_docs = 0
    for path in sorted(DOCS.glob("*.md")):
        res = extract_document(path)
        n_docs += 1
        for e in res["entities"]:
            con.execute("INSERT OR IGNORE INTO nodes VALUES (?,?,?)",
                        (e["name"], e["type"], e["source"]))
        for e in res["edges"]:
            con.execute("INSERT OR IGNORE INTO edges VALUES (?,?,?,?,?)",
                        (e["source"], e["target"], e["type"], e["sentence"], e["source_doc"]))
    con.commit()
    nodes = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edges = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    con.close()
    print(f"built {DB.name} from {n_docs} documents: {nodes} nodes, {edges} edges")


if __name__ == "__main__":
    build()
