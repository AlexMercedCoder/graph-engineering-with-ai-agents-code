#!/usr/bin/env python3
"""The Chapter 11 semantic layer: navigation, resolution, compilation, and the
four lineage checks, with rejections that name the nearest valid alternative.

Every helper the chapter's listings call is defined here: Catalog.search,
Catalog.resolve, Catalog.validate, compile_to_sql, and format_rejection.

    python3 validate.py --list
    python3 validate.py --metric net_written_premium --dimensions region --range 2026-Q3
    python3 validate.py --metric net_written_premium --dimensions claim_severity
    python3 validate.py --sql "SELECT region FROM analytics.fct_premiums"
    python3 validate.py --sql-file query.sql

Set CATALOG_IDENTITY (analyst, emea-analyst, finance) to see the catalog as that
identity sees it. Requires PyYAML; everything else is standard library.
"""
import argparse
import difflib
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("This script needs PyYAML:  pip install pyyaml")

HERE = Path(__file__).resolve().parent
IDENTITIES = {"analyst", "emea-analyst", "finance"}
SQL_WORDS = {"where", "on", "join", "left", "right", "inner", "outer", "cross", "group",
             "order", "limit", "using", "natural", "full", "union", "having", "as", "select"}


def current_identity():
    return os.environ.get("CATALOG_IDENTITY", "analyst")


