#!/usr/bin/env python3
"""Score routing accuracy for the Chapter 4 evaluation set.

Usage:
    # 1. Record what your harness actually routed to, one line per prompt id:
    #        1 code-review
    #        2 code-review
    #    ...saved as results.txt
    # 2. python3 score.py results.txt

Reads prompts.jsonl for the expected answers. Reports accuracy overall and
split by the unambiguous and ambiguous halves, because they diagnose different
problems. Standard library only.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def load_expected():
    expected = {}
    with open(HERE / "prompts.jsonl", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rec = json.loads(line)
                expected[rec["id"]] = (rec["expected"], rec["kind"], rec["prompt"])
    return expected


def load_results(path):
    results = {}
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            parts = raw.split(None, 1)
            if len(parts) != 2:
                sys.exit(f"cannot parse result line: {raw!r} (want: '<id> <skill-name>')")
            results[int(parts[0])] = parts[1].strip()
    return results


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    expected = load_expected()
    actual = load_results(sys.argv[1])

    missing = sorted(set(expected) - set(actual))
    if missing:
        print(f"warning: no result recorded for prompt ids {missing}\n")

    halves = {"unambiguous": [0, 0], "ambiguous": [0, 0]}
    wrong = []
    for pid, (want, kind, prompt) in sorted(expected.items()):
        if pid not in actual:
            continue
        halves[kind][1] += 1
        if actual[pid] == want:
            halves[kind][0] += 1
        else:
            wrong.append((pid, kind, prompt, want, actual[pid]))

    total_ok = sum(h[0] for h in halves.values())
    total_n = sum(h[1] for h in halves.values())

    print(f"{'half':<14}{'correct':>9}{'of':>4}{'accuracy':>11}")
    for kind, (ok, n) in halves.items():
        pct = f"{ok / n:.0%}" if n else "n/a"
        print(f"{kind:<14}{ok:>9}{n:>4}{pct:>11}")
    if total_n:
        print(f"{'overall':<14}{total_ok:>9}{total_n:>4}{total_ok / total_n:>11.0%}")

    if wrong:
        print("\nmis-routed:")
        for pid, kind, prompt, want, got in wrong:
            print(f"  [{pid:>2}] ({kind}) {prompt}")
            print(f"       expected {want}, got {got}")

    print("\nReading the split:")
    print("  unambiguous low   -> a description does not describe its own skill")
    print("  ambiguous low     -> descriptions overlap; add an anti-pattern clause and a sibling redirect")
    print("  both high         -> routing is fine; any remaining failure is in the skill body")


if __name__ == "__main__":
    main()
