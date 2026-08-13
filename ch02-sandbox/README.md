# Chapter 2: Hardening the Agent Sandbox

The sandbox and permission snippets from Chapter 2. Each shows the same
least-privilege policy expressed in a different configuration format. Pick the
format that matches your harness.

## The policy in plain language

```text
## Agent permissions

Allow:
- Read: all files in this project
- Write: src/, tests/
- Shell: npm test, python -m pytest, git status, git diff

Deny:
- Write: migrations/, .env, package-lock.json, yarn.lock
- Shell: git push, git commit, rm, curl, wget
- Network: all external endpoints
- Spawn: subagents
```

```text
## Agent scope

This agent operates with restricted permissions:

- File reads: entire project tree
- File writes: src/ and tests/ only
- Shell: test commands only (npm test, pytest)
- No network access
- No subagent spawning
```

## YAML form

```yaml
approval_policy: on_failure
shell:
  allowed:
    - npm test
    - python -m pytest
    - git status
    - git diff
  denied:
    - git push
    - git commit
    - rm
    - curl
files:
  read: "*"
  write:
    - "src/**"
    - "tests/**"
  deny_write:
    - "migrations/**"
    - ".env"
    - "*.lock"
```

## JSON form

```json
{
  "build_mode": {
    "allowed_write_paths": ["src/", "tests/"],
    "shell_commands": ["npm test", "python -m pytest"],
    "network": "disabled"
  }
}
```

## TypeScript tool-configuration form

```ts
const agent = new Agent({
  tools: [readFileTool, writeFileTool({ paths: ["src/", "tests/"] }), runTestsTool],
  shellPolicy: "deny_all",
  networkPolicy: "deny_all",
});
```

```ts
export const devAgent = defineAgent({
  name: "dev-agent",
  tools: [
    readFile({ scope: "project" }),
    writeFile({ scope: ["src/", "tests/"] }),
    runCommand({ allowed: ["npm test", "pytest"] }),
  ],
});
```

## Project context file (advisory constraints)

The harness also reads an advisory project file. This is the shape the book
uses. Enforced constraints are the subject of Chapter 6.

```markdown
# Project configuration

## Project context

This is a small order-management API in JavaScript, ESM, with no runtime
dependencies. Tests run with the built-in Node test runner. Database
access belongs in the repository classes under src/repositories/.

## Architecture rules

- Database access: use the repository classes only. Services must not
  call query() or update() directly.
- Error handling: every callback path handles its error argument. Every
  promise has a rejection path.
- Dependencies: none. package.json keeps an empty dependency list.
- Testing: write a test for every new function before marking a task
  complete.

## Workflow rules

- After writing any file in src/, run `npm test` to verify nothing broke.
- After all tests pass, output a brief summary of what changed and why.
- Do not modify files in migrations/, .env, or any *.lock file.

## Scope

You are working on the feature described in the current task. Do not
refactor unrelated code or update dependencies unless explicitly asked.
```

Each harness names this file differently. The companion reference
`../reference/harness-guide.md` lists the per-harness file names.
