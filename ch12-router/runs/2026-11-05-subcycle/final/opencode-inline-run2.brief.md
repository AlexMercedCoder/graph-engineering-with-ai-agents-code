# On-call lead brief

## 1

**E4021 means “Payment authorization expired.”** The authorization hold lapsed before capture. It is **not retryable**: re-authorize, then capture; do not retry capture alone. Source: `lookup_error_code('E4021')`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "E4021 means payment authorization expired: the hold lapsed before capture; it is not retryable, and handling is to re-authorize then capture, not retry capture alone.",
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

**OrderService and RenewalsWorker** are the direct callers whose payment-taking is affected. Both call PaymentsAPI, exposed by PaymentsService. Source: `find_dependents('PaymentsService', max_depth=1)`; coverage is complete for direct callers.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "OrderService and RenewalsWorker directly call PaymentsAPI exposed by PaymentsService and are affected when PaymentsService is down.",
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

NotificationsAPI delivery uses **three attempts with a 250 ms backoff**, configured by `RETRY_ATTEMPTS`. After all three fail, the message moves to the dead-letter list **without notifying the caller**. Callers needing confirmation must poll message status.

This answer comes from the closest documents found, particularly `notifications-service#Delivery and retries` and `notifications-service#Overview`; search coverage is unknown. Source: `search_docs('NotificationsAPI retry semantics', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "NotificationsService exposes NotificationsAPI; delivery uses three attempts with a 250ms backoff configured by RETRY_ATTEMPTS, then moves failed messages to the dead-letter list without telling the caller; callers needing confirmation poll message status.",
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
| --- | ---: |
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

The governed metric is gross written premium less cancellations, recognized in the month the premium takes effect, excluding quotes. Currency was not specified in the returned results. Sources: `navigate_catalog(concept='net written premium', entity='')` and `execute_query(<signed SQL from generate_governed_sql>)` (catalog revision `2026-11-03`).

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Net written premium is gross written premium less cancellations, recognized in the month the premium takes effect and excluding quote rows.",
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

**Unavailable from governed project knowledge:** the semantic path refused because the catalog does not model loss ratio. No Q3 2026 regional ratios can be reported. Source: `navigate_catalog(concept='loss ratio', entity='')`.

The fallback search's closest documents did not supply the requested ratios; confidence was low and coverage unknown. Source: `search_docs('loss ratio by region Q3 2026', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog does not model loss ratio and returned no matching metric.",
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
    "claim": "The closest documents returned concern billing invoice storage, reporting integrations, and audit buffering; they provide no Q3 2026 loss ratio by region.",
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

**Unavailable from governed project knowledge:** the semantic path refused because no catalog metric matched commission paid to agents. No Q3 2026 commission amount can be reported. Source: `navigate_catalog(concept='commission paid to agents', entity='')`.

The fallback search's closest documents did not supply a commission total; confidence was low and coverage unknown. Source: `search_docs('commission paid to agents Q3 2026 governed metric', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "The governed catalog returned no metric matching commission paid to agents.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='commission paid to agents', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 57,
    "freshness": "2026-11-05T16:49Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "The closest documents returned concern payment-provider retries, user token caching, and order authorization timeouts; they provide no Q3 2026 agent commission total.",
    "source": {"path": "vector", "identifier": "search_docs('commission paid to agents Q3 2026 governed metric', k=3)"},
    "confidence": "low",
    "coverage": "unknown",
    "cost_tokens": 158,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["best match scored 0.59; the documents may not cover this", "re-routed to vector after semantic returned refused"]
  }
]
```
