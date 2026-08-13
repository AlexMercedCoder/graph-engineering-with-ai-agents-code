"""Knowledge lookups behind the Chapter 9 MCP server.

Every helper the book's listings call lives here, so the listings run rather
than illustrate. Standard library only.
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "knowledge"

ERROR_CODES = json.loads((DATA / "error_codes.json").read_text(encoding="utf-8"))
SCHEMAS = json.loads((DATA / "config_schemas.json").read_text(encoding="utf-8"))
KNOWN_SERVICES = sorted(SCHEMAS)


def _load_sections():
    text = (DATA / "architecture.md").read_text(encoding="utf-8")
    sections = []
    for chunk in re.split(r"^## ", text, flags=re.M):
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.split("\n")
        title = lines[0].strip()
        body_lines, classification = [], "internal"
        for line in lines[1:]:
            if line.startswith("classification:"):
                classification = line.split(":", 1)[1].strip()
            else:
                body_lines.append(line)
        sections.append({
            "title": title,
            "body": "\n".join(body_lines).strip(),
            "classification": classification,
        })
    return sections


SECTIONS = _load_sections()
TOPICS = [s["title"] for s in SECTIONS]


def suggest_nearby(code, limit=2):
    """Nearest known codes by numeric distance, so E4023 suggests E4022 and E4021."""
    code = (code or "").upper()
    digits = re.sub(r"\D", "", code)
    if not digits:
        return sorted(ERROR_CODES)[:limit]
    target = int(digits)
    ranked = sorted(ERROR_CODES, key=lambda c: abs(int(re.sub(r"\D", "", c)) - target))
    return ranked[:limit]


def render_schema(schema):
    rows = ["KEY                  TYPE      REQUIRED  DEFAULT"]
    for key, meta in schema.items():
        default = "(value not shown)" if meta["secret"] else str(meta["default"])
        rows.append(f"{key:<21}{meta['type']:<10}{str(meta['required']):<10}{default}")
    return "\n".join(rows)


def search_sections(topic):
    """Rank sections by term overlap with the topic. No embeddings required."""
    terms = [t for t in re.split(r"\W+", (topic or "").lower()) if len(t) > 2]
    scored = []
    for section in SECTIONS:
        haystack = (section["title"] + " " + section["body"]).lower()
        score = sum(haystack.count(t) for t in terms)
        if score:
            scored.append((score, section))
    scored.sort(key=lambda pair: -pair[0])
    return [section for _, section in scored]


def visible_classifications(identity):
    """Which classifications an identity may see. Fails closed on the unknown."""
    return {
        "reviewer": ["internal"],
        "engineer": ["internal"],
        "security": ["internal", "restricted"],
    }.get(identity, [])


def current_identity():
    """In a real deployment this comes from the validated token. See Chapter 9."""
    import os
    return os.environ.get("KB_IDENTITY", "engineer")
