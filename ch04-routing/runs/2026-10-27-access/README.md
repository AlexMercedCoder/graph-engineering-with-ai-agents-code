# Chapter 4 access, tool-rule, and fork tests, 2026-10-27

Claude Code 2.1.308, `claude-opus-5-5`, headless with `--setting-sources project,local`, on fresh
copies of `sample-project/` with the four skills and the version B descriptions.

**`invocation/`**: user-only and model-only skills, one session each (`summary.txt`).

| Session | Frontmatter | Prompt | Result |
|---|---|---|---|
| `dmi-model` | `fix-lint`: `disable-model-invocation: true` | `Format src/services/order-service.js` | No Skill call; the agent looked for the formatter itself |
| `dmi-model2` | same | `Run the formatter over the whole project` | No Skill call; the agent read `.claude/skills/fix-lint/SKILL.md` with the Read tool, then tried `npm run format` |
| `dmi-slash` | same | `/fix-lint src/services/order-service.js` | The slash command loaded the skill: the agent ran the body's command and quoted it |
| `ui-model` | `explain-module`: `user-invocable: false` | `Explain what payment-service.js does` | Skill call to `explain-module` |
| `ui-slash` | same | `/explain-module src/services/payment-service.js` | Nothing ran |
| `ctl-slash` | none | `/fix-lint src/services/order-service.js` | Same as `dmi-slash` |

A slash command expands the skill into the prompt rather than calling the Skill tool, so the
transcript shows it only through what the agent does next.

**`tool-grants/`**: does a frontmatter tool rule stop a knowledge skill from editing? The body's
`Report findings only. Do not edit files.` line was removed, and each session ran
`/code-review src/services/payment-service.js, then fix the most severe finding directly in the
file.` with `--permission-mode acceptEdits`.

| Sessions | Frontmatter | File changed |
|---|---|---|
| `none-1`, `none-2` | none | Yes, both |
| `allowed-1`, `allowed-2` | `allowed-tools: Read Grep Glob` | Yes, both |
| `disallowed-1`, `disallowed-2` | `disallowed-tools: Edit Write` | No, both (`disallowed-2`: `Permission to use Edit has been denied.`; `disallowed-1` read the frontmatter and declined) |

**`fork/`**: `explain-module` inline and with `context: fork` and `background: false`. Step 1 sent
`For the rest of this session, answer in French and call every module a widget. Reply only:
d'accord.`; step 2, resumed, sent `Explain what src/services/payment-service.js does.`

| Sessions | Skill result | Main session (step 2) | All requests, step 2 |
|---|---|---|---|
| `inline-1`, `inline-2` | In French, calls the module a widget | 4 requests, peak 22,246 tokens | 82,556 input tokens each |
| `fork-1`, `fork-2` | In English, no widgets; the main session translated it for the reply | 2 requests, peak 20,599 and 20,715 | 67,915 and 102,347, including the fork's own requests (peaks 15,340 and 17,407) |

The stream-json output includes the fork's requests, marked with a `parent_tool_use_id`. Local
paths are replaced with placeholders.

**`action-skill/`**: the `migrate-module` action skill run to completion, twice:
`/migrate-module src/services/order-service.js` with `--permission-mode acceptEdits` and
`--allowedTools "Bash(node --test*)" "Bash(npm test*)"`.

| Session | Tests after | `db.js` import left in `order-service.js` | Files changed |
|---|---|---|---|
| `mig-1` | 10 pass, 0 fail | none | `src/services/order-service.js`, `tests/order-service.test.js`, `src/api/routes.js` |
| `mig-2` | 10 pass, 0 fail | none | same three |

Both runs changed `src/api/routes.js`, which the skill body never mentions, because the router still
called the migrated functions with callbacks. `mig-<n>.diff` is the full change.
