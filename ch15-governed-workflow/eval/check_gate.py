#!/usr/bin/env python3
"""The gate's guarantees, checked without a model.

    python3 check_gate.py        prints each check; exits 1 if any fails

Runs the gate's tool function in-process against a scratch state folder, with
a four-second timeout, and plays the reviewer from a second task.
"""
import asyncio
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CH15 = HERE.parent
scratch = Path(tempfile.mkdtemp())
os.environ.update(GOVERNED_STATE=str(scratch / "state"), GOVERNED_CONFIG=str(scratch / "config"),
                  GATE_TIMEOUT="4")
os.environ.pop("COLLECTOR", None)
import subprocess  # noqa: E402
subprocess.run([sys.executable, CH15 / "tools" / "make-test-tokens.py"], check=True, capture_output=True)
subprocess.run([sys.executable, CH15 / "tools" / "seed-deploy.py", "--fault", "both"], check=True,
               capture_output=True)
sys.path[:0] = [str(CH15 / "servers"), str(CH15 / "gate")]
import approvals  # noqa: E402
import gate_server as g  # noqa: E402

PROD = scratch / "state" / "deploy" / "production" / "payments.conf"
STAGING = scratch / "state" / "deploy" / "staging" / "payments.conf"
EVIDENCE = json.dumps([{**json.loads(g.knowledge_server.lookup_error_code("E4021"))["evidence"],
                        "claim": "E4021 means the authorization hold lapsed before capture."}])
failures = 0


