# Production payments: E4021 capture failures

## What changed
- **Environment:** production
- **Service:** payments
- **Key:** `AUTH_HOLD_MINUTES`, changed from 10 to **60**
- **Gate outcome:** Approved by test-reviewer and applied. The reviewer gave no reason.
- **Request id:** `apr_e36e545aa2e7`
- **Rollback:** propose `AUTH_HOLD_MINUTES=10`. That goes through review too.

## Cause
E4021 means "Payment authorization expired": the authorization hold ran out before capture (`lookup_error_code('E4021')`). In production, `AUTH_HOLD_MINUTES=10` was lower than `CAPTURE_DELAY_MINUTES=15` (`read_config('production', 'payments')`). The schema requires `AUTH_HOLD_MINUTES` to be greater than `CAPTURE_DELAY_MINUTES` and gives 60 as the default (`get_config_schema('payments')`). The new value is that default.

## Side effects to watch
`AUTH_HOLD_MINUTES` also configures two other services (`trace_configuration('AUTH_HOLD_MINUTES')`):
- **LedgerService:** reverses pending entries for uncaptured authorizations later than before (after 60 minutes instead of 10).
- **RenewalsWorker:** holds renewal authorizations for 60 minutes before capture.

## Follow-up
E4021 is not retryable. Captures that already failed won't recover from this change alone. Each one has to be re-authorized and then captured. Retrying the capture by itself won't work.

## Evidence
```json
[{"schema_version":1,"status":"found","claim":"E4021 means the payment authorization hold lapsed before capture; it is not retryable.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"The payments schema documents AUTH_HOLD_MINUTES with default 60 and the rule that it must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold is shorter than the capture delay.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:13Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES also configures LedgerService (when uncaptured authorizations lapse and pending entries are reversed) and RenewalsWorker (how long renewal authorizations are held before capture).","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":72,"freshness":"2026-11-06T02:31Z","caveats":[]}]
```
