#!/usr/bin/env python3
"""Deterministic checks for the router and the evidence checker. Standard library only.

    python3 check_router.py

1. The rules alone route the labeled set as the chapter reports (36 of 42).
2. A known false positive stays fixed, and each combined question fans out
   to graph and vector.
3. An unmatched question lands in ROUTER_LOG, mode 600, with its email
   address and token-shaped strings redacted.
4. evidence.check() accepts a valid document and names each fault in bad ones.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import router  # noqa: E402
from evidence import check  # noqa: E402

failed = []


def expect(name, ok):
    print(f"{'ok  ' if ok else 'FAIL'} {name}")
    if not ok:
        failed.append(name)


os.environ.pop("ROUTER_MODEL", None)
out = subprocess.run([sys.executable, str(HERE / "route_eval.py")], capture_output=True, text=True).stdout
expect("rules route 36 of 42 labeled questions", "routing accuracy: 36/42" in out)

expect("a breakdown with no business figure stays off the catalog",
       router.route("Why does ApiGateway rate-limit requests by region?").paths == ("vector",))

combined = [json.loads(l)["q"] for l in (HERE / "combined.jsonl").read_text().splitlines() if l.strip()]
expect("combined questions fan out to graph and vector",
       all(set(router.route(q).paths) == {"graph", "vector"} for q in combined))

with tempfile.TemporaryDirectory() as tmp:
    os.environ["ROUTER_LOG"] = str(Path(tmp) / "logs" / "fallthrough.jsonl")
    r = router.route("Can jane.doe@example.com reuse sk-test-0123456789abcdef, AKIAIOSFODNN7EXAMPLE, "
                     "Bearer abc123def456ghi789jk, or eyJhbGciOi.eyJzdWIiOi.c2lnbmF0dXJl for the gateway?")
    log = Path(os.environ["ROUTER_LOG"])
    line, mode = log.read_text(), log.stat().st_mode & 0o777
    del os.environ["ROUTER_LOG"]
expect("unmatched question is logged, redacted, readable only by you",
       r.matched_by == "default" and "<email>" in line and mode == 0o600
       and not any(x in line for x in ("example.com", "0123456789abcdef", "AKIAIOSFODNN7EXAMPLE",
                                       "abc123def456ghi789jk", "eyJzdWIiOi")))

good = {"schema_version": 1, "status": "found", "claim": "E4021 is not retryable.",
        "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"},
        "confidence": "high", "coverage": "complete", "cost_tokens": 43,
        "freshness": "2026-11-04T02:09Z", "caveats": []}
expect("valid document passes", check(good) == [])
expect("missing cost_tokens is named", check({k: v for k, v in good.items() if k != "cost_tokens"})
       == ["missing cost_tokens"])
expect("unknown field is named", any("unknown field section" in p for p in check(good | {"section": "## 1"})))
expect("numeric confidence is refused", any(p.startswith("confidence") for p in check(good | {"confidence": 0.94})))
expect("a newer schema_version is refused", any(p.startswith("schema_version") for p in check(good | {"schema_version": 2})))

print(f"{'all router checks passed' if not failed else f'{len(failed)} failed'}")
sys.exit(1 if failed else 0)
