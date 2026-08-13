#!/usr/bin/env python3
"""Append one row of the Chapter 3 context-consumption curve to a CSV.

Harnesses report token usage differently, so this takes the number you read off
your own counter rather than guessing at a log format. It exists to keep the
bookkeeping honest: one row per task, both runs, so the two curves are
comparable.

    python3 parse-usage.py --task 3 --tokens 24000 --aas 3 --run continuous
    python3 parse-usage.py --task 3 --tokens 9000  --aas 3 --run fresh

Standard library only. Writes curve.csv in the working directory.
"""
import argparse
import csv
import sys
from pathlib import Path

FIELDS = ["run", "task", "tpr", "cts", "aas", "aas_max", "cost_usd", "notes"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logfile", nargs="?", help="optional test log, recorded for provenance")
    ap.add_argument("--task", type=int, required=True)
    ap.add_argument("--tokens", type=int, required=True, help="tokens per request for this task")
    ap.add_argument("--aas", type=int, required=True, help="constraints held, out of --aas-max")
    ap.add_argument("--aas-max", type=int, default=3)
    ap.add_argument("--run", choices=["fresh", "continuous"], default="continuous")
    ap.add_argument("--cost", type=float, default=0.0)
    ap.add_argument("--csv", default="curve.csv")
    ap.add_argument("--notes", default="")
    a = ap.parse_args()

    path = Path(a.csv)
    rows = []
    if path.exists():
        rows = list(csv.DictReader(path.open()))
    cts = sum(int(r["tpr"]) for r in rows if r["run"] == a.run) + a.tokens

    notes = a.notes
    if a.logfile and Path(a.logfile).exists():
        text = Path(a.logfile).read_text(errors="replace")
        fails = text.count("not ok") + text.count("✖")
        notes = (notes + f" test-failures={fails}").strip()

    rows.append({"run": a.run, "task": a.task, "tpr": a.tokens, "cts": cts,
                 "aas": a.aas, "aas_max": a.aas_max, "cost_usd": f"{a.cost:.4f}",
                 "notes": notes})

    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"{path}: {len(rows)} row(s)")
    print(f"  {a.run} run, task {a.task}: TPR {a.tokens}, CTS {cts}, AAS {a.aas}/{a.aas_max}")
    if a.aas < a.aas_max:
        print("  AAS below maximum: check whether TPR rose at the same time. That")
        print("  crossover is the saturation threshold this chapter is looking for.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
