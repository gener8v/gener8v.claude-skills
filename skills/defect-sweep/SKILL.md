# Defect Sweep Skill

## Purpose

Search existing code for defects that nobody is looking for. This skill is not anchored to
a delivery, a ticket, or a spec — it takes a subsystem and sweeps it for known defect
classes, reporting what it finds and proving each finding is real.

It is the complement to the three review skills. Code Review asks *did you build the right
thing*, Quality Review asks *did you build it well*, Security Review asks *is it safe* —
and all three review **what was just built**. None of them looks at the code around it.
That perimeter is where a large share of real defects live, because it is the code nobody
has a reason to open: a callee whose defaults you inherited, a sibling route that writes
the same table, a control that claims coverage it does not have.

Building and sweeping are different modes. A builder verifies the thing they made and is
incurious about its neighbours — which is exactly the blind spot this skill exists to
cover, and why it should be run by a fresh pass rather than folded into Delivery.

## When to Use

Use this skill when:
- A subsystem has taken several changes in a short window and nobody has looked at it whole
- A control, gate, or guard was recently added and its coverage has not been enumerated
- Code was delivered fast under deadline and the perimeter was not swept
- A defect was found and you want to know whether it has siblings
- Before a launch, over the surface that a launch will expose
- Periodically, over the subsystems that carry the most consequence

Do **not** use this skill to review a specific delivery — that is Code Review. Do not use
it to check pipeline documents — that is Audit.

## Input

**Source:** A subsystem, named by directory, feature, or entry point
**Read from:**
- The named code and everything it calls
- Everything that calls the named code
- Tests covering it
- `CLAUDE.md` / `CONTRIBUTING.md` for repo-specific rules a sweep should enforce

**Nothing from `.gener8v/` is required.** This skill works on repositories that have never
run the pipeline, which is the common case for the code most worth sweeping.

## Output

**Write to:** `.gener8v/sweeps/[subsystem-slug]-sweep.md` (or a path the user names)

A findings document, ordered by consequence. Each finding states what breaks, in what
circumstance, and carries the evidence that makes it checkable rather than plausible.

## Output Format

```markdown
# [Subsystem]: Defect Sweep

## Scope

What was swept, and what was deliberately not. A sweep that does not say where it stopped
reads as a clean bill of health for code nobody opened.

## Findings

### DS-001: [Consequence, as a sentence — not a category]

**What breaks.** One or two sentences, consequence first.

**Mechanism.** The code path, with file:line. Why it happens, not merely that it does.

**Circumstance.** What has to be true for this to fire. A defect that needs an impossible
state is a note; one that needs a Friday afternoon is a finding.

**Proof.** How to see it: a failing test, a query, a reproduction. If a fix is proposed,
state what breaks when the fix is removed.

**Class.** One of the classes below.

### DS-002: ...

## Swept and clean

The classes checked that turned up nothing, named explicitly. Silence is ambiguous —
a reader cannot tell "checked and fine" from "never looked".

## Verdict

What should be fixed now, what can wait, and what needs a decision rather than a fix.
```

## Defect Classes

These are the sweeps. Each is a question to ask of the subsystem, not a rule to check.

### Inherited defaults

A callee applies a default the caller never chose. Query builders with a default `limit`,
clients with a default timeout, parsers with a default encoding.

*Ask:* for every function this code calls, what does it do when an argument is absent?

*Smell:* the caller reads the callee's **type signature** and stops there. Optional
parameters are where defaults hide, and a type signature does not show you the default.

### Sibling writers

One path into a resource is guarded and another is not. A DELETE handler that refuses
under a condition, next to a POST that overwrites without asking.

*Ask:* what else reads or writes this table, this file, this key?

*Smell:* a guard whose comment explains a hazard. If the hazard is real, it applies to
every writer — find them all.

### Incomplete gates

A control claims coverage it does not have. A kill switch on three of four entry points, a
permission check on the routes somebody remembered.

*Ask:* enumerate every entry point into the guarded capability, then check each one.

*Smell:* a comment stating how many places call something. Count them.

### Fail-open on the error path

An unknown or errored state is treated as permissive. A gate that has not read its
configuration yet, a role lookup that returns null on outage and null when disabled.

*Ask:* for every guard, what happens when its input cannot be read?

*Smell:* `??` or `||` supplying a default to a **security or safety** decision. Failing
open is sometimes right, but it must be a decision with a reason attached, not a fallback.

### Silent truncation

A partial answer is presented as a complete one. Pagination limits, result caps, sampling,
`top-N` — where the consumer is not told what was dropped.

*Ask:* can this return fewer things than exist? Does the caller learn that it did?

*Smell:* a bulk operation that reports successes without reporting a total.

