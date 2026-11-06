# Staging payment capture fix

Changed `AUTH_HOLD_MINUTES` from `10` to `60` in `config/staging/payments.conf`.

The file configures a 15-minute capture delay, so its previous 10-minute authorization hold expired before capture. The payments schema requires the hold to exceed the capture delay and documents a 60-minute default (`get_config_schema('payments')`). Using that default satisfies the constraint without changing capture timing.

E4021 means the authorization expired before capture (`lookup_error_code('E4021')`). Already-expired authorizations require re-authorization before capture; retrying capture alone does not resolve them. No other configuration values were changed.

Validation: the configured hold is now greater than the capture delay (`60 > 15`). Live staging captures and effective runtime overrides have not been verified; the evidence does not establish provider-side hold behavior or reload requirements.

## Supporting evidence documents

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The staging payments file configures CAPTURE_DELAY_MINUTES=15 and, before this edit, AUTH_HOLD_MINUTES=10.",
    "source": {
      "path": "file",
      "identifier": "config/staging/payments.conf:5-6 (before edit)"
    },
    "confidence": "high",
    "coverage": "complete"
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means Payment authorization expired: the authorization hold lapsed before capture.",
    "source": {
      "path": "tool",
      "identifier": "lookup_error_code('E4021')"
    },
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 43,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 is not retryable; handling is to re-authorize, then capture, not retry capture alone.",
    "source": {
      "path": "tool",
      "identifier": "lookup_error_code('E4021')"
    },
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 43,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The payments schema requires AUTH_HOLD_MINUTES to exceed CAPTURE_DELAY_MINUTES to avoid authorization holds lapsing before capture; their defaults are 60 and 15 minutes respectively.",
    "source": {
      "path": "tool",
      "identifier": "get_config_schema('payments')"
    },
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 261,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [
      "config/staging/payments.conf was not inspected; current staging values and effective overrides are unknown.",
      "The schema establishes a constraint, not an exact staging replacement value or evidence that changing the configured hold changes the provider's actual hold.",
      "No exact minimal file edit is supported by the retrieved evidence."
    ]
  }
]
```

The schema evidence's file-inspection caveat describes the retrieval step. Direct inspection subsequently established the staging values above. Choosing `60` uses the documented default; it is not a staging-specific value prescribed by the source.
