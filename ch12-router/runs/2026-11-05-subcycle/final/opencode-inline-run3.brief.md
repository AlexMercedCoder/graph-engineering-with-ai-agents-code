# On-call lead brief

## 1

**E4021: Payment authorization expired.** The authorization hold lapsed before capture. It is **not retryable**: re-authorize, then capture; do not retry capture alone. Source: `lookup_error_code('E4021')`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means payment authorization expired because the hold lapsed before capture; it is not retryable, and handling requires re-authorization before capture rather than retrying capture alone.",
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

**OrderService and RenewalsWorker** are the direct callers affected: both call PaymentsAPI, exposed by PaymentsService, so their payment operations are blocked when it is down. Source: `find_dependents('PaymentsService', max_depth=1)`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The direct callers of PaymentsAPI exposed by PaymentsService are OrderService and RenewalsWorker.",
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

The closest documents found describe **three delivery attempts with a 250 ms backoff**, configured by `RETRY_ATTEMPTS`. After all three fail, the message moves to the dead-letter list **without notifying the caller**. Callers needing confirmation must poll message status. Search coverage is unknown. Source: `search_docs('NotificationsAPI retry semantics', k=3)`, section `notifications-service#Delivery and retries`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "NotificationsAPI delivery uses three attempts with a 250ms backoff configured by RETRY_ATTEMPTS, then moves failed messages to the dead-letter list without telling the caller; callers needing confirmation poll message status.",
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

Currency was not specified in the returned results. Source: `execute_query(<signed SQL from generate_governed_sql>)`, revision `catalog 2026-11-03`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Net written premium by region for Q3 2026 was APAC 278969.21, EMEA 343269.84, LATAM 308624.73, and North America 312420.42.",
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

**Unavailable from governed project data.** The semantic lookup refused the request because the catalog does not model loss ratio. No Q3 2026 regional loss ratios can be reported from this evidence. Source: `navigate_catalog(concept='loss ratio', entity='')`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog returned no matching metric for loss ratio and explicitly states that loss ratio is not modeled.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 53,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["re-routed to vector after semantic returned refused"]
  }
]
```

## 6

**Unavailable from governed project data.** The semantic lookup refused the request because no metric matched agent commissions paid. No Q3 2026 commission amount can be reported from this evidence. Source: `navigate_catalog(concept='agent commissions paid', entity='')`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog returned no matching metric for agent commissions paid.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='agent commissions paid', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 56,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["re-routed to vector after semantic returned refused"]
  }
]
```
