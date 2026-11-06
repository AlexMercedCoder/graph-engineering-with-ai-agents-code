# On-call brief (2026-11-05)

Status at a glance: questions 1, 2 and 4 have firm answers. Question 3 is partly answered, from similarity search. Questions 5 and 6 have **no answer**, because the governed catalog does not model those metrics and the fallback document search failed.

## 1

**E4021 means "Payment authorization expired". It is not retryable.**

- Cause: the authorization hold lapsed before capture.
- What to do: re-authorize, then capture. Do **not** retry the capture on its own.

Source: `lookup_error_code('E4021')`. Confidence high, coverage complete.

```json
[
  {"schema_version": 1, "claim": "E4021 means Payment authorization expired.", "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "claim": "Cause: The authorization hold lapsed before capture.", "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "claim": "Handling: Re-authorize, then capture. Do not retry capture alone.", "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": []},
  {"schema_version": 1, "claim": "E4021 is not retryable (Retryable: False).", "status": "found", "source": {"path": "tool", "identifier": "lookup_error_code('E4021')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 43, "freshness": "2026-11-04T02:09Z", "caveats": []}
]
```

## 2

**Two services call PaymentsAPI directly. PaymentsAPI is exposed by PaymentsService. The two services are:**

- **OrderService**
- **RenewalsWorker**

Source: `find_dependents('PaymentsService', max_depth=1)`. Confidence high, coverage complete.

Caveat: the graph only shows direct (1-hop) CALLS edges. It does **not** show whether either service has a fallback that still takes payments when PaymentsService is down. Both lose their direct payment path. Whether they can take payments at all in an outage has not been confirmed.

```json
[
  {"schema_version": 1, "status": "found", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "cost_tokens": 48, "freshness": "2026-11-04T02:56Z", "caveats": ["Graph shows the 1-hop CALLS edges only. It does not establish whether these callers have a fallback path that still takes payments when PaymentsService is down."], "claim": "2 services are affected within 1 hop of PaymentsService: OrderService and RenewalsWorker."},
  {"schema_version": 1, "status": "found", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "cost_tokens": 48, "freshness": "2026-11-04T02:56Z", "caveats": ["Graph shows the 1-hop CALLS edges only. It does not establish whether these callers have a fallback path that still takes payments when PaymentsService is down."], "claim": "OrderService calls PaymentsAPI directly (OrderService -CALLS-> PaymentsAPI), and PaymentsAPI is exposed by PaymentsService."},
  {"schema_version": 1, "status": "found", "source": {"path": "graph", "identifier": "find_dependents('PaymentsService', max_depth=1)"}, "confidence": "high", "coverage": "complete", "cost_tokens": 48, "freshness": "2026-11-04T02:56Z", "caveats": ["Graph shows the 1-hop CALLS edges only. It does not establish whether these callers have a fallback path that still takes payments when PaymentsService is down."], "claim": "RenewalsWorker calls PaymentsAPI directly (RenewalsWorker -CALLS-> PaymentsAPI), and PaymentsAPI is exposed by PaymentsService."}
]
```

## 3

**Partial answer, from the closest documents found by similarity search.** Coverage is unknown, so this may not be complete.

From `notifications-service#Delivery and retries`:

- Delivery is attempted **3 times in total**, with a **250 ms backoff**. The number of attempts is set by `RETRY_ATTEMPTS`.
- A message that fails all three attempts goes to the **dead-letter list**. **The caller is not told.**
- Callers that need confirmation of delivery must **poll the message status**.

From `api-gateway#Operations`, which covers clients calling through the gateway:

- The gateway does **not** retry failed upstream requests. A 5xx is passed to the client unchanged, and the client library decides whether to retry.

Not answered by the evidence:

- Idempotency behaviour.
- Which error types are retried.
- Whether the dead-letter list can be inspected or replayed.

Note: the source calls it NotificationsService. It is assumed to be what serves NotificationsAPI.

