#!/usr/bin/env python3
"""Grade run_agents.py results against questions.jsonl.

    python3 grade.py results/            grade with a model judge (needs Claude Code)
    python3 grade.py results/ --regex    grade by name matching only, no model

The judge reads each answer and reports which expected entities it gives as
part of its answer, and, for closed-set questions (every multi-hop one), which
other services, APIs, databases, or keys it also gives as part of the answer.
Recall is the share of expected entities given; precision is the share of
given entities that were expected. An answer is fully correct when it gives
every expected entity and, on a closed-set question, nothing else. Name
matching alone over-credits, because an answer that says "OrderService is not
affected" still names OrderService. Judgments are saved next to each result
as <name>.judge3.json, so regrading is free.

The table reports fully correct answers, mean recall and precision, and tool
calls and input tokens per question, by harness, side, and question shape.
--by-question prints each question's results across runs.
"""
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
QS = {r["id"]: r for r in (json.loads(l) for l in
      (HERE / "questions.jsonl").read_text().splitlines() if l.strip())}
JUDGE_MODEL = "claude-sonnet-5-5"
JUDGE_PROMPT = """\
You are grading an answer to an architecture question. For each expected item
below, decide whether the answer presents that item as part of its answer to
the question. An item the answer mentions only to exclude it ("X is not
affected"), or only as background, does not count. Then list every other
item of the kind the question asks for (services, if it asks which services;
services, APIs, and databases, if it asks what something needs) that the
answer presents as part of its answer. Leave out items it names only as
background, as a step in a path, or to rule them out, and the subject of the
question itself.

Question: {q}
Expected items: {items}

Answer:
<<<
{answer}
>>>

Return only JSON: {{"included": [true or false for each expected item, in order],
 "extra": ["other items the answer gives as part of its answer"]}}
"""


def names(q):
    """Readable labels for the expect patterns, for the judge prompt."""
    return [q.get("labels", q["expect"])[i] for i in range(len(q["expect"]))]


def judge(path, r, q):
    cached = path.with_suffix(".judge3.json")
    if cached.exists():
        return json.loads(cached.read_text())
    prompt = JUDGE_PROMPT.format(q=q["q"], items=json.dumps(names(q)), answer=r["answer"])
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


def measure(found, extra, closed):
    given = sum(found) + (len(extra) if closed else 0)
    recall = sum(found) / len(found)
    precision = sum(found) / given if given else 0.0
    full = all(found) and not (closed and extra)
    return full, recall, precision


results = [(p, json.loads(p.read_text())) for p in sorted(Path(sys.argv[1]).glob("*.json"))
           if ".judge" not in p.name]
use_regex = "--regex" in sys.argv
if not use_regex:
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(6) as pool:
        verdicts = list(pool.map(lambda pr: judge(pr[0], pr[1], QS[pr[1]["id"]]), results))
cells = defaultdict(list)
per_q = defaultdict(list)
for i, (path, r) in enumerate(results):
    q = QS[r["id"]]
    if use_regex:
        found, extra = [bool(re.search(p, r["answer"], re.I)) for p in q["expect"]], []
    else:
        found, extra = verdicts[i]["included"], verdicts[i]["extra"]
    closed = q.get("closed", False)
    full, recall, precision = measure(found, extra, closed)
    precision = precision if closed else None
    cells[(r["harness"], r["side"], q["hops"])].append(
        (full, recall, precision, len(r["tool_calls"]), r["input_tokens"], r.get("cost_usd")))
    per_q[(r["id"], r["harness"], r["side"])].append(
        f"{'FULL' if full else 'part'} r={recall:.2f}" + (f" p={precision:.2f}" if closed else "")
        + (f" extra={extra}" if extra and q.get("closed") else ""))

print(f"{'harness':<9}{'side':<8}{'shape':<8}{'full':>7}{'recall':>8}{'prec':>7}{'calls':>7}"
      f"{'input tok':>11}{'cost':>9}")
for key in sorted(cells):
    v = cells[key]
    n = len(v)
    print(f"{key[0]:<9}{key[1]:<8}{key[2]:<8}{sum(x[0] for x in v):>4}/{n:<2}"
          f"{sum(x[1] for x in v) / n:>8.2f}"
          f"{(f'{sum(x[2] for x in v) / n:.2f}' if v[0][2] is not None else '-'):>7}"
          f"{sum(x[3] for x in v) / n:>7.1f}{sum(x[4] for x in v) / n:>11.0f}"
          + (f"{sum(x[5] for x in v) / n:>9.4f}" if all(x[5] is not None for x in v) else f"{'-':>9}"))
if "--by-question" in sys.argv:
    for key in sorted(per_q):
        print(f"q{key[0]:02d} {key[1]:<9}{key[2]:<7}" + " | ".join(per_q[key]))
