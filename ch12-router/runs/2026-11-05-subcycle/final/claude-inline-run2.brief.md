# On-call brief — 2026-11-05

Answers are drawn from project knowledge (error-code tool, service graph, architecture docs, governed catalog). Evidence documents are listed under each answer. Total retrieval cost: 1,141 tokens.

## 1

**What does E4021 mean, and is it retryable?**

E4021 is **"Payment authorization expired"**. The authorization hold ran out before capture happened. **It is not retryable.** To handle it, re-authorize and then capture. Never retry the capture by itself. (Source: `lookup_error_code('E4021')`)

```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means 'Payment authorization expired': the authorization hold lapsed before capture; handling is re-authorize then capture, never retry capture alone; Retryable: False.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 2

**If PaymentsService is down, which services that call its API directly can no longer take payments?**

Two services call the PaymentsAPI (exposed by PaymentsService) directly, one hop away:

- **OrderService**
- **RenewalsWorker**

(Source: `find_dependents('PaymentsService', max_depth=1)`. Coverage: complete.)

```json
[
  {"schema_version":1,"status":"found","claim":"Two services call PaymentsAPI (exposed by PaymentsService) directly, within 1 hop: OrderService and RenewalsWorker.","source":{"path":"graph","identifier":"find_dependents('PaymentsService', max_depth=1)"},"confidence":"high","coverage":"complete","cost_tokens":48,"freshness":"2026-11-04T02:56Z","caveats":[]}
]
```

## 3

**What are the NotificationsAPI retry semantics?**

NotificationsService exposes the NotificationsAPI. It makes **three attempts with a 250 ms backoff**, set by `RETRY_ATTEMPTS`. If all three attempts fail, the message goes to the **dead-letter list and the caller is not told**. Callers that need confirmation must poll the message status. (Source: `search_docs('NotificationsAPI retry semantics', k=3)`, section `notifications-service#Delivery and retries`.)

*Note: this comes from a document search, so coverage is unknown. The answer is based on the closest documents found, not a confirmed complete source.*

```json
[
  {"schema_version":1,"status":"found","claim":"NotificationsAPI (exposed by NotificationsService) retries three attempts with a 250ms backoff, configured by RETRY_ATTEMPTS; a message failing all three moves to the dead-letter list without notifying the caller, so callers needing confirmation must poll message status.","source":{"path":"vector","identifier":"search_docs('NotificationsAPI retry semantics', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":222,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 4

**What was net written premium by region in Q3 2026?**

| Region | Net written premium (2026-Q3) |
|---|---|
| APAC | 278,969.21 |
| EMEA | 343,269.84 |
| LATAM | 308,624.73 |
| North America | 312,420.42 |

Definition (governed catalog, owner finance-reporting): SUM(premium_amt) − SUM(cancellation_amt), excluding quotes, counted in the month the policy takes effect (eff_dt 2026-07-01 up to but not including 2026-10-01). (Sources: `navigate_catalog`, `generate_governed_sql`, `execute_query`. Catalog revision 2026-11-03.)

```json
[
  {"schema_version":1,"status":"found","claim":"net_written_premium is defined as SUM(premium_amt) - SUM(cancellation_amt) over rows with status != 'quote', monthly grain, with region as a valid dimension.","source":{"path":"semantic","identifier":"navigate_catalog(concept='net written premium', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":221,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Governed SQL for net_written_premium by region over 2026-Q3 (eff_dt 2026-07-01 to before 2026-10-01) was generated, signature 327aee46513b1dbd.","source":{"path":"semantic","identifier":"generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":100,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium in 2026-Q3 by region: APAC 278969.21, EMEA 343269.84, LATAM 308624.73, North America 312420.42.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]}
]
```

## 5

**What was our loss ratio by region in Q3 2026?**

**No answer is available.** The governed catalog **refused** the request: it states that it does not model loss ratio. A follow-up document search found nothing relevant (low confidence, best match 0.60). No number is given here. Loss ratio needs a source outside the governed catalog, or the metric has to be added to it. (Sources: `navigate_catalog(concept='loss ratio')`, `search_docs('loss ratio by region', k=3)`.)

```json
[
  {"schema_version":1,"status":"refused","claim":"The governed catalog has no metric matching 'loss ratio'; it explicitly does not model loss ratio.","source":{"path":"semantic","identifier":"navigate_catalog(concept='loss ratio', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":53,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Architecture docs closest to 'loss ratio by region' (best score 0.60: billing-service#Data, reporting-service#Integrations, audit-service#Operations) contain no loss ratio figures or definition.","source":{"path":"vector","identifier":"search_docs('loss ratio by region', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":211,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.60; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```

## 6

**How much commission did we pay agents in Q3 2026?**

**No answer is available.** The governed catalog **refused** the request because it has no agent-commission metric. The only metrics it can query are claims_paid, gross_written_premium, net_written_premium and policies_written. A follow-up document search found nothing relevant (low confidence, best match 0.60). No number is given here. (Sources: `navigate_catalog(concept='agent commission')`, `search_docs('agent commission paid', k=3)`.)

```json
[
  {"schema_version":1,"status":"refused","claim":"The governed catalog has no metric matching 'agent commission'; queryable metrics are claims_paid, gross_written_premium, net_written_premium, policies_written.","source":{"path":"semantic","identifier":"navigate_catalog(concept='agent commission', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":54,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Architecture docs closest to 'agent commission paid' (best score 0.60: order-service#Integrations, billing-service#Overview, payments-service#Operations) contain no agent commission information.","source":{"path":"vector","identifier":"search_docs('agent commission paid', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":160,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.60; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```