```json
[
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics: retry count, backoff, idempotency, which errors are retried', k=3) -> [notifications-service#Delivery and retries]"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 184, "freshness": "2026-11-04T02:09Z", "caveats": ["The first search_docs call returned 'Connection closed'; the same query was retried once and returned this result.", "cost_tokens 184 is the cost of the single search_docs call shared by the first four documents; count it once in the total.", "The retrieved sections do not state idempotency behavior or which error types are retried. Those parts of the question are unanswered by this evidence.", "Similarity search cannot establish completeness; coverage is unknown."], "claim": "NotificationsService retries message delivery three attempts in total with a 250ms backoff."},
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics: retry count, backoff, idempotency, which errors are retried', k=3) -> [notifications-service#Delivery and retries]"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 184, "freshness": "2026-11-04T02:09Z", "caveats": ["cost_tokens shared with the search_docs call that produced this document; count once."], "claim": "The NotificationsService retry attempt count is configured by the RETRY_ATTEMPTS setting."},
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics: retry count, backoff, idempotency, which errors are retried', k=3) -> [notifications-service#Delivery and retries]"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 184, "freshness": "2026-11-04T02:09Z", "caveats": ["cost_tokens shared with the search_docs call that produced this document; count once.", "The source does not say whether the dead-letter list can be inspected or replayed."], "claim": "A notification message that fails all three attempts is moved to the dead-letter list, and the caller is not told."},
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics: retry count, backoff, idempotency, which errors are retried', k=3) -> [notifications-service#Delivery and retries]"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 184, "freshness": "2026-11-04T02:09Z", "caveats": ["cost_tokens shared with the search_docs call that produced this document; count once."], "claim": "Callers of NotificationsService that need delivery confirmation must poll the message status."},
  {"schema_version": 1, "status": "found", "source": {"path": "vector", "identifier": "search_docs('NotificationsAPI retry semantics: retry count, backoff, idempotency, which errors are retried', k=3) -> [api-gateway#Operations]"}, "confidence": "high", "coverage": "unknown", "cost_tokens": 184, "freshness": "2026-11-04T02:09Z", "caveats": ["cost_tokens shared with the search_docs call that produced this document; count once.", "This describes the API gateway, not NotificationsAPI itself. It is included because it sets the retry behavior for clients calling through the gateway."], "claim": "The API gateway does not retry failed upstream requests; a 5xx from a service is passed to the client unchanged, and the client library decides whether to retry."}
]
```

## 4

**Net written premium, Q3 2026 (effective dates 2026-07-01 to 2026-09-30):**

| Region        | Net written premium |
|---------------|--------------------:|
| APAC          | 278,969.21 |
| EMEA          | 343,269.84 |
| LATAM         | 308,624.73 |
| North America | 312,420.42 |

Definition: gross written premium less cancellations, recognized in the month the premium takes effect. Quotes are excluded.

Source: governed SQL (signature `1012fdb0a2b720bc`) run against catalog revision 2026-11-03. Confidence high, coverage complete. The sources give no currency.

```json
[
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='net written premium', entity='region')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 221, "freshness": "2026-11-04T02:15Z", "caveats": [], "claim": "net_written_premium (Net Written Premium) is defined as gross written premium less cancellations, recognized in the month the premium takes effect, computed as SUM(premium_amt) - SUM(cancellation_amt), with rows counted where status != 'quote', and is valid by region."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "generate_governed_sql('net_written_premium', ['region'], '2026-Q3', None)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 100, "freshness": "2026-11-04T02:15Z", "caveats": [], "claim": "The governed SQL for net_written_premium by region for 2026-Q3 sums premium_amt minus cancellation_amt from analytics.fct_policy_premium joined to analytics.dim_geography, filtered to status != 'quote' and eff_dt from 2026-07-01 up to but excluding 2026-10-01, grouped by region (signature 1012fdb0a2b720bc)."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-04T02:15Z", "caveats": [], "claim": "Net written premium for APAC in 2026-Q3 is 278969.21."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-04T02:15Z", "caveats": [], "claim": "Net written premium for EMEA in 2026-Q3 is 343269.84."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-04T02:15Z", "caveats": [], "claim": "Net written premium for LATAM in 2026-Q3 is 308624.73."},
  {"schema_version": 1, "status": "found", "source": {"path": "semantic", "identifier": "execute_query(<signed SQL from generate_governed_sql>)", "revision": "catalog 2026-11-03"}, "confidence": "high", "coverage": "complete", "cost_tokens": 29, "freshness": "2026-11-04T02:15Z", "caveats": [], "claim": "Net written premium for North America in 2026-Q3 is 312420.42."}
]
```

