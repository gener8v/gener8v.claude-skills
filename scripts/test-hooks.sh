#!/usr/bin/env bash
# Deterministic tests for scripts/hook.sh + scripts/hooks.py, run against a throwaway git copy of
# evals/fixture/project. No model calls: each case feeds the hook the JSON Claude Code would send and
# checks what comes back. The eval suite checks outcomes; this checks the hooks themselves, because a
# model that declines on its own never exercises them.
#
# Usage: scripts/test-hooks.sh    Exit 0 when every case passes.
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$REPO/scripts/hook.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

P="$WORK/proj"
cp -R "$REPO/evals/fixture/project" "$P"
mkdir -p "$P/tests" "$WORK/data"
( cd "$P" && git init -q . && git add -A && git -c user.name=t -c user.email=t@example.com commit -qm fixture )
python3 "$REPO/scripts/gener8v-state.py" state --root "$P" --quiet
export CLAUDE_PROJECT_DIR="$P" CLAUDE_PLUGIN_DATA="$WORK/data"

pass=0 fail=0
# expect NAME EVENT JSON PATTERN   (PATTERN "" means the hook must print nothing)
expect() {
  local out
  out="$(cd "$P" && printf '%s' "$3" | "$HOOK" "$2")"
  if { [ -z "$4" ] && [ -z "$out" ]; } || { [ -n "$4" ] && printf '%s' "$out" | grep -Eq -- "$4"; }; then
    pass=$((pass + 1)); printf 'ok    %s\n' "$1"
  else
    fail=$((fail + 1)); printf 'FAIL  %s\n      expected: %s\n      got:      %s\n' "$1" "${4:-<nothing>}" "${out:-<nothing>}"
  fi
}
tick() { sleep 1.1; }  # mtimes have one-second resolution on some filesystems

S=.gener8v/pipeline-state.yaml
DENY='"permissionDecision": "deny"'

echo "PreToolUse: the generated state file"
expect "Edit of the state file is denied"        pre-tool '{"tool_name":"Edit","tool_input":{"file_path":"'"$P/$S"'"}}' "$DENY"
expect "sed -i on the state file is denied"      pre-tool '{"tool_name":"Bash","tool_input":{"command":"sed -i \"\" s/a/b/ '"$S"'"}}' "$DENY"
expect "a redirect into the state file is denied" pre-tool '{"tool_name":"Bash","tool_input":{"command":"echo stage: x > '"$S"'"}}' "$DENY"
expect "a heredoc into the state file is denied" pre-tool '{"tool_name":"Bash","tool_input":{"command":"cat > '"$S"' <<EOF\nstage: x\nEOF"}}' "$DENY"
expect "cp onto the state file is denied"        pre-tool '{"tool_name":"Bash","tool_input":{"command":"cp /tmp/s.yaml '"$S"'"}}' "$DENY"
expect "reading the state file is allowed"       pre-tool '{"tool_name":"Bash","tool_input":{"command":"cat '"$S"' > /tmp/copy.yaml"}}' ""
expect "regenerating it is allowed"              pre-tool '{"tool_name":"Bash","tool_input":{"command":"python3 x/gener8v-state.py state"}}' ""
expect "the deny names a runnable command"       pre-tool '{"tool_name":"Edit","tool_input":{"file_path":"'"$S"'"}}' "python3 /[^ ]+/scripts/gener8v-state.py state"

echo "PreToolUse: reviewer agents"
expect "a reviewer writing source is denied"     pre-tool '{"tool_name":"Write","agent_type":"gener8v:code-reviewer","tool_input":{"file_path":"src/search/query_input.py"}}' "$DENY"
expect "a reviewer writing its report is allowed" pre-tool '{"tool_name":"Write","agent_type":"gener8v:security-reviewer","tool_input":{"file_path":".gener8v/changes/support-search/reviews/search-and-retrieval-ticket-001-security-review.md"}}' ""
expect "the sweeper writing a test is allowed"   pre-tool '{"tool_name":"Write","agent_type":"gener8v:defect-sweeper","tool_input":{"file_path":"tests/test_fail_open.py"}}' ""
expect "the sweeper writing source is denied"    pre-tool '{"tool_name":"Edit","agent_type":"gener8v:defect-sweeper","tool_input":{"file_path":"src/search/query_input.py"}}' "$DENY"
expect "a write outside the project is ignored"  pre-tool '{"tool_name":"Write","agent_type":"gener8v:code-reviewer","tool_input":{"file_path":"/tmp/scratch.txt"}}' ""

