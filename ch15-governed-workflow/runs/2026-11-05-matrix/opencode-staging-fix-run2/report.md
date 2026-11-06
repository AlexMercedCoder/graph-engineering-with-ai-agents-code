# Staging payments configuration fix

- Environment: staging; service: payments.
- Changed `AUTH_HOLD_MINUTES` from `10` to `60`, the documented default. The previous hold expired before the configured 15-minute capture delay. Sources: `read_config('staging', 'payments')` (03:10Z), `get_config_schema('payments')`.
- Gate outcome: applied to staging; no approval required. Request id: not returned. Reviewer reason: none.
- Verification: configuration read-back confirms `AUTH_HOLD_MINUTES=60` and `CAPTURE_DELAY_MINUTES=15`. Source: `read_config('staging', 'payments')` (03:11Z). Capture execution was not tested.
- Existing E4021 failures require re-authorization followed by capture; capture alone must not be retried. Source: `lookup_error_code('E4021')`.
- Configuration graph identifies RenewalsWorker as configured by this key. Source: `trace_configuration('AUTH_HOLD_MINUTES')`.

## Evidence

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
    "claim": "The payments AUTH_HOLD_MINUTES default is 60 and must exceed CAPTURE_DELAY_MINUTES to prevent authorizations lapsing before capture.",
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
    "claim": "Staging payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15.",
    "source": {"path": "tool", "identifier": "read_config('staging', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T03:10Z",
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
    "claim": "Staging payments now has AUTH_HOLD_MINUTES=60 and CAPTURE_DELAY_MINUTES=15.",
    "source": {"path": "tool", "identifier": "read_config('staging', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T03:11Z",
    "caveats": []
  }
]
```
