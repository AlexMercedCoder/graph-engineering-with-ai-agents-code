# On-call lead brief

## 1

**E4021 means payment authorization expired:** the authorization hold lapsed before capture. **It is not retryable.** Re-authorize, then capture; do not retry capture alone. Source: `lookup_error_code('E4021')`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means payment authorization expired because the authorization hold lapsed before capture; it is not retryable: re-authorize, then capture, and do not retry capture alone.",
    "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 43,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  }
]
```

## 2

**OrderService and RenewalsWorker** are the direct callers of PaymentsAPI exposed by PaymentsService. A PaymentsService outage therefore blocks their PaymentsAPI-dependent payment operations: OrderService authorization/capture and RenewalsWorker renewal authorization. Direct callers are established by `find_dependents('PaymentsService', max_depth=2)`; payment operations come from the closest documents found by `search_docs('OrderService RenewalsWorker payment authorization capture PaymentsAPI unavailable', k=5)`. Those documents do not establish whether alternative payment paths exist, so an absolute claim that neither can take any payments is not verified.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "OrderService and RenewalsWorker directly CALL PaymentsAPI, exposed by PaymentsService.",
    "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=2)"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 180,
    "freshness": "2026-11-04T02:56Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "OrderService calls PaymentsAPI to authorize and capture payments.",
    "source": {"path": "vector", "identifier": "search_docs('OrderService RenewalsWorker payment authorization capture PaymentsAPI unavailable', k=5)"},
    "confidence": "high",
    "coverage": "unknown",
    "cost_tokens": 279,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["This establishes payment capability and direct API use, but does not explicitly document outage behavior or alternative payment paths."]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "RenewalsWorker calls PaymentsAPI directly without going through OrderService because a renewal has no cart; a renewal whose authorization fails is retried on days three and seven, with suspension and customer email after the third failure.",
    "source": {"path": "vector", "identifier": "search_docs('OrderService RenewalsWorker payment authorization capture PaymentsAPI unavailable', k=5)"},
    "confidence": "high",
    "coverage": "unknown",
    "cost_tokens": 279,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["Evidence supports renewal authorization capability, not an explicit capture operation or an exhaustive assertion that no payments can be taken during an outage."]
  }
]
```

## 3

The closest documents found describe **three delivery attempts with a 250 ms backoff**, with the attempt count configured by `RETRY_ATTEMPTS`. Exhausted messages go to a dead-letter list **without notifying the caller**; callers must poll message status for confirmation. Source: `search_docs('NotificationsAPI retry semantics', k=3)`; retrieval coverage is unknown.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "NotificationsService exposes NotificationsAPI and documents three delivery attempts with a 250ms backoff configured by RETRY_ATTEMPTS; exhausted messages go to a dead-letter list without telling the caller, who must poll message status for confirmation.",
    "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"},
    "confidence": "high",
    "coverage": "unknown",
    "cost_tokens": 222,
    "freshness": "2026-11-04T02:09Z",
    "caveats": []
  }
]
```

## 4

**Q3 2026 net written premium by region:**

| Region | Net written premium |
| --- | ---: |
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

Currency/units were not specified in the returned evidence. The governed metric is premium less cancellations, excluding quotes and recognizing premium in its effective month. The query covers July 1 through September 30, 2026. Sources: `navigate_catalog(concept='net written premium by region Q3 2026', entity='')`, `generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)`, and `execute_query(<signed SQL from generate_governed_sql>)`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The governed net_written_premium metric is SUM(premium_amt) minus SUM(cancellation_amt), excludes quote rows, and recognizes premium in its effective month; region is a valid dimension and finance-reporting owns the metric.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='net written premium by region Q3 2026', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 221,
    "freshness": "2026-11-05T16:49Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The governed Q3 2026 regional net_written_premium query uses effective dates >= 2026-07-01 and < 2026-10-01, excluding quote rows and rounding regional sums to two decimal places.",
    "source": {"path": "semantic", "identifier": "generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)", "revision": "catalog 2026-11-03"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 100,
    "freshness": "2026-11-05T16:49Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Executed governed net_written_premium by region for Q3 2026 returned APAC: 278969.21; EMEA: 343269.84; LATAM: 308624.73; North America: 312420.42.",
    "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 29,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["The returned evidence does not specify currency or units."]
  }
]
```

## 5

**Q3 2026 loss ratio by region is unavailable from the governed catalog.** The request was refused because loss ratio is not modeled; no regional ratios can be reported from this evidence. Source: `navigate_catalog(concept='loss ratio by region Q3 2026', entity='')`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog refused loss ratio by region for Q3 2026 because loss ratio is not modeled; no loss ratio number is available from this retrieval.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio by region Q3 2026', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 57,
    "freshness": "2026-11-05T16:49Z",
    "caveats": []
  }
]
```

## 6

**Agent commission paid in Q3 2026 is unavailable from the governed catalog.** The request was refused with no matching metric, so no amount can be reported from this evidence. Source: `navigate_catalog(concept='commission paid agents Q3 2026', entity='')`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog found no metric matching commission paid agents Q3 2026; its queryable metrics are claims_paid, gross_written_premium, net_written_premium and policies_written, so no commission amount is reported.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='commission paid agents Q3 2026', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 58,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["The refusal's generic unmodeled-metrics list names loss ratio, reinsurance recoveries and claim frequency, not commission; the explicit no-match response is the evidence of unavailability for this request."]
  }
]
```
