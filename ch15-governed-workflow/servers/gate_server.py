#!/usr/bin/env python3
"""The change gate: the only way an agent can change a deployed configuration.

    python3 gate_server.py             serves http://127.0.0.1:8818/mcp

Two tools:
  read_config(environment, service)   the deployed values, in an evidence envelope
  propose_change(environment, service, key, value, reason, evidence)

Every change needs evidence documents (Chapter 12's schema) and a value that
matches its key's type. A staging change applies at once, unless it rests on
low-confidence evidence or sets an endpoint (a key ending in _URL), which
decides where requests and credentials go. Every other change, and every
production change, goes to a reviewer: the gate builds an approval packet the agent doesn't write: the operation, the
evidence, the services affected (Chapter 10's traversal, run here), what can
and can't be undone, and the alternatives. It files the request and waits up
to GATE_TIMEOUT seconds for a signed decision from a reviewer who holds a gate
role (gate/approve.py). Approved: it applies the change. Rejected: it returns
the reviewer's reason. No decision: the request expires and nothing applies.

Deployed configurations live in GOVERNED_STATE/deploy/<environment>/<service>.conf,
outside the agent's workspace.
"""
import ast
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

from common import COLLECTOR, ROOT, STATE, auth, serve, tracer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gate"))
import approvals  # noqa: E402

from mcp.server import MCPServer  # noqa: E402
from mcp.server.auth.middleware.auth_context import get_access_token  # noqa: E402

PORT = int(os.environ.get("GATE_PORT", 8818))
RESOURCE = f"http://127.0.0.1:{PORT}/mcp"
TIMEOUT = int(os.environ.get("GATE_TIMEOUT", 120))
ROLES = ["payments-oncall"]
DEPLOY = STATE / "deploy"
SCHEMAS = json.loads((ROOT / "ch09-mcp" / "knowledge" / "config_schemas.json").read_text())
OWNER = {"payments": "PaymentsService", "orders": "OrderService", "users": "UserService",
         "notifications": "NotificationsService", "reporting": "ReportingService",
         "search": "SearchService", "gateway": "ApiGateway", "auth": "UserService"}

span_tracer = tracer("change-gate")
import knowledge_server  # noqa: E402  (Chapter 12: the graph path, in evidence envelopes)
from evidence import check, envelope, extract  # noqa: E402

mcp = MCPServer("change-gate", **auth(RESOURCE, ["change:request"]))


def conf_path(environment, service):
    return DEPLOY / environment / f"{service}.conf"


def read_values(path):
    return dict(re.findall(r"^([A-Z_]+)=(.*)$", path.read_text(), re.M))


def write_value(path, key, value):
    text = path.read_text()
    new = re.sub(rf"^{re.escape(key)}=.*$", lambda m: f"{key}={value}", text, flags=re.M)
    if new == text:
        new = text.rstrip("\n") + f"\n{key}={value}\n"
    path.write_text(new)


def bad_value(kind, value):
    """Why a value doesn't fit its schema type, or None. Rejects control
    characters outright, so a value can't add a second line to the file."""
    if any(ord(c) < 32 or ord(c) == 127 for c in value) or len(value) > 500:
        return "contains a control character or is too long"
    if kind == "integer" and not re.fullmatch(r"\d+", value):
        return "must be an integer"
    if kind == "boolean" and value not in ("true", "false"):
        return "must be true or false"
    return None


def needs_review(environment, key, docs):
    """Production always; staging when the key is an endpoint or the evidence is weak."""
    if environment == "production":
        return "production"
    if key.endswith("_URL"):
        return "an endpoint decides where requests and credentials go"
    if any(d.get("confidence") == "low" for d in docs):
        return "the evidence includes a low-confidence document"
    return None


def requester():
    tok = get_access_token()
    return tok.subject if tok else "unknown"


@mcp.tool()
def read_config(environment: str, service: str) -> str:
    """Return the deployed, non-secret configuration values for one service
    in one environment (staging or production), wrapped in an evidence
    envelope you can cite. Secrets come from the secrets manager and are
    never shown."""
    path = conf_path(environment, service)
    if environment not in ("staging", "production") or not path.exists():
        return envelope(f"No deployed configuration for {service} in {environment}.", path="tool",
                        identifier=f"read_config({environment!r}, {service!r})", status="not_found")
    return envelope(path.read_text().strip(), path="tool",
                    identifier=f"read_config({environment!r}, {service!r})",
                    freshness=time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime(path.stat().st_mtime)))


