#!/usr/bin/env bash
# Entry point for the hooks in scripts/hooks.py: hook.sh <pre-tool|post-tool|stop|subagent-start|subagent-stop>
#
# Silent outside a project with .gener8v/, and when python3 is missing — the plugin is installed per
# user, so these hooks fire in every project, and most of them are not on the pipeline.
set -u
ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -d "$ROOT/.gener8v" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/hooks.py" "$@"
