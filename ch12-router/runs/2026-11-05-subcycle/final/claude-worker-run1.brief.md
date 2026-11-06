# On-call brief — 2026-11-05

Answers come from project-knowledge evidence documents. Each section lists the documents its answer rests on.

## 1

**E4021 means "Payment authorization expired."** It happens when the authorization hold lapses before capture.

**It is not retryable** (`Retryable: False`). Re-authorize, then capture. Don't retry the capture on its own.

Source: `lookup_error_code('E4021')` (high confidence, complete coverage).

```json
[
  {"schema_version":1,"status":"found","claim":"E4021 means 'Payment authorization expired'.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"E4021 is caused by the authorization hold lapsing before capture.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"E4021 is not retryable (Retryable: False); the handling is to re-authorize, then capture, and not to retry capture alone.","source":{"path":"tool","identifier":"lookup_error_code('E4021')"},"confidence":"high","coverage":"complete","cost_tokens":43,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 2

Two services call PaymentsAPI directly. PaymentsAPI is exposed by PaymentsService.

- **OrderService**
- **RenewalsWorker**

Source: `find_dependents('PaymentsService', max_depth=1)` (high confidence, complete coverage). This list covers direct (1-hop) callers only. The graph shows that these services call the API. It does not say whether they have a fallback, so "can no longer take payments" is our inference, not a documented fact.

```json
[
  {"schema_version":1,"status":"found","claim":"OrderService calls PaymentsAPI, which is exposed by PaymentsService (direct CALLS edge, 1 hop).","source":{"path":"graph","identifier":"find_dependents('PaymentsService', max_depth=1)"},"confidence":"high","coverage":"complete","cost_tokens":48,"freshness":"2026-11-04T02:56Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"RenewalsWorker calls PaymentsAPI, which is exposed by PaymentsService (direct CALLS edge, 1 hop).","source":{"path":"graph","identifier":"find_dependents('PaymentsService', max_depth=1)"},"confidence":"high","coverage":"complete","cost_tokens":48,"freshness":"2026-11-04T02:56Z","caveats":[]}
]
```

## 3

- Message delivery is retried **3 times with a 250 ms backoff**. `RETRY_ATTEMPTS` sets the number of attempts.
- If all three attempts fail, the message moves to the **dead-letter list, and the caller is not notified**.
- Callers that need delivery confirmation must **poll the message status**.

Source: `search_docs('NotificationsAPI retry semantics', k=3)`. Coverage is "unknown" because this was a vector search, so these are the closest documents found and may not be the full picture. Note that the docs describe *NotificationsService*.

```json
[
  {"schema_version":1,"status":"found","claim":"NotificationsService retries message delivery three times with a 250ms backoff, configured by RETRY_ATTEMPTS.","source":{"path":"vector","identifier":"search_docs('NotificationsAPI retry semantics', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":222,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"A message that fails all three delivery attempts moves to the dead-letter list, and the caller is not told.","source":{"path":"vector","identifier":"search_docs('NotificationsAPI retry semantics', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":222,"freshness":"2026-11-04T02:09Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Callers that need confirmation of delivery poll the message status.","source":{"path":"vector","identifier":"search_docs('NotificationsAPI retry semantics', k=3)"},"confidence":"high","coverage":"unknown","cost_tokens":222,"freshness":"2026-11-04T02:09Z","caveats":[]}
]
```

## 4

Net written premium, 2026-Q3:

| Region        | Net written premium |
|---------------|--------------------:|
| APAC          | 278,969.21 |
| EMEA          | 343,269.84 |
| LATAM         | 308,624.73 |
| North America | 312,420.42 |

Source: a governed query, `execute_query(<signed SQL from generate_governed_sql>)`, against catalog revision 2026-11-03 (high confidence, complete coverage). The evidence does not state a currency.

```json
[
  {"schema_version":1,"status":"found","claim":"Net written premium for 2026-Q3 for APAC is 278969.21.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium for 2026-Q3 for EMEA is 343269.84.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium for 2026-Q3 for LATAM is 308624.73.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"Net written premium for 2026-Q3 for North America is 312420.42.","source":{"path":"semantic","identifier":"execute_query(<signed SQL from generate_governed_sql>)","revision":"catalog 2026-11-03"},"confidence":"high","coverage":"complete","cost_tokens":29,"freshness":"2026-11-05T16:49Z","caveats":[]}
]
```

## 5

**No answer is available.** The governed catalog **refused** the request because it does not model loss ratio (`navigate_catalog(concept='loss ratio')`). A fallback document search found nothing relevant either: the best match scored 0.58 and is about invoice numbering. No loss-ratio figure is reported here. Answering this needs the owner of loss and claims data.

```json
[
  {"schema_version":1,"status":"refused","claim":"The catalog refused the concept 'loss ratio': No metric matches 'loss ratio'. The catalog does not model loss ratio.","source":{"path":"semantic","identifier":"navigate_catalog(concept='loss ratio', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":53,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"No section returned by search_docs for 'loss ratio by region Q3 2026' defines or reports a loss ratio; the best match (billing-service#Data, score 0.58) covers invoice numbering.","source":{"path":"vector","identifier":"search_docs('loss ratio by region Q3 2026', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":211,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.58; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```

## 6

**No answer is available.** The governed catalog **refused** the request because no metric matches "commission paid to agents" (`navigate_catalog(concept='commission paid to agents')`). A fallback document search found nothing relevant either: the best match scored 0.57 and is about provider retry behavior. No commission figure is reported here. Answering this needs the owner of agent compensation data.

```json
[
  {"schema_version":1,"status":"refused","claim":"The catalog refused the concept 'commission paid to agents': No metric matches 'commission paid to agents'.","source":{"path":"semantic","identifier":"navigate_catalog(concept='commission paid to agents', entity='')"},"confidence":"high","coverage":"complete","cost_tokens":57,"freshness":"2026-11-05T16:49Z","caveats":[]},
  {"schema_version":1,"status":"found","claim":"No section returned by search_docs for 'agent commission paid Q3 2026' reports agent commission; the best match (payments-service#Operations, score 0.57) describes provider retry behavior.","source":{"path":"vector","identifier":"search_docs('agent commission paid Q3 2026', k=3)"},"confidence":"low","coverage":"unknown","cost_tokens":173,"freshness":"2026-11-04T02:09Z","caveats":["best match scored 0.57; the documents may not cover this","re-routed to vector after semantic returned refused"]}
]
```
