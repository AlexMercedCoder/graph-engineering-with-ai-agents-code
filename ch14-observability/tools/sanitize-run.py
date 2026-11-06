#!/usr/bin/env python3
"""Prepare run folders for publishing: keep the spans, events, and transcript lines
the chapter reads, and drop everything that describes the machine they ran on.

    python3 tools/sanitize-run.py <runs-dir>

Rewrites each run folder in place. Spans of the five node kinds graphspans.py
reads, plus OpenCode's ai.toolCall, keep their attributes without prompt,
response, or tool content; every other span keeps only its IDs, name, and
times, so the tree still joins up. user.id and session.id are hashed. OpenCode's operational logs and Claude Code's
plugin and settings events are dropped, as are transcript init and rate-limit
records. Local paths become <run-dir> or <home>, and email addresses and your
username are removed.
"""
import getpass
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from graphspans import kind_of  # noqa: E402

DROP_ATTRS = re.compile(r"^(ai\.prompt|ai\.response\.(text|toolCalls|providerMetadata)|ai\.toolCall\.(result|args)"
                        r"|ai\.request\.headers\.|ai\.telemetry\.metadata\.userId|user_prompt$|prompt$"
                        r"|response$|new_context|tool_input|tool_parameters|system_prompt|full_command"
                        r"|file_path$|bash_command)")
DROP_EVENTS = {"plugin_loaded", "managed_settings_resolved", "hook_registered", "plugin_installed",
               "user_prompt", "assistant_response"}
PATHS = [(re.compile(r"/tmp/tmp\.[A-Za-z0-9]+"), "<run-dir>"),
         (re.compile(r"/tmp/claude-\d+/[^\s\"']*"), "<scratch>"),
         (re.compile(r"/home/[a-z0-9_-]+"), "<home>"),
         (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}"), "<email>"),
         (re.compile(rf"\b{re.escape(getpass.getuser())}\b"), "<user>")]


def scrub(text):
    for pattern, repl in PATHS:
        text = pattern.sub(repl, text)
    return text


HASHED = {"user.id", "session.id"}


def clean_attrs(d):
    import hashlib
    return {k: ("sha256:" + hashlib.sha256(str(v).encode()).hexdigest()[:12]
                if k in HASHED and v and not str(v).startswith(("sha256:", "hmac:")) else v)
            for k, v in d.items() if not DROP_ATTRS.search(k)}


def rewrite(path, keep):
    if not path.exists():
        return
    out = []
    for line in path.open():
        rec = json.loads(line)
        rec = keep(rec)
        if rec is not None:
            rec = hash_ids(rec)
            out.append(scrub(json.dumps(rec)))
    path.write_text("".join(l + "\n" for l in out))


def span(rec):
    if not (kind_of(rec) or rec["name"] == "ai.toolCall"):
        # Keep the span's place in the tree (IDs, name, times) and nothing else,
        # as collector.py --agent-spans-only does.
        return {k: rec[k] for k in ("trace_id", "span_id", "parent_span_id", "name", "start_ns",
                                    "end_ns")} | {"skeleton": True, "attributes": {}, "events": [],
                                                  "resource": {"service.name": rec["resource"].get("service.name")}}
    a = rec["attributes"]
    if a.get("ai.toolCall.name") == "skill" and "ai.toolCall.skill" not in a:
        try:
            a["ai.toolCall.skill"] = json.loads(a.get("ai.toolCall.args", "{}")).get("name")
        except ValueError:
            pass
    rec["attributes"] = clean_attrs(a)
    rec["events"] = [dict(e, attributes=clean_attrs(e["attributes"])) for e in rec.get("events", [])]
    return rec


def log(rec):
    if rec["resource"].get("service.name") != "claude-code" or rec["event"] in DROP_EVENTS:
        return None
    rec["attributes"] = clean_attrs(rec["attributes"])
    return rec


def transcript(rec):
    if rec.get("type") in ("system", "rate_limit_event") or rec.get("subtype") == "init":
        return None
    return rec


def hash_ids(rec):
    """Hash user.id and session.id wherever they appear: attributes, resources."""
    if isinstance(rec, dict):
        return {k: (clean_attrs({k: v})[k] if k in HASHED else hash_ids(v)) for k, v in rec.items()}
    if isinstance(rec, list):
        return [hash_ids(v) for v in rec]
    return rec


for run in sorted(p for p in Path(sys.argv[1]).iterdir() if p.is_dir()):
    rewrite(run / "telemetry" / "spans.jsonl", span)
    rewrite(run / "telemetry" / "logs.jsonl", log)
    rewrite(run / "telemetry" / "metrics.jsonl", lambda r: r)
    rewrite(run / "transcript.jsonl", transcript)
    if (run / "server.log").exists():
        (run / "server.log").rename(run / "server-stderr.txt")
    for f in ("server-stderr.txt", "triage.json"):
        if (run / f).exists():
            (run / f).write_text(scrub((run / f).read_text()))
    print(f"sanitized {run.name}")
