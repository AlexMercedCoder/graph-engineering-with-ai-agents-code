# Staging payment captures failing with E4021

## Change

`config/staging/payments.conf`: `AUTH_HOLD_MINUTES` changed from `10` to `60`. Nothing else changed.

## Why

- E4021 means "Payment authorization expired". It happens when the authorization hold runs out before the capture (`lookup_error_code('E4021')`).
- The payments schema says `AUTH_HOLD_MINUTES` must be larger than `CAPTURE_DELAY_MINUTES`, "or holds lapse before capture" (`get_config_schema('payments')`).
- Staging had `CAPTURE_DELAY_MINUTES=15` and `AUTH_HOLD_MINUTES=10`. The capture worker waited 15 minutes, but the hold ran out at 10, so every delayed capture hit E4021.
- `CAPTURE_DELAY_MINUTES=15` is the schema default. `AUTH_HOLD_MINUTES=10` was the only value that differed from its default (60). I set it back to 60, which makes the hold longer than the delay again.

## Things I didn't change, and caveats

- No other keys changed. `PAYMENT_BASE_URL`, `PROVIDER_REGION`, `CAPTURE_TIMEOUT` and `MAX_CAPTURE_RETRIES` are all valid under the schema, and no evidence ties them to E4021. Raising `MAX_CAPTURE_RETRIES` would not help: E4021 is not retryable. The documented fix is to re-authorize and then capture.
- The link between these staging values and the E4021 failures is an inference from the schema rule. No staging logs were checked.
- The docs search (vector search, so it may not have found everything) turned up no documented staging-specific values for payments. So 60 rests on the schema default, not on a staging spec. If the sandbox provider really holds authorizations for less than 15 minutes, lowering `CAPTURE_DELAY_MINUTES` below the real hold would be the right fix instead.
- Authorizations that have already expired still need to be re-authorized before they can be captured.

## Evidence

```json
[
  {"schema_version":1,"claim":"E4021 is the payment error 'Payment authorization expired'.","status":"found","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"E4021 is caused by the authorization hold lapsing before capture.","status":"found","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"E4021 handling is to re-authorize, then capture, and not to retry capture alone.","status":"found","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"E4021 is not retryable (Retryable: False).","status":"found","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"CAPTURE_DELAY_MINUTES is an optional integer defaulting to 15, giving the minutes after authorization at which the capture worker captures.","status":"found","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"AUTH_HOLD_MINUTES is an optional integer defaulting to 60, giving the minutes the provider holds an authorization; it must exceed CAPTURE_DELAY_MINUTES or holds lapse before capture.","status":"found","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"MAX_CAPTURE_RETRIES is an optional integer defaulting to 4, giving the capture retries on retryable provider errors.","status":"found","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"claim":"The supplied staging value CAPTURE_DELAY_MINUTES=15 is not less than the supplied staging value AUTH_HOLD_MINUTES=10, which violates the schema constraint that AUTH_HOLD_MINUTES must exceed CAPTURE_DELAY_MINUTES.","status":"found","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":["Staging values were supplied by the user, not retrieved from a source; the comparison is derived from the schema constraint.","The schema states holds lapse before capture when this constraint fails; this links the staging values to the E4021 cause but is an inference."]},
  {"schema_version":1,"claim":"No retrieved architecture document states an expected staging value for any payments config key.","status":"found","source":{"path":"vector","identifier":"search_docs('staging environment configuration for payments service sandbox endpoint', k=3)"},"confidence":"medium","coverage":"unknown","cost_tokens":144,"freshness":"2026-11-04T02:09Z","caveats":["Similarity search cannot confirm completeness; the staging values in the user's question could not be checked against a documented expectation."]}
]
```
