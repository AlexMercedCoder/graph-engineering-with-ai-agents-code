# Production payments configuration change

## Outcome

No production configuration was changed. Request `apr_0e93846731d4` expired because no reviewer decided within 90 seconds. No reviewer reason was returned. A late approval will not apply the change; a new request requires the user to ask. The change still needs review through a new request.

## Diagnosis and proposed fix

Production payments has `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15` (`read_config('production', 'payments')`). This violates the documented rule that the authorization hold must exceed the capture delay. The proposed change was `AUTH_HOLD_MINUTES: 10 → 60`, the documented default (`get_config_schema('payments')`).

E4021 means authorization expired before capture. Existing expired authorizations require re-authorization followed by capture; capture alone must not be retried (`lookup_error_code('E4021')`). The configuration graph identifies RenewalsWorker as configured by this key (`trace_configuration('AUTH_HOLD_MINUTES')`).

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
    "freshness": "2026-11-06T02:46Z",
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
