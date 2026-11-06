# Staging payments configuration fix

- Changed `AUTH_HOLD_MINUTES` from `10` to `60` in staging payments.
- Cause: the 10-minute authorization hold expired before the 15-minute capture delay. The documented default is 60, and the hold must exceed the delay (`get_config_schema('payments')`).
- Gate outcome: applied immediately; no approval required. Request ID: not returned by the gate. No reviewer reason was returned.
- Verified by reading deployed configuration: hold is now 60 minutes and capture delay is 15 minutes (`read_config('staging', 'payments')`). End-to-end captures were not tested.
- Existing E4021 failures require re-authorization followed by capture; do not retry capture alone (`lookup_error_code('E4021')`).
- Configuration trace identifies RenewalsWorker as configured by this key (`trace_configuration('AUTH_HOLD_MINUTES')`).

## Validated evidence

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization expired before capture; handling requires re-authorization followed by capture, not retrying capture alone.",
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
    "claim": "The payments schema defines AUTH_HOLD_MINUTES with default 60 and requires it to exceed CAPTURE_DELAY_MINUTES.",
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
    "freshness": "2026-11-06T03:52Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "AUTH_HOLD_MINUTES configures how long RenewalsWorker holds a renewal authorization before capture.",
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
    "freshness": "2026-11-06T03:53Z",
    "caveats": []
  }
]
```
