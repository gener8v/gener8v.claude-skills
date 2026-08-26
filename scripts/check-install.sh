#!/usr/bin/env bash
# Report drift between this repository's skills/ and a copied install in ~/.claude/skills/.
# The copy route (README "Skills only") has no update mechanism; this makes drift visible.
#
# Usage: scripts/check-install.sh [install-dir]   (default: ~/.claude/skills)
# Exit 0 when identical, 1 when anything differs, is missing, or is extra.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL="${1:-$HOME/.claude/skills}"
rc=0
[ -d "$INSTALL" ] || { echo "no install directory at $INSTALL"; exit 1; }

for d in "$HERE"/skills/*/; do
  name="$(basename "$d")"
  if [ ! -d "$INSTALL/$name" ]; then
    echo "MISSING  $name  (in repo, not installed)"; rc=1; continue
  fi
  if ! diff -rq "$d" "$INSTALL/$name" >/dev/null 2>&1; then
    echo "DIFFERS  $name"; diff -rq "$d" "$INSTALL/$name" | sed 's/^/           /'; rc=1
  fi
done
for d in "$INSTALL"/*/; do
  name="$(basename "$d")"
  [ -f "$d/SKILL.md" ] || continue
  if [ ! -d "$HERE/skills/$name" ] && grep -q '\.gener8v/' "$d/SKILL.md" 2>/dev/null; then
    echo "EXTRA    $name  (installed, writes to .gener8v/, not in repo)"; rc=1
  fi
done
[ $rc -eq 0 ] && echo "OK — installed skills match the repository" || echo "Drift found. Prefer the plugin install (README) so exactly one copy exists."
exit $rc
