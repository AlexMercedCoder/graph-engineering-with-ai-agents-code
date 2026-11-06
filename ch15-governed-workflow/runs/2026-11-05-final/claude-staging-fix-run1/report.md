# Staging payments: E4021 fix

## What changed
- **Environment:** staging
- **Service:** payments
- **Key:** `AUTH_HOLD_MINUTES`, changed from `10` to `60`

## Why
E4021 means the payment authorization expired: the hold ran out before capture (`lookup_error_code('E4021')`).
In staging, `AUTH_HOLD_MINUTES=10` was lower than `CAPTURE_DELAY_MINUTES=15` (`read_config('staging', 'payments')`).
So every hold ran out 5 minutes before the capture worker tried to capture.
The schema requires `AUTH_HOLD_MINUTES` to be greater than `CAPTURE_DELAY_MINUTES`, and its documented default is 60 (`get_config_schema('payments')`).
The new value is that default.

## Gate outcome
- Applied right away. Staging changes don't need approval, so there was no reviewer and no reason to report.
- The gate returned no request id.
- Checked afterwards: `read_config('staging', 'payments')` now shows `AUTH_HOLD_MINUTES=60`.
- To undo: propose `AUTH_HOLD_MINUTES=10` for staging.

## Notes
- The knowledge graph shows that `AUTH_HOLD_MINUTES` also configures **RenewalsWorker**: it sets how long renewal authorizations are held before capture (`trace_configuration('AUTH_HOLD_MINUTES')`). With this change, staging renewal holds also last 60 minutes.
- E4021 can't be retried. Captures that already failed with it need a new authorization and then a capture. Retrying the capture alone won't work.
- Production was not checked or changed.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means the payment authorization expired: the authorization hold lapsed before capture; not retryable, re-authorize then capture.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Payments AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Staging payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold is shorter than the capture delay.","source":{"path":"tool","identifier":"read_config('staging', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:51Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}
]
```
