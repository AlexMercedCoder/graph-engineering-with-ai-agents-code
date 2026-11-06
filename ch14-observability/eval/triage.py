#!/usr/bin/env python3
"""The three triage questions, asked of one traced session, plus a topology check.

    python3 eval/triage.py <run-dir>            # reads telemetry/ and transcript.jsonl
    python3 eval/triage.py <run-dir> --json     # one JSON object, for summarize.py

1. Route:     did the blast-radius skill load, and did find_dependents run?
2. Evidence:  did the traversal reach every dependent the baseline expects,
              with complete coverage?
3. Reasoning: does the answer's `Affected services:` line name every service
              the traversals returned, and nothing they didn't?

The first question that fails names the class: execution graph, knowledge
graph, or reasoning. A session that didn't end normally (an API error, a reply
cut off) is "incomplete" and gets no class, because its answer says nothing
about either graph. The expected route and evidence are in expected.json,
recorded from a passing baseline run.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from graphspans import graph, load  # noqa: E402

EXPECTED = json.loads((HERE / "expected.json").read_text())


def answer_text(run):
    """The agent's final reply, from either harness's JSON transcript."""
    lines = [json.loads(l) for l in (run / "transcript.jsonl").open() if l.strip().startswith("{")]
    results = [l["result"] for l in lines if l.get("type") == "result" and "result" in l]
    if results:
        return results[-1]
    texts = [l["part"]["text"] for l in lines if l.get("type") == "text"]
    return texts[-1] if texts else ""


def finished(run):
    """Whether the session ended normally, from the harness's own record of how it
    stopped rather than from the reply: Claude Code's result event, or OpenCode's
    final text after its last step."""
    lines = [json.loads(l) for l in (run / "transcript.jsonl").open() if l.strip().startswith("{")]
    results = [l for l in lines if l.get("type") == "result"]
    if results:
        r = results[-1]
        return r.get("subtype") == "success" and not r.get("is_error"), r.get("terminal_reason") or r.get("subtype")
    types = [l.get("type") for l in lines]
    if "text" not in types or types[-1] == "step_start":
        return False, "no final reply"
    return True, "completed"


def skills_loaded(run, nodes):
    """Skill names from Claude Code's skill_name span attribute, or from OpenCode's
    skill tool call: the collector copies the name to ai.toolCall.skill before it
    drops the call's arguments."""
    names = [n["skill"] for n in nodes.values() if n["kind"] == "tool" and n.get("skill")]
    for s in load(run / "telemetry"):
        a = s["attributes"]
        if s["name"] == "ai.toolCall" and a.get("ai.toolCall.name") == "skill":
            if a.get("ai.toolCall.skill"):
                names.append(a["ai.toolCall.skill"])
                continue
            try:
                names.append(json.loads(a.get("ai.toolCall.args", "{}")).get("name"))
            except ValueError:
                pass
    return names


def mentioned(text, names):
    """The services the answer reports. The skill ends every answer with an
    `Affected services:` line; read that when it's there. Without it, fall back
    to every service name the prose mentions, which counts a sentence such as
    "I left ApiGateway out" as naming ApiGateway."""
    lines = re.findall(r"^\W*Affected services:\W*(.*)$", text, re.M | re.I)
    source = lines[-1] if lines else text
    return {n for n in names if re.search(rf"\b{re.escape(n)}\b", source)}, bool(lines)


