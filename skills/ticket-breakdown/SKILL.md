---
name: ticket-breakdown
description: "Decompose one capability area's requirements for one change into implementable tickets with Priority, Value, acceptance criteria, Prior Art, Output contracts, Known Hazards, dependency ordering and relative sizing — one TICKET-NNN.md per ticket plus backlog.md — at .gener8v/changes/<change-slug>/tickets/<area-slug>/. Use when a specification is approved and the team needs work items."
argument-hint: "<capability area> [for <change-slug>]"
---
# Ticket Breakdown Skill

**Invoked with:** `$ARGUMENTS`

If that is empty, ask the user which capability area's specification to break down before doing anything else. Never guess the target.

Every breakdown belongs to a change. When the argument carries no `for <change-slug>`, read `.gener8v/pipeline-state.yaml`: if exactly one change lists this area under `pending_breakdown`, or exactly one change is active (`active_changes`; a change is active while its status is `ready` or `in_delivery` — a change with no tickets yet is `planned`, not active), default to it; when several changes could apply, ask which change before doing anything else. If no change exists at all, stop and recommend running the Planning skill to open one.

## Purpose

Decompose a fully specified capability into implementable work items (tickets) that a developer or team can pick up and execute. Each ticket is self-contained, has clear acceptance criteria, references its source requirements, and is sized for a single meaningful unit of work. The output bridges the gap between "what the system should do" and "what someone builds next."

## When to Use

Use this skill when:
- A Specification has been reviewed and approved for implementation
- Constraints and Dependencies analyses have been completed (or explicitly deferred)
- The team needs actionable work items to begin building
- A capability area needs to be estimated at the work-item level
- Sprint or iteration planning requires a backlog of defined tickets

## Input

**Source:** The change brief and the living Specification for the capability area, plus the corresponding Constraints analysis, Dependency Map, and Technical Design
**Read from:**
- Change brief: `.gener8v/changes/[change-slug]/change.md` — the **Priority Cut** and this area's row in **Affected Capability Areas**
- Specification: `.gener8v/specifications/[capability-area-slug].md`
- Constraints: `.gener8v/constraints/prd.md` and `.gener8v/constraints/[capability-area-slug].md` (whichever exist)
- Dependency Map: `.gener8v/dependencies/dependency-map.md` (if available)
- Technical Design: `.gener8v/technical-design/[capability-area-slug].md` or `.gener8v/technical-design/system-design.md` (if available)

**Expects:** At minimum, a change brief and a Specification with numbered requirements ([PREFIX]-REQ-XXX and, where present, [PREFIX]-NFR-XXX). If Constraints, Dependency Map, or Technical Design files are not available, note "Not yet performed" in the Source Context section of the output and proceed without them.

**Scope:** Only the requirements and NFRs the brief's Affected Capability Areas row *adds* or *modifies* for this area are in scope, unless the brief says otherwise (for example, a row that names an unchanged requirement the change also delivers). The living specification carries every requirement the product has ever had; the brief says which of them this change is about. The Priority Cut decides what not to build — a requirement the brief places under *Could / later* may be left without a ticket, and the breakdown says so.