class Catalog:
    """The catalog as one identity sees it. Unknown identities see nothing."""

    def __init__(self, path=HERE / "catalog.yaml", identity=None):
        self.doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        self.identity = identity or current_identity()
        self.revision = str(self.doc["revision"])
        known = self.identity in IDENTITIES
        visible = lambda obj: known and (not obj.get("access") or self.identity in obj["access"])
        self.datasets = {d["name"]: d for d in self.doc["datasets"] if visible(d)}
        self.metrics = {m["name"]: m for m in self.doc["metrics"] if visible(m)}
        self.dims = {d["name"]: d for d in self.doc["dimensions"] if d["dataset"] in self.datasets}
        self.rels = [r for r in self.doc["relationships"]
                     if r["from"] in self.datasets and r["to"] in self.datasets]
        self.not_modelled = self.doc.get("not_modelled", [])

    # --- navigation -------------------------------------------------------
    def search(self, concept="", entity=""):
        """Metrics whose name, label, description, or synonyms match the concept."""
        term = (concept or entity or "").lower().strip()
        syn = self.doc.get("ai_context", {}).get("synonyms", {})
        hits = []
        for name, m in self.metrics.items():
            phrases = [name.replace("_", " "), m["label"].lower(),
                       *[s.lower() for s in syn.get(name, [])]]
            if (not term or any(p in term for p in phrases)
                    or term in " ".join(phrases + [m["description"].lower()])):
                hits.append(m)
        return hits

    def columns(self, table):
        ds = self.datasets.get(table)
        return {f["name"] for f in ds["fields"]} if ds else set()

    # --- resolution: a structured request becomes a plan or a rejection ----
    def resolve(self, metric, dimensions, time_range, filters=None):
        errors = []
        if metric not in self.metrics:
            near = difflib.get_close_matches(metric, list(self.metrics), n=2, cutoff=0.4)
            errors.append(("metric", metric, near or sorted(self.metrics)))
            return Plan(None, [], None, {}, errors, self)
        m = self.metrics[metric]
        for d in list(dimensions) + list((filters or {}).keys()):
            if d not in m["dimensions"]:
                near = difflib.get_close_matches(d, m["dimensions"], n=2, cutoff=0.4)
                errors.append(("dimension", d, near or m["dimensions"], f"valid for {metric}"))
        span = parse_time_range(time_range)
        if span is None:
            errors.append(("time range", time_range,
                           ["2026-Q3", "2026", "2026-03", "2026-01..2026-06"],
                           f"{metric} has {m['grain']} grain, so give whole months"))
        return Plan(m, list(dimensions), span, dict(filters or {}), errors, self)

    # --- the four checks over SQL ----------------------------------------
    def validate(self, sql):
        """Table resolution, column resolution, join validity, metric lineage and grain."""
        problems = []
        body = re.sub(r"--[^\n]*", "", re.sub(r"'[^']*'", "''", sql))
        body = re.sub(r'["`\[\]]', "", body)   # "quoted", `quoted`, and [quoted] identifiers
        # 1. table resolution, over FROM lists (including comma joins) and JOINs;
        #    names a WITH clause defines are skipped
        refs = re.findall(r"\bJOIN\s+([\w.]+)(?:\s+(?:AS\s+)?(\w+))?", body, re.I)
        for clause in re.findall(r"\bFROM\s+(.+?)(?=\b(?:WHERE|GROUP|ORDER|LIMIT|HAVING|UNION|"
                                 r"JOIN|LEFT|RIGHT|INNER|FULL|CROSS|NATURAL)\b|\)|;|$)", body, re.I | re.S):
            for item in clause.split(","):
                m = re.match(r"\s*([\w.]+)(?:\s+(?:AS\s+)?(\w+))?", item, re.I)
                if m and not item.strip().startswith("("):
                    refs.append((m[1], m[2] or ""))
        ctes = {n.lower() for n in re.findall(r"(?:\bWITH\s+(?:RECURSIVE\s+)?|,\s*)(\w+)\s+AS\s*\(",
                                              body, re.I)}
        aliases = {}
        for table, alias in refs:
            bare = table.split(".")[-1]
            if bare.lower() in ctes:  # a common table expression, checked where it's defined
                continue
            aliases[bare] = bare
            if alias and alias.lower() not in SQL_WORDS:
                aliases[alias] = bare
            if bare not in self.datasets:
                near = difflib.get_close_matches(bare, list(self.datasets), n=1, cutoff=0.5)
                problems.append(f"Table `{table}` does not exist in the catalog."
                                + (f"\n   Nearest match: `analytics.{near[0]}`." if near else ""))
        # 2. column resolution, for every qualified reference
        for ref, col in sorted(set(re.findall(r"\b(\w+)\.(\w+)\b", body))):
            table = aliases.get(ref)
            if table in self.datasets and col not in self.columns(table):
                owner = next((d for d in self.dims.values() if d.get("column") == col), None)
                hint = ""
                if owner:
                    via = next((r for r in self.rels if r["name"] == owner.get("via")), None)
                    hint = (f"\n   It is a dimension on `{owner['dataset']}`"
                            + (f", joined on `{via['on']}`." if via else "."))
                problems.append(f"Column `{col}` is not on `{table}`.{hint}")
        # 3. join validity
        for a, ca, b, cb in re.findall(r"\b(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)", body):
            ta, tb = aliases.get(a), aliases.get(b)
            if ta in self.datasets and tb in self.datasets:
                if not any({r["from"], r["to"]} == {ta, tb} and ca == cb == r["on"] for r in self.rels):
                    declared = [f"{r['to']} ({r['on']})" for r in self.rels if r["from"] == ta]
                    problems.append(f"Join `{ta}.{ca} = {tb}.{cb}` is not a declared relationship."
                                    f"\n   Declared joins from {ta}: {', '.join(declared) or 'none'}.")
        # 4. metric lineage and grain, for any output column named after a metric
        norm = re.sub(r"\s+", " ", re.sub(r"--[^\n]*", "", sql)).lower()
        for expr, name in labeled_columns(body):
            m = self.metrics.get(name)
            if not m:
                continue
            allowed = {c.split(".")[1] for c in m["lineage"]}
            used = set(re.findall(r"\b(\w+)\b", expr)) & self.columns(m["bindings"]["table"])
            for c in sorted(used - allowed):
                problems.append(f"`{name}` is computed from `{c}`, which is not in its lineage."
                                f"\n   Declared lineage: {', '.join(m['lineage'])}.")
            for f in m["bindings"]["filters"]:
                col, rest = f.split(" ", 1)
                if not re.search(rf"\b{col}\s*{re.escape(rest.lower())}", norm):
                    problems.append(f"`{name}` requires the filter `{f}`, and this query does not apply it.")
            group = re.search(r"GROUP BY (.+?)(?:ORDER BY|LIMIT|$)", body, re.I | re.S)
            if group and re.search(rf"(?:^|[\s,.]){m['time']}\b(?!\s*\))", group.group(1)):
                problems.append(f"`{name}` has {m['grain']} grain, and this query groups by "
                                f"`{m['time']}`, a day.\n   Group by the month instead: "
                                f"strftime('%Y-%m', {m['time']}).")
        return Result(problems)


