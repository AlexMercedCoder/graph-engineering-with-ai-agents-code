#!/usr/bin/env python3
"""Prepare run folders for publishing, in place.

    python3 tools/sanitize-runs.py <runs-dir>

Transcripts lose their init, system, and rate-limit records. Spans keep the
attributes check_trace.py and Chapter 14's graphspans.py read (harness turns,
model requests, tool calls, server calls, and the gate's own span) without
prompt, response, or tool content; other spans keep only their place in the
tree. Telemetry logs and metrics are dropped. Every text file has local
paths, email addresses, and the username replaced.
"""
import getpass
import hashlib
import json
import re
import sys
from pathlib import Path

KEEP_SPANS = re.compile(r"^(claude_code\.(interaction|llm_request|tool)$|tools/call |gate\.)")
DROP_ATTRS = re.compile(r"(prompt|response|tool_input|tool_parameters|full_command|file_path|"
                        r"bash_command|new_context|user\.email|organization)")
HASHED = {"user.id", "session.id", "user.account_uuid", "user.account_id"}
PATHS = [(re.compile(r"/tmp/tmp[A-Za-z0-9_.]+"), "<run-dir>"),
         (re.compile(r"/tmp/claude-\d+/[^\s\"'\\]*"), "<scratch>"),
         (re.compile(r"/home/[a-z0-9_-]+"), "<home>"),
         (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}"), "<email>"),
         (re.compile(rf"\b{re.escape(getpass.getuser())}\b"), "<user>")]


def scrub(text):
    for pattern, repl in PATHS:
        text = pattern.sub(repl, text)
    return text


def attrs(d):
    return {k: ("sha256:" + hashlib.sha256(str(v).encode()).hexdigest()[:12] if k in HASHED else v)
            for k, v in d.items() if not DROP_ATTRS.search(k)}


def span(rec):
    if not KEEP_SPANS.search(rec["name"]):
        return {k: rec.get(k) for k in ("trace_id", "span_id", "parent_span_id", "name", "start_ns", "end_ns")} \
            | {"skeleton": True, "attributes": {}, "events": [],
               "resource": {"service.name": rec["resource"].get("service.name")}}
    rec["attributes"] = attrs(rec["attributes"])
    rec["resource"] = attrs(rec.get("resource", {}))
    rec["events"] = [dict(e, attributes=attrs(e.get("attributes", {}))) for e in rec.get("events", [])]
    return rec


def transcript(rec):
    if rec.get("type") in ("system", "rate_limit_event") or rec.get("subtype") == "init":
        return None
    return rec


def rewrite(path, keep):
    if path.exists():
        out = [scrub(json.dumps(r)) for r in (keep(json.loads(l)) for l in path.open() if l.strip()) if r]
        path.write_text("".join(l + "\n" for l in out))


for run in sorted(p for p in Path(sys.argv[1]).iterdir() if p.is_dir()):
    rewrite(run / "telemetry" / "spans.jsonl", span)
    for f in ("logs.jsonl", "metrics.jsonl"):
        (run / "telemetry" / f).unlink(missing_ok=True)
    rewrite(run / "transcript.jsonl", transcript)
    for f in run.iterdir():
        if f.is_file() and f.name not in ("transcript.jsonl",):
            f.write_text(scrub(f.read_text()))
    print(f"sanitized {run.name}")
