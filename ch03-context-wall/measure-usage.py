#!/usr/bin/env python3
"""Summarize the payload of a harness session's model requests, from the harness's own output.

Chapter 3 measures the payload: the tokens the harness sends on each request (input plus
cached input). This script reads two formats:

  Claude Code   the output of `claude -p ... --output-format stream-json --verbose`
  OpenAI Codex  a session log from ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl (the output of
                `codex exec --json` carries no per-request usage, so pass the log instead)

Usage:
  python3 measure-usage.py task3.jsonl
  python3 measure-usage.py ~/.codex/sessions/2026/10/22/rollout-...jsonl
  python3 measure-usage.py --csv task*.jsonl        one CSV row per file
  python3 measure-usage.py --each task3.jsonl       also list every request's payload
  python3 measure-usage.py --turns rollout-...jsonl  one line per turn (task) of a Codex session

For each file it prints the number of requests, the first, peak, and last payload, the total
input across requests, and the share of that input that was cached. Standard library only.
"""
import argparse
import json
import sys


def claude_requests(lines):
    """One entry per model request. Claude Code emits several events per request, so key by message id."""
    by_id = {}
    for e in lines:
        if e.get("type") == "assistant":
            m = e.get("message", {})
            by_id[m.get("id")] = m.get("usage") or {}
    reqs = []
    for u in by_id.values():
        cached = u.get("cache_read_input_tokens") or 0
        payload = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) + cached
        reqs.append((payload, cached))
    return reqs


def codex_turns(lines):
    """Requests grouped by turn: a resumed Codex session keeps every turn in one log."""
    turns = [[]]
    for e in lines:
        p = e.get("payload") or {}
        if e.get("type") == "event_msg" and p.get("type") == "task_started" and turns[-1]:
            turns.append([])
        if e.get("type") == "event_msg" and p.get("type") == "token_count" and p.get("info"):
            last = p["info"].get("last_token_usage") or {}
            turns[-1].append((last.get("input_tokens", 0), last.get("cached_input_tokens", 0)))
    return [t for t in turns if t]


def codex_requests(lines):
    return [r for t in codex_turns(lines) for r in t]


def read(path):
    out = []
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def measure(path):
    lines = read(path)
    if any(e.get("type") == "assistant" for e in lines):
        return "claude", claude_requests(lines)
    return "codex", codex_requests(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--csv", action="store_true", help="print one CSV row per file instead of text")
    ap.add_argument("--each", action="store_true", help="also print the payload of every request")
    ap.add_argument("--turns", action="store_true", help="Codex logs: print one line per turn")
    a = ap.parse_args()
    if a.csv:
        print("file,harness,requests,first_payload,peak_payload,last_payload,total_input,cached_share")
    for path in a.files:
        harness, reqs = measure(path)
        if a.turns and harness == "codex":
            for i, t in enumerate(codex_turns(read(path)), 1):
                pay = [r[0] for r in t]
                print(f"{path} turn {i}: {len(t)} requests, payload first {pay[0]:,} / peak {max(pay):,}, "
                      f"total input {sum(pay):,}")
            continue
        if not reqs:
            print(f"{path}: no requests found", file=sys.stderr)
            continue
        pay = [r[0] for r in reqs]
        total = sum(pay)
        share = sum(r[1] for r in reqs) / total if total else 0
        if a.csv:
            print(f"{path},{harness},{len(reqs)},{pay[0]},{max(pay)},{pay[-1]},{total},{share:.2f}")
        else:
            print(f"{path} ({harness}): {len(reqs)} requests, payload first {pay[0]:,} / peak {max(pay):,} "
                  f"/ last {pay[-1]:,}, total input {total:,}, {share:.0%} cached")
            if a.each:
                for i, (p, c) in enumerate(reqs, 1):
                    print(f"  request {i}: payload {p:,} ({c:,} cached)")


if __name__ == "__main__":
    main()
