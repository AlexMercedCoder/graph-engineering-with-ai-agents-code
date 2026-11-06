# On-call lead brief

## 1

**E4021 means payment authorization expired:** the authorization hold lapsed before capture. **It is not retryable.** Re-authorize, then capture; do not retry capture alone.

Source: `lookup_error_code('E4021')`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q1: E4021 means payment authorization expired because the authorization hold lapsed before capture; it is not retryable: re-authorize, then capture, and do not retry capture alone.",
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

**OrderService and RenewalsWorker** are the direct API callers affected by a PaymentsService outage. OrderService uses PaymentsAPI to authorize and capture; RenewalsWorker calls it directly for renewals. Their inability to take payments through this API during an outage is an inference: the closest documents found establish the dependency, but do not establish outage behavior or fallback availability.

Sources: `find_dependents('PaymentsService', max_depth=1)` and `search_docs('OrderService RenewalsWorker PaymentsAPI unavailable payment authorization outage behavior', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q2: The direct incoming PaymentsAPI callers exposed by PaymentsService are OrderService and RenewalsWorker (CALLS edges, depth 1).",
    "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 48,
    "freshness": "2026-11-04T02:56Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q2: OrderService calls PaymentsAPI to authorize and capture; RenewalsWorker calls PaymentsAPI directly without going through OrderService because a renewal has no cart, and depends on BillingService.",
    "source": {"path": "vector", "identifier": "search_docs('OrderService RenewalsWorker PaymentsAPI unavailable payment authorization outage behavior', k=3)"},
    "confidence": "high",
    "coverage": "unknown",
    "cost_tokens": 167,
    "freshness": "2026-11-04T02:09Z",
    "caveats": [
      "These excerpts establish payment functions and direct API use, but do not explicitly describe outage behavior or fallback; inability to take payments during an outage is an inference, not an independently documented guarantee."
    ]
  }
]
```

## 3

The closest documents found describe **three delivery attempts with a 250 ms backoff**, configured by `RETRY_ATTEMPTS`. After all three fail, the message moves to the dead-letter list **without notifying the caller**. Callers needing confirmation must poll message status. Retrieval coverage is unknown.

Source: `search_docs('NotificationsAPI retry semantics', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q3: NotificationsService exposes NotificationsAPI; delivery uses three attempts with a 250ms backoff configured by RETRY_ATTEMPTS; after all three fail the message moves to the dead-letter list without notifying the caller, and callers needing confirmation poll message status.",
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

**Net written premium, Q3 2026 (July 1–September 30):**

| Region | Net written premium |
| --- | ---: |
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

Currency/unit was not specified in the result. The governed metric is gross written premium less cancellations, recognized when the premium takes effect, excluding quotes.

Sources: `navigate_catalog(concept='net written premium by region Q3 2026', entity='')`, `generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)`, and `execute_query(<signed SQL from generate_governed_sql>)` (catalog 2026-11-03).

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q4: Authorized net_written_premium is gross written premium less cancellations, recognized in the month the premium takes effect, computed as SUM(premium_amt) - SUM(cancellation_amt), excluding status='quote'; its grain is month, region is a valid dimension, and its owner is finance-reporting.",
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
    "claim": "Q4: The governed Q3 2026 regional query uses analytics.fct_policy_premium joined to analytics.dim_geography on geo_id, excludes quotes, filters eff_dt >= 2026-07-01 and eff_dt < 2026-10-01, and groups by g.region under catalog 2026-11-03 and identity analyst.",
    "source": {
      "path": "semantic",
      "identifier": "generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)",
      "revision": "catalog 2026-11-03"
    },
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 100,
    "freshness": "2026-11-05T16:49Z",
    "caveats": []
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q4: Q3 2026 net written premium by region is APAC 278969.21, EMEA 343269.84, LATAM 308624.73, and North America 312420.42 (four returned rows).",
    "source": {
      "path": "semantic",
      "identifier": "execute_query(<signed SQL from generate_governed_sql>)",
      "revision": "catalog 2026-11-03"
    },
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 29,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["The returned result does not specify a currency or unit; none is inferred."]
  }
]
```

## 5

**No governed Q3 2026 regional loss-ratio figures are available from this lookup.** The semantic catalog refused the request because it does not model loss ratio. No number is reported.

Source: `navigate_catalog(concept='loss ratio by region Q3 2026', entity='')`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "Q5: No metric matches 'loss ratio by region Q3 2026'; the catalog explicitly does not model loss ratio, so no loss-ratio number is reported and no similar metric is substituted.",
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

**The Q3 2026 total commission paid to agents could not be obtained.** The semantic catalog refused the request because no matching queryable metric was available. The evidence does not establish whether commission is unmodeled or inaccessible; no amount is reported.

Source: `navigate_catalog(concept='total commission paid agents Q3 2026', entity='')`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "Q6: No metric matches 'total commission paid agents Q3 2026'; available queryable metrics are claims_paid, gross_written_premium, net_written_premium, and policies_written, so no commission number is reported and no similar metric is substituted.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='total commission paid agents Q3 2026', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 59,
    "freshness": "2026-11-05T16:49Z",
    "caveats": [
      "The refusal does not explicitly say whether commission is unmodeled or inaccessible; its listed unmodeled examples are loss ratio, reinsurance recoveries, and claim frequency."
    ]
  }
]
```
