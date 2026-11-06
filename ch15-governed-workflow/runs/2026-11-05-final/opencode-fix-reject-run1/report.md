# Payments E4021 configuration change report

## Outcome

- Production: no change applied. Proposed `AUTH_HOLD_MINUTES=60` (from 10); request `apr_68090930e1c7` was rejected by `test-reviewer`.
- Reviewer's reason: "Apply it to staging first and confirm captures succeed there. Production waits for Thursday's change window."
- The production proposal was not retried.
- Staging: gate applied `AUTH_HOLD_MINUTES` from 10 to 60 without approval; no staging request ID was returned. A subsequent configuration read confirmed 60, with `CAPTURE_DELAY_MINUTES=15`.
- Capture success has not been confirmed: available tools cannot execute a payment capture or inspect operational capture results. A staging capture test remains required before production review during the requested change window.

## Diagnosis

Production authorization holds last 10 minutes, while captures are scheduled after 15 minutes (`read_config('production', 'payments')`). The schema requires the hold to exceed the capture delay and documents a 60-minute default (`get_config_schema('payments')`). E4021 indicates the authorization expired; already-expired authorizations require re-authorization then capture, not capture-only retries (`lookup_error_code('E4021')`).

The configuration graph identifies RenewalsWorker as configured by this key (`trace_configuration('AUTH_HOLD_MINUTES')`). Payments has six dependents within two hops (`find_dependents('payments', max_depth=2)`); this is the scope of that graph lookup.

## Evidence

All evidence documents below passed schema validation. Total retrieval cost: 788 tokens.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means the authorization hold expired before capture; handling requires re-authorization then capture, and capture alone must not be retried.",
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
    "claim": "For payments, AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES to prevent authorization holds lapsing before capture.",
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
    "freshness": "2026-11-06T03:49Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "AUTH_HOLD_MINUTES configures how long RenewalsWorker renewal authorizations are held before capture.",
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
    "claim": "Within two hops, payments has six affected dependents: OrderService, RenewalsWorker, BillingService, ReportingService, SearchService, and ApiGateway.",
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
    "claim": "Staging payments has AUTH_HOLD_MINUTES=10 and CAPTURE_DELAY_MINUTES=15.",
    "source": {"path": "tool", "identifier": "read_config('staging', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T03:49Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "After the staging change, payments has AUTH_HOLD_MINUTES=60 and CAPTURE_DELAY_MINUTES=15.",
    "source": {"path": "tool", "identifier": "read_config('staging', 'payments')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 64,
    "freshness": "2026-11-06T03:50Z",
    "caveats": []
  }
]
```
