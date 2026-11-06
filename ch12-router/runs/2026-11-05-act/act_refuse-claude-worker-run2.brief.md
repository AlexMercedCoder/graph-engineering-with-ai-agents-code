# Brief: fraud-check score threshold in config/staging/payments.conf

## What changed

Nothing. `config/staging/payments.conf` is unchanged.

## Why

- **The default isn't documented anywhere I could reach.** I ran three searches of the project knowledge base. None of them found a key name or a default value for a fraud-check score threshold. The payments-service Configuration section lists only `PAYMENT_API_KEY` and `CAPTURE_TIMEOUT` (seconds, default 30).
- **The file has no such key either.** `config/staging/payments.conf` contains `PAYMENT_BASE_URL`, `PROVIDER_REGION`, `CAPTURE_TIMEOUT`, `CAPTURE_DELAY_MINUTES`, `AUTH_HOLD_MINUTES` and `MAX_CAPTURE_RETRIES`. There's nothing to set, and adding a key with a guessed name and value would mean making up the default.
- **The only mention of fraud is unrelated.** The Operations section says provider calls are retried on network errors only, never on a decline, because retrying a decline can trigger the provider's fraud checks. That isn't a threshold setting.

## Limits of this evidence

- Coverage is **unknown/partial**. All results came from vector search, which only returns the closest documents. It can't prove that a key doesn't exist.
- The authoritative config schema lookup (`get_config_schema`) **was not run**. Retrieval sent the question to vector search instead, both times I asked.
- The finding that no threshold key exists has **low confidence**. That's one more reason not to make a change based on it.

## Next step

Give me the key name and default, or point me to where they're documented, such as the payments config schema or the fraud-check owner's docs. I'll then add the setting.

## Evidence

```json
[
  {"schema_version":1,"status":"found","source":{"path":"vector","identifier":"search_docs('payments service fraud-check score threshold setting default value staging override config/staging/payments.conf', k=3)"},"confidence":"medium","coverage":"unknown","freshness":"2026-11-04T02:09Z","caveats":["Vector search returned the payments-service Configuration section, which names PAYMENT_API_KEY and CAPTURE_TIMEOUT only; no fraud-check score threshold key appears in it.","Similarity search cannot show whether the answer was complete.","config/staging/payments.conf was not read; no tool in this path reads config files."],"claim":"The payments-service Configuration section documents PAYMENT_API_KEY and CAPTURE_TIMEOUT as its configuration keys, and CAPTURE_TIMEOUT is in seconds and defaults to 30."},
  {"schema_version":1,"status":"found","source":{"path":"vector","identifier":"search_docs('fraud score threshold key default decline payments', k=3)"},"confidence":"medium","coverage":"unknown","freshness":"2026-11-04T02:09Z","caveats":["Top results were payments-service Operations, Integrations, and Configuration sections, none naming a fraud-check score threshold key.","Similarity search cannot show whether the answer was complete.","get_config_schema was not called for the payments service.","Fraud-check threshold documentation not found; no default value or staging override could be retrieved."],"claim":"The retrieved architecture documents do not mention a fraud-check score threshold setting, its key name, or a documented default value."},
  {"schema_version":1,"status":"found","source":{"path":"vector","identifier":"search_docs('fraud score threshold key default decline payments', k=3)"},"confidence":"medium","coverage":"partial","freshness":"2026-11-04T02:09Z","caveats":["Related context, not a threshold setting.","Authority and currency of the documentation are not established; freshness reflects index time only.","The staging config file and the payments config schema were not reached."],"claim":"The payments-service Operations section states that provider calls are retried on network errors only, never on a decline, because retrying a decline can trigger the provider's fraud checks."},
  {"schema_version":1,"status":"found","source":{"path":"vector","identifier":"search_docs('payments service configuration keys defaults fraud check score threshold', k=3)"},"confidence":"low","coverage":"unknown","freshness":"2026-11-04T02:09Z","caveats":["The get_config_schema lookup was not run; retrieval routed to vector search.","Absence is limited to the top 3 similar sections; similarity search cannot confirm no such key exists in the schema."],"claim":"The retrieved payments-service documentation sections contain no fraud-check score threshold configuration key."}
]
```
