---
name: act-on-evidence
description: Rules for answering, writing, or changing anything based on evidence documents from project knowledge. Use whenever you hold evidence documents (JSON with schema_version, status, claim, source, confidence, coverage).
---

Before you act on evidence documents:

1. Answer from the claims. If status is not "found", report what the path
   said (not found, refused, unavailable) and don't fill the gap yourself.
2. If coverage is "partial", say what wasn't reached. If it is "unknown"
   (vector search), say the answer comes from the closest documents found.
3. If confidence is "low", don't make an irreversible change. Report the
   finding and ask.
4. If a caveat says a document changed after the graph was built, say the
   graph may be stale.
5. If two documents conflict, report both with their sources. Don't choose.
6. Cite each claim's source identifier, and keep the documents with your
   answer so a reader can check them.