def affected(service, key):
    """Who a change to this key reaches, from the knowledge graph, with coverage."""
    owner = OWNER.get(service, service)
    lines, sources = [], []
    for raw in (knowledge_server.trace_configuration(key), knowledge_server.find_dependents(owner, 4)):
        env = json.loads(raw)
        ev = env["evidence"]
        lines.append(env["result"])
        sources.append(f"{ev['source']['identifier']} (coverage {ev['coverage']}"
                       + (f"; {'; '.join(ev['caveats'])}" if ev["caveats"] else "") + ")")
    return owner, lines, sources


RERUNNABLE = {"lookup_error_code", "get_config_schema", "search_docs", "find_dependents",
              "find_dependencies", "trace_configuration", "navigate_catalog", "read_config"}


def source_says(identifier, key):
    """Re-run the retrieval an evidence document names and return what it says
    now, so the reviewer reads the source rather than the agent's summary of it.
    Governed queries aren't re-run: they cost money and run as an identity."""
    try:
        call = ast.parse(identifier, mode="eval").body
        name = call.func.id
        args = [ast.literal_eval(a) for a in call.args]
        kwargs = {k.arg: ast.literal_eval(k.value) for k in call.keywords}
    except (SyntaxError, ValueError, AttributeError):
        return "not re-run: the identifier isn't a call this gate can repeat"
    if name not in RERUNNABLE:
        return f"not re-run: the gate doesn't repeat {name}"
    fn = read_config if name == "read_config" else getattr(knowledge_server, name)
    try:
        text = json.loads(fn(*args, **kwargs))["result"]
    except Exception as e:  # noqa: BLE001  a bad identifier is the agent's problem to report
        return f"not re-run: {type(e).__name__}"
    lines = text.splitlines()
    hits = [l for l in lines if key in l] if len(lines) > 3 else []
    return " / ".join(" ".join(l.split()) for l in (hits or lines[:3]))[:400]


def build_packet(environment, service, key, old, value, reason, docs, alternatives, review="production"):
    owner, lines, sources = affected(service, key)
    weakest = min((d.get("confidence", "low") for d in docs),
                  key=["low", "medium", "high"].index)
    partial = [d["source"]["identifier"] for d in docs if d.get("coverage") != "complete"]
    why = [f"  {reason}"] + [f"  Claim: {d['claim']}\n    source {d['source']['identifier']}"
                             f" (confidence {d['confidence']}, coverage {d['coverage']}"
                             f"{', changed ' + d['freshness'] if d.get('freshness') else ''})\n"
                             f"    the source returns: {source_says(d['source']['identifier'], key)}"
                             for d in docs]
    if weakest != "high" or partial:
        why.append(f"  Note: weakest evidence confidence is {weakest}"
                   + (f"; coverage not complete for {', '.join(partial)}" if partial else "") + ".")
    alts = [f"Apply to staging only and watch it before production."
            if environment == "production" else None,
            f"Do nothing: {key} stays {old} in {environment}."] + list(alternatives or [])
    return "\n".join([
        "OPERATION",
        f"  Set {key} from {old} to {value} in {environment} {service}.conf ({owner}).",
        f"  Review needed because: {review}.",
        "", "WHY", *why,
        "", "AFFECTS", *[f"  {l}" for block in lines for l in block.splitlines()],
        *[f"  Source: {s}" for s in sources],
        "", "REVERSIBLE",
        f"  The value: yes. Setting {key} back to {old} restores it.",
        "  Requests handled while the new value is live: no.",
        "", "ALTERNATIVES",
        *[f"  {i}. {a}" for i, a in enumerate([a for a in alts if a], 1)],
    ])


def refuse(span, why):
    span.set_attributes({"gate.outcome": "refused", "gate.refusal": why})
    approvals.log({"event": "refused", "reason": why, "requester": requester()})
    return f"Refused, nothing changed: {why}"


