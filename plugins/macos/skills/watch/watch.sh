#!/bin/bash
# /macos:watch — see every local Claude Code session from one terminal.
#
#   watch.sh                 status: hook state, live sessions, recent alerts
#   watch.sh --install       install the "session wants you" Notification hook
#   watch.sh --uninstall     remove it
#   watch.sh --alerts [N]    last N alert lines (default 15)
#   watch.sh --feed [MINS]   live feed of every session's messages (long-running)
#   watch.sh --notify        hook entry point; reads the hook JSON on stdin
#   --relay                  always exit 0, so the skill can relay any message
set -u

LOG="$HOME/.claude/session-alerts.log"
NOTIFIER="$HOME/.claude/hooks/macos-session-alert.sh"
SETTINGS="$HOME/.claude/settings.json"
PROJECTS="$HOME/.claude/projects"
RELAY=0
CMD=""
ARG=""

for a in "$@"; do
  case "$a" in
    --relay)          RELAY=1 ;;
    --install)        CMD=install ;;
    --uninstall)      CMD=uninstall ;;
    --alerts)         CMD=alerts ;;
    --feed)           CMD=feed ;;
    --notify)         CMD=notify ;;
    --status)         CMD=status ;;
    -h|--help)        CMD=help ;;
    -*)               echo "Unknown option: $a  (try --help)" >&2; [ "$RELAY" = 1 ] && exit 0; exit 2 ;;
    *)                ARG="$a" ;;
  esac
done
[ -n "$CMD" ] || CMD=status

die() { echo "$@" >&2; [ "$RELAY" = 1 ] && exit 0; exit 1; }
command -v jq >/dev/null 2>&1 || die "jq is required but not on PATH. Install it with: brew install jq"

# ---------------------------------------------------------------- feed filter
# One line per message. Emits "<sortable ts>\t<display line>"; callers cut -f2-.
FILTER='
  select(.type == "user" or .type == "assistant")
  | (.cwd // "" | split("/") | last // "?")   as $proj
  | (.timestamp // "")                         as $ts
  | (if .type == "user" then
       (.message.content
        | if type == "string" then .
          else [.[]? | select(.type == "text") | .text] | join(" ") end)
     else
       [.message.content[]?
        | if .type == "text" then .text
          elif .type == "tool_use" then "[\(.name)]"
          else empty end] | join(" ")
     end)                                      as $raw
  | ($raw | gsub("\\s+"; " ") | ltrimstr(" ")) as $txt
  | select($txt != "" and ($txt | startswith("<") | not))
  | "\($ts)\t\($ts[11:19])  \(($proj + "                              ")[0:30])  \(if .type == "user" then "›" else "‹" end) \($txt[0:150])"
'

# Populate FILES with transcripts touched in the last $1 minutes.
collect_files() {
  FILES=()
  while IFS= read -r f; do
    [ -n "$f" ] && FILES+=("$f")
  done < <(find "$PROJECTS" -name '*.jsonl' -mmin "-$1" 2>/dev/null)
}

hook_installed() {
  [ -f "$SETTINGS" ] || return 1
  jq -e '
    [ (.hooks.Notification // [])[]? | .hooks[]? | .command // "" ]
    | any(contains("macos-session-alert.sh"))
  ' "$SETTINGS" >/dev/null 2>&1
}

# ------------------------------------------------------------------- commands
case "$CMD" in

help)
  sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
  ;;

notify)
  payload=$(cat)
  cwd=$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)
  msg=$(printf '%s' "$payload" | jq -r '.message // empty' 2>/dev/null)
  sid=$(printf '%s' "$payload" | jq -r '.session_id // .sessionId // empty' 2>/dev/null)
  proj=$(basename "${cwd:-unknown}")
  msg=${msg:-waiting for input}
  mkdir -p "$(dirname "$LOG")"
  printf '%s  %-38s  %-8s  %s\n' \
    "$(date '+%m-%d %H:%M:%S')" "$proj" "${sid:0:8}" "$msg" >> "$LOG"
  osascript -e 'on run argv
display notification (item 1 of argv) with title (item 2 of argv)
end run' "$msg" "Claude · $proj" >/dev/null 2>&1 &
  exit 0
  ;;

install)
  mkdir -p "$HOME/.claude/hooks"
  # Standalone copy: settings.json must not point into the versioned plugin
  # cache, which moves on every plugin update.
  cat > "$NOTIFIER" <<'NOTIFY'
#!/bin/bash
# Installed by /macos:watch --install. Notification hook: record when a Claude
# Code session is waiting on you. Safe to delete; /macos:watch --uninstall
# removes the settings entry that calls it.
set -u
LOG="$HOME/.claude/session-alerts.log"
payload=$(cat)
cwd=$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)
msg=$(printf '%s' "$payload" | jq -r '.message // empty' 2>/dev/null)
sid=$(printf '%s' "$payload" | jq -r '.session_id // .sessionId // empty' 2>/dev/null)
proj=$(basename "${cwd:-unknown}")
msg=${msg:-waiting for input}
mkdir -p "$(dirname "$LOG")"
printf '%s  %-38s  %-8s  %s\n' \
  "$(date '+%m-%d %H:%M:%S')" "$proj" "${sid:0:8}" "$msg" >> "$LOG"
