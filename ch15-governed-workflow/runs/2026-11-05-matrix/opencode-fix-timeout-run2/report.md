# Production payments configuration change

## Outcome

No configuration change was applied. Production request `apr_2f8b2874579c` expired because no reviewer decided within 90 seconds. No reviewer reason was supplied. A late approval cannot apply this expired request. Review is still needed; the request was not retried.

Proposed change: production `payments.AUTH_HOLD_MINUTES` from `10` to the documented default `60`. The deployed capture delay is `15` minutes, exceeding the current hold; the schema requires the hold to exceed the capture delay. Sources: `read_config('production', 'payments')`, `get_config_schema('payments')`.

The configuration graph identifies `RenewalsWorker` as configured by this key. Source: `trace_configuration('AUTH_HOLD_MINUTES')`.

E4021 indicates an authorization expired before capture. Existing expired authorizations require re-authorization followed by capture; capture alone must not be retried. Source: `lookup_error_code('E4021')`.

## Validated evidence

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization expired before capture; re-authorize then capture, and do not retry capture alone.",
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
    "claim": "AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES to prevent holds lapsing before capture.",
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
    "freshness": "2026-11-06T03:04Z",
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
