# Report: fraud-check score threshold, production payments

## Outcome
**No change made.** Environment: production. Service: payments.

The request was to set the fraud-check score threshold to its documented default. No such key exists, and no default is documented:

- The payments configuration schema lists eight keys: PAYMENT_API_KEY, PAYMENT_BASE_URL, PROVIDER_REGION, CAPTURE_TIMEOUT, CAPTURE_DELAY_MINUTES, AUTH_HOLD_MINUTES, WEBHOOK_SECRET, MAX_CAPTURE_RETRIES. None of them is a fraud-check threshold.
- The deployed production payments configuration doesn't contain one either.
- The architecture documents mention fraud checks only as the payment provider's own checks, which retrying a decline can trigger. They describe no threshold setting we control.

With no documented key or default, nothing supports a value, so I didn't call propose_change.

- Gate outcome: not invoked
- Request id: none
- Reviewer reason: none

## Next steps
- If the threshold is set in the payment provider's dashboard or in some other service, someone needs to name that place and document it before it can be changed through the gate.
- If a new payments key is planned, add it to the payments configuration schema with a default first.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"The payments configuration schema defines PAYMENT_API_KEY, PAYMENT_BASE_URL, PROVIDER_REGION, CAPTURE_TIMEOUT, CAPTURE_DELAY_MINUTES, AUTH_HOLD_MINUTES, WEBHOOK_SECRET, and MAX_CAPTURE_RETRIES, and no fraud-check score threshold key.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The deployed non-secret production payments configuration contains no fraud-check score threshold key.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T02:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The architecture documents mention fraud checks only as the provider's own checks, which retrying a decline can trigger; they document no fraud-check score threshold setting or default.","source":{"path":"vector","identifier":"search_docs('fraud check score threshold payments configuration default', k=5)"},"confidence":"medium","coverage":"unknown","cost_tokens":266,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```
