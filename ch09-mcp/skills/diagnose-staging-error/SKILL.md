---
name: diagnose-staging-error
description: Diagnoses an error code reported from a deployed environment (staging or production) using the project-knowledge MCP tools and the environment's configuration file, and names the setting most likely at fault. Use when the user reports an E-code (E followed by four digits) seen in an environment's logs or responses. Reads only and proposes a fix without editing.
---

# Diagnosing an environment error

1. Call `lookup_error_code` with the code. Note its cause and handling.
2. Call `find_architecture_docs` with the error's title to learn which service raises
   it and which settings control it.
3. Call `get_config_schema` for that service. Read the NOTES column for rules that
   relate settings to each other. If the call is refused for a missing scope, say
   which scope, and continue with the rules from step 2.
4. Read `config/<environment>/<service>.conf` for the environment the user named.
5. Compare each value with the schema and with the rules from steps 2 and 3. A value
   can be valid on its own and still break a rule that relates it to another key.
6. Report the code's meaning, the key or keys at fault with their current values,
   the rule they break, and the change you recommend. Don't edit any file.
