// Runs the same cases through opencode/guards.js, the way OpenCode calls it.
import { readFileSync, mkdtempSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { Guards } from "../opencode/guards.js";

const dir = join(mkdtempSync(join(tmpdir(), "guards-")), "terraform", "app");
mkdirSync(dir, { recursive: true });
const hooks = await Guards({ directory: dir });
const rest = (l, skip) => l.trim().replace(new RegExp(`^(\\S+\\s+){${skip}}`), "");
const lines = (file) => readFileSync(new URL(file, import.meta.url), "utf8").split("\n").filter((l) => l.trim() && !l.startsWith("#"));

let fail = 0, i = 0;
async function refused(tool, args) {
  try { await hooks["tool.execute.before"]({ tool, sessionID: "t", callID: String(i++) }, { args }); return false; }
  catch { return true; }
}
for (const l of lines("commands.txt")) {
  const expect = l.split(/\s+/)[0], cmd = rest(l, 1);
  const want = expect === "block" || expect === "overblock";
  if (await refused("bash", { command: cmd }) !== want) { console.log(`FAIL plugin bash (${expect}): ${cmd}`); fail = 1; }
}
for (const l of lines("paths.txt")) {
  const expect = l.split(/\s+/)[0], path = rest(l, 1).replaceAll("<project>", dir);
  const want = expect === "block" || expect === "overblock";
  if (await refused("write", { filePath: path }) !== want) { console.log(`FAIL plugin write (${expect}): ${path}`); fail = 1; }
  const patch = `*** Begin Patch\n*** Add File: ${path}\n+x\n*** End Patch`;
  if (await refused("apply_patch", { patchText: patch }) !== want) { console.log(`FAIL plugin apply_patch (${expect}): ${path}`); fail = 1; }
}
const secrets = lines("secrets.txt").map((l) => [l.split(/\s+/)[0], l.split(/\s+/)[1], rest(l, 2)]);
for (const [, , cmd] of secrets) await refused("bash", { command: cmd });
const log = readFileSync(join(dir, ".agent-work", "audit.jsonl"), "utf8");
for (const [expect, secret] of secrets) {
  if (expect === "mask" && log.includes(secret)) { console.log(`FAIL plugin audit kept: ${secret}`); fail = 1; }
  if (expect === "gap" && !log.includes(secret)) { console.log(`FAIL plugin audit now masks a listed gap: ${secret}`); fail = 1; }
}
process.exit(fail);
