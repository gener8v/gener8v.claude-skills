---
name: rot-watch
description: "Detect decay in code that is being actively written: measure six signals (packaging drift, dependency direction, comment language, growth slopes, tests, the detectable subset of SOLID) against a recorded baseline and report only what moved, at .gener8v/rot/. Use once code has been delivered and again every few deliveries, before a release, or when asked 'is the codebase getting worse' or 'has this module drifted'. The first run records the baseline and reports nothing. Not for one delivery's quality (quality-review), defects (defect-sweep) or whether the architecture was right (architecture-review)."
argument-hint: "[subsystem or path]"
effort: xhigh
---

# Rot Watch Skill

**Invoked with:** `<subsystem or path>` — or empty, to watch everything the baseline covers.

## Purpose

Detect decay in code that is being actively written. Not whether the code is good — that is Quality Review's question, asked once per delivered ticket against one diff. This skill asks a question no single review can: **is the codebase worse than it was?** Rot is a property of a trend, so it is invisible to any reviewer who only sees the change in front of them. The twelfth ticket can be individually reasonable and still be the one that finally inverts a dependency, and every review of every ticket up to it will have passed.

## When to Use

Use this skill when:
- Several tickets have been delivered since the last watch — the interval is the point; a watch over one delivery measures nothing
- A module has been touched by three or more consecutive deliveries
- Before opening a new capability area, so the area is not built on drift
- Before a release, over the subsystems the release exposes
- On a schedule, over whatever is being written most

Do **not** use this skill when:
- No baseline exists and no code has been delivered — run it once after the first delivery to *record* the baseline, and it will report nothing
- You want to know whether one delivery is well written — that is Quality Review
- You want to know whether a subsystem has defects — that is Defect Sweep
- You want to know whether the architecture was right — that is Architecture Review

## Input

**Source:** The repository, plus the previous baseline
**Read from:**
- `.gener8v/rot/baseline.md` — the recorded shape of the code at the last watch, if one exists
- `.gener8v/technical-design/*.md` — Component Design, for each module's *declared* responsibility and the dependency directions the architecture decisions permit
- `.gener8v/specifications/*.md` — the `## Non-Functional Requirements`, whose verification methods are tests that must still exist and still assert what they claimed
- `.gener8v/changes/*/delivery/*.md` — which tickets touched which files since the last watch
- `.gener8v/CONVENTIONS.md`
- The source itself

**Expects:** Delivered code. Without a baseline the first run records one and reports nothing — say so rather than inventing findings.

**If input is missing:**
- No technical design: dependency direction and module responsibility cannot be checked against anything declared. Note it, and fall back to comparing against the *previous baseline's* observed shape rather than an intended one
- No delivery records: the watch still runs, but it cannot attribute drift to tickets

## Output

**Produces:** A dated rot report, and an updated baseline
**Write to:**
- `.gener8v/rot/rot-YYYY-MM-DD.md` — the report
- `.gener8v/rot/baseline.md` — regenerated every run; **never hand-edited**
**Creates directory:** `.gener8v/rot/` if it does not exist

## Output Format

Write the report in the shape of `assets/rot-report.md` — Read it before writing and follow it exactly, headings included. `gener8v-state.py` finds reports by their `rot-YYYY-MM-DD.md` filename and reads nothing inside them; the line it parses is the baseline's `**Deliveries:** N` (see Troubleshooting).

## The Six Signals

Each maps to a stated quality and, more importantly, to something observable *as movement*.
A signal with no observable movement is an opinion, and belongs in Quality Review.

### 1. Packaging — is each module still about one thing?

**Watch:** a module's imports and exports growing outside the responsibility its Component Design
declares; a file acquiring dependencies from a layer its module has no business touching; a
"utils" or "helpers" module growing without a stated responsibility at all.
**Movement, not state:** a module that has always been broad is a design choice; one that
*became* broad over four deliveries is rot.

### 2. Separation — do dependencies still point the way they were declared to?

**Watch:** an import whose direction contradicts the layering the technical design records; a new
cycle between modules; a lower layer reaching into a higher one.
**This is the mechanism the project may already have.** Where the codebase builds a dependency
graph of its own corpora, the same traversal answers this question about the codebase itself —
prefer reusing it over writing a second import analyser.

### 3. Comment language — are comments still readable by someone who was not there?

