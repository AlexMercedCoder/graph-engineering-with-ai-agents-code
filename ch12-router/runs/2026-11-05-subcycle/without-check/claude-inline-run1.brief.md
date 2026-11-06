# On-call brief — 2026-11-05

## 1

**E4021 means "Payment authorization expired." It is not retryable.** The authorization hold ran out before capture. To handle it, re-authorize and then capture. Do not retry the capture by itself. (Source: `lookup_error_code('E4021')`)

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

**Two services call the PaymentsAPI directly and are affected: OrderService and RenewalsWorker.** The PaymentsAPI is exposed by PaymentsService. The graph lists both services as direct dependents at 1 hop, via `CALLS -> PaymentsAPI`. (Source: `find_dependents('PaymentsService', max_depth=1)`)

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Services that directly call the PaymentsAPI (exposed by PaymentsService) are OrderService and RenewalsWorker (2 affected within 1 hop).",
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

**The NotificationsAPI tries a message three times, with a 250ms backoff between attempts.** RETRY_ATTEMPTS sets the number of attempts. A message that fails all three goes to the dead-letter list, and **the caller is not told**. Callers that need confirmation have to poll the message status. NotificationsService exposes the NotificationsAPI. (Source: `notifications-service#Delivery and retries`, via `search_docs`)

This came from vector search, so coverage is unknown. The answer is drawn from the closest documents found, which may not be everything written on the topic.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "NotificationsAPI (exposed by NotificationsService) retries three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS; a message failing all three moves to the dead-letter list without notifying the caller; callers needing confirmation poll message status.",
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

**Net written premium by region, Q3 2026 (policies effective 2026-07-01 to 2026-09-30):**

| Region | Net written premium |
|---|---:|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

The metric is `net_written_premium`: gross written premium less cancellations, excluding quotes. It is owned by finance-reporting. The figures come from a governed query against catalog revision 2026-11-03. (Source: `execute_query(<signed SQL from generate_governed_sql>)`)

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "net_written_premium is defined as SUM(premium_amt) - SUM(cancellation_amt) over rows with status != 'quote', recognized in the month the premium takes effect; valid dimensions include region.",
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
    "claim": "Governed SQL for net_written_premium by region over 2026-Q3 filters eff_dt >= '2026-07-01' and < '2026-10-01', status != 'quote' (signature c7441fb8210cc0b7).",
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
    "claim": "Net written premium Q3 2026 by region: APAC 278969.21, EMEA 343269.84, LATAM 308624.73, North America 312420.42 (4 rows).",
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

**No answer: the governed catalog refused this.** The catalog says it does not model loss ratio. The metrics it does offer are claims_paid, gross_written_premium, net_written_premium and policies_written. I also searched the architecture docs once as a fallback. That search came back low-confidence, and none of the documents it found are about loss ratio. **No number is given here.** A loss ratio would need a governed metric, so it should not be worked out by hand from claims_paid and premium. (Sources: `navigate_catalog(concept='loss ratio')`, `search_docs('loss ratio by region', k=3)`)

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog has no metric matching 'loss ratio'; it states it does not model loss ratio, reinsurance recoveries, or claim frequency.",
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
    "claim": "Architecture documents nearest to 'loss ratio by region' (billing-service#Data, reporting-service#Integrations, audit-service#Operations) do not mention loss ratio.",
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

**No answer: the governed catalog refused this.** There is no metric for agent commission. The metrics available are claims_paid, gross_written_premium, net_written_premium and policies_written. I searched the architecture docs once as a fallback. That search came back low-confidence, and none of the documents it found are about commissions. **No number is given here.** (Sources: `navigate_catalog(concept='agent commission')`, `search_docs('agent commission paid', k=3)`)

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog has no metric matching 'agent commission'; queryable metrics are claims_paid, gross_written_premium, net_written_premium, policies_written.",
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
    "claim": "Architecture documents nearest to 'agent commission paid' (order-service#Integrations, billing-service#Overview, payments-service#Operations) do not mention agent commission.",
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
