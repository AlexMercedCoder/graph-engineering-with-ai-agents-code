# Production payments configuration fix

## Outcome

Approved by `test-reviewer` and applied to **production payments**.

- Request ID: `apr_fb8ae2da34dd`
- Changed `AUTH_HOLD_MINUTES` from `10` to `60`.
- Gate outcome: approved and applied. No separate reviewer reason was returned.

Production had a 10-minute authorization hold and a 15-minute capture delay (`read_config('production', 'payments')`). The payments schema requires the hold to exceed the capture delay and documents 60 minutes as the default (`get_config_schema('payments')`).

E4021 indicates an expired authorization. Already-expired authorizations require re-authorization followed by capture; capture alone must not be retried (`lookup_error_code('E4021')`). Payment recovery and post-change capture success have not been verified.

The configuration graph identifies RenewalsWorker as configured by this key (`trace_configuration('AUTH_HOLD_MINUTES')`).

## Evidence

All four evidence documents passed `check_evidence` before submission. Total retrieval cost: 399 tokens.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization expired before capture; handling requires re-authorization then capture, not retrying capture alone.",
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
    "freshness": "2026-11-06T03:18Z",
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
  }
]
```
