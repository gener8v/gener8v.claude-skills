---
name: specification
description: "Expand one capability area from .gener8v/prd.md into a functional specification with atomic, testable [PREFIX]-REQ-XXX requirements, behaviors, edge cases and open questions at .gener8v/specifications/<slug>.md. Use when a PRD capability area needs elaboration before constraints, technical design or tickets."
argument-hint: "<capability area> [for <change-slug>]"
---
# Specification Skill

**Invoked with:** `$ARGUMENTS`

If that is empty, ask the user which capability area (from `## Functional Capabilities` in `.gener8v/prd.md`) to specify before doing anything else. Never guess the target.

The optional `for <change-slug>` names the change this specification work belongs to (`.gener8v/changes/<change-slug>/change.md`). When it is absent, read `.gener8v/pipeline-state.yaml`: if exactly one change lists this area under `pending_specification`, or exactly one change is active (`active_changes`), use that one; when several changes could apply, ask the user which change before doing anything else. If no change exists at all, stop and recommend running the Planning skill — every specification amendment belongs to a change (only Brownfield writes the baseline without one).

## Purpose

Transform a single Capability Area from a Planning Skill PRD into a detailed functional specification. The specification enumerates all functional requirements, defines behaviors, describes edge cases, and surfaces decisions needed—all while remaining implementation-agnostic. The output is designed for downstream analysis (Constraints, Dependencies) and eventual decomposition into tickets.

## When to Use

Use this skill when:
- A Capability Area from a PRD needs detailed elaboration before implementation planning
- A change brief's `## Affected Capability Areas` row for an area still says `(pending specification)`
- Stakeholders need to review and approve detailed requirements
- The scope of a capability area is ambiguous and needs explicit definition
- Preparing input for the Constraints, Dependencies, or Ticket Breakdown skills

## Input

**Source:** A single Capability Area from a Planning Skill PRD, specified for one change
**Read from:** `.gener8v/prd.md` and `.gener8v/changes/<change-slug>/change.md`
**Expects:** A PRD with `## Functional Capabilities` containing `### [Capability Area]` subsections, and a change brief whose `## Affected Capability Areas` table names this area (its Why, Outcome and Priority Cut bound what this run adds, modifies or withdraws). This skill operates on one capability area at a time.

## Output

**Produces:** A detailed functional specification for one capability area — a living artifact, amended in place by every change that touches the area
**Write to:** `.gener8v/specifications/[capability-area-slug].md`
**Updates:** `.gener8v/changes/<change-slug>/change.md` — the area's row in `## Affected Capability Areas` (Adds / Modifies / Withdraws with the real IDs) and a `## Change Log` line
**Creates directory:** `.gener8v/specifications/` if it does not exist
**Naming convention:** Lowercase, hyphen-separated slug of the capability area name (e.g., `search-and-retrieval.md`, `documentation-ingestion.md`)

Run this skill once per capability area per change. A PRD with 5 capability areas produces 5 specification files; a later change that touches two of them amends those two.

## Output Format

Produce a markdown document with the following structure:

```markdown
# [Capability Area Name] Specification

## Overview

[2-3 sentences summarizing what this capability does and why it matters.
Should be understandable without reading the source PRD.]

## Source Context

**Parent PRD:** [Title of the PRD this capability came from]
**Requirement prefix:** [XX — recorded here so every downstream skill and the lint use the same one]
**Status:** [Draft / Approved — the skill writes Draft]
**Approved by:** [Product Owner — name, YYYY-MM-DD — or "pending"]
**Related Capabilities:** [List other capability areas this interacts with]

## Functional Requirements

[Detailed enumeration of what the system should do. Group into logical
subsections. Each requirement should be atomic and testable.]

### [Subsection Name]

- **[XX]-REQ-001** *(must · change: <change-slug>)*: The system should [verb] [what] [conditions/context]
- **[XX]-REQ-002** *(should · change: <change-slug>)*: The system should...
- **[XX]-REQ-003**: [A baseline requirement written by Brownfield carries no tag]
- **[XX]-REQ-004** *(must · change: <change-slug>)*: [Text amended by a later change] *(amended YYYY-MM-DD by <change-slug>)*

[XX] is a 2-4 letter prefix derived from the capability area name
(e.g., SR for Search & Retrieval, DI for Documentation Ingestion).
This prefix ensures requirement IDs are unique across the project.

The tag in parentheses carries an optional priority word (`must` / `should` /
`could`, from the change brief's Priority Cut) and, for every requirement a
change introduces, the change slug. A requirement whose text a change amends
appends `*(amended YYYY-MM-DD by <change-slug>)*`. Baseline (Brownfield)
requirements carry no tag.

## Non-Functional Requirements

[Measurable targets the system must achieve — as distinct from constraints,
which are boundaries it must operate within. Categories to consider:
performance, availability, capacity/retention, observability (what must be
logged or metered), accessibility, and security posture that is a target
rather than a boundary. Each NFR names a measurable target and how it will be
verified; an NFR that cannot be verified is an Open Question, not an NFR.
NFRs take the same priority and change tags as requirements.]

- **[XX]-NFR-001** *(must · change: <change-slug>)*: [measurable target, e.g. p95 search latency ≤ 800 ms at 50 concurrent users] — **verified by:** [benchmark script, load test, lint, audit query]
- **[XX]-NFR-002** *(should · change: <change-slug>)*: [measurable target] — **verified by:** [...]

## Behaviors & Rules

[Business logic, validation rules, and behavioral specifications.]

### [Behavior Category]

- When [condition], the system should [behavior]
- If [state], then [outcome]

## Edge Cases & Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| [Edge case description] | The system should... |
| [Error condition] | The system should... |

## States & Transitions (if applicable)

[State A] → [Action] → [State B]

## Data Requirements

- The system should capture [data element] for [purpose]
- The system should display [information] when [condition]

## User Interactions (if applicable)

- The user should be able to [action] by [interaction pattern]
- The system should provide feedback when [event]

## Open Questions

- [ ] **OQ-001**: [Question requiring stakeholder input]

## Assumptions

- Assumption: [Statement assumed to be true]

## @spec Coverage

[Maps each requirement to its `@spec` annotation location(s) in the codebase.
Do not include this section when first creating a greenfield specification —
the Delivery skill appends a row for every requirement it annotates (Process step 14)
and Code Review verifies the rows against the code. The Brownfield skill writes it
immediately, in this same table format.]

| Requirement | Code Location(s) |
|-------------|-----------------|
| [XX]-REQ-XXX | [file:function] |
```

