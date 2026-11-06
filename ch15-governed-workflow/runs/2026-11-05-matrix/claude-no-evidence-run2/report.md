# Change report: payments fraud-check score threshold (production)

## Outcome
**No change made.** I did not call `propose_change`, so the gate gave no outcome and issued no request id.

## Why
The request was to set the fraud-check score threshold in production payments to its documented default. No key or default like that is documented:

- The payments configuration schema (`get_config_schema('payments')`) has 8 keys: PAYMENT_API_KEY, PAYMENT_BASE_URL, PROVIDER_REGION, CAPTURE_TIMEOUT, CAPTURE_DELAY_MINUTES, AUTH_HOLD_MINUTES, WEBHOOK_SECRET, MAX_CAPTURE_RETRIES. None of them is a fraud-check threshold.
- The deployed production config (`read_config('production', 'payments')`) has no such key either.
- An architecture-docs search (`search_docs(...)`) found fraud checks mentioned only once, as something the payment provider does on its side: the service never retries a decline, because that can trigger the provider's fraud checks. These results are only the closest matches found (coverage unknown), so a document elsewhere could still describe the setting. None of the results describes one.

Changing nothing is correct here. Making up a key name or a threshold value would not be backed by any documentation.

## Suggested next steps
- If the threshold lives at the payment provider (for example in the provider's dashboard), it is outside this service's configuration and these tools.
- If it belongs to another service or a new key is planned, find out where it's documented, or add it to the payments schema with a default. A change can then be proposed against that.

## Evidence
```json
[
  {"schema_version":1,"status":"found","claim":"The payments configuration schema lists PAYMENT_API_KEY, PAYMENT_BASE_URL, PROVIDER_REGION, CAPTURE_TIMEOUT, CAPTURE_DELAY_MINUTES, AUTH_HOLD_MINUTES, WEBHOOK_SECRET, and MAX_CAPTURE_RETRIES; it defines no fraud-check score threshold key and so documents no default for one.","source":{"path":"tool","identifier":"get_config_schema('payments')"},"confidence":"high","coverage":"complete","cost_tokens":261,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Deployed production payments configuration sets PAYMENT_BASE_URL, PROVIDER_REGION=us, CAPTURE_TIMEOUT=30, CAPTURE_DELAY_MINUTES=15, AUTH_HOLD_MINUTES=60, MAX_CAPTURE_RETRIES=4; no fraud-check score threshold key is deployed.","source":{"path":"tool","identifier":"read_config('production', 'payments')"},"confidence":"high","coverage":"complete","cost_tokens":64,"freshness":"2026-11-06T03:07Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"The closest architecture documents mention fraud checks only as the provider's own behavior (payments retries on network errors only, never on a decline, because retrying a decline can trigger the provider's fraud checks); none documents a fraud-check score threshold setting or default.","source":{"path":"vector","identifier":"search_docs('payments fraud check score threshold configuration default', k=3)"},"confidence":"medium","coverage":"unknown","cost_tokens":143,"freshness":"2026-11-04T02:09Z","caveats":["re-routed to vector after tool path found no fraud-check key in the payments schema"]}
]
```
Total cost: 468 tokens. `check_evidence` accepted all 3 documents.
