---
name: retrieve-evidence
description: How to look up project knowledge (error codes, config schemas, architecture documents, the service graph, governed business data) and turn each result into a structured evidence document. Use for every question that needs a lookup.
---

1. For each question, call route_question and use only the tools of the
   path or paths it returns:
   - tool: lookup_error_code, get_config_schema
   - vector: search_docs
   - graph: find_dependents, find_dependencies, trace_configuration
   - semantic: navigate_catalog, then generate_governed_sql, then
     execute_query with the generated SQL unchanged
2. Every tool returns an "evidence" envelope and a "result". For each claim,
   write one evidence document: copy status, source, confidence, coverage,
   cost_tokens, freshness, and caveats from the envelope of the call the
   claim came from, add "schema_version": 1, and write "claim" as one
   checkable statement taken from the result.
3. If a call comes back not_found or refused, try search_docs once and add
   "re-routed to vector after <path> returned <status>" to caveats. A
   business number may come only from execute_query. If the semantic path
   refuses, return its refusal as the evidence and state no number.
4. Add up cost_tokens as you go. Past 6,000, stop, set coverage to "partial"
   on the last document, and add a caveat naming what you didn't reach.
5. Pass the array to check_evidence and fix every problem it names. Keep
   the documents; they are what you act on.
