# Provenance: Pre-Flight Reconciliation + Known Hazards

**Date:** 2026-05-26
**Status:** Draft — context behind the `skills/reconciliation-and-hazards` changes
**Skills touched:** `delivery`, `audit`, `ticket-breakdown`, plus a `README` design principle

## What prompted this

A real engagement: reviewing an externally-authored build-prompt set (a six-segment "Phase 6" plan — six phase plans + 25 ready-to-run Claude Code prompts + a governance `CLAUDE.md`) and judging how executable it actually was against the target codebase. The prompt set was unusually high quality — front-loaded "Critical Notes," testable acceptance criteria, named reuse contracts, an explicit source-of-truth hierarchy. As *artifacts*, they were excellent.

The problem surfaced only when we stopped reading the artifacts and **read the code.**

## What the code said that the plan didn't

The plan's stated premise was "overwhelmingly build-on-existing-schema; the prior phase put the schema in place." Verified against the actual repo (`shared/schema.ts`, `migrations/`, `package.json`, `infra/`):

- **Schema objects the plan assumed didn't exist** — a required enum/column and a whole table the correctness-critical flow writes to were absent, and never appeared in any migration (net-new prerequisites, not drift). Several prompts' own pre-work checks would hard-stop on day one.
- **The gate script every prompt invokes (`scripts/pre-build-gate.sh`) didn't exist.** Literal step one failed.
- **The primary specs for four of six segments, and all the governance logs the closure prompts edit, were not in the repo;** the supporting docs that were present were version-stale vs. what the prompts pinned.
- **Two "Decision Points" flagged for the human were already settled by the code** — one by a `NOT NULL` column, one by an existing dependency. They never needed escalation.

The single most valuable feature of the prompts — the thing that most reduced confident-wrong builds — was the **"Critical Note" header** that named supersessions and spec conflicts *before* the work.

## What generalized into the pipeline

| Learning | Change |
|---|---|
| A plan's premises are claims to verify against ground truth, not facts to trust | **Delivery**: new lead principle + a three-phase model (Reconcile → Plan → Execute) with a Pre-Flight Reconciliation table and a Blocked-before-planning gate. **Audit**: new "Reconciliation Audit (artifact vs. reality)" mode + Ground-Truth Reconciliation checks. **README**: "Verify against ground truth before escalating" design principle. |
| Resolve from code what the code can answer; escalate only what's genuinely undecided | Same principle; reconciliation explicitly records decisions closed by the code rather than passing them to the user. |
| Front-load the traps | **Ticket Breakdown**: new `Known Hazards` field (supersessions / cross-doc conflicts / schema gotchas, each with a resolution) + principle + process step. |
| Ceremony should track correctness risk, not artifact count | **README**: Scale Guidance refinement. |

## Open thoughts (not yet acted on)

- Reconciliation now lives in two places by design — inline in Delivery (self-check every build) and as a standalone Audit mode (vet an externally-authored plan before it enters delivery). Watch whether the duplication earns its keep or should consolidate.
- The Brownfield skill maps code→artifacts; Reconciliation is the inverse-direction *check* (artifact→code). There may be a tighter integration between the two worth designing later.
- Consider whether `orchestrate`/`pipeline-state.yaml` should carry a per-ticket reconciliation verdict so a Blocked-on-prereq ticket is visible at the pipeline level.
