## 1

**E4021 means payment authorization expired:** the authorization hold lapsed before capture. It is **not retryable**; re-authorize, then capture rather than retrying capture alone. Source: `lookup_error_code('E4021')`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q1: E4021 means payment authorization expired: the authorization hold lapsed before capture.",
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
    "claim": "Q1: E4021 is not retryable; re-authorize, then capture, rather than retrying capture alone.",
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

**OrderService and RenewalsWorker** directly call PaymentsAPI, exposed by PaymentsService. Their payment operations through that API are blocked if PaymentsService is down. The dependency graph does not establish whether they have fallback payment paths or whether their other functions remain available. Source: `find_dependents('PaymentsService', max_depth=1)`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q2: The direct inbound API callers of PaymentsService are OrderService and RenewalsWorker, each through a CALLS edge to PaymentsAPI exposed by PaymentsService.",
    "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 48,
    "freshness": "2026-11-04T02:56Z",
    "caveats": ["Direct callers only; transitive dependencies excluded. The graph establishes API dependency, not fallback behavior or complete service unavailability."]
  }
]
```

## 3

The closest documents found describe **three delivery attempts**, configured by `RETRY_ATTEMPTS`, with a **250 ms backoff**. They do not specify whether the backoff changes between attempts. After all three attempts fail, the message goes to the **dead-letter list without notifying the caller**; callers requiring confirmation must poll message status. Search coverage is unknown. Source: `search_docs('NotificationsAPI retry semantics', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q3: NotificationsAPI delivery uses three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS.",
    "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"},
    "confidence": "high",
    "coverage": "unknown",
    "cost_tokens": 222,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["The documentation does not specify whether the backoff changes between attempts."]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q3: After all three delivery attempts fail, the message moves to the dead-letter list without notifying the caller; callers requiring confirmation poll message status.",
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

**Q3 2026 net written premium**, using effective dates July 1 through September 30 and excluding quote rows:

| Region | Net written premium |
| --- | ---: |
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

The governed definition is gross written premium less cancellations, recognized in the month the premium takes effect. **Currency was not specified**; source-data completeness and reconciliation were not established by the query result. Sources: `navigate_catalog(concept='net written premium', entity='region')`, `generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)`, and `execute_query(<signed SQL from generate_governed_sql>)` (catalog revision `2026-11-03`).

```json
[
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q4: Governed net_written_premium is gross written premium less cancellations, recognized in the month the premium takes effect, computed as SUM(premium_amt) minus SUM(cancellation_amt), excluding quote rows.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='net written premium', entity='region')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 221,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["This is written premium, not an earned-premium measure; currency is not specified in the returned metadata."]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q4: The governed Q3 2026 query selects non-quote premiums with effective dates from 2026-07-01 inclusive to 2026-10-01 exclusive, grouped by region.",
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
    "claim": "Q4: Q3 2026 net written premium by region is APAC 278969.21; EMEA 343269.84; LATAM 308624.73; North America 312420.42.",
    "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 29,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["All four returned rows are included; currency and underlying source-data completeness or reconciliation are not specified by the query result."]
  }
]
```

## 5

**Q3 2026 loss ratio by region could not be established.** The governed catalog refused the lookup because loss ratio is not modeled. The closest fallback documents found did not supply a loss-ratio or earned-premium definition; their coverage is unknown and confidence is low. No ratio was inferred from claims paid and written premium. A governed definition and covered regional data are needed to answer. Sources: `navigate_catalog(concept='loss ratio', entity='region')` and `search_docs('loss ratio governed definition earned premium Q3 2026 data coverage', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "Q5: The governed catalog does not model loss ratio, so no governed Q3 2026 regional loss-ratio number is available from this retrieval.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='region')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 53,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["re-routed to vector after semantic returned refused", "No ratio was calculated or inferred from claims paid and written premium; an earned-premium definition was not supplied."]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q5: The fallback document search returned ReportingService integrations and overview and BillingService data sections, without a loss-ratio or earned-premium definition.",
    "source": {"path": "vector", "identifier": "search_docs('loss ratio governed definition earned premium Q3 2026 data coverage', k=3)"},
    "confidence": "low",
    "coverage": "unknown",
    "cost_tokens": 174,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["best match scored 0.59; the documents may not cover this", "re-routed to vector after semantic returned refused", "Q3 2026 loss-ratio data coverage remains unestablished; no business number reported."]
  }
]
```

## 6

**The total commission paid to agents in Q3 2026 could not be established.** The governed catalog refused the lookup because no matching metric was available. The closest fallback documents found did not define paid versus accrued agent commission; their coverage is unknown and confidence is low. No accrued amount was substituted for paid commission. A governed paid-commission definition and covered Q3 payment data are needed to answer. Sources: `navigate_catalog(concept='total commission paid agents', entity='')` and `search_docs('agent commission paid versus accrued Q3 2026 data coverage', k=3)`.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "claim": "Q6: The governed catalog returned no metric matching total commission paid agents, so no Q3 2026 paid-agent-commission total is reported.",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='total commission paid agents', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 57,
    "freshness": "2026-11-05T16:49Z",
    "caveats": ["re-routed to vector after semantic returned refused", "No accrued commission was substituted for paid commission; the catalog response supplied neither definition."]
  },
  {
    "schema_version": 1,
    "status": "found",
    "claim": "Q6: The fallback search returned PaymentsService operations and integrations and ReportingService integrations, without a paid-versus-accrued agent commission definition.",
    "source": {"path": "vector", "identifier": "search_docs('agent commission paid versus accrued Q3 2026 data coverage', k=3)"},
    "confidence": "low",
    "coverage": "unknown",
    "cost_tokens": 197,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["best match scored 0.64; the documents may not cover this", "re-routed to vector after semantic returned refused", "Q3 2026 paid-commission data coverage remains unestablished; no business number reported."]
  }
]
```
