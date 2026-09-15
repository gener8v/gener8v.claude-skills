#!/usr/bin/env bash
# Pipeline state for a skill to read before it runs. Orchestrate and Audit inject its output with
# !`…` in SKILL.md, so the generator has already run by the time the model sees the skill.
#
#   pipeline-context.sh orchestrate [PROJECT_DIR]   state (writes pipeline-state.yaml), summary, lint, metrics
#   pipeline-context.sh audit       [PROJECT_DIR]   lint, metrics
#
# PROJECT_DIR is ${CLAUDE_PROJECT_DIR} as the skill substitutes it (it may contain spaces, so every
# remaining argument is joined back into one path); without it, the current directory.
#
# Always exits 0. A failing injected command aborts the whole skill, and the situations where this
# script cannot help are ordinary: a copied install has no scripts/ beside skills/, and a project may
# have no .gener8v/ yet. Each prints one line saying which, and the skill falls back to its manual steps.
set -u
mode="${1:-orchestrate}"
shift || true
root="${*:-$PWD}"
case "$root" in '${CLAUDE_PROJECT_DIR}'|'') root="$PWD" ;; esac

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE="$HERE/../../../scripts/gener8v-state.py"

if [ ! -f "$STATE" ]; then
  echo "state script: unavailable (copied install — only skills/ is present). Do the scan by hand."
  exit 0
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "state script: python3 is not on PATH. Do the scan by hand."
  exit 0
fi
if [ ! -d "$root/.gener8v" ]; then
  echo "state script: $root has no .gener8v/ directory — the pipeline has not been set up here."
  exit 0
fi

run() {
  echo "\$ gener8v-state.py $1"
  out="$(python3 "$STATE" "$1" --root "$root" 2>&1)"
  rc=$?
  [ -n "$out" ] && printf '%s\n' "$out"
  [ "$rc" -eq 0 ] || echo "(exit $rc)"
  echo
}

case "$mode" in
  orchestrate) run state; run summary; run lint; run metrics ;;
  audit)       run lint; run metrics ;;
  *)           echo "pipeline-context.sh: unknown mode '$mode' (orchestrate | audit)" ;;
esac
exit 0
