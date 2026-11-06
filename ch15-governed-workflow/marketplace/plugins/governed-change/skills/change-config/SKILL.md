---
name: change-config
description: Fix or change a deployed service configuration value in staging or production, from evidence. Use when asked to fix a failing service through its configuration, or to change or set a configuration value in a deployed environment.
---

1. Find the cause with project knowledge, following retrieve-evidence:
   error codes, the service's configuration schema, and what the key
   affects. Read the deployed values with read_config for the environment
   the request names.
2. Decide the change from the evidence, following act-on-evidence. Change
   one key, to a value the evidence supports, such as a documented default
   or a documented rule. If nothing documented supports a value, change
   nothing and say why.
3. Call propose_change with the evidence documents the change rests on, as
   a JSON array that check_evidence accepts. Don't ask the user to approve
   first: the gate decides whether a reviewer must, and builds what the
   reviewer reads.
4. If a reviewer rejects the change, don't propose it again. If the reason
   asks for a step you can take with these tools, such as applying the
   change to staging first, take it. If the request expires, stop.
5. Write report.md: what changed or didn't, in which environment, the
   gate's outcome and request id, the reviewer's reason if there was one,
   and the evidence documents in a ```json block.
