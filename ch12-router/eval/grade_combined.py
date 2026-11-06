#!/usr/bin/env python3
"""Grade run_routed.py --questions combined.jsonl results.

    python3 grade_combined.py results/            model judge (needs Claude Code)
    python3 grade_combined.py results/ --regex    name matching only

Each combined question asks for a set of services and a fact from one
document. The judge, as in Chapter 10's grade.py, reports which expected items
the answer gives as part of its answer and which other services it presents
as answers. An answer is fully correct when it gives every expected item and
no other service. Verdicts are cached next to each result as <name>.judge.json.
"""
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
QS = {r["id"]: r for r in (json.loads(l) for l in
      (HERE / "combined.jsonl").read_text().splitlines() if l.strip())}
JUDGE_MODEL = "claude-sonnet-5-5"
JUDGE_PROMPT = """\
You are grading an answer to an architecture question that asks for a set of
services and for one fact. For each expected item below, decide whether the
answer presents that item as part of its answer. An item mentioned only to
exclude it, or only as background, does not count; a fact counts when the
answer states it in any wording. Then list every other service the answer
presents as part of the set of services the question asks for. Leave out
services named only as background, as a step in a path, or to rule them out,
and the subject of the question itself.

Question: {q}
Expected items: {items}

Answer:
<<<
{answer}
>>>

Return only JSON: {{"included": [true or false for each expected item, in order],
 "extra": ["other services the answer gives as part of the set"]}}
"""


def judge(path, r, q):
    cached = path.with_suffix(".judge.json")
    if cached.exists():
        return json.loads(cached.read_text())
    prompt = JUDGE_PROMPT.format(q=q["q"], items=json.dumps(q["labels"]), answer=r["answer"])
    with tempfile.TemporaryDirectory() as empty:
        out = subprocess.run(["claude", "-p", prompt, "--model", JUDGE_MODEL, "--tools", "",
                              "--strict-mcp-config", "--setting-sources", "project",
                              "--output-format", "json", "--no-session-persistence"],
                             cwd=empty, capture_output=True, text=True, timeout=300,
                             stdin=subprocess.DEVNULL)
    body = json.loads(out.stdout)["result"]
    verdict, _ = json.JSONDecoder().raw_decode(body[body.index("{"):])
    verdict = {"included": verdict["included"], "extra": verdict.get("extra", [])}
    cached.write_text(json.dumps(verdict) + "\n")
    return verdict


def main():
    results = [(p, json.loads(p.read_text())) for p in sorted(Path(sys.argv[1]).glob("*.json"))
               if ".judge" not in p.name]
    regex = "--regex" in sys.argv
    if regex:
        verdicts = [{"included": [bool(re.search(e, r["answer"], re.I)) for e in QS[r["id"]]["expect"]],
                     "extra": []} for _, r in results]
    else:
        with ThreadPoolExecutor(6) as pool:
            verdicts = list(pool.map(lambda pr: judge(pr[0], pr[1], QS[pr[1]["id"]]), results))
    cells = defaultdict(list)
    for (path, r), v in zip(results, verdicts):
        full = all(v["included"]) and not v["extra"]
        cells[(r["harness"], r["side"])].append(
            (full, sum(v["included"]) / len(v["included"]), len(r["tool_calls"]),
             r["input_tokens"], r.get("cost_usd")))
        if "--by-question" in sys.argv:
            print(f"{path.stem}: {'FULL' if full else 'part'} {v}")
    print(f"{'harness':<9}{'setup':<8}{'full':>7}{'items':>7}{'calls':>7}{'input tok':>11}{'cost':>9}")
    for key in sorted(cells):
        v = cells[key]
        n = len(v)
        cost = f"{sum(x[4] for x in v) / n:.4f}" if all(x[4] is not None for x in v) else "-"
        print(f"{key[0]:<9}{key[1]:<8}{sum(x[0] for x in v):>4}/{n:<2}{sum(x[1] for x in v) / n:>7.2f}"
              f"{sum(x[2] for x in v) / n:>7.1f}{sum(x[3] for x in v) / n:>11.0f}{cost:>9}")


if __name__ == "__main__":
    main()
