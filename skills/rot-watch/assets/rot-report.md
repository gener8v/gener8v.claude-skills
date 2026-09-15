# [Subsystem or Repository] — Rot Watch YYYY-MM-DD

## Verdict

[One of: **Holding** — nothing moved in the wrong direction · **Drifting** — movement worth
correcting before it compounds · **Rotting** — a declared boundary is now violated]

## Overview

[2-3 sentences. What was watched, over which interval, how many deliveries since the last
watch, and the single most consequential movement.]

## Source Context

**Baseline:** `.gener8v/rot/baseline.md` recorded YYYY-MM-DD · **Interval:** N deliveries, tickets [list]
**Technical Design:** [file, or "Not yet performed — drift measured against observed shape only"]
**Watched:** [paths]

## Movements

[Only what moved, and only in the wrong direction. A metric that improved is listed under
Improvements. A metric that did not move is not listed at all — an unchanged number is not a
finding, and listing it buries the ones that are.]

### ROT-001: [What moved]

**Signal:** [Which of the six checks below]
**Movement:** [from → to, with the interval] — e.g. `core/kg/retrieve/expand.py: 180 → 520 lines over 4 deliveries`
**Attributed to:** [ticket IDs from delivery records, where attributable]
**Why it matters:** [The consequence if the trend continues — not a restatement of the metric]
**Correction:** [What to do, concretely. A movement without a correction is an observation, not a finding]
**Severity:** [Breach / Drift / Watch]

## Improvements

[Movement in the right direction, briefly. Recording it is what keeps the report honest —
a report that only ever lists decay reads as noise and gets ignored.]

## Baseline Delta Summary

| Signal | Baseline | Now | Direction |
|---|---|---|---|
| Longest file in scope | | | |
| Modules importing outside their layer | | | |
| Dependency cycles | | | |
| Source-to-test ratio | | | |
| NFR verifications live | | | |
| `@spec` annotations | | | |
| Deferred markers (TODO/FIXME/XXX) | | | |

## Not Watched

[What this run could not check, and why. A watch that silently skips a subsystem is worse
than one that says it skipped it.]
