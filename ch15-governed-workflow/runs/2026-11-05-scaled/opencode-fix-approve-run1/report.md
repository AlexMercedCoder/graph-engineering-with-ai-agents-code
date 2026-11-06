# Production payments configuration change

- Environment: production
- Service: payments
- Applied change: `AUTH_HOLD_MINUTES` from `10` to `60`.
- Gate outcome: approved by `test-reviewer` and applied.
- Request ID: `apr_fe8afdde24fd`.
- Reviewer reason: none provided.

## Findings

Production's 10-minute hold was shorter than its 15-minute capture delay (`read_config('production', 'payments')`). The schema requires the hold to exceed the capture delay and documents a 60-minute default (`get_config_schema('payments')`). E4021 indicates authorization expiration; affected payments require re-authorization followed by capture, rather than retrying capture alone (`lookup_error_code('E4021')`).

The configuration graph also identifies LedgerService lapse reversal timing and RenewalsWorker renewal authorization hold timing as consumers of this key (`trace_configuration('AUTH_HOLD_MINUTES')`). These impacts were included in the review evidence.

The gate confirmed application of the configuration change. Successful payment capture after the change has not been verified.

## Validated evidence

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization expired before capture; recovery requires re-authorization followed by capture, and capture alone must not be retried.",
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
    "claim": "Payments AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES to prevent authorizations lapsing before capture.",
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
    "freshness": "2026-11-06T03:14Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "AUTH_HOLD_MINUTES also configures LedgerService authorization lapse reversal timing and RenewalsWorker renewal authorization hold timing.",
    "source": {"path": "graph", "identifier": "trace_configuration('AUTH_HOLD_MINUTES')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 72,
    "freshness": "2026-11-06T02:31Z",
    "caveats": []
  }
]
```