### Stale assertions

A comment, docstring, or document asserts behaviour that is not true — or never was.

*Ask:* for each comment describing what the system does, check it against the system.

*Smell:* specific, confident claims — port numbers, counts, credential types, "X cannot
read Y". Specificity reads as authority and is checked by nothing.

### Identity confusion

Two things keyed differently are assumed to travel together. Records keyed by a natural
key while their subject is keyed by an id, so regenerating the subject rebinds the records.

*Ask:* what is this row keyed by, and does that key survive the operations applied to its
subject?

*Smell:* a delete that leaves rows behind, or a create that finds rows already there.

### Time-based inference

Elapsed time is treated as evidence of intent. "Nobody claimed this in 48 hours, so it was
abandoned" — true only if somebody was able to claim it the whole time.

*Ask:* does this clock keep running during states where the expected actor could not act?

*Smell:* a reaper, sweeper, or timeout that infers neglect from a duration.

### Unasked authorization

Data is returned without asking who is reading. Common where middleware is assumed to
have resolved identity but only resolves *authentication*.

*Ask:* for every route returning person-level data, what permission does it require, and
does the middleware actually supply the thing it is assumed to?

*Smell:* a route with no permission call, in a codebase where most routes have one.

### Over-serving the client

More data crosses the wire than is drawn. Server components passing whole objects to client
components; APIs returning a full record because the type was convenient.

*Ask:* what does the renderer actually read, and what is it handed?

*Smell:* an object built for one audience passed to a narrower one.

## Principles

### A finding is a failure, not a smell

Every finding names a circumstance in which something breaks. "This is fragile" is not a
finding. If the circumstance cannot be stated, it belongs in Quality Review.

### Prove it or drop it

A finding that has not been checked against the running system or a test is a hypothesis.
Say which it is. A sweep whose findings are half-real teaches the reader to discount all
of them — and the next real one goes unfixed.

### State the proof as a falsifiable claim

Not "tests pass". *"Remove the gate and four targeted tests fail."* The reader can run it.
This is also the only honest way to show a test would have caught the defect.

### Consequence first, mechanism second

Lead with what breaks and for whom. A reader triaging twelve findings needs the impact in
the first sentence; the code path is what they read once they care.

### Say where you stopped

A sweep is bounded. Name the classes checked, the classes skipped, and the code left
unopened. Coverage silently omitted reads as coverage achieved.

### Bundling needs a stated reason

Several defects in one subsystem may share a change, but the reader must be told why.
State the rationale at the top: *"five defects in one subsystem; each needs its own
sentence to be reviewable, and splitting them would put five one-line changes through the
same two files."* Absent that, one defect per change.

### Sweep the code, not the author

Findings describe code. A sweep that reads as a verdict on whoever wrote it gets argued
with instead of fixed — and the person best placed to confirm a finding is usually its
author.

## Process

1. **Bound the sweep.** Name the subsystem and its edges. Write down what is out of scope
   before starting, so the boundary is a decision rather than wherever attention ran out.

2. **Map the perimeter.** Before reading the subsystem's own logic, enumerate:
   - every function it calls, and what each does with absent arguments
   - every caller of its entry points
   - every other writer to the resources it owns
   - every entry point into any capability it guards

   This step is the skill. The subsystem's own code is usually the part that has been read
   the most; the perimeter is the part nobody has opened.

3. **Run each class.** Take the defect classes in turn. Most will find nothing — record
   that they were run.

4. **Check every assertion.** Grep the subsystem's comments for claims about behaviour and
   verify each against the code. Counts, names, and capabilities especially.

5. **Prove each finding.** Reproduce it, write a failing test, or run the query. Downgrade
   anything that will not reproduce to a hypothesis and say so.

6. **Order by consequence**, not by discovery order or severity label. What hurts most,
   soonest, to the most people.

7. **Report what was clean**, and where the sweep stopped.

## Example

### Input

> Sweep the generation stop controls in `Fail-Persist-Exceed` — pause, cancel, and the
> material-set delete added this week.

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
owner is told their materials failed. The stop switch destroys the work it was thrown to
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

### DS-002: The stop switch does not cover pull-aside

**What breaks.** An administrator pausing during a GPU incident still has tutors starting
generations.

**Mechanism.** `pause-guard.ts:5` states three routes call it. Two do. Pull-aside submits
a lesson sequence through the same builder and never asks.

**Proof.** `grep -rl generationPausedResponse src/app/api/` returns two files.

**Class.** Incomplete gates — found by checking a stale assertion.

## Swept and clean
Inherited defaults, sibling writers, silent truncation, over-serving the client.

## Verdict
DS-001 and DS-002 before the pause is used on anything live.
```
