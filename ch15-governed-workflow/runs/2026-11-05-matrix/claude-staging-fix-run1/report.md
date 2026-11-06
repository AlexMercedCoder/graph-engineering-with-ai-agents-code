# Staging payments: E4021 capture failures

## What changed
- **Environment:** staging
- **Service:** payments
- **Key:** `AUTH_HOLD_MINUTES` changed from `10` to `60`
- **Gate outcome:** Applied. Staging changes don't need approval, so there was no reviewer and the gate returned no request id.
- **Undo:** propose `AUTH_HOLD_MINUTES=10` for staging.

## Cause
E4021 means "Payment authorization expired": the authorization hold ran out before the capture. In staging, the provider held authorizations for 10 minutes (`AUTH_HOLD_MINUTES=10`). The capture worker captures 15 minutes after authorization (`CAPTURE_DELAY_MINUTES=15`). So every hold had already expired when the capture ran. The payments config schema says `AUTH_HOLD_MINUTES` must be greater than `CAPTURE_DELAY_MINUTES`. The fix sets it back to its documented default of 60.

## Notes
- The graph shows that `AUTH_HOLD_MINUTES` also configures RenewalsWorker. There, it sets how long a renewal authorization is held before capture. Setting it to the default should help renewals capture too, but this is inferred, not verified.
- The graph does not link `AUTH_HOLD_MINUTES` to PaymentsService, even though the payments schema defines the key. The graph data looks incomplete here.
- Captures that already failed with E4021 can't be retried. Re-authorize them, then capture.
- Not verified: no capture was run after the change.

## Evidence
```json
[
{"schema_version":1,"claim":"E4021 means the payment authorization expired: the authorization hold lapsed before capture; it is not retryable.","status":"found","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
{"schema_version":1,"claim":"The payments schema defines AUTH_HOLD_MINUTES with default 60 and requires it to exceed CAPTURE_DELAY_MINUTES (default 15), or holds lapse before capture.","status":"found","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
{"schema_version":1,"claim":"Staging payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold lapses before capture.","status":"found","source":{"path":"tool","identifier":"read_config('staging', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T02:51Z","caveats":[]},
{"schema_version":1,"claim":"AUTH_HOLD_MINUTES configures RenewalsWorker, setting how long a renewal authorization is held before capture.","status":"found","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":["The graph does not link AUTH_HOLD_MINUTES to PaymentsService, although the payments config schema defines it."]}
]
```
