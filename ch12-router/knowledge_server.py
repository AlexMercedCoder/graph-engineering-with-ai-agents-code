#!/usr/bin/env python3
"""One MCP server for every knowledge path in Part 3, with evidence envelopes.

    python3 knowledge_server.py        runs over stdio; register it as project-knowledge

It reuses the earlier chapters' code rather than copying it:
  tool      lookup_error_code, get_config_schema       (ch09-mcp)
  vector    search_docs                                 (ch10-graph/eval/chunks.py)
  graph     find_dependents, find_dependencies, trace_configuration (ch10-graph)
  semantic  navigate_catalog, generate_governed_sql, execute_query  (ch11-catalog)
plus route_question, which runs router.py and retrieves nothing, and
check_evidence, which validates evidence documents before they leave the worker.

Every retrieval tool returns JSON: an "evidence" envelope (status, source,
confidence, coverage, cost_tokens, freshness, caveats) and the "result" text.
The governed-data tools read CATALOG_IDENTITY and CATALOG_SCOPES as in
Chapter 11.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "ch09-mcp" / "server"),
                str(ROOT / "ch10-graph" / "graph"), str(ROOT / "ch10-graph" / "eval")]
from mcp.server import MCPServer  # noqa: E402

import router  # noqa: E402
import traversal  # noqa: E402
from chunks import search  # noqa: E402
from evidence import check, envelope, extract, mtime  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kb = _load("ch09_tools", ROOT / "ch09-mcp" / "server" / "tools.py")
gov = _load("ch11_tools", ROOT / "ch11-catalog" / "server" / "tools.py")

CH09 = ROOT / "ch09-mcp" / "knowledge"
DOCS = sorted((ROOT / "ch10-graph" / "docs").glob("*.md"))
GRAPH_DB = traversal.DB
CH11 = ROOT / "ch11-catalog"
VECTOR_HIGH, VECTOR_MEDIUM = 0.75, 0.65      # top-hit similarity, set on this corpus

mcp = MCPServer("project-knowledge")


@mcp.tool()
def route_question(question: str) -> str:
    """Classify a question by the retrieval path that should answer it: tool
    (an exact identifier such as an error code or a config schema), vector
    (what something is or how it works), graph (how services relate, what a
    change affects), or semantic (a business number from governed data).
    Retrieves nothing. Call it first, then use only the chosen path's tools."""
    r = router.route(question)
    return json.dumps({"paths": list(r.paths), "why": r.why, "matched_by": r.matched_by})


@mcp.tool()
def check_evidence(documents: str) -> str:
    """Validate evidence documents (a JSON array, as text) against the evidence
    schema. Call it before you reply, and fix every problem it names."""
    docs = extract(documents)
    if not docs:
        return "No evidence documents found. Pass a JSON array of documents with schema_version 1."
    problems = [f"document {i}: {'; '.join(p)}" for i, d in enumerate(docs, 1) if (p := check(d))]
    return "\n".join(problems) or f"All {len(docs)} documents are valid."


# --- tool path (Chapter 9) ----------------------------------------------------

def _tool(result, identifier, missing):
    status = "not_found" if result.startswith(missing) else "found"
    return envelope(result, path="tool", identifier=identifier, status=status,
                    freshness=mtime(*CH09.glob("*.json")))


@mcp.tool()
def lookup_error_code(code: str) -> str:
    """Return the meaning, cause, and handling for a project error code
    (E followed by four digits), wrapped in an evidence envelope."""
    return _tool(kb.lookup_error_code(code), f"lookup_error_code({code!r})", "No error code")


@mcp.tool()
def get_config_schema(service: str) -> str:
    """Return the configuration schema (keys, types, defaults, required) for one
    service: payments, orders, notifications, users, auth, reporting, search,
    or gateway. Wrapped in an evidence envelope."""
    return _tool(kb.get_config_schema(service), f"get_config_schema({service!r})", "Unknown service")


# --- vector path (Chapter 10's baseline) -------------------------------------

@mcp.tool()
def search_docs(query: str, k: int = 3) -> str:
    """Search the architecture documents for the k most similar sections
    (default 3, at most 8). Use for what a service stores, how it behaves,
    where something lives, or why. Wrapped in an evidence envelope whose
    coverage is always unknown, because similarity can't tell whether the
    answer was complete."""
    hits = search(query, min(max(k, 1), 8))
    result = "\n\n".join(f"[{h['id']}] (score {h['score']:.2f})\n{h['text']}" for h in hits)
    top = hits[0]["score"] if hits else 0.0
    confidence = "high" if top >= VECTOR_HIGH else "medium" if top >= VECTOR_MEDIUM else "low"
    return envelope(result, path="vector", identifier=f"search_docs({query!r}, k={k})",
                    confidence=confidence, coverage="unknown", freshness=mtime(*DOCS),
                    caveats=[] if confidence != "low" else
                    [f"best match scored {top:.2f}; the documents may not cover this"])


