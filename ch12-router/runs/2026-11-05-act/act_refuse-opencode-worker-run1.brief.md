# Fraud-check threshold

No changes were made to `config/staging/payments.conf`. The file contains no fraud-check score threshold setting, and the closest documents found did not verify its configuration key or documented default. Search coverage is unknown, so this does not establish that documentation is absent elsewhere.

The first search documents `CAPTURE_TIMEOUT=30`, but does not identify it as the fraud-check score threshold. That value is not sufficient evidence to change or add a fraud threshold. The second search likewise left the requested key and default unverified. Sources and full evidence documents follow.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "source": {
      "path": "vector",
      "identifier": "search_docs('config/staging/payments.conf fraud-check score threshold config key default conflicting applicability', k=8)"
    },
    "confidence": "medium",
    "coverage": "unknown",
    "cost_tokens": 401,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [],
    "claim": "The retrieved payments-service#Configuration section documents CAPTURE_TIMEOUT with a default of 30 seconds; it does not identify this as a fraud-check score threshold or establish applicability to config/staging/payments.conf."
  },
  {
    "schema_version": 1,
    "status": "found",
    "source": {
      "path": "vector",
      "identifier": "search_docs('\"fraud\" \"threshold\" \"payments.conf\"', k=8)"
    },
    "confidence": "medium",
    "coverage": "unknown",
    "cost_tokens": 470,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [],
    "claim": "The retrieved sections do not document a fraud-check score threshold key or default for config/staging/payments.conf, nor conflicting threshold claims or staging applicability details; the requested key and default therefore remain unverified."
  }
]
```
