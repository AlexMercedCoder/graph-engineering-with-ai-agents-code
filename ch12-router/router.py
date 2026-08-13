#!/usr/bin/env python3
"""The Chapter 12 retrieval router: rules first, model fallback second.

Every symbol the chapter's listing calls is real here: RULES, Route, matches(),
and classify_with_model() (which is a stub you point at your own provider).

    python3 router.py "what does error code E4021 mean"
    python3 router.py --eval queries.jsonl
"""
import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("router")

TOOL, VECTOR, GRAPH, SEMANTIC = "tool", "vector", "graph", "semantic"


@dataclass
class Rule:
    pattern: str
    route: str
    why: str

    def matches(self, query: str) -> bool:
        return re.search(self.pattern, query, re.I) is not None


RULES = [
    Rule(r"\bE\d{4}\b",                                  TOOL,     "names an error code"),
    Rule(r"\b(config|configuration) schema\b",           TOOL,     "names a schema lookup"),
    Rule(r"\bwhat breaks if\b|\bblast radius\b",         GRAPH,    "asks for impact"),
    Rule(r"\bwhat depends on\b|\bwho calls\b",           GRAPH,    "asks for relationships"),
    Rule(r"\bwhich services\b",                          GRAPH,    "asks across services"),
    Rule(r"\bif .* (goes down|changes|is lost)\b",       GRAPH,    "conditional impact"),
    Rule(r"\b(net written premium|gross written premium|revenue|total)\b", SEMANTIC, "names a metric"),
    Rule(r"\bby (region|product line|month|quarter)\b",  SEMANTIC, "asks for a slice"),
    Rule(r"\blast (quarter|month|year)\b",               SEMANTIC, "names a time range"),
    Rule(r"\bwhy\b|\bhow does\b|\bwhat is\b|\bexplain\b", VECTOR,  "definitional"),
]


def classify_with_model(query: str) -> str:
    """Fallback for anything the rules do not match.

    Left as a stub on purpose: wiring it to a provider is three lines and a key,
    and the chapter's argument is that you should not need it often. Until you
    wire it, the safe default is the more capable path, which is what the chapter
    recommends for ambiguous cases.
    """
    log.info("router: falling through to model for %r", query)
    return GRAPH


def route(query: str):
    for rule in RULES:
        if rule.matches(query):
            return rule.route, rule.why
    return classify_with_model(query), "model fallback"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?")
    ap.add_argument("--eval", help="a jsonl file of {q, expected}")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO if a.v else logging.WARNING, format="%(message)s")

    if a.eval:
        rows = [json.loads(l) for l in Path(a.eval).read_text().splitlines() if l.strip()]
        ok, fell = 0, 0
        wrong = []
        for r in rows:
            got, why = route(r["q"])
            if why == "model fallback":
                fell += 1
            if got == r["expected"]:
                ok += 1
            else:
                wrong.append((r["q"], r["expected"], got))
        print(f"routing accuracy: {ok}/{len(rows)} = {ok/len(rows):.0%}")
        print(f"rule fallthrough: {fell}/{len(rows)} = {fell/len(rows):.0%}  (each one costs a model call)")
        for q, want, got in wrong:
            print(f"  MIS-ROUTED  {q!r}\n              expected {want}, got {got}")
        if wrong:
            print("\nEach mis-route is one rule away. That backlog is the exercise.")
        return 0

    if not a.query:
        ap.error("give a query or --eval")
    got, why = route(a.query)
    print(f"{got}  ({why})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
