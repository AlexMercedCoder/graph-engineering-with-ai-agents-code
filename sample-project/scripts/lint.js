#!/usr/bin/env node
// A dependency-free stand-in for eslint and prettier, so the Chapter 6 hooks
// have something real to run on a machine with no npm install.
// Checks: no tab indentation, no trailing whitespace, file ends in one newline.
import { readdirSync, readFileSync, writeFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const fix = process.argv.includes('--fix');
const targets = process.argv.slice(2).filter((a) => !a.startsWith('--'));

function walk(dir) {
  return readdirSync(dir).flatMap((e) => {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) return walk(p);
    return p.endsWith('.js') ? [p] : [];
  });
}

const files = targets.length ? targets : [...walk('src'), ...walk('tests')];
let problems = 0;

for (const f of files) {
  const before = readFileSync(f, 'utf8');
  let after = before.replace(/\t/g, '  ').replace(/[ \t]+$/gm, '');
  if (!after.endsWith('\n')) after += '\n';
  after = after.replace(/\n{3,}$/, '\n');
  if (after !== before) {
    if (fix) writeFileSync(f, after);
    else { console.error(`${f}: formatting`); problems += 1; }
  }
}

if (problems && !fix) {
  console.error(`${problems} file(s) need formatting. Run: npm run format`);
  process.exit(1);
}
console.log(fix ? `formatted ${files.length} file(s)` : `${files.length} file(s) clean`);
