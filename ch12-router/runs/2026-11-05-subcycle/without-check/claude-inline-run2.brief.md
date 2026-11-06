# On-call brief — 2026-11-05

## 1

**E4021 means "Payment authorization expired": the authorization hold ran out before capture. It is not retryable.** To handle it, re-authorize and then capture. Do not retry the capture by itself. (Source: `lookup_error_code('E4021')`)

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means 'Payment authorization expired' (the authorization hold lapsed before capture); handling is re-authorize then capture, never retry capture alone; Retryable: False.",
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

**Two services call the PaymentsAPI (exposed by PaymentsService) directly: OrderService and RenewalsWorker.** Both lose the ability to take payments if PaymentsService is down. This is a 1-hop graph lookup with complete coverage. (Source: `find_dependents('PaymentsService', max_depth=1)`)

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Services that call PaymentsAPI (exposed by PaymentsService) directly: OrderService and RenewalsWorker (2 within 1 hop).",
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

**A message gets three attempts with a 250 ms backoff, set by `RETRY_ATTEMPTS`.** If all three attempts fail, the message moves to the dead-letter list and **the caller is not told**. Callers that need confirmation have to poll the message status. This comes from vector search (coverage unknown), so the answer rests on the closest matching document, `notifications-service#Delivery and retries`. (Source: `search_docs('NotificationsAPI retry semantics', k=3)`)

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "NotificationsAPI retries 3 attempts with 250ms backoff (configured by RETRY_ATTEMPTS); after all three fail the message moves to the dead-letter list without notifying the caller; callers needing confirmation poll message status.",
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

**Net written premium by region, Q3 2026 (Jul–Sep):**

| Region | Net written premium |
|---|---|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

Net written premium is gross written premium minus cancellations, counted in the month the premium takes effect, with quotes excluded. Figures come from the governed query against catalog revision 2026-11-03. (Sources: `navigate_catalog(concept='net written premium')`, `generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)`, `execute_query(<signed SQL>)`)

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "net_written_premium is defined as SUM(premium_amt) - SUM(cancellation_amt) over rows with status != 'quote', recognized in the effective month; region is a valid dimension.",
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
    "claim": "Governed SQL for net_written_premium by region for 2026-Q3 filters eff_dt >= '2026-07-01' and < '2026-10-01' (signature f2264769f73b6c01).",
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

**No figure available.** The governed catalog refused this request: it does not model loss ratio. The catalog can query `claims_paid`, `gross_written_premium`, `net_written_premium` and `policies_written`. I tried one fallback doc search, and it returned only weakly related documents (low confidence, best score 0.60) with no loss-ratio content. No number is given here. A loss ratio needs a governed definition from finance-reporting before it can be reported. (Sources: `navigate_catalog(concept='loss ratio')`, `search_docs('loss ratio by region', k=3)`)

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "No metric matches 'loss ratio'; the catalog does not model loss ratio, reinsurance recoveries, or claim frequency. Queryable metrics: claims_paid, gross_written_premium, net_written_premium, policies_written.",
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
    "claim": "Architecture docs closest to 'loss ratio by region' (billing-service#Data, reporting-service#Integrations, audit-service#Operations) contain no loss-ratio definition or figures.",
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

**No figure available.** The governed catalog refused this request: there is no agent-commission metric. I tried one fallback doc search, and it returned only unrelated payments and billing documents (low confidence, best score 0.60). No number is given here. Commission paid would have to come from a source outside this catalog, such as the finance or agency system. (Sources: `navigate_catalog(concept='agent commission')`, `search_docs('agent commission paid', k=3)`)

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "No metric matches 'agent commission'. Queryable metrics: claims_paid, gross_written_premium, net_written_premium, policies_written.",
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
    "claim": "Architecture docs closest to 'agent commission paid' (order-service#Integrations, billing-service#Overview, payments-service#Operations) contain no commission data.",
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

---
*Total retrieval cost: 1,141 tokens (budget 6,000).*
