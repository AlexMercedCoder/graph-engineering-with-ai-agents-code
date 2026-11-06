# Production payments: E4021 capture failures

## What changed
- **Environment:** production
- **Service:** payments
- **Key:** `AUTH_HOLD_MINUTES`: `10` -> `60`
- **Gate outcome:** Approved by test-reviewer and applied
- **Request id:** `apr_acaaff5d057e`
- **Reviewer's reason:** none given

## Cause
E4021 means the authorization hold expired before capture (`lookup_error_code('E4021')`). In production, `AUTH_HOLD_MINUTES=10` was lower than `CAPTURE_DELAY_MINUTES=15` (`read_config('production', 'payments')`). The capture worker therefore ran after every hold had already expired. The payments schema says `AUTH_HOLD_MINUTES` must be greater than `CAPTURE_DELAY_MINUTES` and sets its default to 60 (`get_config_schema('payments')`). The new value is that default.

## Side effect
`AUTH_HOLD_MINUTES` also configures RenewalsWorker (`trace_configuration('AUTH_HOLD_MINUTES')`), so renewal authorizations are now also held for 60 minutes.

## Follow-up
E4021 is not retryable. Captures that already failed won't succeed if retried alone. Each one must be re-authorized and then captured.

## Rollback
Propose `AUTH_HOLD_MINUTES=10`. That change also goes through review.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means the payment authorization hold lapsed before capture; it is not retryable and capture alone must not be retried.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The payments schema sets AUTH_HOLD_MINUTES default to 60 and requires it to exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold is shorter than the capture delay.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T02:38Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES also configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}
]
```
