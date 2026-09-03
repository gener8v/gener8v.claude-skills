---
name: watch
description: See every local Claude Code session from one terminal (macOS). Installs a Notification hook that logs a line and raises a banner whenever any session is waiting on you, shows recent alerts, and follows a live feed of every session's messages. Runs only when the user types /macos:watch.
argument-hint: [--install] [--uninstall] [--alerts N] [--feed MINS]
disable-model-invocation: true
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/skills/watch/watch.sh:*)
---

The watch script has already run with the user's arguments. Its output:

!`${CLAUDE_PLUGIN_ROOT}/skills/watch/watch.sh --relay $ARGUMENTS 2>&1`

Relay the outcome to the user in one or two lines. Rules:

- Do not run the script again and do not try any other approach.
- With no arguments the output is a status report: say whether the hook is installed, how many sessions are live, and — only if the hook is missing — that `/macos:watch --install` turns it on.
- After `--install`, say that every session will now log a line and raise a banner when it needs the user, and give them the `tail -f` command from the output verbatim. Mention that sessions already running pick the hook up too; no restarts.
- After `--uninstall`, confirm the settings entry is gone and that the notifier script was left on disk.
- If the output says jq is missing, quote the `brew install jq` line and stop.
- The last line of a status report is the `--feed` command. It is long-running and never returns, so **never run it yourself** — print it for the user to run in their own terminal.
- If the output is an error about settings.json not being valid JSON, say nothing was changed and let the user fix the file.
