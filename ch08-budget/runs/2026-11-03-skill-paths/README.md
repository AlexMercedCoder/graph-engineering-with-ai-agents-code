# A skill with a paths field

A `route-review` skill with `paths: ["src/api/**"]`. `<n>.before.md` is `/context` at the start;
`<n>.read` reads `src/api/routes.js`; `<n>.after.md` is `/context` in the same session afterward.

In both runs, the startup skill listing (7,989 characters) didn't include `route-review`, and right
after the read the session file recorded a 178-character skill listing entry for it:
`- route-review: Reviews a route in src/api/routes.js for the API conventions and reports problems
as a list. Use when the user asks whether a route is correct or safe. Read-only.` `/context` doesn't
show skills added this way.