**Other sources of tickets** (the same ticket file format, added as new `TICKET-NNN.md` files to the area's `tickets/<area-slug>/` directory under the active change with IDs above the current maximum — or to a new `fix-<subsystem>` change opened via Planning when no change is active): findings a Defect Sweep verdict says to fix now (`.gener8v/sweeps/*-sweep.md`, cite `DS-XXX`), review findings deferred to a new ticket (cite `<change-slug>/<report-slug>/CR-XXX` etc.), and behaviours Brownfield flagged as bugs in a specification's Open Questions. A bug fix is a Small ticket whose Requirements Covered names the requirement the bug violates — it does not need a new PRD.

**If input is missing or malformed:**
- If no change brief exists, stop and recommend running the Planning skill to open the change first
- If no specification exists for the target capability area, or the brief's row for this area still says `(pending specification)`, stop and recommend running the Specification skill for this change first
- If constraints, dependencies, or technical design are missing, proceed but note the gap — tickets will lack constraint-informed criteria, dependency ordering, or architecture context respectively

## Output

**Produces:** A ticket breakdown for one capability area within one change — a directory holding one file per ticket plus an area-level backlog
**Write to:** `.gener8v/changes/[change-slug]/tickets/[capability-area-slug]/` — `TICKET-NNN.md` for each ticket, and `backlog.md` for the overview, source context, dependency chain, suggested ordering and backlog summary
**Creates directory:** `.gener8v/changes/[change-slug]/tickets/[capability-area-slug]/` if it does not exist
**Naming convention:** The directory matches the specification filename without its extension (e.g., `search-and-retrieval/`); ticket files are `TICKET-001.md`, `TICKET-002.md`, … — zero-padded to three digits

Run this skill once per change and capability area. Ticket IDs restart at TICKET-001 in every `tickets/<area-slug>/` directory; from any other document a ticket is referenced qualified — `<change-slug>/<area-slug>/TICKET-003` (`CONVENTIONS.md` §4). The output feeds Delivery, which implements one ticket at a time from that ticket's own file.

**Legacy shape:** a per-area file `tickets/<area-slug>.md` holding `### TICKET-NNN:` sections is still read by the state script (with a warning). Never write it. If the target area exists only in that shape, convert it first with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py" split-tickets` (add `--remove` to delete the originals after the split), then add tickets to the resulting directory.

## Output Format

Two templates. Every ticket is its own file; the area-level narrative lives in `backlog.md`.

### Ticket file — `TICKET-NNN.md`

```markdown
# TICKET-001: [Concise action-oriented title]

**Change:** [change-slug]
**Capability Area:** [Area name] ([area-slug])
**Specification:** specifications/[area-slug].md

**Summary:** [1-2 sentences describing what this ticket accomplishes]
**Priority:** [Must / Should / Could — from the change brief's Priority Cut]
**Value:** [One sentence — what the user or operator gets when this lands]

**Requirements Covered:**
- [XX]-REQ-001: [Brief description]
- [XX]-REQ-002: [Brief description]
- [XX]-NFR-001: [target — verified by … — NFR IDs are listed exactly like REQ IDs]

**Prior Art:** [What to read/understand before starting. For tickets with
no dependencies, point to relevant pipeline documents. For tickets that
depend on other tickets, specify the files and directories produced by
those tickets that this work builds on.]
- Read: [root-relative file path — source file, config, module, or pipeline artifact] — [what to look for in that file and why it matters]

**Acceptance Criteria:**
- [ ] [Observable, verifiable condition that must be true when complete]
- [ ] [Another condition]
- [ ] [For each NFR carried: the measurable target and its verification method —
      e.g., "p95 latency ≤ 800 ms at 50 concurrent users, verified by the k6 load test"]

**Output:**
- [File or directory this ticket produces or modifies, root-relative to the
  workspace (e.g., `api/src/search/query.ts`), with enough detail that
  downstream tickets can locate the work]
- [The test file(s) that prove the acceptance criteria — every ticket with
  testable criteria lists at least one; name which criterion each test covers]

**Constraints:** [Qualified constraint IDs and brief description, or "None identified"]

**Known Hazards:** [Front-loaded traps the implementer must know *before* starting — or "None identified". This is where decision supersessions, cross-document conflicts, and schema/pattern gotchas live, so they are seen first, not discovered mid-build. Each hazard names what to do about it.]
- [e.g., "AD-004 supersedes the spec's wording of SR-REQ-006 — rank on the stored score, NOT on recomputed similarity; the spec text is stale"]
- [e.g., "Spec conflict: SR-REQ-009 and TC-002 disagree on whether a source reference may be a URL — implement per TC-002, flag the conflict in the delivery record's Decisions, do NOT silently reconcile"]
- [e.g., "`status` has no DB CHECK — enforce the enum at the application layer at every write path"]

**Depends On:** [Other ticket IDs this is blocked by, or "None"]
**Blocks:** [Other ticket IDs this unblocks, or "None"]

**Size:** [Small / Medium / Large]

**Notes:** [Implementation hints, context, or warnings — optional]
```

The three header lines (`**Change:**`, `**Capability Area:**`, `**Specification:**`) make the file self-describing when read alone — which is the point. A withdrawn ticket keeps its file and gains `**Status:** Withdrawn` as the first line after the title.

### Area backlog — `backlog.md`

````markdown
# [Capability Area Name] — Backlog ([change-slug])

## Overview

[2-3 sentences summarizing the breakdown. State total ticket count,
how they cluster, and any notable sequencing from the dependency analysis.]

## Source Context

**Specification:** [Title] · **Constraints Analysis:** [Title, or "Not yet performed"] · **Dependency Map:** [Title, or "Not yet performed"] · **Technical Design:** [Title, or "Not yet performed"]
**Change brief:** changes/[change-slug]/change.md (Priority Cut applied)

## Ticket Dependency Chain

[Visual representation of ticket ordering]

```
TICKET-001 ──→ TICKET-003 ──→ TICKET-005
TICKET-002 ──→ TICKET-004 ──┘
```

## Suggested Ordering

[Recommended implementation sequence with rationale — weigh priority with
dependency and risk; a Could ticket never precedes a Must ticket unless a
dependency forces it]

1. **TICKET-001** — [Why first: foundational, unblocks others, etc.]
2. **TICKET-002** — [Can parallel with TICKET-001 because...]
3. ...

## Backlog Summary

| Ticket | Title | Priority | Size | Depends On | Status |
|--------|-------|----------|------|------------|--------|
| TICKET-001 | [Title] | Must | Small | None | Ready |
| TICKET-002 | [Title] | Must | Medium | None | Ready |
| TICKET-003 | [Title] | Should | Large | TICKET-001 | Blocked |
| ... | ... | ... | ... | ... | ... |

**Total Tickets:** [Count]
**Ready to Start:** [Count of tickets with no unresolved dependencies]

*Status here is as of this breakdown. Live status (delivered, reviewed, done) is derived from delivery records and reviews into `.gener8v/pipeline-state.yaml`; this table is not updated as tickets progress.*
````

---

## Principles

### One Ticket, One Outcome
Each ticket should produce a single, demonstrable outcome. If a ticket requires the developer to make unrelated decisions or produce multiple distinct artifacts, it should be split. The test: can you demo what this ticket accomplished in one sentence?

### One Ticket, One File
A ticket is read, delivered and reviewed alone, so it lives alone: `TICKET-NNN.md` opens with its title and the three header lines that say which change, area and specification it belongs to, then the fields. It must stand alone — a reader holding only that file knows what to build, what to read first, what to produce and what it blocks. The area-level narrative (overview, dependency chain, ordering, summary table) belongs in `backlog.md`, never inside a ticket, and no ticket exists only as a heading in another file.

### Acceptance Criteria Are the Contract
Acceptance criteria define "done." They must be observable and verifiable—not aspirational. A ticket without clear acceptance criteria is a ticket that will be argued about at review time.

**Good:** "Search returns results ranked by relevance score, with the highest-scoring result first."
**Avoid:** "Search works well and returns good results."

### Trace to Requirements
Every ticket should reference the requirements (REQ-XXX) and non-functional requirements (NFR-XXX) it satisfies. Every in-scope requirement — the ones the change brief adds or modifies for this area — should appear in at least one ticket. If a requirement has no ticket, it has been dropped—intentionally (the Priority Cut put it under *Could / later*) or accidentally. Both should be visible. A ticket that carries an NFR lists the NFR's verification method under its Acceptance Criteria; an NFR whose target cannot be verified is an Open Question, not a criterion.

### Priority and Value Come From the Brief
Every ticket carries a **Priority** (`Must` / `Should` / `Could`) and a one-sentence **Value**. Priority is read from the change brief's Priority Cut, not invented per ticket; when a ticket covers requirements of mixed priority it takes the highest, and the split is worth reconsidering. Value states what the user or operator gets when the ticket lands — if that sentence is hard to write, the ticket is probably an implementation step rather than an outcome.

### Size Is Relative, Not Absolute
Size indicators (Small / Medium / Large) communicate relative complexity and scope, not duration. They help with planning and load balancing without the false precision of hour estimates.

- **Small**: Well-understood, limited scope, low uncertainty. A single focused work session.
- **Medium**: Clear scope but involves multiple components or moderate complexity. May surface minor unknowns.
- **Large**: Significant scope, multiple moving parts, or meaningful uncertainty. Consider whether it should be split further.

### Dependencies Flow Down
Ticket dependencies should reflect actual implementation order, informed by the Dependency Map. Do not create artificial dependencies based on assumed workflow. If two tickets are genuinely independent, they should be marked as such even if one "feels" like it should come first.

### Constraints Shape Acceptance Criteria
Constraints from the Constraints analysis should manifest as acceptance criteria or notes on relevant tickets. A compliance constraint becomes a testable condition. A technical constraint becomes a boundary the implementation must respect.

### Front-Load the Hazards
The most expensive failure mode in agent-driven delivery is the implementer building confidently on a wrong assumption — a stale spec, a superseded decision, a schema gotcha, or a conflict between two source documents. The single most effective mitigation is a **Known Hazards** section at the top of the ticket that names these traps *before* the work, with what to do about each. Three kinds belong here: (1) **supersessions** — where an architecture decision (AD-XXX), a delivery decision (DEL-XXX) or a resolved Open Question overrides spec text the implementer would otherwise follow; (2) **cross-document conflicts** — where two artifacts disagree, with an instruction to implement one and surface the conflict rather than silently reconcile it; (3) **schema/pattern gotchas** — invariants enforced only at the application layer, unusual delete semantics, permission-matrix variations that look uniform but aren't. Review skills may append a hazard here when they defer a finding to this ticket. A hazard without a "so do X" is a worry, not a hazard — always state the resolution.

### Self-Contained Tickets
Each ticket should be understandable without reading every other ticket. Include enough context in the summary and acceptance criteria that a developer can pick it up and know what to build. Reference other tickets for dependency, not for comprehension.

### Prior Art Tells You Where to Look
Every ticket must include a **Prior Art** section that tells the implementing agent exactly what to read before starting. For tickets with no dependencies, this points to pipeline documents (specifications, constraints, dependency map). For tickets that depend on other tickets, this points to the specific files and modules those tickets produced. An LLM picking up TICKET-003 should never have to guess where TICKET-001's code lives.

### Output Tells Downstream Where to Find You
Every ticket must include an **Output** section that describes the files or directories the ticket produces or modifies. This is the contract between this ticket and any ticket that depends on it. Be specific: name the file path — root-relative to the workspace root, so `api/src/search/query.ts` rather than `src/search/query.ts` when several repositories share the root (`CONVENTIONS.md` §8) — describe what it exposes (function signatures, data structures, configuration), and note what downstream tickets will consume from it. A ticket that touches two repositories is two tickets unless the change is atomic.

## Process

1. **Gather Inputs**: Collect the change brief, the Specification, Constraints Analysis, Dependency Map and Technical Design for the capability area. From the brief's Affected Capability Areas row, list the requirement and NFR IDs in scope for this change; from its Priority Cut, note the priority each will carry. Note any open questions that remain unresolved.

2. **Identify Natural Boundaries**: Read through the Specification's requirements and look for natural groupings—subsections, data flows, interaction patterns, or state transitions that form coherent units of work.

2b. **Load the Existing Directory**: If `tickets/[capability-area-slug]/` already exists, read every `TICKET-*.md` in it and its `backlog.md` first. Every existing ID and file is kept; a new ticket takes the next ID above the highest existing `TICKET-*.md` in that directory (append-only; never renumber); a ticket no longer applicable keeps its file with `**Status:** Withdrawn` at the top rather than being deleted; a delivered ticket's file is never rewritten. IDs are append-only (`CONVENTIONS.md` §4) — code and downstream documents reference them, and renumbering silently re-binds those references. If the area exists only as the legacy per-area file, run `split-tickets` first (see Output).

3. **Draft Tickets**: For each boundary, create a ticket. Write the summary first, then map requirements, then define acceptance criteria.

4. **Define Prior Art**: For each ticket, identify what the implementing agent needs to read before starting. Point to pipeline artifacts (`.gener8v/` files) and, for dependent tickets, the specific source files and modules produced by predecessor tickets — every code path root-relative to the workspace root. **Verify every path you cite exists** (or is declared in a predecessor's Output) — a Prior Art entry pointing at a file that is not there is exactly the wrong assumption the Known Hazards section exists to prevent.

5. **Define Output**: For each ticket, specify what files or directories it produces or modifies, including the test file(s) that prove its acceptance criteria. Name paths, describe exposed interfaces, and note what downstream tickets will consume. Use `{ext}` as a placeholder when the language/framework is not yet decided.

6. **Apply Constraints**: Review each ticket against the Constraints Analysis. Add relevant constraints as acceptance criteria or notes.

7. **Surface Known Hazards**: For each ticket, scan the source artifacts for traps the implementer must know before starting — decision supersessions (an architecture or delivery decision that overrides spec text), cross-document conflicts (two artifacts that disagree), and schema/pattern gotchas (app-layer-only invariants, unusual delete semantics, permission variations). Record each in the ticket's **Known Hazards** field with its resolution. If none exist, state "None identified" — the empty field is a signal that the scan was done, not skipped.

8. **Map Ticket Dependencies**: Using the Dependency Map and the requirements themselves, determine which tickets block which. Keep the graph as flat as possible—deep chains reduce parallelization.

9. **Size Tickets**: Assign relative size. If any ticket is Large, evaluate whether it can be split without creating artificial boundaries.

9b. **Write Each Ticket File**: As soon as a ticket's fields are complete, write it to its own `TICKET-NNN.md` — title, the three header lines, then the fields in the Output Format order. Do not hold finished tickets back for the backlog; a ticket file that exists is already deliverable.

10. **Verify Coverage**: Check that every in-scope requirement and NFR appears in at least one ticket. Check that no requirement is orphaned; where the Priority Cut deliberately leaves one out, say so in the Overview. Check that every ticket file opens with the three header lines and has Priority, Value, Prior Art, Output, and Known Hazards sections, and that every ticket carrying an NFR names its verification method in the Acceptance Criteria.

11. **Determine Ordering**: Propose an implementation sequence that weighs priority with dependencies and risk: Must before Should before Could, risky things first within a priority band, demonstrable capability early. A Could ticket never precedes a Must ticket unless a dependency forces it — and if one does, say which.

12. **Write `backlog.md` Last**: Once every ticket file is written, write `backlog.md` — overview, source context, dependency chain, suggested ordering, and the backlog summary with priority and dependency status so "ready to start" tickets — and the Must tickets among them — are immediately visible. On a re-run, regenerate it from the whole directory, withdrawn tickets included.

13. **Flag Gaps**: If open questions from upstream skills affect ticket definition, note them. If a ticket cannot be fully specified, say so and identify what is needed.

## Example

The worked example decomposes the Search & Retrieval area of the Support Documentation Search System for the `support-search` change into four tickets — `backlog.md` plus `TICKET-001.md` … `TICKET-004.md`, each in its own file with the three header lines — with Priority and Value on every ticket, an NFR with its verification method on TICKET-003, Known Hazards, root-relative Output paths, and the Backlog Summary with its Priority column.
It is at `skills/ticket-breakdown/references/example.md`.
Read it before producing your first artifact of this kind.

---

## Integration with Other Skills

**Upstream:**
- **Planning Skill**: Provides the PRD that defines capability areas and the change brief (`changes/<change-slug>/change.md`) whose Priority Cut and Affected Capability Areas row scope this breakdown
- **Specification Skill**: Provides the detailed requirements and NFRs that are decomposed into tickets, and records in the brief which IDs the change adds or modifies
- **Constraints Skill**: Provides constraints that shape acceptance criteria and surface implementation boundaries
- **Dependencies Skill**: Provides sequencing information and external dependency awareness
- **Technical Design Skill**: Provides architecture decisions, component boundaries, and interface contracts that inform ticket scope and Prior Art references
- **Defect Sweep / Code, Quality and Security Review**: Route findings to tickets — sweep findings a Verdict says to fix now (`DS-XXX`) and review findings deferred to a new ticket (qualified `<change-slug>/<report-slug>/CR-XXX` etc.) — added as new `TICKET-NNN.md` files to the owning area's `tickets/<area-slug>/` directory under the active change, or to a `fix-<subsystem>` change opened via Planning

**Downstream:**
- **Delivery Skill**: implements one ticket at a time, reading that ticket's `TICKET-NNN.md` and `backlog.md` for ordering context
- **Orchestrate**: derives ticket status (blocked/ready/…) from each ticket's Depends On and the delivery records under the same change, orders ready tickets Must → Should → Could, and warns on a ticket with no Priority
- **Audit Skill**: checks coverage, Prior Art/Output completeness and hazard quality

## Revisions

- Re-run this skill when the source specification, constraints, dependencies, or technical design change in ways that affect ticket scope or ordering
- When re-running, load the existing directory — tickets keep their IDs and files, a delivered ticket's file is never rewritten, new tickets are added as new files above the current maximum, obsolete undelivered tickets keep their file with `**Status:** Withdrawn` at the top, and `backlog.md` is regenerated
- A new change gets its own `tickets/<area-slug>/` directory under `changes/<change-slug>/`; never add another change's tickets to this one, and never renumber against another directory — IDs are only unique within a directory, which is why references from elsewhere are qualified
- If only a single requirement changes, consider updating the affected undelivered ticket file(s) rather than regenerating the whole directory; a delivered ticket is never edited — the follow-up work becomes a new ticket
- If the technical design introduces new architecture decisions, tickets may need new acceptance criteria or Prior Art references

## Notes

- Generate one ticket directory per change and capability area; do not combine multiple capability areas — or multiple changes — into one directory
- Re-running adds files; it never rewrites a delivered ticket's file
- If a requirement spans multiple tickets, note this and ensure acceptance criteria collectively cover the full requirement
- Large tickets should prompt reconsideration—can they be split without creating artificial boundaries?
- Open questions from upstream skills that affect ticket definition should be listed; do not invent acceptance criteria to fill gaps left by unresolved questions
- This skill does not assign tickets to individuals or teams
- This skill does not estimate duration—size indicators communicate relative scope only
- When a Technical Design is available, tickets should reference Architecture Decisions (AD-XXX) in their notes or constraints, and Prior Art should point to technical design documents alongside specifications
