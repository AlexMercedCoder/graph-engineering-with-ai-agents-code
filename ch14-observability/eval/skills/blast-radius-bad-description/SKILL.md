---
name: blast-radius
description: Summarize a service's dependencies for release notes. Use when writing the dependency section of a service's release notes.
---

# Blast radius

1. Call `find_dependents` from the project-graph tools with the service or API
   name and `max_depth` 4.
2. Report every service it returns, with the path that connects it. Group them
   by distance: direct dependents first, then each further hop.
3. If the tool says nothing depends on the service, say so. If it says coverage
   is partial, tell the user the list may be incomplete. If the name didn't
   resolve, report the closest names it suggested and stop.
4. End with one line that starts `Affected services:` and lists the services
   you reported, separated by commas, or `none`.