def ok(name, cond, detail=""):
    global failures
    failures += not cond
    print(f"  {'ok  ' if cond else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not cond else ""))


def value(path, key="AUTH_HOLD_MINUTES"):
    return re.search(rf"^{key}=(.*)$", path.read_text(), re.M).group(1)


async def propose(env, key="AUTH_HOLD_MINUTES", val="60", evidence=EVIDENCE, reviewer=None):
    """Call propose_change; reviewer(req) runs once the request is filed."""
    async def review():
        while not approvals.pending():
            await asyncio.sleep(0.1)
        reviewer(approvals.pending()[0])
    task = asyncio.create_task(review()) if reviewer else None
    reply = await g.propose_change(env, "payments", key, val, "Holds lapse before capture.", evidence)
    if task:
        task.cancel()
    return reply


async def main():
    r = await propose("staging")
    ok("staging applies without review", r.startswith("Applied to staging") and value(STAGING) == "60", r)
    r = await propose("production", evidence="[]")
    ok("production refuses a change with no evidence", r.startswith("Refused") and value(PROD) == "10", r)
    r = await propose("production", evidence='[{"schema_version": 1, "claim": "trust me"}]')
    ok("production refuses evidence that breaks the schema", "don't match the schema" in r, r)
    r = await propose("production", key="PAYMENT_API_KEY", val="x")
    ok("secrets can't be changed through the gate", "secret" in r, r)
    r = await propose("production", key="FRAUD_SCORE_THRESHOLD", val="80")
    ok("keys outside the schema are refused", "not in the payments configuration schema" in r, r)

    r = await propose("staging", key="PAYMENT_BASE_URL", val="https://x.example.com\nPAYMENT_API_KEY=stolen")
    ok("a value with a line break is refused", "control character" in r and "stolen" not in STAGING.read_text(), r)
    r = await propose("staging", key="CAPTURE_TIMEOUT", val="thirty")
    ok("a value that doesn't fit its type is refused", "must be an integer" in r, r)
    r = await propose("staging", key="PAYMENT_BASE_URL", val="https://elsewhere.example.com",
                      reviewer=lambda req: approvals.decide(req["id"], "reject", "dana", "Not that host."))
    ok("an endpoint change goes to a reviewer even in staging",
       "Not that host." in r and "elsewhere" not in STAGING.read_text(), r)
    weak = json.dumps([{**json.loads(EVIDENCE)[0], "confidence": "low"}])
    r = await propose("staging", key="CAPTURE_TIMEOUT", val="45", evidence=weak,
                      reviewer=lambda req: approvals.decide(req["id"], "reject", "dana", "Weak evidence."))
    ok("low-confidence evidence sends a staging change to a reviewer",
       "Weak evidence." in r and value(STAGING, "CAPTURE_TIMEOUT") == "30", r)

    def tamper(req):
        path = approvals.STORE / f"{req['id']}.request.json"
        stored = json.loads(path.read_text())
        stored["packet"] = stored["packet"].replace("RenewalsWorker", "")
        path.write_text(json.dumps(stored))
        tampered.append(subprocess.run([sys.executable, CH15 / "gate" / "approve.py", "approve", req["id"],
                                        "--as", "dana"], capture_output=True, text=True, env=os.environ))
    tampered = []
    r = await propose("production", reviewer=tamper)
    ok("a request edited after filing can't be approved",
       bool(tampered) and tampered[0].returncode != 0 and "changed after the gate filed it" in tampered[0].stderr
       and value(PROD) == "10", tampered[0].stderr if tampered else r)

    r = await propose("production", reviewer=lambda req: approvals.decide(req["id"], "reject", "dana",
                                                                           "Staging first."))
    ok("a rejection leaves production unchanged and returns the reason",
       "Staging first." in r and value(PROD) == "10", r)
    r = await propose("production")
    ok("no decision: the request expires and nothing applies", "expired" in r and value(PROD) == "10", r)
    expired = [p for p in approvals.STORE.glob("*.request.json")
               if json.loads(p.read_text())["status"] == "expired"][0]
    late = subprocess.run([sys.executable, CH15 / "gate" / "approve.py", "approve",
                           expired.name.split(".")[0], "--as", "dana"], capture_output=True, text=True,
                          env=os.environ)
    ok("a late approval is refused", late.returncode != 0 and value(PROD) == "10", late.stdout + late.stderr)

    task = asyncio.create_task(g.propose_change("production", "payments", "AUTH_HOLD_MINUTES", "60",
                                                "Holds lapse before capture.", EVIDENCE))
    while not approvals.pending():
        await asyncio.sleep(0.1)
    rid = approvals.pending()[0]["id"]
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    late = subprocess.run([sys.executable, CH15 / "gate" / "approve.py", "approve", rid, "--as", "dana"],
                          capture_output=True, text=True, env=os.environ)
    ok("a request the client abandons is withdrawn, and can't be approved afterward",
       approvals.load(rid)["status"] == "withdrawn" and late.returncode != 0 and value(PROD) == "10",
       late.stdout + late.stderr)

    def forged(req):
        (approvals.STORE / f"{req['id']}.decision.json").write_text(json.dumps({
            "request_id": req["id"], "action_digest": req["action_digest"], "decision": "approve",
            "reason": "", "reviewer": "dana", "decided_at": approvals.now(), "signature": "0" * 64}))
    r = await propose("production", reviewer=forged)
    ok("a decision with a bad signature is ignored", "expired" in r and value(PROD) == "10", r)

    def wrong_digest(req):
        d = {"request_id": req["id"], "action_digest": "sha256:" + "0" * 64, "decision": "approve",
             "reason": "", "reviewer": "dana", "decided_at": approvals.now()}
        key = approvals.reviewers()["dana"]["key"]
        (approvals.STORE / f"{req['id']}.decision.json").write_text(
            json.dumps({**d, "signature": approvals.sign(d, key)}))
    r = await propose("production", reviewer=wrong_digest)
    ok("a decision for a different packet is ignored", "expired" in r and value(PROD) == "10", r)
    r = await propose("production", reviewer=lambda req: approvals.decide(req["id"], "approve", "sam"))
    ok("a reviewer without a gate role can't approve", "expired" in r and value(PROD) == "10", r)

    def edit_then_approve(req):
        PROD.write_text(PROD.read_text().replace("AUTH_HOLD_MINUTES=10", "AUTH_HOLD_MINUTES=20"))
        approvals.decide(req["id"], "approve", "dana")
    r = await propose("production", reviewer=edit_then_approve)
    ok("an approval for a value that changed meanwhile applies nothing",
       "no longer describes it" in r and value(PROD) == "20", r)
    PROD.write_text(PROD.read_text().replace("AUTH_HOLD_MINUTES=20", "AUTH_HOLD_MINUTES=10"))

    r = await propose("production", reviewer=lambda req: approvals.decide(req["id"], "approve", "dana"))
    ok("a signed approval from a gate role applies the change",
       r.startswith("Approved by dana") and value(PROD) == "60", r)
    log = [json.loads(l) for l in approvals.LOG.read_text().splitlines()]
    req = [e for e in log if e["event"] == "requested"][-1]
    packet = req["packet"]
    ok("the decision log keeps the packet the reviewer approved",
       any(e["event"] == "applied" and e.get("id") == req["id"] for e in log) and "AFFECTS" in packet)
    ok("the packet's affected services come from the graph",
       "RenewalsWorker" in packet and "OrderService" in packet and "find_dependents" in packet, packet)
    ok("the packet offers doing nothing", "Do nothing" in packet, packet)
    ok("the packet shows what each cited source returns, re-run by the gate",
       "the source returns: E4021: Payment authorization expired" in packet, packet)
    ok("the packet dates each source and says why it needs review",
       ", changed 20" in packet and "Review needed because: production." in packet, packet)


asyncio.run(main())
print("all gate checks passed" if not failures else f"{failures} gate checks failed")
sys.exit(1 if failures else 0)