## 5

**No answer. The lookup was refused.** The governed catalog does not model loss ratio. The only metrics it can query are:

- claims_paid
- gross_written_premium
- net_written_premium
- policies_written

The fallback document search failed ("Connection closed") and returned nothing.

No loss ratio has been made up from claims_paid and premium. A non-governed number like that would need an agreed definition (for example, earned or written premium, and whether reserves are included). To get an answer: ask the data owner for a governed loss ratio definition, or retry the document search.

Source: `navigate_catalog(concept='loss ratio')`.

```json
[
  {"schema_version": 1, "claim": "No metric matches 'loss ratio' in the governed catalog, so no loss ratio by region for Q3 2026 can be returned from the semantic path.", "status": "refused", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 53, "freshness": "2026-11-04T02:15Z", "caveats": ["re-routed to vector after semantic returned refused: the search_docs call (query: 'loss ratio by region definition claims paid earned premium Q3 2026') returned 'Connection closed' and produced no evidence, so no vector-path support was obtained.", "No business number is stated; the semantic path refused and no execute_query was run.", "navigate_catalog was called twice with identical arguments; both calls returned the same refusal envelope (53 tokens each)."]},
  {"schema_version": 1, "claim": "The catalog does not model loss ratio, reinsurance recoveries, or claim frequency.", "status": "refused", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 53, "freshness": "2026-11-04T02:15Z", "caveats": ["re-routed to vector after semantic returned refused: the search_docs call returned 'Connection closed' and produced no evidence.", "No business number is stated; the semantic path refused and no execute_query was run."]},
  {"schema_version": 1, "claim": "The queryable governed metrics are claims_paid, gross_written_premium, net_written_premium, and policies_written.", "status": "refused", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='loss ratio', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 53, "freshness": "2026-11-04T02:15Z", "caveats": ["re-routed to vector after semantic returned refused: the search_docs call returned 'Connection closed' and produced no evidence.", "These metrics are listed as queryable but were not queried; no business number is stated for loss ratio or any region."]}
]
```

## 6

**No answer. The lookup was refused.** No governed metric covers commission paid to agents. The fallback document search failed ("Connection closed"), so commission documentation was **not** checked (coverage partial).

To get an answer:

- Ask the data owner whether commission is modeled under another name, or
- Retry the document search.

Source: `navigate_catalog(concept='commission paid to agents')`.

```json
[
  {"schema_version": 1, "claim": "No governed metric matches the concept 'commission paid to agents'.", "status": "refused", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='commission paid to agents', entity='')"}, "confidence": "high", "coverage": "complete", "cost_tokens": 57, "freshness": "2026-11-04T02:15Z", "caveats": ["re-routed to vector after semantic returned refused; search_docs call failed with 'Connection closed' and returned no evidence"]},
  {"schema_version": 1, "claim": "The catalog does not model loss ratio, reinsurance recoveries, or claim frequency.", "status": "refused", "source": {"path": "semantic", "identifier": "navigate_catalog(concept='commission paid to agents', entity='')"}, "confidence": "high", "coverage": "partial", "cost_tokens": 0, "freshness": "2026-11-04T02:15Z", "caveats": ["Same navigate_catalog call as the prior document; cost_tokens counted once there. Coverage set to partial because no vector search completed, so commission-related documentation was not checked."]}
]
```
