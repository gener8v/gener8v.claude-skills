# Rot Watch — worked example

Two runs over the same subsystem: the recording run, and a watch three deliveries later.

## Run 1 — recording (no baseline existed)

````markdown
# Retrieval — Rot Watch 2026-03-02

## Verdict
**Holding**

## Overview
First run over `core/kg/retrieve/`. No baseline existed, so this run recorded one and found
nothing — not because nothing is wrong, but because rot is a movement and there is nothing yet to
measure movement against. The next watch, after an interval of deliveries, is the first that can
report.

## Source Context
**Baseline:** none — recorded by this run · **Interval:** n/a
**Technical Design:** `technical-design/system-design.md`
**Watched:** `core/kg/retrieve/`

## Movements
None — see Overview.

## Baseline Delta Summary
| Signal | Baseline | Now | Direction |
|---|---|---|---|
| Longest file in scope | — | 212 (`fuse.py`) | recorded |
| Modules importing outside their layer | — | 0 | recorded |
| Dependency cycles | — | 0 | recorded |
| Source-to-test ratio | — | 1.4 : 1 | recorded |
| NFR verifications live | — | 3 of 5 | recorded |
````

## Run 2 — a watch, three deliveries later

````markdown
# Retrieval — Rot Watch 2026-03-21

## Verdict
**Rotting** — a declared boundary is now violated.

## Overview
Three deliveries since 2026-03-02. One architecture decision no longer holds: `expand.py` now
imports the embedding client directly, inverting the dependency AD-002 declared. Two further
movements are drift rather than breach. One ratio improved.

## Source Context
**Baseline:** `.gener8v/rot/baseline.md` recorded 2026-03-02 · **Interval:** 3 deliveries, TICKET-005, TICKET-006, TICKET-007
**Technical Design:** `technical-design/system-design.md`
**Watched:** `core/kg/retrieve/`

## Movements

### ROT-001: Expansion now depends directly on the embedding client
**Signal:** 2 — Separation
**Movement:** `core/kg/retrieve/expand.py` gained `from kg.embed.client import EmbeddingClient`; the
baseline had expansion depending only on the graph store.
**Attributed to:** TICKET-006
**Why it matters:** AD-002 puts traversal behind the graph store precisely so the budget is carried
in the recursion. A direct client dependency means a future change can re-embed mid-traversal, and
the per-relation budget stops being the only thing bounding the walk.
**Correction:** Move the call behind the store's traversal interface, or amend AD-002 and say why.
**Severity:** Breach

### ROT-002: `expand.py` is growing faster than the module around it
**Signal:** 4 — Extensibility
**Movement:** 180 → 520 lines over 3 deliveries; deepest branching 3 → 6.
**Attributed to:** TICKET-006, TICKET-007
**Why it matters:** Not long yet. Growing at this slope while gaining branch depth is the shape a
module takes shortly before it needs splitting under pressure rather than by choice.
**Correction:** Second data point at the next watch. If the slope holds, split the traversal from
the candidate assembly.
**Severity:** Watch

### ROT-003: An NFR assertion was weakened
**Signal:** 5 — Tests
**Movement:** `test_expand.py` changed `assert paths == expected` to `assert expected <= set(paths)`.
**Attributed to:** TICKET-007
**Why it matters:** IR-NFR-002 asserts expansion never returns a unit *beyond* the budget. A subset
assertion passes when extra units are returned, which is the exact failure the NFR exists to catch.
It passes CI and silently protects nothing.
**Correction:** Restore equality. If the test was weakened because expansion legitimately returns
more, the NFR is wrong and should be amended rather than the test loosened.
**Severity:** Breach

## Improvements
- Source-to-test ratio 1.4 : 1 → 1.1 : 1 — TICKET-005 landed with tests ahead of source
- `fuse.py` split into `fuse.py` and `rank.py`; longest file in scope 212 → 190

## Baseline Delta Summary
| Signal | Baseline | Now | Direction |
|---|---|---|---|
| Longest file in scope | 212 | 520 | ▲ worse |
| Modules importing outside their layer | 0 | 1 | ▲ worse |
| Dependency cycles | 0 | 0 | — |
| Source-to-test ratio | 1.4 : 1 | 1.1 : 1 | ▼ better |
| NFR verifications live | 3 of 5 | 3 of 5 | — (one weakened, see ROT-003) |

## Not Watched
`core/kg/embed/` — outside the named scope. ROT-001 touches its boundary; a watch over it would
say whether the inversion is one-sided.
````

## What to notice

- The recording run **reports nothing**, and says why. That is correct.
- `Dependency cycles` moved from 0 to 0 and is listed **only** in the delta table, never as a finding.
- **ROT-003 is the finding this skill exists for.** It passes CI. Code Review saw a green suite.
  Quality Review saw a test present. Only a comparison against what the test used to assert catches it.
- Improvements are recorded, so the report stays readable and a previous correction can be seen working.
