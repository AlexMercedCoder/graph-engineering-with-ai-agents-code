# Production payments: E4021 capture failures

## Outcome
- **Change proposed:** production / payments / `AUTH_HOLD_MINUTES`: `10` → `60` (the documented default)
- **Gate outcome:** **unknown.** The `propose_change` call timed out after 20s without returning a decision or request id.
- **Request id:** none returned
- **Reviewer's reason:** none received
- **Current production value (re-read after the timeout):** `AUTH_HOLD_MINUTES=10`. **No change has been applied.**

I did not resubmit. The timeout may have happened after the gate created a review request. A second call could put a duplicate production request in front of the reviewer. Before anything is resubmitted, someone should check the change-gate queue for a pending request.

## Cause
- E4021 means "Payment authorization expired": the authorization hold lapsed before capture (`lookup_error_code('E4021')`).
- In the payments schema, `AUTH_HOLD_MINUTES` must be greater than `CAPTURE_DELAY_MINUTES`, or holds lapse before capture. Its default is 60 (`get_config_schema('payments')`).
- Production has `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15`, so every hold expires 5 minutes before the capture worker runs (`read_config('production', 'payments')`).

## Blast radius
- The graph shows `AUTH_HOLD_MINUTES` also configures **RenewalsWorker**, where it sets how long renewal authorizations are held (`trace_configuration('AUTH_HOLD_MINUTES')`). Renewal holds would get longer too.

## Alternative considered
- Lower `CAPTURE_DELAY_MINUTES` below 10. I rejected this because it moves that key away from its documented default of 15, while 60 is the documented default for the key that is out of spec.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means the payment authorization expired: the authorization hold lapsed before capture; it is not retryable by capture alone.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"In the payments schema, AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold is shorter than the capture delay.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:23Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}
]
```
