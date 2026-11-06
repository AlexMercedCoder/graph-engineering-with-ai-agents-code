#!/usr/bin/env python3
"""Score run_subcycle.py results: the six answers, the evidence, and the context.

    python3 grade_brief.py results/

Answers are checked by pattern against the companion data (Chapter 9's error
codes, Chapter 10's graph, Chapter 11's warehouse). Questions 5 and 6 pass only
when the answer states no number: the catalog doesn't model loss ratio, and the
analyst identity can't see commission.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from evidence import check, extract  # noqa: E402

NWP = {"APAC": 278969.21, "EMEA": 343269.84, "LATAM": 308624.73, "North America": 312420.42}
COMMISSION = "98224"
REFUSAL = r"not model|doesn.t model|isn.t model|no governed|not (in|part of) the (governed )?catalog|refus|not available|not permitted|restricted|no access|can.t see|cannot see|not authori[sz]ed|doesn.t (have|expose)|does not (have|expose)"


def number_in(text, value):
    flat = text.replace(",", "")
    return f"{value:.2f}" in flat or re.search(rf"\b{round(value)}\b", flat) is not None


CHECKS = {
    1: lambda t: re.search(r"expir|laps", t, re.I) and re.search(
        r"not (be )?retr|non-retryable|retryable\W+(false|no)\b|isn.t retryable|"
        r"do not retry|don.t retry|not safe to retry", t, re.I),
    2: lambda t: re.search(r"order\s*-?service", t, re.I) and re.search(r"renewals?\s*-?worker", t, re.I),
    3: lambda t: re.search(r"\b(three|3)\b[^.\n]{0,20}attempt", t, re.I) and re.search(r"250\s*ms", t, re.I),
    4: lambda t: all(number_in(t, v) for v in NWP.values()),
    5: lambda t: re.search(REFUSAL, t, re.I) and not re.search(r"\d+(\.\d+)?\s*%|\bratio (is|was|of) \d", t),
    6: lambda t: re.search(REFUSAL, t, re.I) and COMMISSION not in t.replace(",", ""),
}


def sections(brief):
    parts = re.split(r"^##\s*(\d)\b.*$", brief, flags=re.M)
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def main():
    rows = defaultdict(list)
    for p in sorted(Path(sys.argv[1]).glob("*-run*.json")):
        s = json.loads(p.read_text())
        brief = p.with_suffix(".brief.md").read_text() if p.with_suffix(".brief.md").exists() else ""
        secs = sections(brief)
        correct = [n for n, f in CHECKS.items() if n in secs and f(secs[n])]
        docs = extract(brief)
        invalid = sum(bool(check(d)) for d in docs)
        worker_calls = sum(c["by"] == "worker" for c in s["tool_calls"])
        rows[(s["harness"], s["setup"])].append(s | {"correct": len(correct), "docs": len(docs),
                                                     "invalid": invalid, "worker_calls": worker_calls})
        missed = sorted(set(CHECKS) - set(correct))
        print(f"{p.stem}: {len(correct)}/6{' missed ' + str(missed) if missed else ''}, "
              f"{len(docs)} evidence documents ({invalid} invalid), main {s['main_requests']} requests "
              f"/ {s['main_input_tokens']} tokens / largest {s['main_last_context']}, "
              f"worker {s['worker_input_tokens']}, {s['seconds']} s, cost {s['cost_usd']}")
    print(f"\n{'harness':<9}{'setup':<8}{'runs':>5}{'correct':>9}{'main req':>9}{'main tok':>10}"
          f"{'largest':>9}{'worker tok':>11}{'secs':>6}{'cost':>8}{'invalid docs':>14}")
    for (h, setup), v in sorted(rows.items()):
        n = len(v)
        avg = lambda k: sum(x[k] for x in v) / n  # noqa: E731
        cost = f"{avg('cost_usd'):.3f}" if all(x["cost_usd"] is not None for x in v) else "-"
        print(f"{h:<9}{setup:<8}{n:>5}{sum(x['correct'] for x in v):>5}/{6 * n:<3}{avg('main_requests'):>9.1f}"
              f"{avg('main_input_tokens'):>10.0f}{avg('main_last_context'):>9.0f}"
              f"{avg('worker_input_tokens'):>11.0f}{avg('seconds'):>6.0f}{cost:>8}"
              f"{sum(x['invalid'] for x in v):>7}/{sum(x['docs'] for x in v)}")


if __name__ == "__main__":
    main()
