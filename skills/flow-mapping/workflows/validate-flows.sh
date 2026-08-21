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
EDGE_RE='(\-\->|\.\->|==>|\.\-x|\.\-o|\-\-x|\-\-o|\-\-[^-]|===)'
MAX_NODES="${MAX_NODES:-18}"      # above this a single diagram stops being readable — split it
case "$MAX_NODES" in
  ''|*[!0-9]*) echo "MAX_NODES must be a whole number (got '$MAX_NODES')" >&2; exit 2 ;;
esac
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

# Every node id in a diagram, one per line, declared or implicit.
#
# Mermaid declares a node either with a shape — Name["label"] — or simply by naming it at
# one end of an edge. Both are nodes. Counting only the bracketed form reported a valid
# two-node diagram as declaring none.
#
# Labels are stripped before identifiers are read, or a word inside "member number | batch"
# becomes a node. Arrow operators are stripped whole, longest first, so the `x` and `o`
# arrowheads in `--x` / `-.-o` are not mistaken for node names.
node_names() {  # $1=diagram file
  local d="$1"
  grep -oE '(^|[^A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*(\[|\(|\{)' "$d" \
    | sed -E 's/.*[^A-Za-z0-9_]?([A-Za-z_][A-Za-z0-9_]*)(\[|\(|\{)/\1/'
  grep -E "$EDGE_RE" "$d" \
    | sed -E 's/"[^"]*"/ /g; s/\|[^|]*\|/ /g' \
    | sed -E 's/(\-\.\-[>xo]?|\-\-[>xo]|==+>|===+|\-\-|\-\.\-|\.\->)/ /g' \
    | grep -oE '(^|[^A-Za-z0-9_])[A-Za-z_][A-Za-z0-9_]*' \
    | sed -E 's/^[^A-Za-z_]+//' \
    | grep -vxE '(graph|flowchart|subgraph|end|class|classDef|style|click|linkStyle|direction|TD|TB|BT|LR|RL|o|x)'
}

lint() {  # $1=diagram file, $2=label
  local d="$1" label="$2"

  # --- compilation: the hard gate ---
  if ! "${MMDC[@]}" -i "$d" -o "$work/out.svg" >"$work/err.txt" 2>&1; then
    fail "$label does not compile:"
    sed -n '1,6p' "$work/err.txt" | sed 's/^/        /'
    local errlines
    errlines=$(wc -l < "$work/err.txt" | tr -d ' ')
    # Say what was cut. Six silent lines of a forty-line parse error reads as the whole
    # message, and the part naming the offending token is usually further down.
    [ "$errlines" -gt 6 ] && echo "        … $((errlines - 6)) more line(s); rerun mmdc on the block for the rest"
    return
  fi

  # An edge is any arrow form mermaid accepts, including the x/o arrowheads used to mark a broken
  # or non-arriving flow (-.-x, --x, --o). Matching only '-->' misses dotted and blocked edges and
  # reports genuinely-connected nodes as orphans.
  grep -E "$EDGE_RE" "$d" > "$work/edges.txt" || true

  # --- clarity ---
  # Count nodes DECLARED with a shape and nodes that exist only as edge endpoints.
  # `A --> B` declares two nodes: mermaid does not require a shape, and counting only
  # bracketed forms called a valid two-node diagram empty — failing the hard gate on the
  # very draft SKILL.md's example describes as one that compiles.
  local nodes
  nodes=$(node_names "$d" | sort -u | wc -l | tr -d ' ')
  [ "$nodes" -gt "$MAX_NODES" ] && warn "$label has $nodes nodes (>$MAX_NODES) — split by domain"
  [ "$nodes" -eq 0 ] && fail "$label declares no nodes"

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
