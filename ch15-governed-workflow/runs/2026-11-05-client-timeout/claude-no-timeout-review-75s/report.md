# Production payments: E4021 capture failures

## What changed
- **Environment:** production
- **Service:** payments
- **Key:** `AUTH_HOLD_MINUTES`: `10` → `60`
- **Gate outcome:** Approved by test-reviewer and applied.
- **Request id:** `apr_b62f317a34e0`
- **Reviewer's reason:** None given (approved).
- **Undo:** propose `AUTH_HOLD_MINUTES=10`. That also goes through review.

## Why
- E4021 means "Payment authorization expired": the authorization hold ran out before capture (`lookup_error_code('E4021')`).
- The payments schema sets `AUTH_HOLD_MINUTES` to 60 by default. It must be greater than `CAPTURE_DELAY_MINUTES`, or holds run out before capture (`get_config_schema('payments')`).
- In production, `AUTH_HOLD_MINUTES` was 10 and `CAPTURE_DELAY_MINUTES` was 15. Every hold therefore ran out 5 minutes before the capture worker ran (`read_config('production', 'payments')`).
- The fix restores the documented default (60), which is greater than the 15-minute capture delay.

## Notes
- The service graph shows `AUTH_HOLD_MINUTES` configuring **RenewalsWorker** (renewal authorization holds) (`trace_configuration('AUTH_HOLD_MINUTES')`). The graph does not list payments for this key, but the payments schema does. Both sources are reported as they are. Renewal holds now last 60 minutes too.
- E4021 can't be fixed by retrying capture alone. Payments that already failed need to be authorized again, then captured. This config change only prevents new failures.

## Evidence
```json
[{"schema_version":1,"status":"found","claim":"E4021 means the payment authorization expired: the authorization hold lapsed before capture; it is not retryable by capture alone.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"The payments schema sets AUTH_HOLD_MINUTES default 60 and requires it to exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold is shorter than the capture delay.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:20Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}]
```
