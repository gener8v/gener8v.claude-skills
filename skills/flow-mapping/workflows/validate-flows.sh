#!/usr/bin/env bash
# Validate mermaid flow diagrams: compilation (hard gate) + structural clarity/maturity lints.
#
# Usage:  validate-flows.sh <file.md|file.mmd> [...]
#
# Extracts every ```mermaid fence from Markdown (or treats a .mmd as one diagram), compiles each
# with mmdc, and runs the structural lints that do not need an LLM. Exit 1 if any diagram fails
# compilation or any ERROR lint fires. WARN lints report but do not fail.
#
# Compilation is the only gate that is fully decidable here. Clarity/maturity checks that need
# judgement (is this label meaningful? is this flow evidenced?) belong to the SKILL.md rubric —
# this script covers the mechanical subset so the LLM pass is not spent on what a regex can catch.

set -uo pipefail

MMDC=(npx --yes @mermaid-js/mermaid-cli@11)
MAX_NODES="${MAX_NODES:-18}"      # above this a single diagram stops being readable — split it
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
rc=0

fail() { echo "  ERROR $1"; rc=1; }
warn() { echo "  WARN  $1"; }

extract() {  # $1=src $2=outdir -> writes NNN.mmd per diagram
  local src="$1" out="$2"
  case "$src" in
    *.mmd) cp "$src" "$out/001.mmd" ;;
    *) awk -v out="$out" '
        /^[[:space:]]*```mermaid[[:space:]]*$/ { inb=1; n++; f=sprintf("%s/%03d.mmd", out, n); next }
        /^[[:space:]]*```[[:space:]]*$/        { inb=0; next }
        inb { print > f }
      ' "$src" ;;
  esac
}

lint() {  # $1=diagram file, $2=label
  local d="$1" label="$2"

  # --- compilation: the hard gate ---
  if ! "${MMDC[@]}" -i "$d" -o "$work/out.svg" >"$work/err.txt" 2>&1; then
    fail "$label does not compile:"
    sed -n '1,6p' "$work/err.txt" | sed 's/^/        /'
    return
  fi

  # --- clarity ---
  local nodes
  nodes=$(grep -oE '(^|[^A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*(\[|\(|\{)' "$d" \
          | sed -E 's/.*[^A-Za-z0-9_]([A-Za-z_][A-Za-z0-9_]*)(\[|\(|\{)/\1/' | sort -u | wc -l | tr -d ' ')
  [ "$nodes" -gt "$MAX_NODES" ] && warn "$label has $nodes nodes (>$MAX_NODES) — split by domain"
  [ "$nodes" -eq 0 ] && fail "$label declares no nodes"

  # An edge is any arrow form mermaid accepts, including the x/o arrowheads used to mark a broken
  # or non-arriving flow (-.-x, --x, --o). Matching only '-->' misses dotted and blocked edges and
  # reports genuinely-connected nodes as orphans.
  local EDGE_RE='(\-\->|\.\->|==>|\.\-x|\.\-o|\-\-x|\-\-o|\-\-[^-]|===)'
  grep -E "$EDGE_RE" "$d" > "$work/edges.txt" || true

  # Every edge should say WHAT moves. Mermaid carries a label either as -->|payload| or as a quoted
  # string between the arrow halves: -- "payload" --> / -. "payload" .-> / -. "payload" .-x .
  # Accept every form; matching only one dialect reports labelled edges as unlabelled.
  local LABEL_RE='\|[^|]+\||(\-\-|\-\.|==)[[:space:]]*"[^"]+"[[:space:]]*(\.)?(\-\->|\-\-x|\-\-o|\-\->|==>|\-x|\-o|\->)'
  local edges labelled
  edges=$(wc -l < "$work/edges.txt" | tr -d ' ')
  labelled=$(grep -cE "$LABEL_RE" "$work/edges.txt" || true)
  if [ "$edges" -gt 0 ] && [ "$labelled" -lt "$edges" ]; then
    warn "$label: $((edges - labelled))/$edges edge(s) unlabelled — state the payload"
  fi

  # Orphans: a declared node never referenced by an edge is usually a modelling slip — EXCEPT when
  # it is classed `isolated`, where having no flows IS the finding (an orphaned data store nothing
  # reads or writes). Warning on those inverts the meaning of the diagram.
  local n
  for n in $(grep -oE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*(\[|\(|\{)' "$d" \
             | sed -E 's/^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)(\[|\(|\{)/\1/' | sort -u); do
    grep -qE "(^|[^A-Za-z0-9_])$n([^A-Za-z0-9_]|$)" "$work/edges.txt" && continue
    grep -qE "^[[:space:]]*class[[:space:]]+([A-Za-z0-9_,]*,)?$n(,[A-Za-z0-9_,]*)?[[:space:]]+isolated" "$d" \
      && continue  # deliberately isolated — the point of the node
    warn "$label: node '$n' is declared but never flows anywhere (and is not classed 'isolated')"
  done

  # --- maturity ---
  grep -q 'classDef' "$d" \
    || warn "$label: no classDef — reliability of each store/flow is unstated"
  if grep -q 'classDef' "$d" && ! grep -qE '^[[:space:]]*class ' "$d"; then
    warn "$label: classDef declared but no node assigned to a class"
  fi
  # Cadence lives inside the edge label, whichever delimiter the diagram uses — scan the edge lines,
  # not just pipe-delimited text.
  grep -qiE '(nightly|daily|hourly|real[- ]?time|weekly|monthly|batch|on[- ]demand|manual|ad[- ]hoc|quarterly|annual)' \
    "$work/edges.txt" \
    || warn "$label: no cadence on any edge — a flow without timing is not current-state"
}

[ $# -eq 0 ] && { echo "usage: validate-flows.sh <file.md|file.mmd> [...]"; exit 2; }

for src in "$@"; do
  echo "== $src"
  [ -f "$src" ] || { fail "no such file"; continue; }
  d="$work/$(echo "$src" | tr '/.' '__')"; mkdir -p "$d"
  extract "$src" "$d"
  shopt -s nullglob
  found=("$d"/*.mmd)
  if [ ${#found[@]} -eq 0 ]; then
    warn "no mermaid diagrams found"
    continue
  fi
  for f in "${found[@]}"; do lint "$f" "$(basename "$f" .mmd)"; done
done

[ $rc -eq 0 ] && echo "OK — all diagrams compile" || echo "FAILED — fix ERRORs above"
exit $rc
