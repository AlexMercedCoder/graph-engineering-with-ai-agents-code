---
name: blast-radius
description: Find every service affected by a change to a named service or API, with the dependency path for each. Use when someone asks what breaks, what is affected, or what to test if a service or API changes.
---

# Blast radius

1. Call `find_dependents` from the project-graph tools with the service or API
   name and `max_depth` 4.
2. Report the direct dependents it returns, the services that call or depend on
   the named one themselves, with the path for each.
3. If the tool says nothing depends on the service, say so. If it says coverage
   is partial, tell the user the list may be incomplete. If the name didn't
   resolve, report the closest names it suggested and stop.
4. End with one line that starts `Affected services:` and lists the services
   you reported, separated by commas, or `none`.
