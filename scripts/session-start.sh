#!/usr/bin/env bash
# SessionStart hook: put the pipeline's current state in front of the model at the
# start of every session (startup / resume / clear / compact) — deterministically,
# instead of asking the model to remember to run /orchestrate.
#
# Reads the hook JSON on stdin ({"source": "startup"|"resume"|"clear"|"compact", ...}).
# Prints a JSON hookSpecificOutput.additionalContext block. Silent when the project has
# no .gener8v/ directory, so the hook costs nothing outside pipeline projects.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE="$HERE/gener8v-state.py"
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
input="$(cat)"
source="$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("source",""))' 2>/dev/null || echo "")"

[ -d "$ROOT/.gener8v" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

python3 "$STATE" state --root "$ROOT" --quiet 2>/dev/null || true
stage="$(python3 - "$ROOT/.gener8v/pipeline-state.yaml" <<'PY2' 2>/dev/null || true
import re,sys
t=open(sys.argv[1]).read(); m=re.search(r"^stage: (\S+)", t, re.M); print(m.group(1) if m else "")
PY2
)"
printf '{"ts":"%s","event":"session_start","source":"%s","stage":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$source" "$stage" >> "$ROOT/.gener8v/runs.jsonl" 2>/dev/null || true
summary="$(python3 "$STATE" summary --root "$ROOT" 2>/dev/null || true)"
[ -n "$summary" ] || exit 0

resume=""
case "$source" in
  compact)
    resume=$'\n\nContext was just compacted. Before continuing: re-read .gener8v/pipeline-state.yaml, and if any delivery record is "In Progress", re-read that record — its Pre-Flight Reconciliation and approved Implementation Plan are the authority for what to build next.' ;;
  resume)
    resume=$'\n\nThis is a resumed session. If a delivery record is "In Progress", continue from its Implementation Plan; otherwise take the first next step above.' ;;
esac

python3 - "$summary" "$resume" <<'PY'
import json, sys
summary, resume = sys.argv[1], sys.argv[2]
ctx = ("<gener8v-pipeline>\n" + summary +
       "\n\nThis project uses the gener8v pipeline. Non-trivial code changes flow through /delivery on a ticket; "
       "pipeline artifacts live in .gener8v/ and pipeline-state.yaml is generated (never hand-edit it). "
       "Run /orchestrate for the full coverage matrix and recommendations." + resume + "\n</gener8v-pipeline>")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}))
PY
