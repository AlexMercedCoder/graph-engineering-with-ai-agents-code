# E4021 payment capture failures: configuration fix

## Cause
E4021 means the payment authorization expired because the hold ran out before capture (`lookup_error_code('E4021')`). The payments schema says `AUTH_HOLD_MINUTES` (default 60) must be greater than `CAPTURE_DELAY_MINUTES` (default 15), or holds expire before capture (`get_config_schema('payments')`). Production has `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15`, so each hold expires 5 minutes before the capture worker runs (`read_config('production', 'payments')`). Staging had the same values.

Blast radius: `AUTH_HOLD_MINUTES` also configures RenewalsWorker, where it sets how long renewal authorizations are held (`trace_configuration('AUTH_HOLD_MINUTES')`).

## Change proposed
`payments` / `AUTH_HOLD_MINUTES`: 10 → 60 (the documented default).

## Outcome
| Environment | Result | Request id |
|---|---|---|
| production | **Rejected** by test-reviewer. Nothing was applied. | apr_d07e372290be |
| staging | **Applied** (no approval needed). Re-read confirms `AUTH_HOLD_MINUTES=60`. | (none; staging applies at once) |

Reviewer's reason: "Apply it to staging first and confirm captures succeed there. Production waits for Thursday's change window."

**Production is still misconfigured and E4021 failures will continue.** Next steps:
1. Confirm that captures now succeed in staging. I can't do this with the available tools. Someone needs to run a capture that is authorized and then captured after the 15-minute delay.
2. Re-propose the production change in Thursday's change window.

To revert staging, propose `AUTH_HOLD_MINUTES=10` for staging.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means the payment authorization expired: the authorization hold lapsed before capture. Not retryable.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"payments AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold lapses 5 minutes before capture.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T02:40Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Staging payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, the same misconfiguration as production.","source":{"path":"tool","identifier":"read_config('staging', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T02:40Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES also configures RenewalsWorker, setting how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}
]
```
