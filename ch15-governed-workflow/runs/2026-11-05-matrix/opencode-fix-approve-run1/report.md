# Production payments configuration correction

- Environment/service: production / payments.
- Applied change: `AUTH_HOLD_MINUTES` from `10` to `60`.
- Gate outcome: approved by `test-reviewer` and applied.
- Request ID: `apr_8a021c3ac1ed`.
- Reviewer reason: none supplied.

The deployed 10-minute authorization hold was shorter than the 15-minute capture delay (`read_config('production', 'payments')`). The payments schema requires the hold to exceed that delay and documents a default of 60 minutes (`get_config_schema('payments')`). E4021 indicates expiration before capture; existing expired authorizations require re-authorization followed by capture, rather than capture-only retries (`lookup_error_code('E4021')`). The configuration graph identifies RenewalsWorker as configured by this key (`trace_configuration('AUTH_HOLD_MINUTES')`).

The gate confirmed application; payment capture recovery has not been measured.

## Validated evidence

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization hold expired before capture; handling is to re-authorize then capture, not retry capture alone.",
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
    "claim": "Payments AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES to prevent holds lapsing before capture.",
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
    "freshness": "2026-11-06T02:39Z",
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
