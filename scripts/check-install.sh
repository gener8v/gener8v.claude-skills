#!/usr/bin/env bash
# Report how the gener8v skills are installed on this machine and whether a copied install drifts.
#
#   plugin present  -> lists any copies still lingering in ~/.claude/skills/ (they shadow the plugin's
#                      skills as /<skill> next to /gener8v:<skill> and never update)
#   no plugin       -> diffs skills/ in this repo against a copied ~/.claude/skills/ install
#
# Usage: scripts/check-install.sh [install-dir]   (default: ~/.claude/skills)
# Exit 0 when nothing lingers/differs, 1 otherwise.
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL="${1:-$HOME/.claude/skills}"
CACHE="$HOME/.claude/plugins/cache/gener8v-claude-skills/gener8v"
rc=0

if [ -d "$CACHE" ] && ls "$CACHE" >/dev/null 2>&1 && [ -n "$(ls "$CACHE" 2>/dev/null)" ]; then
  ver="$(ls "$CACHE" | sort -V | tail -1)"
  echo "plugin: gener8v $ver installed ($CACHE/$ver)"
  for d in "$HERE"/skills/*/; do
    name="$(basename "$d")"
    if [ -d "$INSTALL/$name" ]; then
      echo "LINGERS  $INSTALL/$name  (copied install shadows the plugin; move it aside)"; rc=1
    fi
  done
  [ $rc -eq 0 ] && echo "OK — no copied gener8v skills alongside the plugin" || echo "Move the listed directories out of $INSTALL (see README: Upgrading from a copied install)."
  exit $rc
fi

[ -d "$INSTALL" ] || { echo "no plugin install and no copied install at $INSTALL"; exit 1; }
echo "plugin: not installed — checking the copied install at $INSTALL"
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
