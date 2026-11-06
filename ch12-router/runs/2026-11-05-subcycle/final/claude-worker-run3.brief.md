# On-call brief — 2026-11-05

## 1

**E4021 = "Payment authorization expired"**: the authorization hold lapsed before capture. It is **not retryable**. Re-authorize, then capture. Retrying the capture on its own won't work. (Source: `lookup_error_code('E4021')`, high confidence, complete coverage.)

```json
{
  "schema_version": 1,
  "status": "found",
  "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"},
  "confidence": "high",
  "coverage": "complete",
  "cost_tokens": 43,
  "freshness": "2026-11-04T02:09Z",
  "caveats": [],
  "claim": "E4021 means 'Payment authorization expired' (the authorization hold lapsed before capture), is not retryable (Retryable: False), and should be handled by re-authorizing and then capturing, not by retrying capture alone."
}
```

## 2

**OrderService** and **RenewalsWorker** call PaymentsAPI (exposed by PaymentsService) directly, so both lose the ability to take payments. BillingService, ReportingService, SearchService and ApiGateway reach PaymentsService only indirectly, through OrderService. (Source: `find_dependents('PaymentsService', max_depth=2)`, high confidence, complete coverage.)

```json
{
  "schema_version": 1,
  "status": "found",
  "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=2)"},
  "confidence": "high",
  "coverage": "complete",
  "cost_tokens": 180,
  "freshness": "2026-11-04T02:56Z",
  "caveats": [],
  "claim": "The services that call PaymentsAPI (exposed by PaymentsService) directly are OrderService and RenewalsWorker; BillingService, ReportingService, SearchService and ApiGateway reach it only indirectly, through OrderService."
}
```

## 3

NotificationsAPI makes **3 attempts with a 250 ms backoff**, set by `RETRY_ATTEMPTS`. If all three attempts fail, the message goes to the **dead-letter list and the caller is not told**. Callers that need confirmation must poll the message status. *Note: this comes from the closest documents a search found (coverage unknown), not a complete lookup.* (Source: `search_docs('NotificationsAPI retry semantics', k=3)`.)

```json
{
  "schema_version": 1,
  "status": "found",
  "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics', k=3)"},
  "confidence": "high",
  "coverage": "unknown",
  "cost_tokens": 222,
  "freshness": "2026-11-04T02:09Z",
  "caveats": [],
  "claim": "NotificationsAPI makes three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS; a message that fails all three attempts moves to the dead-letter list and the caller is not told, so callers needing confirmation poll the message status."
}
```

## 4

Net written premium, 2026-Q3, by region:

| Region | Net written premium |
|---|---|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

(Source: governed query `execute_query(<signed SQL from generate_governed_sql>)`, catalog revision 2026-11-03, high confidence, complete coverage.)

```json
{
  "schema_version": 1,
  "status": "found",
  "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"},
  "confidence": "high",
  "coverage": "complete",
  "cost_tokens": 29,
  "freshness": "2026-11-05T16:49Z",
  "caveats": [],
  "claim": "Net written premium for 2026-Q3 by region was APAC 278969.21, EMEA 343269.84, LATAM 308624.73 and North America 312420.42."
}
```

## 5

**No answer available.** The governed catalog **refused** "loss ratio" because it has no matching metric and doesn't model loss ratio (`navigate_catalog(concept='loss ratio')`). A fallback document search found nothing relevant: the best match (low confidence, score 0.58) was the BillingService Data section on invoice numbering. No loss ratio figure is given here. The metric would need to be added to the catalog, or the number sourced from the actuarial/finance owners.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 53,
    "freshness": "2026-11-05T16:49Z",
    "caveats": [],
    "claim": "navigate_catalog refused 'loss ratio': no metric matches it, and the catalog does not model loss ratio. No number is stated for this question."
  },
  {
    "schema_version": 1,
    "status": "found",
    "source": {"path": "vector", "identifier": "search_docs('loss ratio by region Q3 2026', k=3)"},
    "confidence": "low",
    "coverage": "unknown",
    "cost_tokens": 211,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["best match scored 0.58; the documents may not cover this", "re-routed to vector after semantic returned refused"],
    "claim": "The top search match for loss ratio by region Q3 2026 (score 0.58) is the BillingService Data section, which describes invoice numbering and does not report a loss ratio."
  }
]
```

## 6

**No answer available.** The governed catalog **refused** "agent commission" because no metric matches it. The only metrics it can query are claims_paid, gross_written_premium, net_written_premium and policies_written (`navigate_catalog(concept='agent commission')`). A fallback document search found nothing relevant: its top matches (low confidence, score 0.57) cover PaymentsService/RenewalsWorker retries and OrderService timeouts. No commission figure is given here.

```json
[
  {
    "schema_version": 1,
    "status": "refused",
    "source": {"path": "semantic", "identifier": "navigate_catalog(concept='agent commission', entity='')"},
    "confidence": "high",
    "coverage": "complete",
    "cost_tokens": 54,
    "freshness": "2026-11-05T16:49Z",
    "caveats": [],
    "claim": "navigate_catalog refused 'agent commission': no metric matches it, and the catalog lists claims_paid, gross_written_premium, net_written_premium and policies_written as the metrics it can query. No number is stated for this question."
  },
  {
    "schema_version": 1,
    "status": "found",
    "source": {"path": "vector", "identifier": "search_docs('agent commission paid Q3 2026', k=3)"},
    "confidence": "low",
    "coverage": "unknown",
    "cost_tokens": 173,
    "freshness": "2026-11-04T02:09Z",
    "caveats": ["best match scored 0.57; the documents may not cover this", "re-routed to vector after semantic returned refused"],
    "claim": "The top three search matches for agent commission paid Q3 2026 describe PaymentsService retry rules, RenewalsWorker retries and OrderService payment timeouts; none reports agent commission."
  }
]
```
