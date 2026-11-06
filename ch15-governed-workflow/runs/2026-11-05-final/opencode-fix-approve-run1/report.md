# Production payments configuration fix

- Environment/service: production / payments.
- Changed `AUTH_HOLD_MINUTES` from `10` to `60`, the documented default. The previous 10-minute hold expired before the configured 15-minute capture delay, consistent with E4021.
- Gate outcome: approved by `test-reviewer` and applied.
- Request ID: `apr_08fbfa20c78b`.
- Reviewer reason: none supplied.
- Verification: a post-change configuration read confirmed `AUTH_HOLD_MINUTES=60` and `CAPTURE_DELAY_MINUTES=15`. Capture execution/recovery has not been verified.
- Existing expired authorizations require re-authorization followed by capture; do not retry capture alone (`lookup_error_code('E4021')`).
- Configuration impact: `AUTH_HOLD_MINUTES` also configures `RenewalsWorker` (`trace_configuration('AUTH_HOLD_MINUTES')`).

## Evidence

All documents below passed evidence validation. The pre-change and post-change reads describe successive states, not conflicting observations.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization hold expired before capture; handling requires re-authorization followed by capture, not retrying capture alone.",
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
    "claim": "AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES to prevent authorization holds lapsing before capture.",
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
    "claim": "Production payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15.",
    "source": {"path": "tool", "identifier": "read_config('production', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T03:45Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "AUTH_HOLD_MINUTES configures how long RenewalsWorker holds a renewal authorization before capture.",
    "source": {"path": "graph", "identifier": "trace_configuration('AUTH_HOLD_MINUTES')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 31,
    "freshness": "2026-11-06T01:29Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "After the approved change, production payments has AUTH_HOLD_MINUTES=60 and CAPTURE_DELAY_MINUTES=15.",
    "source": {"path": "tool", "identifier": "read_config('production', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T03:46Z",
    "caveats": []
  }
]
```