---

## Principles

### Atomic Requirements
Each requirement (REQ-XXX) should describe exactly one behavior. If a requirement contains "and," consider splitting it.

### Testable Statements
Every requirement should be verifiable. Avoid subjective language like "quickly," "easily," or "user-friendly."

**Good:** "The system should return results within the user's current session."
**Avoid:** "The system should return results quickly."

### Behavior Over Interface
Describe what happens, not how it looks.

**Good:** "The user should be able to filter results by date range."
**Avoid:** "The user clicks the date picker dropdown and selects start and end dates."

### Explicit Edge Cases
Common failure modes and boundary conditions should be called out explicitly. If unsure, add to Open Questions.

### Namespaced for Traceability
Requirements use [PREFIX]-REQ-XXX identifiers (e.g., SR-REQ-001 for Search & Retrieval) and non-functional requirements [PREFIX]-NFR-XXX. The prefix is derived from the capability area name — typically the first letter of each word or the first 2-4 letters. This ensures requirement IDs are unique across the entire project, preventing ambiguity when tickets, constraints, or audits reference requirements from different specifications.

### Targets, Not Boundaries
A non-functional requirement is a measurable target the system must *achieve* (a latency, an availability, a retention period, what gets logged) with a named way to verify it. A boundary the system must *operate within* (a mandated platform, a regulation, an integration that only exposes one API) is a constraint and belongs to the Constraints skill. If a target has no way to be verified, it is an Open Question until it does.

### Living, Amended by Changes
The specification describes the area as it should be, across every change that has touched it. A change adds, amends or withdraws requirements and says so on each one with its tag; it never regenerates the file. The change brief records which IDs the change touched, so a reader can see the area's history from either side.

## Process

0. **Validate Input**: Confirm `.gener8v/prd.md` exists and contains a `## Functional Capabilities` section with `###` subsections. If the PRD is missing, stop and recommend running the Planning skill. If the target capability area is not found in the PRD, inform the user and list the available areas. Confirm `.gener8v/changes/<change-slug>/change.md` exists (resolving the change as described under **Invoked with**); if it does not, stop and recommend running the Planning skill to open the change.

0b. **Load the Existing Artifact**: If the output file already exists, read it first. Every existing ID and heading is kept; new items are allocated above the current maximum ID; anything no longer applicable is marked `**Status:** Withdrawn` in place rather than deleted. IDs are append-only (`CONVENTIONS.md` §4) — code and downstream documents reference them, and renumbering silently re-binds those references.

0c. **Read the Change Brief**: Take the change's Why, Outcome, Priority Cut and Out of Scope, and this area's row in `## Affected Capability Areas`. Only what the brief calls for is in scope for this run: a change that `modifies` an area amends or adds the requirements the brief describes and leaves the rest of the living specification untouched; a change that `adds area` writes the area from the PRD bullets. Priority words on requirements come from the Priority Cut.