**Watch:** comments added since the baseline that explain *what* the line does rather than *why*
it is that way; jargon or abbreviation introduced without expansion; a comment that no longer
matches the code beneath it.
**Apply the `simple-english` rules** where that skill is available rather than inventing a second
readability standard.

### 4. Extensibility and robustness — is the code getting harder to change?

**Watch:** file length, function length, parameter counts and branching depth, each as a *slope*
across deliveries; error paths that newly swallow rather than propagate; a growing count of
deferred markers; a configuration value newly hard-coded where it was settable.
**The honest caveat:** these are proxies. A long function is not automatically rot. A function
that grew 40% in three deliveries while gaining two parameters is the shape rot takes.

### 5. Tests — did new code arrive with them, and do the old ones still assert what they claimed?

**Watch:** source added without corresponding tests; the source-to-test ratio as a slope; **an
existing assertion weakened** — an equality assertion becoming a containment assertion, a count
becoming a non-zero check, a specific exception becoming a bare catch. And every non-functional
requirement whose specification names a verification method: does that test still exist, and does
it still test that?
**A weakened assertion is the most valuable finding this skill produces**, because it passes CI,
survives review, and silently stops protecting the thing it was written for.

### 6. SOLID — the parts that are detectable

Only the violations that can be *observed changing*, not judged in the abstract:
- **Single responsibility:** a module or class accumulating unrelated reasons to change
- **Open/closed:** a conditional that gains a branch per feature, where an abstraction was intended
- **Liskov:** an override that narrows a contract its base promised
- **Interface segregation:** an interface growing methods that most implementers stub out
- **Dependency inversion:** a concrete import appearing where the technical design declared an abstraction

## Principles

### Report Movement, Not State
The whole value is the derivative. A file that has been long since it was written is a fact about
the design; a file that doubled is a fact about decay. A report that lists absolute badness is
Quality Review with worse timing, and it will be ignored for the same reason a linter with 400
warnings is ignored.

### An Unchanged Metric Is Not a Finding
Never list a signal that did not move. Every line in the report should be something a reader has
to decide about. Padding the report with steady-state numbers is how a watch becomes noise.

### Attribute to Tickets Where Possible
Delivery records say which files each ticket touched. A movement attributed to two tickets is a
conversation with whoever delivered them; an unattributed movement is a chore nobody owns.

### Record Improvements
A report that only ever reports decay trains its reader to skim it. When a ratio improved or a
cycle was removed, say so — it is also the only way to tell whether a previous correction worked.

### Severity Is About Direction and Distance
**Breach** — a declared boundary is now violated: a dependency points the wrong way, or an NFR's
verification no longer exists. **Drift** — movement in the wrong direction that is not yet a
violation. **Watch** — movement worth a second data point before acting. Do not inflate; a report
of ten Breaches will be believed once.

### The Baseline Is Derived, Never Edited
`baseline.md` is regenerated on every run. Editing it by hand to make a report clean is the one
way to make this skill actively harmful, because every future run compares against the lie.

### Findings Become Tickets Only When They Earn It
A Breach becomes a ticket in the owning area (`CONVENTIONS.md` §2, the same route Defect Sweep
uses for `DS-XXX` findings). Drift and Watch stay in the report. A skill that files a ticket per
observation produces a backlog nobody reads.

## Process

1. **Locate the baseline.** If `.gener8v/rot/baseline.md` is absent, this is a recording run:
   measure, write the baseline, write a report whose Verdict is **Holding** and whose Overview
   says plainly that this run established the baseline and found nothing because it could not.

2. **Establish the interval.** Read the delivery records written since the baseline date. List
   the tickets and the files they touched. This is what makes attribution possible.

3. **Read the declared shape.** From the technical design: each component's responsibility, and
   the dependency directions the architecture decisions permit. From the specifications: every
   NFR and the verification method it names. Without a technical design, note the gap and compare
   against the previous baseline's observed shape instead.

4. **Measure the six signals** over the watched paths. Prefer reusing analysis the repository
   already has over writing a parallel one.

5. **Diff against the baseline.** Discard everything that did not move. Discard everything that
   moved in the right direction into Improvements.

6. **Verify each remaining movement against the code.** A metric that moved is a hypothesis. Open
   the file and confirm the movement is what the number implies before writing it as a finding —
   a function split into two files reads as growth by one measure and as improvement by any
   honest reading.

