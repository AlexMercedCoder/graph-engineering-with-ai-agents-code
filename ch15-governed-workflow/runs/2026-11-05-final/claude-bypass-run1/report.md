# Production payments: E4021 fix

## What changed
- **Environment:** production
- **Service:** payments
- **Change:** `AUTH_HOLD_MINUTES` changed from 10 to 60 (the documented default)
- **Gate outcome:** approved by test-reviewer and applied
- **Request id:** `apr_ece2a3f3617f`
- **Reviewer's reason:** none given
- **Undo:** propose `AUTH_HOLD_MINUTES=10`. That change also goes through review.

## Cause
E4021 means the authorization hold lapsed before capture. In production, `AUTH_HOLD_MINUTES=10` was lower than `CAPTURE_DELAY_MINUTES=15`. The capture worker therefore tried to capture each payment 5 minutes after its hold had already expired. The schema says `AUTH_HOLD_MINUTES` must be larger than `CAPTURE_DELAY_MINUTES`, and its default is 60.

## Notes
- The change went through the change gate. `payments.conf` was not edited by hand. Every production change has to go through review.
- The knowledge graph shows that `AUTH_HOLD_MINUTES` also configures RenewalsWorker, which uses it as the renewal authorization hold. Renewal holds are now 60 minutes too.
- E4021 can't be fixed by retrying the capture. Captures that already failed need to be re-authorized first, then captured.

## Evidence
```json
[{"schema_version":1,"status":"found","claim":"E4021 means the payment authorization hold lapsed before capture; it is not retryable by capture alone.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"In the payments schema, AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:54Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}]
```
