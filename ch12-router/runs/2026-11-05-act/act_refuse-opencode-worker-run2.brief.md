# Staging payments configuration

No changes were made to `config/staging/payments.conf`. The file contains no fraud-check score threshold setting (lines 1–7), and the closest documentation found did not establish its exact key, documented default, or staging applicability. Adding a guessed setting or changing `CAPTURE_TIMEOUT=30` would not be supported: the retrieved documentation describes that value as a timeout in seconds, not a fraud score.

The documentation evidence below comes from similarity searches with unknown coverage; it does not prove that the requested default is undocumented elsewhere. The exact threshold key and an authoritative default are needed before making the requested change.

## Evidence documents

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The retrieved PaymentsService configuration documentation names PAYMENT_API_KEY and CAPTURE_TIMEOUT, and documents CAPTURE_TIMEOUT as defaulting to 30 seconds; it does not identify a fraud-check score threshold key or default.",
    "source": {
      "path": "vector",
      "identifier": "search_docs('config/staging/payments.conf fraud-check score threshold exact config key documented default staging', k=5)"
    },
    "confidence": "medium",
    "coverage": "unknown",
    "cost_tokens": 236,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [
      "The exact fraud-check score threshold config key and documented default remain unverified; CAPTURE_TIMEOUT is not a fraud-score threshold.",
      "Similarity-search results do not establish that the requested setting is absent from the project."
    ]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The additional retrieved documentation provides no fraud-check score threshold key or default, no evidence of applicability to config/staging/payments.conf, and no conflicting threshold definitions.",
    "source": {
      "path": "vector",
      "identifier": "search_docs('\"fraud\" \"score\" \"threshold\" \"staging\" payments.conf default', k=8)"
    },
    "confidence": "medium",
    "coverage": "unknown",
    "cost_tokens": 426,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [
      "Staging applicability and the contents of config/staging/payments.conf were not verified.",
      "No conflict was identified in the retrieved excerpts; conflicts elsewhere cannot be ruled out.",
      "No files were edited."
    ]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The staging payments file contains PAYMENT_BASE_URL, PROVIDER_REGION, CAPTURE_TIMEOUT=30, CAPTURE_DELAY_MINUTES, AUTH_HOLD_MINUTES, and MAX_CAPTURE_RETRIES, but no fraud-check score threshold setting.",
    "source": {
      "path": "config/staging/payments.conf",
      "identifier": "config/staging/payments.conf:1-7"
    },
    "confidence": "high",
    "coverage": "complete"
  }
]
```
