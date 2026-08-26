# Defect Sweep — worked example

### Input

> Sweep the generation stop controls in the generation service — pause, cancel, and the
> batch delete added this week.

### Output (abbreviated)

```markdown
# Generation stop controls: Defect Sweep

## Scope
Swept: `lib/scheduling/pause-gate.ts`, `lib/generation/pause-guard.ts`, the routes that
start engine work, `reconcileOverdueQueuedJobs`. Not swept: the engine itself, the GPU
lease.

## Findings

### DS-001: A pause held over a weekend marks the paused queue as abandoned

**What breaks.** Every job held by a pause longer than 48 hours is dead-lettered, and each
owner is told their jobs failed. The stop switch destroys the work it was thrown to
protect.

**Mechanism.** The reaper keeps running under a pause — correct, since settling a dead
worker is not new work. It also runs `reconcileOverdueQueuedJobs`, which dead-letters
queued jobs past `OVERDUE_MS` with `attempts = 0` and no set (`jobs.ts:418`). That is
exactly the shape of a job that never started because generation was paused.

**Circumstance.** Any pause longer than the overdue window. A Friday incident is enough.

**Proof.** Seed a queued job due five days ago, hold the pause, run the reaper: status
`failed`, error `abandoned: overdue in the queue with no worker completion`. With the
clock measured from `greatest(run_after, resumed_at)` it stays `queued`; reverting that
fails three assertions.

**Class.** Time-based inference.

### DS-002: The stop switch does not cover the ad-hoc route

**What breaks.** An administrator pausing during a GPU incident still has users starting
generations.

**Mechanism.** `pause-guard.ts:5` states three routes call it. Two do. The ad-hoc route submits
a job sequence through the same builder and never asks.

**Proof.** `grep -rl generationPausedResponse src/app/api/` returns two files.

**Class.** Incomplete gates — found by checking a stale assertion.

## Swept and clean
Inherited defaults, sibling writers, silent truncation, over-serving the client.

## Verdict
DS-001 and DS-002 before the pause is used on anything live → two tickets. No change is
active on this project, so Planning opens `fix-generation-stop-controls` first and the tickets
go in `changes/fix-generation-stop-controls/tickets/generation-stop-controls/` as `TICKET-001.md`
and `TICKET-002.md`, with `backlog.md` alongside.
```
