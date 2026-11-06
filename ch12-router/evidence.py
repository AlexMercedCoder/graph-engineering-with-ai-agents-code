#!/usr/bin/env python3
"""Evidence envelopes for tool results, and a checker for evidence documents.

    python3 evidence.py check answer.md       validate every evidence document in a file

The knowledge server wraps each retrieval in an envelope that carries
everything an evidence document needs except the claim. The retrieval worker
writes the claim and copies the rest. check() validates documents against
evidence_schema.json with the standard library only.
"""
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = json.loads((Path(__file__).resolve().parent / "evidence_schema.json").read_text())
PROPS = SCHEMA["properties"]


def mtime(*paths):
    """The newest modification time among paths, as ISO 8601 in UTC."""
    t = max(Path(p).stat().st_mtime for p in paths)
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def envelope(result, *, path, identifier, status="found", confidence="high",
             coverage="complete", freshness="", revision=None, caveats=()):
    source = {"path": path, "identifier": identifier}
    if revision:
        source["revision"] = revision
    return json.dumps({
        "evidence": {"schema_version": 1, "status": status, "source": source,
                     "confidence": confidence, "coverage": coverage,
                     "cost_tokens": math.ceil(len(result) / 4), "freshness": freshness,
                     "caveats": list(caveats)},
        "result": result}, indent=1)


def check(doc):
    """Return a list of problems with one evidence document; empty means valid."""
    if not isinstance(doc, dict):
        return ["not a JSON object"]
    problems = [f"missing {k}" for k in SCHEMA["required"] if k not in doc]
    problems += [f"unknown field {k}" for k in doc if k not in PROPS]
    for k, spec in PROPS.items():
        if k not in doc:
            continue
        v = doc[k]
        if "enum" in spec and v not in spec["enum"]:
            problems.append(f"{k} is {v!r}; expected one of {spec['enum']}")
        if "const" in spec and v != spec["const"]:
            problems.append(f"{k} is {v!r}; expected {spec['const']}")
        if spec.get("type") == "string" and (not isinstance(v, str) or len(v) < spec.get("minLength", 0)):
            problems.append(f"{k} must be a non-empty string")
        if spec.get("type") == "integer" and (not isinstance(v, int) or v < 0):
            problems.append(f"{k} must be a whole number of tokens")
        if spec.get("type") == "array" and not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
            problems.append(f"{k} must be a list of strings")
    src = doc.get("source")
    if isinstance(src, dict):
        sp = PROPS["source"]["properties"]
        problems += [f"source missing {k}" for k in PROPS["source"]["required"] if not src.get(k)]
        problems += [f"source has unknown field {k}" for k in src if k not in sp]
        if src.get("path") not in sp["path"]["enum"]:
            problems.append(f"source.path is {src.get('path')!r}")
    elif "source" in doc:
        problems.append("source must be an object")
    return problems


def extract(text):
    """Every JSON object in text that has a schema_version, from fenced blocks or bare."""
    docs, dec = [], json.JSONDecoder()
    for m in re.finditer(r"[\[{]", text):
        try:
            obj, _ = dec.raw_decode(text[m.start():])
        except ValueError:
            continue
        items = obj if isinstance(obj, list) else [obj]
        for o in items:
            if isinstance(o, dict) and "schema_version" in o and o not in docs:
                docs.append(o)
    return docs


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "check":
        sys.exit(__doc__)
    docs = extract(Path(sys.argv[2]).read_text())
    bad = 0
    for i, d in enumerate(docs, 1):
        problems = check(d)
        bad += bool(problems)
        status = "ok" if not problems else "; ".join(problems)
        print(f"{i}. [{d.get('source', {}).get('path', '?')}/{d.get('status', '?')}] {status}")
    print(f"{len(docs)} evidence documents, {bad} invalid")
    return 1 if bad or not docs else 0


if __name__ == "__main__":
    sys.exit(main())
