#!/usr/bin/env python3
"""The Chapter 12 retrieval router: rules first, a small model second.

    python3 router.py "What does error code E4021 mean?"
    python3 router.py --model "Who gets hurt if we take the users service offline?"

route() never retrieves anything. It reads the question and names the path or
paths that should answer it: tool (an exact lookup by identifier), vector
(search over the architecture documents), graph (traversal of the project
graph), or semantic (the governed catalog). eval/route_eval.py measures it.

Set ROUTER_LOG to a file path to append every question the rules didn't
match, with email addresses and token-shaped strings redacted, to a file only
your user can read. Point it outside the repository, or at ch12-router/logs/,
which ch12-router/.gitignore ignores. With ROUTER_MODEL set, an unmatched
question goes to the model provider as typed; redaction covers only the log.
"""
import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

log = logging.getLogger("router")

TOOL, VECTOR, GRAPH, SEMANTIC = "tool", "vector", "graph", "semantic"
PATHS = (TOOL, VECTOR, GRAPH, SEMANTIC)
DEFAULT = VECTOR     # what an unmatched question gets when no model is configured


@dataclass(frozen=True)
class Rule:
    pattern: str
    paths: tuple
    why: str

    def matches(self, query: str) -> bool:
        return re.search(self.pattern, query, re.I) is not None


@dataclass(frozen=True)
class Route:
    paths: tuple
    why: str
    matched_by: str          # "rule", "model", or "default"
    cost_usd: float = 0.0


# First match wins, so the order matters: identifiers, then numbers, then
# relationships, then the broad question words that vector search answers.
RULES = [
    Rule(r"\bE\d{4}\b",                                       (TOOL,),     "names an error code"),
    Rule(r"\bconfig(uration)? schema\b",                       (TOOL,),     "asks for a service's config schema"),
    Rule(r"\b(written premium|loss ratio|commission|claims? paid|paid on .*claims"
         r"|policies (did )?we (write|wr[oi]te|sell|sold))\b",  (SEMANTIC,), "names a business metric"),
    Rule(r"\b(premium|policies|claims|commission|revenue)\b.*\bby (region|product line|severity|month|quarter|channel)\b",
                                                               (SEMANTIC,), "asks for a breakdown of a business figure"),
    Rule(r"\bwhy\b.*\b(after|since)\b.*\b(deploy|release|change)",
                                                               (GRAPH, VECTOR), "asks why a change had an effect"),
    Rule(r"\b(which|what) services\b",                         (GRAPH,),    "asks across services"),
    Rule(r"\bwhat breaks\b|\bblast radius\b|\baffected\b|\bstop working\b",
                                                               (GRAPH,),    "asks for impact"),
    Rule(r"\bwhat depends on\b|\bwho calls\b",                 (GRAPH,),    "asks who relies on something"),
    Rule(r"\bneeds? in order to run\b|\bwithin (two|three|\d) hops?\b",
                                                               (GRAPH,),    "asks for a chain"),
    Rule(r"\bif\b.*\b(goes down|is down|changes|is lost|fails)\b",
                                                               (GRAPH,),    "conditional impact"),
    Rule(r"\bwhy\b|\bhow (does|do|often|long)\b|\bwhat (is|are|does|happens)\b|\bwhere\b"
         r"|\bwhich (database|configuration key|key)\b|\bexplain\b",
                                                               (VECTOR,),   "asks what something is or how it works"),
]

MODEL_PROMPT = """\
Classify this question about a software platform and its business data by the
retrieval path that should answer it. Paths:
- tool: names an exact identifier to look up (an error code like E4021, or a
  service's configuration schema)
- vector: asks what something is, how it works, where it lives, or why, about
  one service (answered from architecture documents)
- graph: asks how services relate, what depends on what, or what is affected
  by a change or outage (answered by traversing a dependency graph)
- semantic: asks for a business number, total, count, or breakdown from
  company data (premiums, policies, claims, commissions)
Return only JSON: {{"paths": ["one path", "or two, only if the question needs both"]}}

Question: {q}"""


def classify_with_model(query: str):
    """Ask a small model. Set ROUTER_MODEL to enable it (for example
    claude-haiku-5-5); this calls it through `claude -p`, so replace the
    subprocess call to use another client. Returns (paths, cost_usd), or None
    when no model is configured or the reply can't be parsed."""
    model = os.environ.get("ROUTER_MODEL")
    if not model:
        return None
    with tempfile.TemporaryDirectory() as empty:     # no project settings or CLAUDE.md
        out = subprocess.run(
            ["claude", "-p", MODEL_PROMPT.format(q=query), "--model", model, "--tools", "",
             "--strict-mcp-config", "--setting-sources", "project,local",
             "--no-session-persistence", "--output-format", "json"],
            cwd=empty, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    try:
        res = json.loads(out.stdout)
        reply = re.search(r"\{.*\}", res["result"], re.S).group(0)
        paths = tuple(p for p in json.loads(reply)["paths"] if p in PATHS)
    except (ValueError, KeyError, AttributeError, TypeError):
        return None
    return (paths, res.get("total_cost_usd")) if paths else None


def match(text):
    for rule in RULES:
        if rule.matches(text):
            return rule
    return None


REDACT = [(re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "<email>"),
          (re.compile(r"\beyJ[\w-]+\.[\w-]+\.[\w-]*"), "<token>"),               # JWT
          (re.compile(r"\b(AKIA|ASIA)[A-Z0-9]{16}\b"), "<token>"),                  # AWS key ID
          (re.compile(r"(?i)\bbearer\s+\S+"), "Bearer <token>"),
          (re.compile(r"\b(sk|pk|ghp|gho|xox[bpa])[-_][A-Za-z0-9_-]{8,}"), "<token>"),
          (re.compile(r"(?<![\w/+])[A-Za-z0-9_/+=-]{24,}"), "<token>")]


def log_fallthrough(query, r):
    """Append an unmatched question to ROUTER_LOG, redacted, for rule writing."""
    path = os.environ.get("ROUTER_LOG")
    if not path:
        return
    for pattern, mask in REDACT:
        query = pattern.sub(mask, query)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as f:
        f.write(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "q": query,
                            "paths": list(r.paths), "by": r.matched_by}) + "\n")


def route(query: str) -> Route:
    # A question joined with ", and" or ";" can ask two things. Route each
    # clause, and fan out when the clauses the rules recognize need different paths.
    clauses = [c for c in re.split(r",\s*and\s+|;\s*", query) if c.strip()]
    hits = [r for r in map(match, clauses) if r]
    if hits:
        paths = tuple(dict.fromkeys(p for r in hits for p in r.paths))
        return Route(paths, "; ".join(dict.fromkeys(r.why for r in hits)), "rule")
    log.info("router: no rule matched; falling through")     # the question itself goes only to ROUTER_LOG
    answer = classify_with_model(query)
    if answer:
        r = Route(answer[0], "model classification", "model", answer[1] or 0.0)
    else:
        r = Route((DEFAULT,), "no rule matched; default path", "default")
    log_fallthrough(query, r)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--model", action="store_true", help="enable the model fallback (claude-haiku-5-5)")
    a = ap.parse_args()
    if a.model:
        os.environ.setdefault("ROUTER_MODEL", "claude-haiku-5-5")
    r = route(a.query)
    print(f"{' + '.join(r.paths)}  ({r.matched_by}: {r.why})")


if __name__ == "__main__":
    sys.exit(main())