echo "PreToolUse: the delivery reminder"
expect "source edit with no delivery in progress" pre-tool '{"tool_name":"Edit","tool_input":{"file_path":"src/search/query_input.py"}}' "no delivery is In Progress"
expect "a Markdown edit gets no reminder"        pre-tool '{"tool_name":"Edit","tool_input":{"file_path":"README.md"}}' ""

echo "PostToolUse: regeneration"
before="$(python3 -c 'import os,sys; print(os.path.getmtime(sys.argv[1]))' "$P/$S")"
tick; echo "note" >> "$P/.gener8v/prd.md"
expect "a shell write under .gener8v/ regenerates quietly" post-tool '{"tool_name":"Bash","tool_input":{"command":"echo note >> .gener8v/prd.md"}}' ""
after="$(python3 -c 'import os,sys; print(os.path.getmtime(sys.argv[1]))' "$P/$S")"
if python3 -c 'import sys; sys.exit(0 if float(sys.argv[2]) > float(sys.argv[1]) else 1)' "$before" "$after"; then
  pass=$((pass + 1)); echo "ok    the state file was rewritten"
else
  fail=$((fail + 1)); echo "FAIL  the state file was not rewritten after a shell write"
fi
expect "the write is logged with via=Bash" post-tool '{"tool_name":"Bash","tool_input":{"command":"true"}}' ""
if tail -1 "$P/.gener8v/runs.jsonl" | grep -q '"via": "Bash"'; then
  pass=$((pass + 1)); echo "ok    runs.jsonl records the shell write"
else
  fail=$((fail + 1)); echo "FAIL  runs.jsonl has no shell-write line"
fi

echo "Stop: the open delivery record"
REC="$P/.gener8v/changes/support-search/delivery/search-and-retrieval-ticket-002-delivery.md"
printf '# TICKET-002 — Delivery Record\n\n**Status:** In Progress\n' > "$REC"
tick; echo "# more" >> "$P/src/search/query_input.py"
expect "source newer than the record sends the turn back" stop '{"session_id":"t1","stop_hook_active":false}' "source changed after the In Progress delivery record"
expect "the same change is reported once"        stop '{"session_id":"t1","stop_hook_active":false}' ""
expect "a continuation never blocks again"       stop '{"session_id":"t2","stop_hook_active":true}' ""
tick; echo "progress" >> "$REC"
expect "an updated record is quiet"              stop '{"session_id":"t3","stop_hook_active":false}' ""

echo "SubagentStart/Stop: reviewers stay in their lane"
( cd "$P" && git add -A && git -c user.name=t -c user.email=t@example.com commit -qm step )
printf '%s\n' '{"message":{"content":[{"type":"tool_use","name":"Bash","input":{"command":"sed -i \"\" s/x/y/ src/search/query_input.py"}}]}}' > "$WORK/t-edit.jsonl"
printf '%s\n' '{"message":{"content":[{"type":"tool_use","name":"Bash","input":{"command":"grep -rn TODO src"}}]}}' > "$WORK/t-read.jsonl"
expect "snapshot at start"                       subagent-start '{"agent_id":"a1","agent_type":"gener8v:code-reviewer"}' ""
tick; echo "# reviewer edit" >> "$P/src/search/query_input.py"
expect "a reviewer's own shell edit sends it back" subagent-stop '{"agent_id":"a1","agent_type":"gener8v:code-reviewer","stop_hook_active":false,"agent_transcript_path":"'"$WORK/t-edit.jsonl"'"}' '"decision": "block"'
expect "a second stop warns the user instead"    subagent-stop '{"agent_id":"a1","agent_type":"gener8v:code-reviewer","stop_hook_active":true,"agent_transcript_path":"'"$WORK/t-edit.jsonl"'"}' '"systemMessage"'
expect "snapshot at start (second reviewer)"     subagent-start '{"agent_id":"a2","agent_type":"gener8v:quality-reviewer"}' ""
tick; echo "# main-session edit" >> "$P/src/chat/rag.py"
expect "the main session's edit is not blamed"   subagent-stop '{"agent_id":"a2","agent_type":"gener8v:quality-reviewer","stop_hook_active":false,"agent_transcript_path":"'"$WORK/t-read.jsonl"'"}' ""

echo "Outside a pipeline project"
( unset CLAUDE_PROJECT_DIR; cd "$WORK" && printf '%s' '{"tool_name":"Edit","tool_input":{"file_path":".gener8v/pipeline-state.yaml"}}' | "$HOOK" pre-tool ) > "$WORK/out.txt"
if [ ! -s "$WORK/out.txt" ]; then pass=$((pass + 1)); echo "ok    silent without .gener8v/"; else fail=$((fail + 1)); echo "FAIL  printed outside a pipeline project"; fi

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