osascript -e 'on run argv
display notification (item 1 of argv) with title (item 2 of argv)
end run' "$msg" "Claude · $proj" >/dev/null 2>&1 &
exit 0
NOTIFY
  chmod +x "$NOTIFIER"

  [ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
  jq -e . "$SETTINGS" >/dev/null 2>&1 || die "$SETTINGS is not valid JSON — fix it first, nothing was changed."

  tmp="${SETTINGS}.watch.$$"
  jq --arg cmd "$NOTIFIER" '
    .hooks //= {}
    | .hooks.Notification //= []
    | .hooks.Notification |= (
        map(select((.hooks // []) | map(.command // "") | any(contains("macos-session-alert.sh")) | not))
        + [{hooks: [{type: "command", command: $cmd, timeout: 5}]}]
      )
  ' "$SETTINGS" > "$tmp" \
    && jq -e . "$tmp" >/dev/null 2>&1 \
    && mv "$tmp" "$SETTINGS" \
    || { rm -f "$tmp"; die "Failed to update $SETTINGS — nothing was changed."; }

  echo "Installed."
  echo "  notifier  $NOTIFIER"
  echo "  settings  $SETTINGS  (hooks.Notification)"
  echo "  log       $LOG"
  echo
  echo "Sessions log a line and raise a banner whenever they need you."
  echo "Watch the log:  tail -f $LOG"
  ;;

uninstall)
  [ -f "$SETTINGS" ] || die "No $SETTINGS — nothing to remove."
  hook_installed || { echo "Not installed; nothing to remove."; exit 0; }
  tmp="${SETTINGS}.watch.$$"
  jq '
    .hooks.Notification |= (
      map(select((.hooks // []) | map(.command // "") | any(contains("macos-session-alert.sh")) | not))
    )
    | if (.hooks.Notification | length) == 0 then del(.hooks.Notification) else . end
    | if (.hooks | length) == 0 then del(.hooks) else . end
  ' "$SETTINGS" > "$tmp" \
    && jq -e . "$tmp" >/dev/null 2>&1 \
    && mv "$tmp" "$SETTINGS" \
    || { rm -f "$tmp"; die "Failed to update $SETTINGS — nothing was changed."; }
  echo "Removed the Notification hook from $SETTINGS."
  echo "The notifier script is still at $NOTIFIER — delete it if you want it gone."
  ;;

alerts)
  n="${ARG:-15}"
  [ -s "$LOG" ] || { echo "No alerts logged yet ($LOG)."; hook_installed || echo "The hook is not installed — run /macos:watch --install."; exit 0; }
  echo "Last $n alerts — $LOG"
  tail -n "$n" "$LOG"
  ;;

feed)
  mins="${ARG:-240}"
  collect_files "$mins"
  [ "${#FILES[@]}" -gt 0 ] || die "No session transcripts written in the last $mins minutes."
  echo "── ${#FILES[@]} session(s), last 25 messages then live; Ctrl-C to stop ──" >&2
  for f in "${FILES[@]}"; do
    tail -n 80 "$f" 2>/dev/null | jq -r "$FILTER" 2>/dev/null
  done | sort | tail -n 25 | cut -f2-
  echo "── live ──" >&2
  tail -q -n 0 -F "${FILES[@]}" 2>/dev/null | jq -r --unbuffered "$FILTER" 2>/dev/null | cut -f2-
  ;;

status)
  echo "Claude Code session watch"
  echo
  if hook_installed; then
    echo "  Hook       installed  ($NOTIFIER)"
  else
    echo "  Hook       NOT installed — run /macos:watch --install"
  fi
  if [ -s "$LOG" ]; then
    echo "  Log        $LOG  ($(wc -l < "$LOG" | tr -d ' ') alerts)"
  else
    echo "  Log        $LOG  (empty)"
  fi
  collect_files 240
  echo "  Sessions   ${#FILES[@]} active in the last 4h"
  echo
  if [ "${#FILES[@]}" -gt 0 ]; then
    echo "Active projects:"
    for f in "${FILES[@]}"; do
      tail -n 1 "$f" 2>/dev/null | jq -r '.cwd // empty' 2>/dev/null
    done | sed 's|.*/||' | sort -u | sed 's/^/  /'
    echo
  fi
  if [ -s "$LOG" ]; then
    echo "Recent alerts:"
    tail -n 5 "$LOG" | sed 's/^/  /'
    echo
  fi
  echo "Live feed (long-running, Ctrl-C to stop):"
  echo "  $0 --feed"
  ;;

*)
  die "Unknown command: $CMD"
  ;;
esac
exit 0