# --- graph path (Chapter 10) ---------------------------------------------------

def _graph(result, identifier):
    if not GRAPH_DB.exists() or "graph" in result.lower() and "extract.py" in result:
        return envelope(result, path="graph", identifier=identifier, status="unavailable",
                        confidence="low", coverage="unknown")
    caveats, status, confidence, coverage = [], "found", "high", "complete"
    if result.startswith("No ") and "named" in result or "matches more than one" in result:
        status, confidence = "not_found", "low"
    if result.startswith("Resolved "):
        confidence = "medium"
        caveats.append(result.splitlines()[0])
    if re.search(r"\.\.\. and \d+ more", result):
        coverage = "partial"
        caveats.append("results capped at 25")
    if DOCS and max(p.stat().st_mtime for p in DOCS) > GRAPH_DB.stat().st_mtime:
        caveats.append("a document changed after the graph was built; run extract.py")
    return envelope(result, path="graph", identifier=identifier, status=status,
                    confidence=confidence, coverage=coverage, freshness=mtime(GRAPH_DB),
                    caveats=caveats)


@mcp.tool()
def find_dependents(service_or_endpoint: str, max_depth: int = 2) -> str:
    """Return the services affected by a change to a named service or API,
    with the path to each (CALLS and DEPENDS_ON, backward). Depth defaults to
    2, capped at 4. Wrapped in an evidence envelope."""
    return _graph(traversal.find_dependents(service_or_endpoint, max_depth),
                  f"find_dependents({service_or_endpoint!r}, max_depth={max_depth})")


@mcp.tool()
def find_dependencies(service: str, max_depth: int = 2) -> str:
    """Return what a named service needs in order to run (CALLS, DEPENDS_ON,
    STORES, forward), with the path to each. Depth defaults to 2, capped at
    4. Wrapped in an evidence envelope."""
    return _graph(traversal.find_dependencies(service, max_depth),
                  f"find_dependencies({service!r}, max_depth={max_depth})")


@mcp.tool()
def trace_configuration(key_or_service: str) -> str:
    """Given a configuration key, return the services it configures; given a
    service, return its configuration keys. Wrapped in an evidence envelope."""
    return _graph(traversal.trace_configuration(key_or_service),
                  f"trace_configuration({key_or_service!r})")


# --- semantic path (Chapter 11) -----------------------------------------------

def _semantic(result, identifier, *, status="found", coverage="complete"):
    if result.startswith(("Forbidden", "No metric matches", "Rejected", "Unknown")):
        status = "refused"
    elif result.startswith("Execution failed"):
        status = "unavailable"
    revision = re.search(r"catalog (?:revision )?(\S+?),? identity", result)
    return envelope(result, path="semantic", identifier=identifier, status=status,
                    coverage=coverage, freshness=mtime(CH11 / "catalog.yaml"),
                    revision=f"catalog {revision[1]}" if revision else None)


@mcp.tool()
def navigate_catalog(concept: str = "", entity: str = "") -> str:
    """Find the governed metrics that match a business concept, with each
    one's definition, grain, and valid dimensions. Use first for any question
    that asks for a number, a trend, or a breakdown. Returns metadata only.
    Wrapped in an evidence envelope; a concept the catalog doesn't model, or
    you may not see, comes back refused."""
    return _semantic(gov.navigate_catalog(concept, entity),
                     f"navigate_catalog(concept={concept!r}, entity={entity!r})")


@mcp.tool()
def generate_governed_sql(metric: str, dimensions: list[str], time_range: str,
                          filters: dict[str, str] | None = None) -> str:
    """Generate validated SQL for one catalog metric, sliced by dimensions,
    over whole months (2026-Q3, 2026, 2026-03, 2026-01..2026-06). Pass the
    result's "result" text unchanged to execute_query. Wrapped in an evidence
    envelope."""
    return _semantic(gov.generate_governed_sql(metric, dimensions, time_range, filters),
                     f"generate_governed_sql({metric!r}, {dimensions!r}, {time_range!r}, {filters!r})")


@mcp.tool()
def execute_query(sql: str, max_rows: int = 1000) -> str:
    """Run SQL exactly as generate_governed_sql returned it (the "result" text,
    including its last line) under the caller's access policies, and return
    the rows. Wrapped in an evidence envelope; truncated results are partial."""
    result = gov.execute_query(sql, max_rows)
    trailer = re.search(r"-- governed: catalog (\S+), identity", sql)
    out = _semantic(result, "execute_query(<signed SQL from generate_governed_sql>)",
                    coverage="partial" if "truncated at the row cap" in result else "complete")
    if trailer and '"revision"' not in out:
        doc = json.loads(out)
        doc["evidence"]["source"]["revision"] = f"catalog {trailer[1]}"
        out = json.dumps(doc, indent=1)
    return out


if __name__ == "__main__":
    mcp.run()