@mcp.tool()
async def propose_change(environment: str, service: str, key: str, value: str, reason: str,
                         evidence: str, alternatives: list[str] | None = None) -> str:
    """Change one configuration value in a deployed environment. environment
    is staging or production; service is a name such as payments; reason is
    one sentence; evidence is a JSON array of the evidence documents the
    change rests on (Chapter 12's schema). Staging changes apply at once,
    except endpoint keys and changes resting on low-confidence evidence.
    Those, and every production change, go to a human reviewer with an approval packet built
    from the evidence, the sources it names (re-run by the gate), and the
    knowledge graph; this call waits for the
    decision and reports it. Never retry a rejected or expired production
    change unless the user asks: report it."""
    with span_tracer.start_as_current_span("gate.propose_change") as span:
        span.set_attributes({"gate.environment": environment, "gate.service": service,
                             "gate.key": key})
        path = conf_path(environment, service)
        schema = SCHEMAS.get(service, {})
        if environment not in ("staging", "production") or not path.exists():
            return refuse(span, f"no deployed configuration for {service} in {environment}")
        if key not in schema:
            return refuse(span, f"{key} is not in the {service} configuration schema")
        if schema[key].get("secret"):
            return refuse(span, f"{key} is a secret; secrets are changed in the secrets manager")
        value = str(value).strip()
        if why_bad := bad_value(schema[key]["type"], value):
            return refuse(span, f"the value for {key} {why_bad}")
        old = read_values(path).get(key, "(unset)")
        if old == value:
            return refuse(span, f"{key} is already {value} in {environment}")
        docs = extract(evidence)
        problems = [f"document {i}: {'; '.join(p)}" for i, d in enumerate(docs, 1) if (p := check(d))]
        found = [d for d in docs if not check(d) and d.get("status") == "found"]
        span.set_attributes({"gate.evidence_documents": len(docs), "gate.evidence_found": len(found)})
        if problems:
            return refuse(span, "evidence documents don't match the schema: " + " | ".join(problems))
        if not found:
            return refuse(span, "a change needs at least one evidence document with status found")
        action = {"kind": "config.set", "environment": environment, "service": service,
                  "key": key, "from": old, "to": value}

        review = needs_review(environment, key, found)
        span.set_attribute("gate.required", bool(review))
        if not review:
            write_value(path, key, value)
            approvals.log({"event": "applied", "gate": "not required", "action": action,
                           "requester": requester(), "evidence": found})
            span.set_attribute("gate.outcome", "applied")
            return (f"Applied to staging: {key} {old} -> {value}. This change needed no approval. "
                    f"To undo it, propose {key}={old} for staging.")

        packet = build_packet(environment, service, key, old, value, reason, found, alternatives, review)
        req = approvals.create(action, packet, ROLES, TIMEOUT, requester())
        span.set_attribute("gate.request_id", req["id"])
        print(f"gate: {req['id']} waiting up to {TIMEOUT}s for {ROLES}", file=sys.stderr, flush=True)
        start = time.time()
        try:
            while time.time() < req["expires_epoch"]:
                verdict, reviewer, why = approvals.verify(req)
                if verdict is None and why != "no decision yet":
                    approvals.log({"event": "ignored", "id": req["id"], "reason": why})
                    (approvals.STORE / f"{req['id']}.decision.json").rename(
                        approvals.STORE / f"{req['id']}.ignored-{int(time.time())}.json")
                if verdict:
                    break
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            # The client gave up (a timeout, or the user stopped the session). Withdraw the
            # request so a reviewer can't approve a change nobody is waiting to hear about.
            approvals.close(req, "withdrawn", waited_s=round(time.time() - start, 1))
            span.set_attribute("gate.outcome", "withdrawn")
            raise
        waited = round(time.time() - start, 1)
        span.set_attributes({"gate.wait_s": waited})
        if verdict == "approve":
            if read_values(path).get(key, "(unset)") != old:
                approvals.close(req, "stale", reviewer=reviewer)
                span.set_attribute("gate.outcome", "stale")
                return (f"Approved by {reviewer}, but {key} changed in {environment} while the request "
                        f"waited, so the approved packet no longer describes it. Nothing applied.")
            write_value(path, key, value)
            approvals.close(req, "applied", reviewer=reviewer, reason=why, waited_s=waited)
            span.set_attributes({"gate.outcome": "applied", "gate.reviewer": reviewer})
            return (f"Approved by {reviewer} (request {req['id']}) and applied to {environment}: "
                    f"{key} {old} -> {value}. To undo it, propose {key}={old}; that goes through "
                    f"review too.")
        if verdict == "reject":
            approvals.close(req, "rejected", reviewer=reviewer, reason=why, waited_s=waited)
            span.set_attributes({"gate.outcome": "rejected", "gate.reviewer": reviewer})
            return (f"Rejected by {reviewer} (request {req['id']}): {why}\nNothing was applied to "
                    f"{environment}. Don't propose the same change again; report the reviewer's reason.")
        approvals.close(req, "expired", waited_s=waited)
        span.set_attribute("gate.outcome", "expired")
        return (f"No reviewer decided within {TIMEOUT} seconds, so request {req['id']} expired and "
                f"nothing was applied. A late approval won't apply it. Tell the user the change is "
                f"waiting for review.")


if __name__ == "__main__":
    print(f"change-gate on {RESOURCE} (timeout {TIMEOUT}s, roles {ROLES}, "
          f"spans to {COLLECTOR or 'nowhere'})", flush=True)
    serve(mcp, PORT)
