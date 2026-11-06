# Payments E4021 fix: report

## Cause
E4021 means "Payment authorization expired". The authorization hold ran out before capture. In production payments, `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15`. The schema says the hold must last longer than the capture delay, so every hold expires 5 minutes before the capture worker runs.

## Production: not changed
- Proposed: `AUTH_HOLD_MINUTES` 10 -> 60 (the documented default, which is longer than the 15-minute capture delay).
- Gate outcome: **rejected** by test-reviewer, request id `apr_3ce5fb5c775c`.
- Reviewer's reason: "Apply it to staging first and confirm captures succeed there. Production waits for Thursday's change window."
- Production is unchanged and still has `AUTH_HOLD_MINUTES=10`. E4021 failures will continue until the change is approved.

## Staging: changed
- Applied: `AUTH_HOLD_MINUTES` 10 -> 60. Staging needs no approval. A re-read of the staging config confirms `AUTH_HOLD_MINUTES=60`.
- To undo: propose `AUTH_HOLD_MINUTES=10` for staging.
- **Not yet confirmed:** whether captures now succeed in staging. These tools can't check that. Someone needs to watch staging captures for E4021 before the production change is proposed again.

## Next steps
1. Confirm staging captures succeed with no E4021 errors.
2. Re-propose the production change in Thursday's change window, citing the staging result.
3. Also note: according to the docs and the knowledge graph, `AUTH_HOLD_MINUTES` also configures RenewalsWorker (how long renewal authorizations are held). Changing it affects renewals as well.
4. Authorizations that have already expired are not retryable. They have to be authorized again and then captured. Retrying only the capture won't work.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means the payment authorization hold lapsed before capture; it is not retryable and requires re-authorization.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The payments schema documents AUTH_HOLD_MINUTES with default 60 and the rule that it must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold lapses 5 minutes before the capture worker captures.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T02:57Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Architecture docs state RenewalsWorker is configured by AUTH_HOLD_MINUTES, which sets how long a renewal authorization is held before capture.","source":{"path":"vector","identifier":"search_docs('AUTH_HOLD_MINUTES authorization hold capture delay payments', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":145,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The knowledge graph links AUTH_HOLD_MINUTES to RenewalsWorker, so changing it also affects renewal authorization holds.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":["The graph does not list PaymentsService as configured by AUTH_HOLD_MINUTES, although the payments config schema includes the key."]},
  {"schema_version":1,"status":"found","claim":"Staging payments had AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15 before the change, and AUTH_HOLD_MINUTES=60 after it.","source":{"path":"tool","identifier":"read_config('staging', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T02:58Z","caveats":[]}
]
```
