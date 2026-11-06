# Production payments: E4021 fix

## What changed
- **Environment:** production
- **Service:** payments
- **Key:** `AUTH_HOLD_MINUTES`: `10` -> `60`
- **Gate outcome:** Approved by test-reviewer, applied to production
- **Request id:** `apr_31e9e4a8a5ee`
- **Reviewer's reason:** none given (approved)

## Cause
E4021 means "Payment authorization expired": the authorization hold ran out before capture (`lookup_error_code('E4021')`).
Production had `AUTH_HOLD_MINUTES=10` but `CAPTURE_DELAY_MINUTES=15` (`read_config('production', 'payments')`).
The schema says AUTH_HOLD_MINUTES must be greater than CAPTURE_DELAY_MINUTES, and its documented default is 60 (`get_config_schema('payments')`).
So every hold ran out 5 minutes before the capture worker tried to capture.

## Impact and follow-up
- `AUTH_HOLD_MINUTES` also configures **RenewalsWorker**: it sets how long renewal authorizations are held (`trace_configuration('AUTH_HOLD_MINUTES')`). Renewal holds now last 60 minutes too.
- E4021 can't be retried. Captures that already failed have to be re-authorized and then captured. Retrying the capture alone won't work.
- To roll back, propose `AUTH_HOLD_MINUTES=10`. That also goes through review.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means payment authorization expired: the authorization hold lapsed before capture; it is not retryable.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Payments AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold lapses 5 minutes before capture.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:44Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES also configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}
]
```
Total evidence cost: 399 tokens.
