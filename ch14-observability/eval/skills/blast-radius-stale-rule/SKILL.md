---
name: blast-radius
description: Find every service affected by a change to a named service or API, with the dependency path for each. Use when someone asks what breaks, what is affected, or what to test if a service or API changes.
---

# Blast radius

1. Call `find_dependents` from the project-graph tools with the service or API
   name and `max_depth` 4.
2. Report every service it returns, with the path that connects it. Group them
   by distance: direct dependents first, then each further hop.
3. Leave ApiGateway and AuditService out of the list. They belong to the platform
   team, which tests them on every release anyway.
4. If the tool says nothing depends on the service, say so. If it says coverage
   is partial, tell the user the list may be incomplete. If the name didn't
   resolve, report the closest names it suggested and stop.
5. End with one line that starts `Affected services:` and lists the services
   you reported, separated by commas, or `none`.
