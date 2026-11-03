// OpenCode version of protect-paths.sh, guard-bash.sh, lint-on-edit.sh, and audit.sh.
// Copy to .opencode/plugins/guards.js in the project. OpenCode loads it at startup.
import { appendFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join, resolve } from "node:path";

const GUARDED = ["migrations/", ".env", "package-lock.json", "terraform/"];
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

export const Guards = async ({ directory }) => {
  const pending = new Map();
  const audit = (event, input, args) => {
    mkdirSync(join(directory, ".agent-work"), { recursive: true });
    const target = pathsOf(input.tool, args ?? {}).join(",") || args?.command || null;
    appendFileSync(join(directory, ".agent-work", "audit.jsonl"),
      JSON.stringify({ ts: new Date().toISOString(), session: input.sessionID, event, tool: input.tool, target }) + "\n");
  };

  return {
    "tool.execute.before": async (input, output) => {
      audit("before", input, output.args);
      pending.set(input.callID, output.args);
      for (const p of pathsOf(input.tool, output.args)) {
        const g = GUARDED.find((x) => p.includes(x));
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
      audit("after", input, args);
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
