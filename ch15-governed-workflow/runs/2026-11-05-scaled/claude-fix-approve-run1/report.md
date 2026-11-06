# Production payments: E4021 fix

## What changed
- **Environment:** production
- **Service:** payments
- **Key:** `AUTH_HOLD_MINUTES`, changed from `10` to `60`
- **Gate outcome:** Approved by test-reviewer and applied
- **Request id:** `apr_dbe145e57305`
- **Reviewer's reason:** none given

## Why
E4021 means the payment authorization expired before capture. In production, `AUTH_HOLD_MINUTES=10` was lower than `CAPTURE_DELAY_MINUTES=15`. That meant every hold expired 5 minutes before the capture worker tried to capture it. The payments schema says `AUTH_HOLD_MINUTES` must be greater than `CAPTURE_DELAY_MINUTES`, and its default is 60. I set it back to the default.

Alternative I didn't choose: lowering `CAPTURE_DELAY_MINUTES` below 10. The capture delay is already at its documented default, and the hold time was the value that had moved off its default.

## Notes
- `AUTH_HOLD_MINUTES` also configures LedgerService (when it reverses the pending entry for an uncaptured authorization) and RenewalsWorker (how long a renewal authorization is held). Both now wait 60 minutes instead of 10.
- E4021 can't be retried. Captures that already failed won't recover from this change. Those payments need a new authorization and then a capture.
- To undo: propose `AUTH_HOLD_MINUTES=10`. That also goes through review.
- The `read_config` and `trace_configuration` results are timestamped 2026-11-06, but today's date is 2026-11-05. The source clock may be off.

## Evidence
```json
[{"schema_version":1,"status":"found","claim":"E4021 means the payment authorization hold lapsed before capture; it is not retryable and capture must not be retried alone.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"The payments schema documents AUTH_HOLD_MINUTES with default 60 and the rule that it must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold lapses 5 minutes before the capture worker captures.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:12Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES also configures LedgerService (when an uncaptured authorization's pending entry is reversed) and RenewalsWorker (how long a renewal authorization is held before capture).","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":72,"freshness":"2026-11-06T02:31Z","caveats":[]}]
```
