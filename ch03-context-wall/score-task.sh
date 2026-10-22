#!/usr/bin/env bash
# Score the changes since the last commit against the Chapter 3 rules, then commit them.
# Run it from a working copy of sample-project/ that is its own Git repository (see
# task-ladder.md), after each task:  bash "$CH3/score-task.sh" task3
#
#   rule 1  no line added in src/services/ imports from db.js or calls query()/update() directly
#   rule 2  if a file in src/ changed, at least one tests/*.test.js file changed too
#   rule 3  package.json has no dependencies
#
# Prints one line: the label, AAS out of 3, c1 to c3 (rules 1 to 3, 1 = kept), the files
# changed, and the test result. Then it commits the changes with the label as the message, so
# the next task is scored on its own. The checks are deliberately simple, so read the diff
# before you record a miss: a changed function that already had a test counts as a rule 2
# miss, and rule 1 can't see an import line that stayed the same.
set -uo pipefail
label=${1:?usage: score-task.sh <label>}
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1 || [ -n "$(git rev-parse --show-prefix)" ] || [ ! -f package.json ]; then
  echo "score-task.sh: run this from the top of a working copy that is its own Git repository:" >&2
  echo "  cp -r sample-project \"\$WORK\" && cd \"\$WORK\" && git init -q && git add -A && git commit -qm baseline" >&2
  exit 1
fi
git add -A >/dev/null
diff=$(git diff --cached -U0)
r1=1
echo "$diff" | awk '/^\+\+\+ b\//{f=$2} /^\+[^+]/{print f": "$0}' | grep -E "^b/src/services/" \
  | grep -qE "from ['\"][./]*db\.js['\"]|(^|[^.[:alnum:]_])(query|update)\(" && r1=0
src=$(git diff --cached --name-only | grep -c "^src/"); tests=$(git diff --cached --name-only | grep -cE "^tests/.*\.test\.js$")
r2=1; [ "$src" -gt 0 ] && [ "$tests" -eq 0 ] && r2=0
r3=$(python3 -c 'import json;print(0 if json.load(open("package.json")).get("dependencies") else 1)')
result=""; for _ in 1 2 3; do result=$(npm test 2>&1 | grep -E "^ℹ (pass|fail)" | tr '\n' ' '); [ -n "$result" ] && break; done
echo "$label aas=$((r1 + r2 + r3))/3 c1=$r1 c2=$r2 c3=$r3 files=$(git diff --cached --name-only | tr '\n' ',') ${result:-tests: no result}"
git -c user.email=ladder@example.com -c user.name=ladder commit -qm "$label" --allow-empty >/dev/null
