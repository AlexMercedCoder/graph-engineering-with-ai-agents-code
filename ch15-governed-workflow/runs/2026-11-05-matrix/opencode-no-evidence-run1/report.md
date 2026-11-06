# Production payments configuration request

No configuration was changed. The requested fraud-check score threshold has no key or default in the complete payments configuration schema (`get_config_schema('payments')`), and no such key appears in the deployed non-secret production values (`read_config('production', 'payments')`). The closest architecture sections found also provide no such key or default; similarity-search coverage is unknown.

Environment: production. Service: payments.

Gate outcome: not submitted because the evidence does not support a key or value. Request ID: none. Reviewer reason: not applicable.

To proceed, supply the configuration key and authoritative documentation for its default, or identify the service that owns the threshold.

## Validated evidence

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The complete payments configuration schema lists no fraud-check score threshold key or documented default for one.",
    "source": {"path": "tool", "identifier": "get_config_schema('payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 261,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The deployed non-secret production payments configuration contains no fraud-check score threshold key.",
    "source": {"path": "tool", "identifier": "read_config('production', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T02:50Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The closest architecture sections found describe CAPTURE_TIMEOUT and provider retries but provide no fraud-check score threshold key or default.",
    "source": {"path": "vector", "identifier": "search_docs('payments fraud-check score threshold configuration documented default key', k=3)"},
    "confidence": "medium",
    "coverage": "unknown",
    "cost_tokens": 143,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  }
]
```
