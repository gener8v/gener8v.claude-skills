#!/usr/bin/env bash
# PreToolUse hook (Write|Edit|MultiEdit):
#   1. deny hand-edits to .gener8v/pipeline-state.yaml — it is generated;
#   2. when source code is about to change and no delivery is in progress, remind the
#      model (non-blocking) that non-trivial changes flow through /delivery.
set -u
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
input="$(cat)"
path="$(printf '%s' "$input" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null || echo "")"
[ -n "$path" ] || exit 0
[ -d "$ROOT/.gener8v" ] || exit 0

case "$path" in
  */.gener8v/pipeline-state.yaml|.gener8v/pipeline-state.yaml)
    python3 -c 'import json; print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": ".gener8v/pipeline-state.yaml is generated. Run: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py state — or run /orchestrate, which does."}}))'
    exit 0 ;;
  */.gener8v/*|.gener8v/*|*.md|*.markdown|*.txt|*.yaml|*.yml|*.json|*.toml|*.lock|*CLAUDE.md) exit 0 ;;
esac

# source-code write outside a delivery: nudge, don't block
if ! grep -lqs '^\*\*Status:\*\* In Progress' "$ROOT"/.gener8v/changes/*/delivery/*-delivery.md "$ROOT"/.gener8v/delivery/*-delivery.md 2>/dev/null; then
  python3 -c 'import json; print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "gener8v: no delivery is In Progress. Trivial fixes (typo, formatting, config) are fine; anything else should be a ticket delivered via /delivery so it gets @spec traceability and reviews."}}))'
fi
exit 0
