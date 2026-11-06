# Staging E4021 fix — brief

## What changed

`config/staging/payments.conf`: `AUTH_HOLD_MINUTES` changed from `10` to `60`. Nothing else changed.

## Why

- E4021 means "Payment authorization expired". It happens when the authorization hold runs out before capture (`lookup_error_code('E4021')`, high confidence, complete coverage).
- The schema says `AUTH_HOLD_MINUTES` (default 60) **must exceed** `CAPTURE_DELAY_MINUTES`, or holds lapse before capture. `CAPTURE_DELAY_MINUTES` sets how many minutes after authorization the capture worker runs (default 15). Source: `get_config_schema('payments')`, high confidence, complete coverage.
- Staging had `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15`. Every hold expired 5 minutes before the worker tried to capture, which matches E4021 exactly.
- `60` is the documented default, and it is well above the 15-minute capture delay.

## What I deliberately did not change

- `MAX_CAPTURE_RETRIES`: E4021 is not retryable. The documented handling is to re-authorize and then capture, not to retry the capture alone. Raising retries would not help.
- `CAPTURE_TIMEOUT`, `PAYMENT_BASE_URL`, `PROVIDER_REGION`: no evidence ties them to E4021. The schema does not say which endpoint staging should use, so the sandbox URL was left as it is.
- Secrets (`PAYMENT_API_KEY`, `WEBHOOK_SECRET`) are not in this file and were not touched.

## Caveats

- The schema came back for service `payments`. The tool did not confirm that it maps to the file name `payments.conf`, and it returned no staging-specific overrides.
- After this config fix, captures that have already failed with E4021 still need to be re-authorized before they can be captured.
- An unrelated open conflict (vector search, unknown coverage, so these are the closest documents found and may not be complete): one document says order-service calls PaymentsAPI to capture, and another says billing-service owns capture. Both are reported here and neither was picked. The fix above does not depend on which one is right.

## Evidence relied on

```json
[
  {"schema_version":1,"claim":"E4021 is the code for 'Payment authorization expired'.","status":"found","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"E4021 is caused by the authorization hold lapsing before capture.","status":"found","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"The documented handling for E4021 is to re-authorize and then capture, and not to retry capture alone.","status":"found","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"E4021 is not retryable (Retryable: False).","status":"found","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"CAPTURE_DELAY_MINUTES is an optional integer that defaults to 15 and sets the minutes after authorization at which the capture worker captures.","status":"found","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":["Schema was returned for service 'payments'; the tool did not confirm the file name payments.conf.","No staging-specific value or override was returned."]},
  {"schema_version":1,"claim":"AUTH_HOLD_MINUTES is an optional integer that defaults to 60 and must exceed CAPTURE_DELAY_MINUTES, or holds lapse before capture.","status":"found","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":["Schema was returned for service 'payments'; the tool did not confirm the file name payments.conf.","No staging-specific value or override was returned; this window is the one tied to E4021."]},
  {"schema_version":1,"claim":"MAX_CAPTURE_RETRIES is an optional integer that defaults to 4 and sets the number of capture retries on retryable provider errors.","status":"found","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":["Schema was returned for service 'payments'; the tool did not confirm the file name payments.conf.","No staging-specific value or override was returned."]}
]
```
