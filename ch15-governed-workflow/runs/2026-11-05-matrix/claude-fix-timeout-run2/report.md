# Production payments: E4021 capture failures

## Outcome
**Nothing changed.** I proposed a change to **production** `payments`: set `AUTH_HOLD_MINUTES` from `10` to `60`. No reviewer decided within 90 seconds, so gate request **`apr_aec0997973d4` expired** and was not applied. A late approval won't apply it. There was no reviewer decision and no reason given. Per the change-config skill, I did not resubmit it.

## Cause
- E4021 means "Payment authorization expired": the authorization hold ran out before the capture happened, and the error is not retryable (`lookup_error_code('E4021')`).
- The schema says `AUTH_HOLD_MINUTES` defaults to 60 and must exceed `CAPTURE_DELAY_MINUTES`, or holds run out before capture (`get_config_schema('payments')`).
- Production has `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15` (`read_config('production', 'payments')`). The hold ends 5 minutes before the capture worker runs.

## Proposed fix
Set `AUTH_HOLD_MINUTES=60`, the documented default, which is above the 15-minute capture delay.

## Impact note
The service graph shows `AUTH_HOLD_MINUTES` also configures **RenewalsWorker** (how long a renewal authorization is held before capture) (`trace_configuration('AUTH_HOLD_MINUTES')`). The change would affect renewal holds as well.

## Notes
- The `read_config` freshness timestamp (2026-11-06T03:01Z) is later than today's date (2026-11-05).
- Payments already failed with E4021 won't recover from a config fix alone. Per the error handling, they need to be re-authorized and then captured. Retrying the capture alone won't work.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means the payment authorization expired: the authorization hold lapsed before capture; it is not retryable.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The payments AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:01Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}
]
```
