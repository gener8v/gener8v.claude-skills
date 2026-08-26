---
name: defect-sweep
description: "Sweep an existing subsystem's perimeter for defect classes nobody is looking for — inherited defaults, sibling writers, incomplete gates, fail-open error paths, silent truncation, stale assertions, identity confusion, time-based inference, unasked authorization — with proof per finding, at .gener8v/sweeps/. Use after a burst of changes, before a launch, or when a found defect may have siblings. Runs as a fresh-context pass."
argument-hint: "<subsystem, directory or entry point>"
context: fork
agent: defect-sweeper
---
# Defect Sweep Skill

**Invoked with:** `$ARGUMENTS`

If that is empty, ask the user which subsystem to sweep and where its edges are before doing anything else. Never guess the target.

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
cover, and why it runs as a fresh pass rather than folded into Delivery: this skill's
frontmatter forks it into the `defect-sweeper` agent, so the sweep never inherits the
builder's context. The agent writes the sweep and returns; the user reads it in the main
session.

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
- `.gener8v/sweeps/<subsystem-slug>-sweep.md` from the previous sweep of the same subsystem, if any —
  to say which earlier findings were fixed, which are still open, and which are new

**Nothing from `.gener8v/` is required.** This skill works on repositories that have never
run the pipeline, which is the common case for the code most worth sweeping. It creates
`.gener8v/sweeps/` if needed; that does not make the project "on the pipeline" (that is
`.gener8v/prd.md`), and Setup/Brownfield still run normally afterwards.

## Output

**Write to:** `.gener8v/sweeps/<subsystem-slug>-sweep.md` (or a path the user names)

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

**Class.** One of the classes in `references/defect-classes.md`.

### DS-002: ...

## Swept and clean

The classes checked that turned up nothing, named explicitly. Silence is ambiguous —
a reader cannot tell "checked and fine" from "never looked".

## Verdict

What should be fixed now, what can wait, and what needs a decision rather than a fix.
Findings to fix now become tickets (see Integration); name them here as `DS-XXX → ticket`,
and name the change they go into.

## Since the last sweep (if any)

[Earlier findings fixed / still open / new this time.]
```

## Defect Classes

Each class is a question to ask of the subsystem, not a rule to check. The full description of
each — what it looks like, the question, and the smell that gives it away — is in
`references/defect-classes.md` (relative to this skill's directory). **Read it before sweeping.**

- **Inherited defaults** — for every function this code calls, what does it do when an argument is absent?
- **Sibling writers** — what else reads or writes this table, this file, this key?
- **Incomplete gates** — enumerate every entry point into the guarded capability; is each one checked?
- **Fail-open on the error path** — for every guard, what happens when its input cannot be read?
- **Silent truncation** — can this return fewer things than exist, and does the caller learn that it did?
- **Stale assertions** — for each comment describing what the system does, is it true of the system?
- **Identity confusion** — what is this row keyed by, and does that key survive the operations applied to its subject?
- **Time-based inference** — does this clock keep running during states where the expected actor could not act?
- **Unasked authorization** — for every route returning person-level data, what permission does it require, and does the middleware actually supply what it is assumed to?
- **Over-serving the client** — what does the renderer actually read, and what is it handed?

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

3. **Run each class.** Take the defect classes in turn, as described in
   `references/defect-classes.md`. Most will find nothing — record that they were run.

4. **Check every assertion.** Grep the subsystem's comments for claims about behaviour and
   verify each against the code. Counts, names, and capabilities especially.

5. **Prove each finding.** Reproduce it, write a failing test, or run the query. Downgrade
   anything that will not reproduce to a hypothesis and say so.

6. **Order by consequence**, not by discovery order or severity label. What hurts most,
   soonest, to the most people.

7. **Report what was clean**, and where the sweep stopped.

## Example

A sweep of a subsystem's stop controls (pause, cancel, a recent delete) on a project that is not on
the pipeline: two proven findings — a time-based inference that dead-letters paused work, and an
incomplete gate found through a stale assertion — the classes swept clean, and a Verdict that
opens a `fix-<subsystem-slug>` change for the tickets. It lives at `references/example.md`
(relative to this skill's directory). Read it before producing your first artifact of this kind.

## Integration with Other Skills

**Upstream:** none required. Reads the code, its tests, `CLAUDE.md`, and the previous sweep of the same
subsystem.

**Downstream:**
- **Ticket Breakdown**: findings the Verdict says to fix now become tickets (cite `DS-XXX`) in
  `changes/<change-slug>/tickets/<area-slug>.md` of the active change — the owning capability area's
  breakdown, or a breakdown for the subsystem when the project has no capability areas. When several
  changes are active, the user names one. A fix is then a normal Delivery with its three reviews.
- **Planning**: when no change is active, open a new change `fix-<subsystem-slug>` via Planning first
  (Why: the sweep; Outcome: the findings closed; Priority Cut from the Verdict), then break the findings
  down under it.
- **Orchestrate**: lists sweeps under `cross_cutting.sweeps` and recommends a sweep when three or more
  deliveries have landed in one capability area since the last one, or before a launch.
- **Audit**: checks that every finding names a circumstance and carries proof, and that the sweep says
  where it stopped.
- **Quality Review** is the home for smells that are not failures; a sweep finding that cannot state a
  breaking circumstance is handed there, not dropped.

## Revisions

- A sweep is point-in-time. Re-run after a burst of changes to the same subsystem, before a launch that
  exposes it, or when a defect found elsewhere may have siblings here.
- Re-running writes a new sweep file (`<subsystem-slug>-sweep.md` is replaced; the previous verdict is
  summarised in **Since the last sweep**) so a reader sees what was fixed and what is still open.
- Periodic sweeps over the subsystems that carry the most consequence are a good use of a scheduled
  routine (`/schedule`) or a cron-driven session; the plugin ships no schedule because the cadence is
  the project's decision.
