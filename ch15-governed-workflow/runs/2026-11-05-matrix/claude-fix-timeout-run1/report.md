# E4021 payment capture failures: production payments configuration

## Outcome

**Nothing changed.** The proposed production change expired before anyone reviewed it.

- Environment: production
- Service: payments
- Proposed change: `AUTH_HOLD_MINUTES` 10 → 60
- Gate outcome: **expired**. No reviewer decided within 90 seconds, so nothing was applied. A late approval will not apply it.
- Request id: `apr_e19c7cfd0a37`
- Reviewer reason: none (no decision was made)

## Cause

- E4021 means the payment authorization expired because the hold lapsed before capture. It is not retryable. (`lookup_error_code('E4021')`)
- In production, `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15`. The capture worker runs 5 minutes after the hold has already lapsed. (`read_config('production', 'payments')`)
- The schema requires `AUTH_HOLD_MINUTES` to be greater than `CAPTURE_DELAY_MINUTES`. Its documented default is 60. (`get_config_schema('payments')`)

## Proposed fix

Set `AUTH_HOLD_MINUTES=60`, the documented default. This satisfies the rule (60 > 15).

Impact: the graph says `AUTH_HOLD_MINUTES` configures RenewalsWorker, which controls how long renewal authorizations are held. Nothing depends on RenewalsWorker within 2 hops. (`trace_configuration('AUTH_HOLD_MINUTES')`, `find_dependents('RenewalsWorker')`)

Alternatives rejected:
- Lowering `CAPTURE_DELAY_MINUTES`: no documented value supports it.
- Retrying captures: E4021 is not retryable.

## Next step

Someone needs to re-request the change, with a reviewer ready to approve it. I did not resubmit it.

## Evidence

```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means the payment authorization expired: the authorization hold lapsed before capture. Not retryable.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"payments AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold lapses 5 minutes before the capture worker runs.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T02:43Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"AUTH_HOLD_MINUTES configures RenewalsWorker (how long a renewal authorization is held before capture); nothing depends on RenewalsWorker within 2 hops.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}
]
```