7. **Attribute, explain the consequence, state the correction.** A movement with no stated
   consequence is a number; one with no correction is a complaint.

8. **Assign severity** by direction and distance from the declared boundary.

9. **Write the report**, then **regenerate the baseline** from the current measurements — so the
   next run measures from here, not from the last clean state. The baseline's header carries
   `**Deliveries:** N`, where N is the number of delivered tickets across every change at the time
   of this watch (the sum of `progress.delivered` over `changes:` in `pipeline-state.yaml`).
   `gener8v-state.py` subtracts it from the current count to decide when the next watch is due; a
   baseline without the line reads as 0 and recommends a watch after every delivery.

10. **Route Breaches.** For each Breach, either open a ticket in the owning area or record in the
    report why it was accepted. An accepted Breach becomes part of the declared shape at the next
    baseline, which is how a deliberate exception stops being reported forever.

## Example

A worked report — a recording run followed by a watch three deliveries later that finds one
Breach (a dependency inverted against a recorded architecture decision), two Drifts and one
Improvement — is in `references/example.md`.

---

## Troubleshooting

- **Orchestrate recommends a watch straight after one ran.** The state script reads the delivery count at the last watch from a `**Deliveries:** N` line in `.gener8v/rot/baseline.md`, and recommends a watch once three more deliveries have landed. A baseline without that line reads as 0, so every run looks overdue. Regenerate the baseline with `**Deliveries:** N` near its top, where N is `totals.delivered` in `.gener8v/pipeline-state.yaml` at the time of the run.
- **Everything outside the old scope reads as growth.** The watched paths changed: a watch over `core/` against a baseline recorded over `core/kg/retrieve/` compares two different populations. Watch the baseline's paths; to widen the scope, make this run a recording run for the new paths and say so under Not Watched and in the Overview.
- **A Breach disappeared between watches with no ticket behind it.** Either the technical design moved the boundary or the violation was fixed. Check the design's history before calling it an Improvement; Revisions requires the report to say when the boundary moved, so a moved boundary is never mistaken for a repair.
- **The same accepted Breach is reported again.** An accepted Breach folds into the declared shape at the next baseline only when the report that accepted it recorded the acceptance (step 10). Record it there — the exception and why — and let the next baseline absorb it; never edit `baseline.md` to make it go away.
- **No delivery records exist for the interval.** The watch still runs and measures, but attribution is empty. Say so in Source Context rather than guessing tickets from filenames or commit messages.

## Integration with Other Skills

**Upstream:**
- **Delivery**: produces the records that make the interval and its attribution knowable
- **Technical Design**: supplies the declared responsibilities and permitted dependency directions that Breach is measured against
- **Specification**: supplies the non-functional requirements whose verification methods must remain live

**Downstream:**
- **Ticket Breakdown**: receives Breaches as tickets in the owning area
- **Quality Review**: reads a recent report for context on the module under review — a ticket delivered into a drifting module is judged differently from one delivered into a stable one
- **Architecture Review**: a Breach that recurs across watches is evidence an architecture decision is not holding, which is that skill's question
- **Orchestrate**: recommends a watch when a module has taken three or more consecutive deliveries since the last one

**Distinct from:**
- **Quality Review** — one delivery, one diff, "is this good?" This skill: many deliveries, "is this worse?"
- **Defect Sweep** — hunts defect classes at a subsystem perimeter. This skill hunts decay, and a decayed module with no defects is still a finding
- **Audit** — checks pipeline artifacts against each other. This skill checks code against its own past

## Revisions

- Re-run after any group of deliveries; the interval is the unit, not the run
- A Breach accepted rather than fixed is folded into the declared shape at the next baseline, with the acceptance recorded in the report that accepted it
- If the technical design changes, the next watch measures against the new declared shape — and should say that the boundary moved, so a Breach that disappears is not mistaken for a repair
- The baseline is regenerated every run and is never edited by hand

## Notes

- The first run over any codebase finds nothing. That is correct behaviour, not a failure
- A watch over a single delivery measures noise; wait for an interval
- Proxies are proxies: length, depth and parameter counts indicate where to look, they do not
  themselves constitute findings. Step 6 exists because of this
- Where the repository already builds a dependency graph, reuse it for signal 2 rather than
  writing a second import analyser that will disagree with the first
