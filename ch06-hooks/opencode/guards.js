// OpenCode version of protect-paths.sh, guard-bash.sh, lint-on-edit.sh, and audit.sh.
// Copy to .opencode/plugins/guards.js in the project. OpenCode loads it at startup.
import { appendFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, resolve } from "node:path";

// Whole path segments below the project folder, as in protect-paths.sh: a directory anywhere
// in the path, or the file name.
function guardedBy(p, root) {
  const path = "/" + (p.startsWith(root + "/") ? p.slice(root.length + 1) : p);
  if (path.includes("/migrations/")) return "migrations/";
  if (path.includes("/terraform/")) return "terraform/";
  const name = path.slice(path.lastIndexOf("/") + 1);
  if (name === ".env" || name.startsWith(".env.")) return ".env";
  if (name === "package-lock.json") return "package-lock.json";
  return null;
}
const BLOCKED = [
  [/rm\s+(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r|-r\s+-f|-f\s+-r|--recursive)/i, "recursive delete", "Delete specific files by name, or ask the user."],
  [/git\s+push/i, "push to remote", "Commit locally and let the user push."],
  [/git\s+reset\s+--hard/i, "hard reset", "Use git stash to set changes aside instead."],
  [/chmod\s+(-R\s+)?0?777/i, "world-writable permissions", "Grant the narrowest mode the task needs."],
  [/(curl|wget).*\|\s*(sudo\s+)?(ba|z)?sh/i, "piping a download to a shell", "Download, inspect, then run explicitly."],
];

// write and edit name one file; apply_patch (used by GPT models) names files inside the patch,
// on its Add, Update, and Delete File lines and on Move to lines for renames.
function pathsOf(tool, args) {
  if (tool === "write" || tool === "edit") return [args.filePath ?? ""];
  if (tool === "apply_patch") {
    return [...(args.patchText ?? "").matchAll(/^\*\*\* (?:(?:Add|Update|Delete) File|Move to): (.+)$/gm)].map((m) => m[1].trim());
  }
  return [];
}

// Mask credentials in commands before they reach the log, as audit.sh does.
const redact = (t) => typeof t !== "string" ? t : t
  .replace(/(authorization:\s*(?:bearer|basic|token)\s+)[^\s"']+/gi, "$1[REDACTED]")
  .replace(/((?:password|passwd|token|secret|api[-_]?key)[=:]\s*)[^\s&"']+/gi, "$1[REDACTED]")
  .replace(/(--(?:password|token|secret|api-key)[= ])[^\s"']+/gi, "$1[REDACTED]")
  .replace(/((?:^|\s)(?:-u|--user)[= ]?[^\s:]+:)[^\s"']+/g, "$1[REDACTED]")
  .replace(/(:\/\/[^/\s:@]+:)[^@\s/]+@/g, "$1[REDACTED]@")
  .replace(/sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]{10,}/g, "[REDACTED]");

export const Guards = async ({ directory }) => {
  const pending = new Map();
  const audit = (event, input, args) => {
    mkdirSync(join(directory, ".agent-work"), { recursive: true });
    const target = redact(pathsOf(input.tool, args ?? {}).join(",") || args?.command || null);
    appendFileSync(join(directory, ".agent-work", "audit.jsonl"),
      JSON.stringify({ ts: new Date().toISOString(), session: input.sessionID, event, agent: null, tool: input.tool, id: input.callID, target }) + "\n");
  };

  return {
    "tool.execute.before": async (input, output) => {
      audit("PreToolUse", input, output.args);
      pending.set(input.callID, output.args);
      for (const p of pathsOf(input.tool, output.args)) {
        const g = guardedBy(p, directory);
        if (g) throw new Error(`Blocked write to ${p}. Paths matching ${g} require human review. Describe the change you need and ask the user to make it.`);
      }
      if (input.tool === "bash") {
        const hit = BLOCKED.find(([re]) => re.test(output.args.command ?? ""));
        if (hit) throw new Error(`Blocked: ${hit[1]}. ${hit[2]}`);
      }
    },
    "tool.execute.after": async (input, output) => {
      const args = pending.get(input.callID) ?? {};
      pending.delete(input.callID);
      audit("PostToolUse", input, args);
      for (const p of pathsOf(input.tool, args)) {
        const file = resolve(directory, p);
        if (!file.endsWith(".js") || !existsSync(file)) continue;
        try { execFileSync("node", ["scripts/lint.js", "--fix", file], { cwd: directory, stdio: "ignore" }); } catch {}
        if (file.includes("/src/services/") && /from ['"]\.\.\/db\.js['"]/.test(readFileSync(file, "utf8"))) {
          output.output += `\n\nlint-on-edit: ${p} still imports from src/db.js. Project rule: a file you edit in src/services/ must get all its data through the repository classes in src/repositories/, with no import from src/db.js, including for functions your task didn't touch. Add a repository method if one is missing.`;
        }
      }
    },
  };
};