1. **Extract Context**: Identify the Capability Area and its relationship to parent PRD and sibling capabilities. Choose the requirement prefix (initials or first letters of the area name, 2–4 upper-case letters, not one of the reserved prefixes in `CONVENTIONS.md` §3, and not used by any existing specification) and record it in Source Context, together with `**Status:** Draft` and `**Approved by:** pending` on a new specification (an existing Approved specification that this change amends goes back to Draft — the amendment needs approval too).
2. **Expand Requirements**: Decompose each bullet into atomic, testable requirements. Tag every requirement this change introduces with `*(<priority> · change: <change-slug>)*`; append `*(amended YYYY-MM-DD by <change-slug>)*` to any existing requirement whose text this change alters.
3. **Capture Non-Functional Requirements**: For each category that applies (performance, availability, capacity/retention, observability, accessibility, security posture), write a measurable target with its verification method as a `[XX]-NFR-NNN` item, tagged like the requirements. A target that cannot be verified goes to Open Questions instead.
4. **Define Behaviors**: Document business rules and conditional behaviors.
5. **Surface Edge Cases**: Identify boundary conditions, error states, unusual scenarios.
6. **Identify States**: Map valid states and transitions for stateful entities.
7. **Capture Data Needs**: List information to capture, store, or display.
8. **Document Interactions**: Describe interaction patterns without prescribing UI.
9. **Flag Unknowns**: Move ambiguity to Open Questions; document assumptions.
10. **Review for Completeness**: Ensure standalone understandability.
11. **Update the Change Brief**: After writing the specification, replace this area's `(pending specification)` cell in the brief's `## Affected Capability Areas` table with the real deltas — `Adds <IDs>; Modifies <IDs>; Withdraws <IDs>` (use `—` for an empty group, ranges like `SR-REQ-011..012` for runs) — and append a `## Change Log` line: `YYYY-MM-DD — <PFX> specification amended: adds …, modifies …, withdraws … (Specification)`.
12. **Record Approval**: Present the specification to the user for Product Owner approval. When they approve in conversation, set `**Status:** Approved` and `**Approved by:** Product Owner — <name>, YYYY-MM-DD` in Source Context; until then the lines stay `Draft` / `pending`, and Audit will warn if tickets are cut from a Draft specification.

## Example

A full worked example — the Search & Retrieval specification of the Support Documentation Search System for the `support-search` change, with tagged requirements, two NFRs, the Draft/Approved lines, and the change-brief row and Change Log line the skill writes afterwards — is in `references/example.md` (relative to this skill's directory). Read it before producing your first artifact of this kind.

---

## Integration with Other Skills

**Upstream:**
- **Planning Skill**: Provides the Capability Area that this skill elaborates, and opens the change brief whose Affected Capability Areas row this skill fills in

**Downstream:**
- **Constraints Skill**: Analyzes for technical, compliance, or operational constraints (boundaries — the NFRs here are targets)
- **Dependencies Skill**: Maps dependencies between capabilities and external systems
- **Technical Design Skill**: Translates requirements into architecture decisions and component design; its Infrastructure Requirements and Technical Risks cite the NFR IDs they serve
- **Ticket Breakdown Skill**: Decomposes the requirements and NFRs the change brief names for this area into implementable work items under `changes/<change-slug>/tickets/`
- **Delivery Skill**: Annotates code with these requirement IDs, appends the `## @spec Coverage` rows, and runs the executable NFR checks in its Verification Run
- **Orchestrate Skill**: Recommends `specification <area> for <change>` while the brief's row for that area still says `(pending specification)`
- **Code Review Skill**: Verifies requirement coverage and the `## @spec Coverage` table against the code
- **Brownfield Skill**: Produces specifications in this format directly from existing code

## Revisions

- Re-running this skill for a later change loads the existing specification and amends it: existing IDs and headings are preserved, new requirements are added above the current maximum with the new change's tag, removed ones are marked Withdrawn — and the new change's brief records the Adds / Modifies / Withdraws
- Downstream artifacts that reference this specification's requirements (constraints, technical designs, tickets, delivery records, and `@spec` annotations in code) become potentially stale when a requirement's *text* changes — say so in the requirement (`*(amended YYYY-MM-DD by <change-slug>)*`) so Audit can find it
- Requirements are never renumbered; a wrong number is withdrawn and re-issued
- An amendment returns an Approved specification to `**Status:** Draft` until the Product Owner approves it again
- If the PRD's capability area description changes, compare the new and existing specification to determine whether a full regeneration or targeted update is appropriate

## Notes

- Generate one specification per Capability Area; do not combine multiple areas
- Requirements should be numbered sequentially within each specification, using the capability area prefix
- Open Questions from source PRD relevant to this capability should be carried forward
- This skill does not define acceptance criteria—that occurs during Ticket Breakdown
- Keep specifications under ~2000 words; split complex capabilities if needed
- The `@spec Coverage` section is not populated during greenfield specification creation — Delivery appends to it as code is delivered. The Brownfield skill populates it immediately since it works from existing code
- `scripts/gener8v-state.py lint` fails on a requirement prefix shared by two specifications and warns on a specification that uses more than one prefix; it treats `[XX]-NFR-NNN` like requirements (uniqueness, dangling references) and warns — not errors — when an NFR is in no ticket
- `NFR` and `REQ` are reserved segments (`CONVENTIONS.md` §3); never choose them as a prefix
