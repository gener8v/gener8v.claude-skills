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
