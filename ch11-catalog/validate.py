#!/usr/bin/env python3
"""Lineage validation for Chapter 11: the four checks, and a useful rejection.

Every helper the chapter's listings call is real here: catalog.search,
catalog.resolve, compile_to_sql, and format_rejection.

    python3 validate.py --list
    python3 validate.py --metric net_written_premium --dimensions region --range 2026-Q1
    python3 validate.py --metric net_written_premium --dimensions claim_severity --range 2026-Q1
    python3 validate.py --sql "SELECT region FROM analytics.fct_premiums"

Requires PyYAML (pip install pyyaml). Everything else is standard library.
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("This script needs PyYAML:  pip install pyyaml")

HERE = Path(__file__).resolve().parent
REVISION = "2026-08-12"


class Catalog:
    def __init__(self, path=HERE / "catalog.yaml"):
        self.doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.revision = REVISION
        self.datasets = {d["name"]: d for d in self.doc["datasets"]}
        self.metrics = {m["name"]: m for m in self.doc["metrics"]}
        self.rels = self.doc["relationships"]

    # --- navigation -------------------------------------------------------
    def groups(self):
        return sorted({m["owner"] for m in self.metrics.values()})

    def search(self, concept="", entity=""):
        term = (concept or entity or "").lower()
        syn = self.doc.get("ai_context", {}).get("synonyms", {})
        hits = []
        for name, m in self.metrics.items():
            haystack = " ".join([name, m["label"], m["description"],
                                 *syn.get(name, [])]).lower()
            if not term or term in haystack:
                hits.append(m)
        return hits

    def dimensions_for(self, metric):
        return self.metrics[metric]["dimensions"]

    def columns(self, table):
        return {f["name"] for f in self.datasets[table]["fields"]} if table in self.datasets else set()

    def dimension_source(self, dim):
        """Which dataset carries a dimension, and how it is reached."""
        for name, ds in self.datasets.items():
            if dim in self.columns(name):
                if name == "fct_policy_premium":
                    return name, None
                rel = next((r for r in self.rels if r["to"] == name), None)
                return name, rel
        return None, None

    # --- resolution -------------------------------------------------------
    def resolve(self, metric, dimensions, time_range, filters=None):
        errors = []
        if metric not in self.metrics:
            near = difflib.get_close_matches(metric, self.metrics, n=2)
            errors.append(("metric", metric, near or sorted(self.metrics)))
            return Plan(None, [], time_range, errors, self)
        valid = self.dimensions_for(metric)
        for d in dimensions:
            if d not in valid:
                near = difflib.get_close_matches(d, valid, n=2)
                errors.append(("dimension", d, near or valid))
        return Plan(self.metrics[metric], dimensions, time_range, errors, self)

    # --- the four checks over raw SQL ------------------------------------
    def validate(self, sql):
        problems = []
        tables = set(re.findall(r"(?:FROM|JOIN)\s+([\w.]+)", sql, re.I))
        known = set(self.datasets)
        for t in tables:
            bare = t.split(".")[-1]
            if bare not in known:
                near = difflib.get_close_matches(bare, known, n=1)
                problems.append(f"Table `{t}` does not exist."
                                + (f"\n   Nearest match: `analytics.{near[0]}`." if near else ""))
        for qualified in re.findall(r"\b(\w+)\.(\w+)\b", sql):
            tbl, col = qualified
            if tbl in known and col not in self.columns(tbl):
                owner, rel = self.dimension_source(col)
                extra = ""
                if owner:
                    extra = (f"\n   It is a dimension reachable through `{owner}`"
                             + (f", joined on `{rel['on']}`." if rel else "."))
                problems.append(f"Column `{col}` is not on `{tbl}`.{extra}")
        for a, ca, b, cb in re.findall(r"(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)", sql):
            if a in known and b in known:
                ok = any({r["from"], r["to"]} == {a, b} and r["on"] in (ca, cb) for r in self.rels)
                if not ok:
                    declared = [f"{r['to']} ({r['on']})" for r in self.rels if r["from"] == a]
                    problems.append(f"Join `{a}.{ca} = {b}.{cb}` is not a declared relationship."
                                    f"\n   Declared joins from {a}: {', '.join(declared) or 'none'}.")
        return Result(problems)


class Result:
    def __init__(self, problems):
        self.problems = problems
    @property
    def ok(self):
        return not self.problems


class Plan:
    def __init__(self, metric, dimensions, time_range, errors, catalog):
        self.metric, self.dimensions, self.time_range = metric, dimensions, time_range
        self.errors, self.catalog = errors, catalog


def format_rejection(errors):
    lines = [f"Rejected: {len(errors)} problem{'s' if len(errors) != 1 else ''}.", ""]
    for i, (kind, value, near) in enumerate(errors, 1):
        lines.append(f"{i}. Unknown {kind} `{value}`.")
        lines.append(f"   Valid {kind}s: {', '.join(near)}.")
    return "\n".join(lines)


def compile_to_sql(plan):
    m, cat = plan.metric, plan.catalog
    base = m["bindings"]["table"]
    selects, joins = [], []
    for d in plan.dimensions:
        owner, rel = cat.dimension_source(d)
        if owner and owner != base:
            joins.append(f"JOIN analytics.{owner} ON analytics.{base}.{rel['on']} = analytics.{owner}.{rel['on']}")
            selects.append(f"analytics.{owner}.{d}")
        else:
            selects.append(f"analytics.{base}.{d}")
    where = list(m["bindings"].get("filters", []))
    where.append(f"eff_dt IN ({plan.time_range})")
    sql = (f"SELECT {', '.join(selects + [m['expression'] + ' AS ' + m['name']])}\n"
           f"FROM analytics.{base}\n"
           + ("".join(f"{j}\n" for j in dict.fromkeys(joins)))
           + f"WHERE {' AND '.join(where)}\n"
           + (f"GROUP BY {', '.join(selects)}" if selects else ""))
    return sql.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--metric")
    ap.add_argument("--dimensions", default="")
    ap.add_argument("--range", dest="rng", default="2026-Q1")
    ap.add_argument("--sql")
    a = ap.parse_args()
    cat = Catalog()

    if a.list:
        for m in cat.search():
            print(f"{m['name']}  (grain {m['grain']}, owner {m['owner']})")
            print(f"  {m['description']}")
            print(f"  dimensions: {', '.join(m['dimensions'])}\n")
        print("Not modelled, and therefore refused rather than guessed:")
        print("  reinsurance recoveries, loss ratio, claim severity")
        return 0

    if a.sql:
        res = cat.validate(a.sql)
        if res.ok:
            print(f"Valid against catalog revision {cat.revision}.")
            return 0
        print(f"Rejected: {len(res.problems)} problem{'s' if len(res.problems) != 1 else ''}.\n")
        for i, p in enumerate(res.problems, 1):
            print(f"{i}. {p}")
        return 1

    if not a.metric:
        ap.error("give --list, --metric, or --sql")
    dims = [d for d in a.dimensions.split(",") if d]
    plan = cat.resolve(a.metric, dims, a.rng)
    if plan.errors:
        print(format_rejection(plan.errors))
        return 1
    print(compile_to_sql(plan))
    print(f"\n-- Validated against catalog revision {cat.revision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
