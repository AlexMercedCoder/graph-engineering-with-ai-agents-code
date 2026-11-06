# On-call lead brief

## 1

**E4021: Payment authorization expired.** The authorization hold lapsed before capture. It is **not retryable**: re-authorize, then capture; do not retry capture alone.

Source: `lookup_error_code('E4021')`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means payment authorization expired because the authorization hold lapsed before capture; it is not retryable, and handling is to re-authorize then capture, not retry capture alone.",
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

**OrderService and RenewalsWorker** directly call PaymentsAPI, exposed by PaymentsService. A PaymentsService outage therefore blocks their payment calls.

Source: `find_dependents('PaymentsService', max_depth=1)`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "OrderService and RenewalsWorker directly call PaymentsAPI exposed by PaymentsService.",
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

The closest documents found describe **three attempts with a 250 ms backoff**, configured by `RETRY_ATTEMPTS`. After all three fail, the message moves to the **dead-letter list without notifying the caller**. Callers needing confirmation must poll message status. Search coverage is unknown, so these documents may not exhaust the API's retry behavior.

Source: `search_docs('NotificationsAPI retry semantics', k=3)`, particularly `notifications-service#Delivery and retries` and `notifications-service#Overview`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "NotificationsService exposes NotificationsAPI and uses three attempts with a 250ms backoff configured by RETRY_ATTEMPTS; messages failing all three attempts move to the dead-letter list without notifying the caller, and callers needing confirmation poll message status.",
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

**Net written premium, Q3 2026 (July–September):**

| Region | Net written premium |
|---|---:|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

Currency was not specified in the returned results. Source: `execute_query(<signed SQL from generate_governed_sql>)`, governed catalog revision `2026-11-03`; query metric `net_written_premium`, dimension `region`, time range `2026-Q3`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q3 2026 net written premium by region was APAC 278969.21, EMEA 343269.84, LATAM 308624.73, and North America 312420.42.",
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

**Unavailable from governed project data.** The catalog refused the request because it does not model loss ratio. The fallback search's closest documents concern billing, reporting integrations, and audit operations; they provide no usable Q3 regional loss ratios. Search coverage is unknown and confidence is low. No ratio is reported.

Sources: `navigate_catalog(concept='loss ratio by region', entity='')` and `search_docs('loss ratio by region Q3 2026', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog has no matching loss ratio by region metric and explicitly does not model loss ratio.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio by region', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 55,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["re-routed to vector after semantic returned refused"]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The closest documents retrieved for loss ratio by region Q3 2026 cover BillingService data, ReportingService integrations, and AuditService operations.",
    "source": {"path": "vector", "identifier": "search_docs('loss ratio by region Q3 2026', k=3)"},
    "confidence": "low",
    "coverage": "unknown",
    "cost_tokens": 211,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["best match scored 0.58; the documents may not cover this", "re-routed to vector after semantic returned refused"]
  }
]
```

## 6

**Unavailable from governed project data.** The catalog refused the request because no metric matches commission paid to agents. The fallback search's closest documents concern payment and order operations and integrations; they provide no usable Q3 commission total. Search coverage is unknown and confidence is low. No amount is reported.

Sources: `navigate_catalog(concept='commission paid to agents', entity='')` and `search_docs('commission paid to agents Q3 2026', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog has no matching commission paid to agents metric; its available metrics are claims_paid, gross_written_premium, net_written_premium, and policies_written.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='commission paid to agents', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 57,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["re-routed to vector after semantic returned refused"]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The closest documents retrieved for commission paid to agents Q3 2026 cover PaymentsService operations and OrderService operations and integrations.",
    "source": {"path": "vector", "identifier": "search_docs('commission paid to agents Q3 2026', k=3)"},
    "confidence": "low",
    "coverage": "unknown",
    "cost_tokens": 152,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["best match scored 0.58; the documents may not cover this", "re-routed to vector after semantic returned refused"]
  }
]
```
