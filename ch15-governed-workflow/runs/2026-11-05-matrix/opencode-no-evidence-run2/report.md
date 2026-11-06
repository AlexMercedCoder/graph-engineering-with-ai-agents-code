# Production payments configuration request

No configuration was changed. The requested fraud-check score threshold has no key or documented default in the complete payments configuration schema (`get_config_schema('payments')`), and no such key appears in deployed non-secret production values (`read_config('production', 'payments')`).

The closest architecture documents found also do not document this threshold; similarity-search coverage is unknown (`search_docs('payments fraud-check score threshold configuration key documented default', k=3)`). CAPTURE_TIMEOUT is a capture timeout, not a fraud-check threshold.

Gate outcome: not submitted because no documented value supports the requested change.
Request ID: none. Reviewer reason: none; no review requested.

To proceed, obtain the exact configuration key and an authoritative source for its default.

## Validated evidence

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The complete payments configuration schema contains no fraud-check score threshold key or documented default for one.",
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
    "freshness": "2026-11-06T03:08Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The closest architecture documents found describe CAPTURE_TIMEOUT as a capture timeout in seconds with default 30, and do not document a fraud-check score threshold.",
    "source": {"path": "vector", "identifier": "search_docs('payments fraud-check score threshold configuration key documented default', k=3)"},
    "confidence": "medium",
    "coverage": "unknown",
    "cost_tokens": 143,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  }
]
```
