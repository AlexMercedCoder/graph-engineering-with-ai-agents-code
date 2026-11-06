# Staging payment capture fix

Changed only `AUTH_HOLD_MINUTES` in `config/staging/payments.conf`, from `10` to the payments schema's documented default of `60`. Capture remains scheduled after `15` minutes, so the configuration now satisfies `AUTH_HOLD_MINUTES > CAPTURE_DELAY_MINUTES` (`60 > 15`). The original values violated this constraint.

The error lookup identifies E4021 as an expired authorization hold. The configuration constraint and default come from `get_config_schema('payments')`; the error meaning and recovery instructions come from `lookup_error_code('E4021')`. No timeout, retry, endpoint, region, or credential changes are supported by this diagnosis.

This corrects the documented configuration mismatch; runtime success has not been verified. Already-expired authorizations require re-authorization followed by capture, not capture-only retries. The evidence does not establish a reload procedure, provider hold limits, or that this setting extends existing authorizations.

The closest architecture documents found by vector search have unknown coverage: they mention `AUTH_HOLD_MINUTES` under renewals-worker, while the payments schema explicitly includes it for payments. They do not resolve staging runtime ownership. The edit rests on the explicit payments schema and the staging file, rather than an inferred architecture relationship.

## Evidence documents

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Before the edit, staging configured CAPTURE_DELAY_MINUTES=15 and AUTH_HOLD_MINUTES=10.",
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
    "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 43,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "For E4021, re-authorize and then capture; do not retry capture alone. The error is not retryable.",
    "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 43,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The payments schema requires AUTH_HOLD_MINUTES to exceed CAPTURE_DELAY_MINUTES; otherwise holds lapse before capture.",
    "source": {"path": "tool", "identifier": "get_config_schema('payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 261,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [
      "This is a supported configuration constraint, not a verified edit for config/staging/payments.conf: its current values were not retrieved.",
      "No staging-specific replacement values, provider-supported hold limits, or reload procedure were established by the retrieved evidence."
    ]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "CAPTURE_DELAY_MINUTES is an optional integer defaulting to 15 and specifies minutes after authorization that the capture worker captures.",
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
    "claim": "AUTH_HOLD_MINUTES is an optional integer defaulting to 60 and specifies minutes the provider holds an authorization.",
    "source": {"path": "tool", "identifier": "get_config_schema('payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 261,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [
      "The schema does not establish that changing this setting extends an existing authorization or overrides provider limits.",
      "Architecture search also describes AUTH_HOLD_MINUTES as configuring RenewalsWorker; whether that usage is shared with payments or documents a different context is unresolved."
    ]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The renewals-worker Configuration architecture section says AUTH_HOLD_MINUTES configures how long a renewal authorization is held before capture.",
    "source": {
      "path": "vector",
      "identifier": "search_docs('payments staging config/staging/payments.conf authorization hold expired capture CAPTURE_DELAY_MINUTES AUTH_HOLD_MINUTES remediation provider constraints', k=8)"
    },
    "confidence": "high",
    "coverage": "unknown",
    "cost_tokens": 428,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [
      "The payments schema also includes this key; the retrieved architecture does not resolve its applicability to staging payment capture."
    ]
  }
]
```
