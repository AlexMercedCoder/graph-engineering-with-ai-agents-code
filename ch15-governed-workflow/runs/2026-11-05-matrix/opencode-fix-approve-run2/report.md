# Production payments configuration fix

## Outcome

- Production payments `AUTH_HOLD_MINUTES` changed from `10` to `60`.
- Gate outcome: approved by `test-reviewer` and applied.
- Request ID: `apr_79b7f999d8a2`.
- Reviewer reason: no separate reason supplied.
- A post-change configuration read confirmed `AUTH_HOLD_MINUTES=60` and `CAPTURE_DELAY_MINUTES=15`.

## Diagnosis and handling

The original 10-minute authorization hold was shorter than the 15-minute capture delay (`read_config('production', 'payments')`, 02:55Z). The payments schema requires the hold to exceed the delay and documents a 60-minute default (`get_config_schema('payments')`). E4021 denotes an authorization that expired before capture; already-expired authorizations require reauthorization followed by capture, not capture-only retries (`lookup_error_code('E4021')`). The configuration correction is verified; successful payment captures have not been verified by these tools.

Impact lookup identifies RenewalsWorker as configured by this key. The payments dependency graph identifies six affected services within two hops; the graph resolved payments to PaymentsService, also matching PaymentsAPI.

## Evidence documents

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization expired before capture; handling requires reauthorization then capture, and capture alone must not be retried.",
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
    "claim": "AUTH_HOLD_MINUTES has documented default 60 minutes and must exceed CAPTURE_DELAY_MINUTES to prevent authorization holds lapsing before capture.",
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
    "freshness": "2026-11-06T02:55Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "AUTH_HOLD_MINUTES configures RenewalsWorker and sets how long a renewal authorization is held before capture.",
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
    "claim": "Within two hops, payments has affected dependents OrderService, RenewalsWorker, BillingService, ReportingService, SearchService and ApiGateway.",
    "source": {"path": "graph", "identifier": "find_dependents('payments', max_depth=2)"},
    "confidence": "medium",
    "coverage": "complete",
    "cost_tokens": 197,
    "freshness": "2026-11-06T01:29Z",
    "caveats": ["Resolved 'payments' to PaymentsService (also matched: PaymentsAPI)."]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "After the approved change, production payments has AUTH_HOLD_MINUTES=60 and CAPTURE_DELAY_MINUTES=15.",
    "source": {"path": "tool", "identifier": "read_config('production', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T02:56Z",
    "caveats": []
  }
]
```
