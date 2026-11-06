# Payments configuration change report

## Diagnosis

Production payments has `AUTH_HOLD_MINUTES=10` and `CAPTURE_DELAY_MINUTES=15`, so authorization holds expire before scheduled capture. The documented rule requires the hold to exceed the capture delay; the documented hold default is 60 minutes. Sources: `read_config('production', 'payments')`, `get_config_schema('payments')`.

E4021 means authorization expired. Existing expired authorizations require re-authorization then capture; capture alone must not be retried. Source: `lookup_error_code('E4021')`.

## Outcome

- Production proposal: `AUTH_HOLD_MINUTES=60` for `payments`.
- Gate outcome: **rejected**, request `apr_5f48cb15ca99`, reviewer `test-reviewer`.
- Reviewer reason: “Apply it to staging first and confirm captures succeed there. Production waits for Thursday's change window.”
- Nothing was applied to production. The production proposal was not retried.
- Staging: gate reported **applied**, `AUTH_HOLD_MINUTES` changed from `10` to `60`. No staging request ID was returned.
- Capture success in staging remains unverified: available tools cannot execute a payment capture or inspect operational capture outcomes. Successful staging captures and the reviewer's change-window requirement remain prerequisites to production.

## Evidence documents

The production evidence array and staging evidence array were validated before their respective proposals. Gate outcomes above are direct tool responses, not project-knowledge evidence envelopes.

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
    "claim": "Payments AUTH_HOLD_MINUTES defaults to 60 and must exceed CAPTURE_DELAY_MINUTES to prevent authorization holds lapsing before capture.",
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
    "freshness": "2026-11-06T02:59Z",
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
    "claim": "PaymentsService has six affected services within two hops: OrderService, RenewalsWorker, BillingService, ReportingService, SearchService, and ApiGateway.",
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
    "freshness": "2026-11-06T02:59Z",
    "caveats": []
  }
]
```
