# Staging payments configuration fix

## Outcome

- Environment: staging; service: payments.
- Changed `AUTH_HOLD_MINUTES` from `10` to `60`, its documented default.
- Gate outcome: applied immediately; staging needs no approval.
- Request ID: not returned by the gate.
- Reviewer reason: no reviewer required.
- Verified by reading deployed configuration after the change: authorization hold is 60 minutes and capture delay is 15 minutes (`read_config('staging', 'payments')`, freshness `2026-11-06T02:53Z`). No capture transaction was executed as part of verification.

## Diagnosis

E4021 means an authorization expired before capture; expired authorizations require re-authorization, then capture, rather than retrying capture alone (`lookup_error_code('E4021')`). Before the change, the staging authorization hold was 10 minutes and capture delay was 15 minutes (`read_config('staging', 'payments')`, freshness `2026-11-06T02:52Z`). The schema requires the hold to exceed the capture delay and documents a default of 60 minutes (`get_config_schema('payments')`). The configuration graph identifies RenewalsWorker as configured by this key (`trace_configuration('AUTH_HOLD_MINUTES')`).

## Validated evidence

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization hold expired before capture; handling requires re-authorization followed by capture, not retrying capture alone.",
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
    "claim": "AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES to prevent authorization holds lapsing before capture.",
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
    "freshness": "2026-11-06T02:52Z",
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
    "claim": "After the change, staging payments has AUTH_HOLD_MINUTES=60 and CAPTURE_DELAY_MINUTES=15.",
    "source": {"path": "tool", "identifier": "read_config('staging', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T02:53Z",
    "caveats": []
  }
]
```
