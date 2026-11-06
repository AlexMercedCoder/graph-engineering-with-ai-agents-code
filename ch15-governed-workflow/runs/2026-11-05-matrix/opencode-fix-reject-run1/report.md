# Payments E4021 configuration change

## Outcome

- Production: no change applied. Proposed `AUTH_HOLD_MINUTES=60` in place of `10`; the gate rejected request `apr_cb7a4eca7df8`.
- Reviewer: `test-reviewer`.
- Reviewer's reason: “Apply it to staging first and confirm captures succeed there. Production waits for Thursday's change window.”
- The rejected production request was not retried.
- Staging: applied `AUTH_HOLD_MINUTES` from `10` to `60`. The gate reported success without approval and supplied no staging request ID. A subsequent configuration read confirmed `AUTH_HOLD_MINUTES=60` and `CAPTURE_DELAY_MINUTES=15`.
- Capture success in staging remains unverified: the available tools do not execute capture tests or expose operational capture results. Successful staging captures and the reviewer's change-window requirement remain prerequisites for production.

## Diagnosis and supported fix

Production holds authorizations for 10 minutes but delays capture for 15 minutes (`read_config('production', 'payments')`). The payments schema requires the authorization hold to exceed the capture delay and documents a default hold of 60 minutes (`get_config_schema('payments')`). E4021 denotes an expired authorization; already-expired authorizations require reauthorization followed by capture, not capture-only retries (`lookup_error_code('E4021')`). The configuration graph also identifies RenewalsWorker as configured by this key (`trace_configuration('AUTH_HOLD_MINUTES')`).

## Evidence

All five documents passed evidence validation. Total retrieval cost: 463 tokens.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization hold expired before capture; re-authorize then capture, and do not retry capture alone.",
    "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 43,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Payments AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES to prevent authorization holds lapsing before capture.",
    "source": {"path": "tool", "identifier": "get_config_schema('payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 261,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15.",
    "source": {"path": "tool", "identifier": "read_config('production', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T02:41Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "AUTH_HOLD_MINUTES configures RenewalsWorker and sets how long a renewal authorization is held before capture.",
    "source": {"path": "graph", "identifier": "trace_configuration('AUTH_HOLD_MINUTES')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 31,
    "freshness": "2026-11-06T01:29Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Staging payments has AUTH_HOLD_MINUTES=60 and CAPTURE_DELAY_MINUTES=15 after the staging change.",
    "source": {"path": "tool", "identifier": "read_config('staging', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T02:43Z",
    "caveats": []
  }
]
```
