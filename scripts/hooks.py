#!/usr/bin/env python3
"""gener8v plugin hooks for tool calls, turn ends and reviewer agents (wired in hooks/hooks.json).

  hooks.py pre-tool        PreToolUse   Write|Edit|MultiEdit|NotebookEdit|Bash
  hooks.py post-tool       PostToolUse  Write|Edit|MultiEdit|NotebookEdit|Bash
  hooks.py stop            Stop
  hooks.py subagent-start  SubagentStart  ^gener8v:(code|quality|security)-reviewer$ | ^gener8v:defect-sweeper$
  hooks.py subagent-stop   SubagentStop   (same matcher)

Reads the hook JSON on stdin; prints a JSON decision or nothing. Run through scripts/hook.sh, which
exits silently outside a project with .gener8v/ and when python3 is missing. Every failure inside is
swallowed: a hook that crashes interrupts the session it was meant to help.

Why shell commands are covered: Claude edits files through Bash (sed -i, heredocs, redirects) as often
as through Write and Edit, so a guard or a regeneration that only watches the file tools is bypassed
half the time.

Why the reviewer rules live here: plugin agents ignore permissionMode and hooks in their own
frontmatter, so "your only write is the report" cannot be enforced in agents/*.md.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "gener8v-state.py")
FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
REVIEWERS = {"gener8v:code-reviewer", "gener8v:quality-reviewer", "gener8v:security-reviewer"}
SWEEPER = "gener8v:defect-sweeper"
DERIVED = {".gener8v/pipeline-state.yaml", ".gener8v/runs.jsonl"}
DOC_EXT = (".md", ".markdown", ".txt", ".yaml", ".yml", ".json", ".toml", ".lock")

# A shell command that writes to the state file: a redirect or tee into it, an in-place edit, a copy or
# move onto it, a delete, or a script opening it for writing. Reading it (cat, grep, yq) is fine.
STATE_WRITE = re.compile(
    r">\s*['\"]?[^\s;|&'\"]*pipeline-state\.yaml"
    r"|\btee\b[^|;&]*pipeline-state\.yaml"
    r"|\b(sed|perl|yq)\b[^|;&]*\s-[A-Za-z]*i[^|;&]*pipeline-state\.yaml"
    r"|\bdd\b[^|;&]*\bof=['\"]?[^\s;|&'\"]*pipeline-state\.yaml"
    r"|\b(cp|mv|install|ln)\b[^|;&]*pipeline-state\.yaml['\"]?\s*($|[;&|])"
    r"|\b(rm|truncate)\b[^|;&]*pipeline-state\.yaml"
    r"|open\([^)]*pipeline-state\.yaml[^)]*['\"][wax+]"
)
TEST_PATH = re.compile(
    r"(^|/)(tests?|__tests__|specs?|e2e)(/|$)"
    r"|(^|/)test_[^/]+$"
    r"|[._-](test|spec)\.[A-Za-z0-9]+$"
    r"|Tests?\.[A-Za-z]+$"
)
IN_PROGRESS = re.compile(r"^\*\*Status:\*\*\s*In Progress", re.M)


def emit(obj):
    sys.stdout.write(json.dumps(obj) + "\n")


def project_root(d):
    return os.environ.get("CLAUDE_PROJECT_DIR") or d.get("cwd") or os.getcwd()


def rel_to(root, path):
    if not path:
        return ""
    p = path if os.path.isabs(path) else os.path.join(root, path)
    return os.path.relpath(os.path.normpath(p), root)


def under_gener8v(rel):
    return rel == ".gener8v" or rel.startswith(".gener8v" + os.sep)


def data_dir():
    d = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(tempfile.gettempdir(), "gener8v-hooks")
    os.makedirs(d, exist_ok=True)
    return d


def log_run(root, event, **fields):
    line = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event}
    line.update(fields)
    try:
        with open(os.path.join(root, ".gener8v", "runs.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(line) + "\n")
    except OSError:
        pass


def regenerate(root):
    subprocess.run([sys.executable, STATE, "state", "--root", root, "--quiet"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)


def working_tree(root):
    """{path: [mtime, size]} for every modified, added or untracked file outside .gener8v/, or None
    when the project is not a git repository."""
    try:
        out = subprocess.run(["git", "-C", root, "status", "--porcelain", "-z", "--untracked-files=all"],
                             capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    entries, tree = out.stdout.decode("utf-8", "replace").split("\0"), {}
    i = 0
    while i < len(entries):
        e = entries[i]
        i += 1
        if len(e) < 4:
            continue
        code, path = e[:2], e[3:]
        if code[0] in "RC":  # rename/copy: the next entry is the source path
            i += 1
        if under_gener8v(path):
            continue
        try:
            st = os.stat(os.path.join(root, path))
            tree[path] = [st.st_mtime, st.st_size]
        except OSError:
            tree[path] = [None, None]  # deleted
    return tree


# --- PreToolUse -------------------------------------------------------------------------------

def pre_tool(d):
    root, tool = project_root(d), d.get("tool_name", "")
    ti, agent = d.get("tool_input") or {}, d.get("agent_type") or ""
    regen = f"python3 {STATE} state"

    if tool == "Bash":
        cmd = ti.get("command", "")
        if "pipeline-state.yaml" in cmd and "gener8v-state.py" not in cmd and STATE_WRITE.search(cmd):
            return deny(f".gener8v/pipeline-state.yaml is generated; a shell command cannot edit it either. "
                        f"Change the artifact it is derived from, or regenerate it: {regen}")
        return None  # a reviewer's shell writes are caught at SubagentStop

    rel = rel_to(root, ti.get("file_path") or ti.get("notebook_path") or "")
    if not rel or rel.startswith(".."):
        return None
    if rel in (".gener8v/pipeline-state.yaml",):
        return deny(f".gener8v/pipeline-state.yaml is generated. Change the artifact it is derived from, "
                    f"or regenerate it: {regen} — /gener8v:orchestrate runs the same thing.")
    if agent in REVIEWERS and not under_gener8v(rel):
        return deny(f"{agent} writes only its review report under .gener8v/, and {rel} is outside it. "
                    "Record what is wrong as a finding with a recommendation; the fix belongs to the "
                    "resolution phase in the main session.")
    if agent == SWEEPER and not under_gener8v(rel) and not TEST_PATH.search(rel):
        return deny(f"{agent} writes only the sweep report under .gener8v/sweeps/ and, as proof of a "
                    f"finding, a failing test. {rel} is neither. A sweep that edits code has stopped being a sweep.")
    if under_gener8v(rel) or rel.endswith(DOC_EXT) or os.path.basename(rel) == "CLAUDE.md" or agent == SWEEPER:
        return None
    if not in_progress_records(root):
        emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext":
              "gener8v: no delivery is In Progress. Trivial fixes (typo, formatting, config) are fine; "
              "anything else should be a ticket delivered via /delivery so it gets @spec traceability and reviews."}})
    return None


def deny(reason):
    emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                 "permissionDecisionReason": reason}})


def in_progress_records(root):
    g = os.path.join(root, ".gener8v")
    found = []
    for p in glob.glob(os.path.join(g, "changes", "*", "delivery", "*-delivery.md")) + \
             glob.glob(os.path.join(g, "delivery", "*-delivery.md")):
        try:
            with open(p, encoding="utf-8") as fh:
                if IN_PROGRESS.search(fh.read(4000)):
                    found.append(p)
        except OSError:
            pass
    return found


# --- PostToolUse ------------------------------------------------------------------------------

def post_tool(d):
    root, tool = project_root(d), d.get("tool_name", "")
    g = os.path.join(root, ".gener8v")
    if tool in FILE_TOOLS:
        ti = d.get("tool_input") or {}
        rel = rel_to(root, ti.get("file_path") or ti.get("notebook_path") or "")
        if under_gener8v(rel) and rel not in DERIVED:
            regenerate(root)
            log_run(root, "artifact_write", path=rel)
        return
    if tool == "Bash":
        # The command's text says little about what it wrote, so ask the directory: regenerate when any
        # artifact is newer than the state file. The state file is rewritten on every regeneration, so
        # this fires once per change, not on every later command.
        state = os.path.join(g, "pipeline-state.yaml")
        since = os.path.getmtime(state) if os.path.exists(state) else 0
        for dirpath, _, files in os.walk(g):
            for f in files:
                p = os.path.join(dirpath, f)
                rel = os.path.relpath(p, root)
                if rel in DERIVED:
                    continue
                try:
                    newer = os.path.getmtime(p) > since
                except OSError:
                    continue
                if newer:
                    regenerate(root)
                    log_run(root, "artifact_write", path=rel, via="Bash")
                    return


# --- Stop -------------------------------------------------------------------------------------

def stop(d):
    """Delivery keeps its record current from plan approval onward. When a record is In Progress and
    source files changed after it was last written, send the turn back once to update it. Each change is
    reported once per session, so unrelated work alongside an open delivery is not nagged every turn."""
    if d.get("stop_hook_active"):
        return
    root = project_root(d)
    records = in_progress_records(root)
    if not records:
        return
    newest = max(os.path.getmtime(r) for r in records)
    tree = working_tree(root)
    if not tree:
        return
    marker = os.path.join(data_dir(), f"stop-{d.get('session_id', 'session')}.json")
    try:
        with open(marker, encoding="utf-8") as fh:
            reported = json.load(fh)
    except (OSError, ValueError):
        reported = {}
    stale = sorted(p for p, (mtime, _) in tree.items()
                   if mtime and mtime > newest and not p.endswith(DOC_EXT) and reported.get(p) != mtime)
    if not stale:
        return
    reported.update({p: tree[p][0] for p in stale})
    with open(marker, "w", encoding="utf-8") as fh:
        json.dump(reported, fh)
    names = ", ".join(os.path.relpath(r, root) for r in records)
    shown = ", ".join(stale[:5]) + (f" and {len(stale) - 5} more" if len(stale) > 5 else "")
    emit({"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext":
          f"gener8v: source changed after the In Progress delivery record was last updated ({names}): {shown}. "
          "Update the record's Progress — and Decisions Made or Deviations from Plan where they apply — before "
          "finishing. If these changes are not part of that delivery, say so in one line and stop."}})


# --- Reviewer agents --------------------------------------------------------------------------

def snapshot_path(d):
    return os.path.join(data_dir(), f"subagent-{d.get('agent_id', 'unknown')}.json")


def subagent_start(d):
    tree = working_tree(project_root(d))
    if tree is None:
        return
    with open(snapshot_path(d), "w", encoding="utf-8") as fh:
        json.dump(tree, fh)


def subagent_stop(d):
    snap = snapshot_path(d)
    try:
        with open(snap, encoding="utf-8") as fh:
            before = json.load(fh)
    except (OSError, ValueError):
        return
    after = working_tree(project_root(d)) or {}
    agent = d.get("agent_type", "")
    # Reviewers run in the background, so the main session may be editing while one works. A file counts
    # against the reviewer only when one of its own shell commands names it; file-tool writes were already
    # refused at PreToolUse.
    commands = agent_shell_commands(d.get("agent_transcript_path"))
    changed = sorted(p for p in set(before) | set(after)
                     if before.get(p) != after.get(p)
                     and not (agent == SWEEPER and TEST_PATH.search(p))
                     and any(p in c or os.path.basename(p) in c for c in commands))
    if not changed:
        os.remove(snap)
        return
    dirty = [p for p in changed if p in before]
    shown = ", ".join(changed[:8]) + (f" and {len(changed) - 8} more" if len(changed) > 8 else "")
    if d.get("stop_hook_active"):
        os.remove(snap)
        emit({"systemMessage": f"{agent} finished with changes outside .gener8v/ it should not have made: {shown}. "
                               "Check them before trusting the working tree."})
        return
    keep = (" These files already had uncommitted changes when you started, so undo only your own edits — "
            "do not git checkout or git restore them: " + ", ".join(dirty[:8]) + ".") if dirty else ""
    emit({"decision": "block", "reason":
          f"You changed files outside .gener8v/: {shown}. Your only write is the report"
          + (" (and, for a sweep, a failing test as proof)" if agent == SWEEPER else "")
          + ". Undo those changes, then finish." + keep})


def agent_shell_commands(transcript):
    """Every Bash command the subagent ran, from its own transcript."""
    commands = []
    try:
        with open(os.path.expanduser(transcript or ""), encoding="utf-8") as fh:
            for line in fh:
                try:
                    msg = json.loads(line).get("message") or {}
                except ValueError:
                    continue
                for part in msg.get("content") or []:
                    if isinstance(part, dict) and part.get("type") == "tool_use" and part.get("name") == "Bash":
                        commands.append(str((part.get("input") or {}).get("command", "")))
    except OSError:
        pass
    return commands


def main():
    try:
        d = json.load(sys.stdin)
    except ValueError:
        return 0
    handlers = {"pre-tool": pre_tool, "post-tool": post_tool, "stop": stop,
                "subagent-start": subagent_start, "subagent-stop": subagent_stop}
    handler = handlers.get(sys.argv[1] if len(sys.argv) > 1 else "")
    if handler:
        try:
            handler(d)
        except Exception:  # never break the session over a hook
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
