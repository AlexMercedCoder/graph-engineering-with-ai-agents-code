"""The approval store: pending requests, signed decisions, and the decision log.

A request records the exact action, the packet the reviewer will read, and a
digest of both. A decision is valid only if it names that digest, is signed
with the key of a reviewer who holds one of the gate's roles, and arrives
before the request expires. Anything else is ignored and logged, so a forged,
stale, or mismatched decision can't apply a change.

The store is a folder (GOVERNED_STATE/approvals). It has to live where the
agent can't write: on another host in production, and outside the agent's
workspace here, where the agent has no shell.
"""
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path

CH15 = Path(__file__).resolve().parent.parent
STATE = Path(os.environ.get("GOVERNED_STATE", CH15 / "state"))
CONFIG = Path(os.environ.get("GOVERNED_CONFIG", CH15 / "config"))
STORE = STATE / "approvals"
LOG = STATE / "decisions.jsonl"


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def digest(action, packet):
    return "sha256:" + hashlib.sha256(canonical({"action": action, "packet": packet}).encode()).hexdigest()


def reviewers():
    return json.loads((CONFIG / "reviewers.json").read_text())


def log(record):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps({"ts": now(), **record}) + "\n")


def create(action, packet, roles, timeout_s, requester):
    STORE.mkdir(parents=True, exist_ok=True)
    rid = "apr_" + secrets.token_hex(6)
    req = {"id": rid, "status": "pending", "created_at": now(),
           "expires_epoch": int(time.time()) + timeout_s, "roles": roles,
           "requester": requester, "action": action, "packet": packet,
           "action_digest": digest(action, packet)}
    (STORE / f"{rid}.request.json").write_text(json.dumps(req, indent=1))
    log({"event": "requested", "id": rid, "action": action, "action_digest": req["action_digest"],
         "requester": requester, "packet": packet})
    return req


def load(rid):
    """A stored request, refused if its packet or action no longer matches its
    digest: whoever edits the file can't change what a reviewer reads and signs."""
    req = json.loads((STORE / f"{rid}.request.json").read_text())
    if digest(req["action"], req["packet"]) != req["action_digest"]:
        raise ValueError(f"{rid} was changed after the gate filed it; don't decide it")
    return req


def pending():
    out = []
    for p in sorted(STORE.glob("*.request.json")) if STORE.exists() else []:
        try:
            req = load(p.name.split(".")[0])
        except ValueError:
            continue
        if req["status"] == "pending" and req["expires_epoch"] > time.time():
            out.append(req)
    return out


def sign(decision, key_hex):
    return hmac.new(bytes.fromhex(key_hex), canonical(decision).encode(), hashlib.sha256).hexdigest()


def decide(rid, verdict, reviewer, reason=""):
    """What a reviewer's client does: sign a decision for one request and file it."""
    req = load(rid)
    key = reviewers()[reviewer]["key"]
    decision = {"request_id": rid, "action_digest": req["action_digest"], "decision": verdict,
                "reason": reason, "reviewer": reviewer, "decided_at": now()}
    signed = {**decision, "signature": sign(decision, key)}
    (STORE / f"{rid}.decision.json").write_text(json.dumps(signed, indent=1))
    return signed


def verify(req):
    """The gate's check of a filed decision: (verdict, reviewer, reason) or (None, None, why_not)."""
    path = STORE / f"{req['id']}.decision.json"
    if not path.exists():
        return None, None, "no decision yet"
    signed = json.loads(path.read_text())
    decision = {k: v for k, v in signed.items() if k != "signature"}
    who = reviewers().get(decision.get("reviewer", ""))
    if who is None:
        return None, None, "decision from an unknown reviewer"
    if not hmac.compare_digest(sign(decision, who["key"]), signed.get("signature", "")):
        return None, None, "decision signature doesn't verify"
    if decision.get("action_digest") != req["action_digest"]:
        return None, None, "decision is for a different action or packet"
    if not set(who["roles"]) & set(req["roles"]):
        return None, None, f"{decision['reviewer']} holds none of the roles {req['roles']}"
    if decision.get("decision") not in ("approve", "reject"):
        return None, None, "decision is neither approve nor reject"
    return decision["decision"], decision["reviewer"], decision.get("reason", "")


def close(req, status, **extra):
    req = {**req, "status": status, "closed_at": now(), **extra}
    (STORE / f"{req['id']}.request.json").write_text(json.dumps(req, indent=1))
    log({"event": status, "id": req["id"], "action_digest": req["action_digest"], **extra})
    return req
