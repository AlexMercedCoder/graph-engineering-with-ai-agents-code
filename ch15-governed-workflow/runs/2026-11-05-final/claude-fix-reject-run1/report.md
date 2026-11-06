# Payments E4021 fix: AUTH_HOLD_MINUTES

## Cause
E4021 means "Payment authorization expired": the authorization hold ran out before capture (`lookup_error_code('E4021')`).
In production payments, `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15` (`read_config('production', 'payments')`).
The schema says `AUTH_HOLD_MINUTES` must be greater than `CAPTURE_DELAY_MINUTES`, or holds run out before capture. Its documented default is 60 (`get_config_schema('payments')`).
So every hold expires 5 minutes before the capture worker runs.

## What changed
| Environment | Change | Gate outcome | Request id |
|---|---|---|---|
| production | AUTH_HOLD_MINUTES 10 -> 60 (proposed) | **Rejected** by test-reviewer. Nothing applied. | apr_60369cce95d0 |
| staging | AUTH_HOLD_MINUTES 10 -> 60 | **Applied** (no approval needed) | n/a |

Reviewer's reason: "Apply it to staging first and confirm captures succeed there. Production waits for Thursday's change window."

## Still open
- **Production is unchanged.** Captures there will keep failing with E4021 until the change goes in during Thursday's change window. I did not propose it again.
- **Not yet confirmed in staging.** None of the available tools can check whether staging captures now succeed. Someone needs to check that before the production change is proposed again.
- **Blast radius:** `AUTH_HOLD_MINUTES` also configures RenewalsWorker, which uses it for renewal authorization holds (`trace_configuration('AUTH_HOLD_MINUTES')`). The RenewalsWorker information comes from the closest documents vector search found, so its coverage is unknown.
- Captures that already failed with E4021 need to be re-authorized and then captured. Retrying the capture alone won't work (E4021 can't be retried).
- To undo the staging change: propose `AUTH_HOLD_MINUTES=10` for staging.

## Evidence
```json
[
{"schema_version":1,"status":"found","claim":"E4021 means the payment authorization hold lapsed before capture; handling is re-authorize then capture, and it is not retryable.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
{"schema_version":1,"status":"found","claim":"The payments schema documents AUTH_HOLD_MINUTES with default 60 and the rule that it must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
{"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold is shorter than the capture delay.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:47Z","caveats":[]},
{"schema_version":1,"status":"found","claim":"Staging payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold is shorter than the capture delay.","source":{"path":"tool","identifier":"read_config('staging', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:47Z","caveats":[]},
{"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES also configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]},
{"schema_version":1,"status":"found","claim":"The RenewalsWorker configuration doc states it is configured by AUTH_HOLD_MINUTES for renewal authorization holds.","source":{"path":"vector","identifier":"search_docs('AUTH_HOLD_MINUTES authorization hold capture delay payments', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":145,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```
