#!/usr/bin/env bash
# PostToolUse hook (Write|Edit|MultiEdit): whenever a pipeline artifact under .gener8v/
# changes, regenerate pipeline-state.yaml so it is never stale — this replaces the
# "run /orchestrate after every skill" directive with something that cannot be forgotten.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
input="$(cat)"
path="$(printf '%s' "$input" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null || echo "")"
[ -n "$path" ] || exit 0
case "$path" in
  */.gener8v/pipeline-state.yaml) exit 0 ;;
  */.gener8v/runs.jsonl) exit 0 ;;
  "$ROOT"/.gener8v/*|.gener8v/*)
    python3 "$HERE/gener8v-state.py" state --root "$ROOT" --quiet 2>/dev/null || true
    printf '{"ts":"%s","event":"artifact_write","path":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${path#"$ROOT"/}" >> "$ROOT/.gener8v/runs.jsonl" 2>/dev/null || true ;;
esac
exit 0
