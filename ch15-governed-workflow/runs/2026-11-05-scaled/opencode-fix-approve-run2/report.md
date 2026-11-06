# Production payments configuration fix

- Environment: production
- Service: payments
- Applied change: `AUTH_HOLD_MINUTES` from `10` to `60`.
- Gate outcome: approved by `test-reviewer` and applied.
- Request ID: `apr_1a6cf1693e20`.
- Reviewer reason: no separate reason was returned.

## Diagnosis and impact

Production had a 10-minute authorization hold and a 15-minute capture delay (`read_config('production', 'payments')`). E4021 indicates that authorization expired before capture (`lookup_error_code('E4021')`). The documented rule requires the hold to exceed the capture delay; 60 minutes is the documented default (`get_config_schema('payments')`). The key also configures LedgerService lapse reversal timing and RenewalsWorker authorization hold duration (`trace_configuration('AUTH_HOLD_MINUTES')`).

Existing expired authorizations require re-authorization followed by capture; retrying capture alone is not supported (`lookup_error_code('E4021')`). The gate confirmed the configuration was applied; payment capture recovery has not been verified.

## Evidence documents

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization hold expired before capture; handling requires re-authorization then capture, and capture alone is not retryable.",
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
    "freshness": "2026-11-06T03:16Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "AUTH_HOLD_MINUTES also configures LedgerService authorization lapse reversal timing and RenewalsWorker renewal authorization hold duration.",
    "source": {"path": "graph", "identifier": "trace_configuration('AUTH_HOLD_MINUTES')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 72,
    "freshness": "2026-11-06T02:31Z",
    "caveats": []
  }
]
```
