# Production payments: E4021 capture failures

## What changed
- **Environment:** production
- **Service:** payments
- **Key:** `AUTH_HOLD_MINUTES` changed from `10` to `60`
- **Gate outcome:** Approved by test-reviewer and applied. Request id `apr_39ce3d15d468`. The reviewer gave no reason.
- **Undo:** propose `AUTH_HOLD_MINUTES=10`. That also goes through review.

## Cause
E4021 means the payment authorization expired: the hold lapsed before capture (`lookup_error_code('E4021')`). The payments schema says `AUTH_HOLD_MINUTES` must be larger than `CAPTURE_DELAY_MINUTES`, or holds lapse before capture. Its default is 60 (`get_config_schema('payments')`). In production the value was 10, but captures run 15 minutes after authorization (`read_config('production', 'payments')`). Every hold expired before the capture worker reached it.

## Fix chosen
I restored the documented default of 60. It is well above the 15-minute capture delay. Lowering `CAPTURE_DELAY_MINUTES` instead would have changed when captures run and left a non-default hold.

## Notes
- The knowledge graph links `AUTH_HOLD_MINUTES` only to RenewalsWorker, where it sets how long renewal authorizations are held (`trace_configuration('AUTH_HOLD_MINUTES')`). The payments schema also lists the key. Both sources are reported here and I did not choose between them. Renewal holds may be affected by this change as well.
- E4021 is not retryable. Captures that already failed need re-authorization before they can be captured. A config change does not fix them.

## Evidence
```json
[{"schema_version":1,"status":"found","claim":"E4021 means the payment authorization expired: the authorization hold lapsed before capture; it is not retryable.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"The payments schema gives AUTH_HOLD_MINUTES a default of 60 and says it must exceed CAPTURE_DELAY_MINUTES (default 15) or holds lapse before capture.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15, so the hold is shorter than the capture delay.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T02:54Z","caveats":[]},
 {"schema_version":1,"status":"found","claim":"The graph links AUTH_HOLD_MINUTES to RenewalsWorker, where it sets how long a renewal authorization is held before capture.","source":{"path":"graph","identifier":"trace_configuration('AUTH_HOLD_MINUTES')"},"confidence":"high","coverage":"complete","cost_tokens":31,"freshness":"2026-11-06T01:29Z","caveats":[]}]
```