def labeled_columns(body):
    """(expression, label) for every `expr AS label` in each SELECT list.

    Splits on top-level commas only, so ROUND(SUM(x), 2) AS label stays whole.
    """
    out = []
    for start in re.finditer(r"\bSELECT\b", body, re.I):
        depth, item, i = 0, "", start.end()
        while i < len(body):
            ch = body[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                if depth == 0:
                    break
                depth -= 1
            if depth == 0 and (ch == "," or re.match(r"\s+FROM\b", body[i:], re.I) or ch == ";"):
                out.append(item)
                item = ""
                if ch != ",":
                    break
            else:
                item += ch
            i += 1
        else:
            out.append(item)
    labeled = []
    for item in out:
        m = re.match(r"\s*(.+?)\s+AS\s+(\w+)\s*$", item, re.I | re.S)
        if m:
            labeled.append((m[1], m[2]))
    return labeled


class Result:
    def __init__(self, problems):
        self.problems = problems

    @property
    def ok(self):
        return not self.problems


class Plan:
    def __init__(self, metric, dimensions, span, filters, errors, catalog):
        self.metric, self.dimensions, self.span, self.filters = metric, dimensions, span, filters
        self.errors, self.catalog = errors, catalog


def parse_time_range(text):
    """Whole months only: 2026, 2026-Q3, 2026-03, or 2026-01..2026-06."""
    t = (text or "").strip()
    if m := re.fullmatch(r"(\d{4})", t):
        return f"{m[1]}-01-01", f"{int(m[1]) + 1}-01-01"
    if m := re.fullmatch(r"(\d{4})-Q([1-4])", t, re.I):
        y, q = int(m[1]), int(m[2])
        return _month(y, 3 * q - 2), _month(y, 3 * q + 1)
    if m := re.fullmatch(r"(\d{4})-(\d{2})", t):
        return _month(int(m[1]), int(m[2])), _month(int(m[1]), int(m[2]) + 1)
    if m := re.fullmatch(r"(\d{4})-(\d{2})\.\.(\d{4})-(\d{2})", t):
        return _month(int(m[1]), int(m[2])), _month(int(m[3]), int(m[4]) + 1)
    return None


def _month(y, mo):
    y, mo = y + (mo - 1) // 12, (mo - 1) % 12 + 1
    return f"{y}-{mo:02d}-01"


def format_rejection(errors):
    lines = [f"Rejected: {len(errors)} problem{'s' if len(errors) != 1 else ''}.", ""]
    for i, (kind, value, near, *why) in enumerate(errors, 1):
        if kind == "metric":
            lines.append(f"{i}. Unknown metric `{value}`.")
        elif kind == "dimension":
            lines.append(f"{i}. `{value}` is not a dimension {why[0]}.")
        else:
            lines.append(f"{i}. `{value}` is not a valid {kind}: {why[0]}.")
        lines.append(f"   Valid {kind}s: {', '.join(near)}.")
    return "\n".join(lines)


def compile_to_sql(plan):
    """Deterministic SQL from a resolved plan. The agent never writes any of this."""
    m, cat = plan.metric, plan.catalog
    base = m["bindings"]["table"]
    alias = {base: "f"}
    selects, joins, group, where = [], [], [], []

    def ref(dim):
        d = cat.dims[dim]
        if d["dataset"] not in alias:
            rel = next(r for r in cat.rels if r["name"] == d["via"])
            alias[d["dataset"]] = d["dataset"].split("_", 1)[1][0]
            joins.append(f"JOIN analytics.{d['dataset']} AS {alias[d['dataset']]} "
                         f"ON f.{rel['on']} = {alias[d['dataset']]}.{rel['on']}")
        if "expression" in d:
            return re.sub(r"\b(\w+_dt)\b", r"f.\1", d["expression"])
        return f"{alias[d['dataset']]}.{d['column']}"

    for d in plan.dimensions:
        selects.append(f"{ref(d)} AS {d}")
        group.append(ref(d))
    measure = m["expression"]
    if "SUM(" in measure:
        measure = f"ROUND({measure}, 2)"
    selects.append(f"{measure} AS {m['name']}")
    where += [f"f.{f}" for f in m["bindings"]["filters"]]
    where.append(f"f.{m['time']} >= '{plan.span[0]}' AND f.{m['time']} < '{plan.span[1]}'")
    for dim, value in plan.filters.items():
        where.append(f"{ref(dim)} = '{str(value).replace(chr(39), chr(39) * 2)}'")
    return (f"SELECT {(','+chr(10)+'       ').join(selects)}\n"
            f"FROM analytics.{base} AS f\n"
            + "".join(f"{j}\n" for j in joins)
            + f"WHERE {' AND '.join(where)}"
            + (f"\nGROUP BY {', '.join(group)}\nORDER BY {', '.join(group)}" if group else ""))


def check_revision(path=HERE / "catalog.yaml", lock=HERE / "catalog.lock", record=False):
    """Fail when catalog.yaml changed but its revision string didn't.

    catalog.lock maps each recorded revision to a hash of the catalog without its
    revision line. Record a new revision after bumping it: --record-revision.
    """
    import hashlib
    text = Path(path).read_text(encoding="utf-8")
    revision = str(yaml.safe_load(text)["revision"])
    body = "\n".join(l for l in text.splitlines() if not l.startswith("revision:"))
    digest = hashlib.sha256(body.encode()).hexdigest()[:16]
    recorded = dict(l.split() for l in Path(lock).read_text().splitlines() if l.strip()) \
        if Path(lock).exists() else {}
    if record:
        if recorded.get(revision, digest) != digest:
            print(f"revision {revision} is already recorded for a different catalog. "
                  "Bump the revision string, then record it.")
            return 1
        recorded[revision] = digest
        Path(lock).write_text("".join(f"{r} {h}\n" for r, h in sorted(recorded.items())))
        print(f"recorded revision {revision}")
        return 0
    if recorded.get(revision) == digest:
        print(f"catalog matches revision {revision}")
        return 0
    if revision in recorded:
        print(f"catalog.yaml changed since revision {revision} was recorded. "
              "Bump the revision, then run validate.py --record-revision.")
    else:
        print(f"revision {revision} is not recorded. Run validate.py --record-revision.")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--metric")
    ap.add_argument("--dimensions", default="")
    ap.add_argument("--range", dest="rng", default="2026-Q3")
    ap.add_argument("--sql")
    ap.add_argument("--sql-file")
    ap.add_argument("--check-revision", action="store_true")
    ap.add_argument("--record-revision", action="store_true")
    a = ap.parse_args()
    if a.check_revision or a.record_revision:
        return check_revision(record=a.record_revision)
    cat = Catalog()

    if a.list:
        for m in cat.search():
            print(f"{m['name']}  (grain {m['grain']}, owner {m['owner']})")
            print(f"  {m['description']}")
            print(f"  dimensions: {', '.join(m['dimensions'])}\n")
        print("Not modelled, and therefore refused rather than guessed:")
        print(f"  {', '.join(cat.not_modelled)}")
        return 0

    if a.sql or a.sql_file:
        sql = a.sql or Path(a.sql_file).read_text(encoding="utf-8")
        res = cat.validate(sql)
        if res.ok:
            print(f"Valid against catalog revision {cat.revision}.")
            return 0
        print(f"Rejected: {len(res.problems)} problem{'s' if len(res.problems) != 1 else ''}.\n")
        print("\n\n".join(f"{i}. {p}" for i, p in enumerate(res.problems, 1)))
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