def triage(run):
    run = Path(run)
    nodes, children = graph(load(run / "telemetry"))
    tools = [n for n in nodes.values() if n["kind"] == "tool"]
    route = EXPECTED["route"]
    skill_ok = route["skill"] in skills_loaded(run, nodes)
    tool_calls = [n["tool"] for n in tools]
    tool_ok = any(str(t).endswith(route["tool"]) for t in tool_calls)

    def under_tool_call(n):
        """The topology check: a traversal counts only if it sits under a
        find_dependents tool call, reached by trace context or joined by time."""
        p = nodes.get(n.get("parent"))
        while p is not None:
            if p["kind"] == "tool":
                return str(p.get("tool", "")).endswith(route["tool"])
            p = nodes.get(p.get("parent"))
        return False

    traversals = [n for n in nodes.values() if n["kind"] == "graph"
                  and n.get("op") == "graph.find_dependents" and under_tool_call(n)]
    evidence = [n for n in traversals if n.get("root") == EXPECTED["evidence"]["root"]]
    best = max(evidence, key=lambda n: n.get("paths_found", 0), default=None)
    found = set(best.get("targets") or []) if best else set()
    # Everything any traversal returned, for the reasoning check: an agent that
    # walks on from each dependent has that evidence too.
    seen = set().union(*(set(n.get("targets") or []) for n in traversals)) - {EXPECTED["evidence"]["root"]}
    expected = set(EXPECTED["evidence"]["targets"])
    evidence_ok = bool(best) and best.get("coverage") == "complete" and found == expected

    text = answer_text(run)
    named, listed = mentioned(text, set(EXPECTED["services"]) - {EXPECTED["evidence"]["root"]})
    reasoning_ok = bool(best) and named == seen

    ok, stop = finished(run)
    if not ok:
        verdict = "incomplete"
    elif not (skill_ok and tool_ok):
        verdict = "execution graph"
    elif not evidence_ok:
        verdict = "knowledge graph"
    elif not reasoning_ok:
        verdict = "reasoning"
    else:
        verdict = "pass"
    llm = [n for n in nodes.values() if n["kind"] == "llm"]
    return {
        "run": run.name, **(json.loads((run / "run.json").read_text()) if (run / "run.json").exists() else {}),
        "verdict": verdict, "stop": stop, "answer_correct": named == expected,
        "route": {"skill_loaded": skill_ok, "find_dependents_called": tool_ok, "tools": tool_calls},
        "evidence": {"paths": best.get("paths_found") if best else None,
                     "coverage": best.get("coverage") if best else None,
                     "depth": f"{best.get('depth_used')}/{best.get('depth_cap')}" if best else None,
                     "joined": best is not None and any(
                         n.get("joined") for n in nodes.values() if n["kind"] == "server")},
        "answer": {"named": len(named), "missing": sorted(seen - named), "extra": sorted(named - seen),
                   "from": "Affected services line" if listed else "mentions in prose"},
        "traversals": len(traversals),
        "tokens": {"input": sum(n["input"] for n in llm), "cache_read": sum(n["cache_read"] for n in llm),
                   "cache_write": sum(n["cache_write"] for n in llm), "output": sum(n["output"] for n in llm),
                   "requests": len(llm)},
    }


def calls(tools):
    """Tool names in first-call order, with a count when a tool ran more than once."""
    names = list(dict.fromkeys(map(str, tools)))
    return ", ".join(n + (f" x{tools.count(n)}" if tools.count(n) > 1 else "") for n in names)


def report(t):
    yes = lambda b: "yes" if b else "NO"  # noqa: E731
    r, e, a = t["route"], t["evidence"], t["answer"]
    print(f"{t['run']}: {t.get('harness', '?')} {t.get('condition', '?')}")
    print(f"  1 route      skill loaded {yes(r['skill_loaded'])}, find_dependents called "
          f"{yes(r['find_dependents_called'])}  ({calls(r['tools']) or 'no tools'})")
    print(f"  2 evidence   {e['paths']} paths, coverage {e['coverage']}, depth {e['depth']}"
          f"{', ' + str(t['traversals']) + ' traversals' if t['traversals'] > 1 else ''}"
          f"{'  (server spans joined by time)' if e['joined'] else ''}")
    print(f"  3 reasoning  named {a['named']}, missing {a['missing'] or 'none'}, extra {a['extra'] or 'none'}"
          f"  (from {a['from']})")
    print(f"  verdict: {t['verdict']}; answer {'correct' if t['answer_correct'] else 'wrong'}"
          f"{'  (session ended: ' + str(t['stop']) + ')' if t['verdict'] == 'incomplete' else ''}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    t = triage(sys.argv[1])
    json.dump(t, open(Path(sys.argv[1]) / "triage.json", "w"), indent=1)
    print(json.dumps(t)) if "--json" in sys.argv else report(t)
