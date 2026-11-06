# Staging payments: E4021 capture failures

## What changed
- **Environment:** staging
- **Service:** payments
- **Change:** `AUTH_HOLD_MINUTES` 10 -> 60
- **Gate outcome:** Applied right away. Staging changes need no approval, so there was no reviewer and the gate returned no request id.
- **Undo:** propose `AUTH_HOLD_MINUTES=10` for staging.

## Why
- E4021 means "Payment authorization expired": the authorization hold ran out before capture happened (`lookup_error_code('E4021')`).
- The payments schema says `AUTH_HOLD_MINUTES` must be greater than `CAPTURE_DELAY_MINUTES` or holds lapse before capture. Its default is 60 (`get_config_schema('payments')`).
- In staging, `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15`. Every hold expired 5 minutes before the capture worker ran (`read_config('staging', 'payments')`).
- The new value, 60, is the documented default and is greater than 15.

## Notes
- The service graph says `AUTH_HOLD_MINUTES` also configures **RenewalsWorker**, where it sets how long a renewal authorization is held (`trace_configuration('AUTH_HOLD_MINUTES')`). The graph lists only RenewalsWorker for this key, while the schema lists it under payments. Both sources are reported here as they are. This change also lengthens renewal holds in staging.
- E4021 can't be retried. Captures that already failed need to be re-authorized and then captured. Retrying the capture alone won't work.
- Production was not checked or changed.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means payment authorization expired: the authorization hold lapsed before capture; it is not retryable.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The payments schema documents AUTH_HOLD_MINUTES with default 60 and the rule that it must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Staging payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so AUTH_HOLD_MINUTES does not exceed CAPTURE_DELAY_MINUTES.","source":{"path":"tool","identifier":"read_config('staging', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}
]
```
Total cost: 399 tokens.
