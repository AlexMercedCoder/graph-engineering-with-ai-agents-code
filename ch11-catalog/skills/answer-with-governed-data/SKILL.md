---
name: answer-with-governed-data
description: Answers a business question from company data through the governed-data tools, by finding the catalog metric, generating validated SQL, and executing it within limits. Use when a question asks for a number, a trend, or a breakdown from company data. Does not answer questions the catalog does not model.
allowed-tools: mcp__governed-data__navigate_catalog mcp__governed-data__generate_governed_sql mcp__governed-data__execute_query
---

1. Call `navigate_catalog` with the business concept from the question.
   Do this even when you think you know the metric name.
2. Pick the metric whose definition matches the question. Confirm every
   dimension the question asks for is in that metric's valid dimensions.
3. If no metric matches, or a dimension is missing, stop. Say what the
   catalog does not model and that the question can't be answered from
   governed data. Don't approximate it from another metric.
4. Call `generate_governed_sql` with the metric, dimensions, and a time
   range of whole months.
5. If it returns a rejection, fix the problem it names and retry once.
   If the retry is rejected too, report the rejection instead.
6. Call `execute_query` with the SQL exactly as returned, last line included.
7. Report the result, the metric definition you used, and the SQL.
