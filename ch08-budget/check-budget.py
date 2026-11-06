#!/usr/bin/env python3
"""Fail when the fixed part of a Claude Code request grows past its ceiling.

Starts a fresh headless session in the project, sends one prompt that needs no tools, and
compares the first request's payload (the harness baseline plus your configuration, skill
listing, and MCP tool names) with the ceiling you wrote down. Exits 1 when it is over, so a
CI job fails on the commit that grew it.

    python3 check-budget.py --ceiling 33000 <project-dir>        run a session and check it
    python3 check-budget.py --ceiling 33000 --log first.jsonl    check a recorded session

The ceiling covers the harness too, so upgrading Claude Code can move the number. When that
happens, measure again and update the ceiling on purpose, in the same commit. Standard
library only.
"""
import argparse
import json
import subprocess
import sys

PROMPT = "Reply with the single word ok. Do not use any tools."


def first_payload(lines):
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        u = event.get("message", {}).get("usage") or {}
        payload = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0) \
            + (u.get("cache_read_input_tokens") or 0)
        if payload:
            return payload
    return None


def run_session(project):
    cmd = ["claude", "-p", PROMPT, "--setting-sources", "project,local", "--max-turns", "1",
           "--output-format", "stream-json", "--verbose"]
    out = subprocess.run(cmd, cwd=project, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return out.stdout.splitlines()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ceiling", type=int, required=True, help="maximum first-request payload")
    ap.add_argument("--log", help="check a recorded stream-json session instead of running one")
    ap.add_argument("--save", help="also write the session's stream-json to this file")
    ap.add_argument("project", nargs="?", default=".")
    args = ap.parse_args()

    lines = open(args.log, errors="replace").read().splitlines() if args.log else run_session(args.project)
    if args.save:
        open(args.save, "w").write("\n".join(lines) + "\n")
    payload = first_payload(lines)
    if payload is None:
        print("no request found; is Claude Code installed and signed in?", file=sys.stderr)
        return 2
    if payload > args.ceiling:
        print(f"FAIL fixed part {payload:,} tokens, ceiling {args.ceiling:,} "
              f"({payload - args.ceiling:,} over)")
        return 1
    print(f"ok   fixed part {payload:,} tokens, ceiling {args.ceiling:,} "
          f"({args.ceiling - payload:,} to spare)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
