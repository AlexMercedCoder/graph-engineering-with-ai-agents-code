# On-call brief — 2026-11-05

## 1

**E4021 means the payment authorization expired, and it is not retryable.** The authorization hold ran out before capture. To handle it, re-authorize and then capture. Don't retry the capture by itself. (Source: `lookup_error_code('E4021')`)

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means 'Payment authorization expired': the authorization hold lapsed before capture; handling is re-authorize then capture, do not retry capture alone; Retryable: False.",
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

**OrderService and RenewalsWorker.** These are the only two services that call the PaymentsAPI (exposed by PaymentsService) directly, within one hop. (Source: `find_dependents('PaymentsService', max_depth=1)`)

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Two services call PaymentsService's API directly (1 hop): OrderService -CALLS-> PaymentsAPI and RenewalsWorker -CALLS-> PaymentsAPI.",
    "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 48,
    "freshness": "2026-11-04T02:56Z",
    "caveats": []
  }
]
```

## 3

**Three attempts with a 250ms backoff, configured by `RETRY_ATTEMPTS`.** If a message fails all three attempts, it moves to the dead-letter list and **the caller is not told**. Callers that need confirmation have to poll the message status. (Source: `search_docs('NotificationsAPI retry semantics', k=3)`, section `notifications-service#Delivery and retries`)

This came from a document search, so it is based on the closest documents found. Coverage is unknown: the search can't confirm nothing else applies.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "NotificationsAPI (NotificationsService) retries three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS; a message failing all three moves to the dead-letter list without notifying the caller; callers needing confirmation poll message status.",
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

**Net written premium, Q3 2026 (Jul–Sep), by region:**

| Region | Net written premium |
|---|---|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

The governed definition is gross written premium minus cancellations, excluding quotes, recognized in the month the premium takes effect. (Source: `execute_query(<signed SQL from generate_governed_sql>)`, catalog 2026-11-03)

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "net_written_premium is defined as SUM(premium_amt) - SUM(cancellation_amt) over rows with status != 'quote', recognized in the month the premium takes effect; region is a valid dimension.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='net written premium', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 221,
    "freshness": "2026-11-05T16:49Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Governed SQL for net_written_premium by region over 2026-Q3 (eff_dt 2026-07-01 to before 2026-10-01) was generated and signed (signature 3338dca515a914de).",
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
    "claim": "Q3 2026 net written premium by region: APAC 278969.21, EMEA 343269.84, LATAM 308624.73, North America 312420.42.",
    "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 29,
    "freshness": "2026-11-05T16:49Z",
    "caveats": []
  }
]
```

## 5

**No number available: the governed catalog refused.** The catalog states that it does not model loss ratio. The metrics it can query are claims_paid, gross_written_premium, net_written_premium and policies_written. (Source: `navigate_catalog(concept='loss ratio', entity='')`)

I tried one document search as a fallback. It found nothing relevant (best match scored 0.60, low confidence: billing invoices, reporting integrations, audit buffering). No loss ratio is stated here, and none was derived from other metrics.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog has no metric matching 'loss ratio'; it explicitly does not model loss ratio. Queryable metrics: claims_paid, gross_written_premium, net_written_premium, policies_written.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 53,
    "freshness": "2026-11-05T16:49Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Architecture documents returned no section about loss ratio; closest matches were billing-service#Data, reporting-service#Integrations, and audit-service#Operations, none of which state a loss ratio.",
    "source": {"path": "vector", "identifier": "search_docs('loss ratio by region', k=3)"},
    "confidence": "low",
    "coverage": "unknown",
    "cost_tokens": 211,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [
      "best match scored 0.60; the documents may not cover this",
      "re-routed to vector after semantic returned refused"
    ]
  }
]
```

## 6

**No number available: the governed catalog refused.** No catalog metric matches agent commission. The metrics it can query are claims_paid, gross_written_premium, net_written_premium and policies_written. (Source: `navigate_catalog(concept='agent commission', entity='')`)

I tried one document search as a fallback. It found nothing relevant (best match scored 0.60, low confidence: order, billing and payments sections). No commission figure is stated here.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog has no metric matching 'agent commission'. Queryable metrics: claims_paid, gross_written_premium, net_written_premium, policies_written.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='agent commission', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 54,
    "freshness": "2026-11-05T16:49Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Architecture documents returned no section about agent commission; closest matches were order-service#Integrations, billing-service#Overview, and payments-service#Operations, none of which state a commission figure.",
    "source": {"path": "vector", "identifier": "search_docs('agent commission paid', k=3)"},
    "confidence": "low",
    "coverage": "unknown",
    "cost_tokens": 160,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [
      "best match scored 0.60; the documents may not cover this",
      "re-routed to vector after semantic returned refused"
    ]
  }
]
```
