---
name: technical-design
description: "Translate specifications, constraints and dependencies into architecture decisions (AD-XXX), component boundaries, data model and interface contracts under .gener8v/technical-design/. Use when technology or architecture choices must be settled before tickets are written, such as 'which datastore should we use' or 'design the components for search'. Skip it when the approach is obvious and uncontested. Not for judging an architecture that has already shipped (architecture-review)."
argument-hint: "[capability area | system]"
---

# Technical Design Skill

**Invoked with:** `$ARGUMENTS`

If that is empty, ask the user whether to design one capability area or the cross-cutting system design before doing anything else. Never guess the target.

## Purpose

Bridge the gap between functional specification and implementation. This skill translates requirements, constraints, and dependencies into architectural decisions, technology choices, component boundaries, and interface contracts. The output is the "how" that complements the specification's "what" — and directly informs ticket breakdown by giving developers a shared technical foundation before work begins.

## When to Use

Use this skill when:
- Specifications and constraints have been completed for one or more capability areas
- The team needs to agree on architecture and technology choices before writing code
- Multiple capability areas share infrastructure, data stores, or services that need coordinated design
- Technology choices materially affect ticket scope, sequencing, or sizing
- The gap between "what to build" and "how to build it" is large enough to warrant explicit decisions

Skip this skill when:
- The implementation approach is obvious and uncontested
- The team has an established architecture and the new work fits cleanly within it
- The scope is small enough that technical decisions can be made within individual tickets

## Input

**Source:** Specifications, Constraints analyses, Dependency Map, and optionally System Context
**Read from:**
- Specifications: `.gener8v/specifications/*.md`
- Constraints: `.gener8v/constraints/*.md` (if available — PRD-level and per-area)
- Dependency Map: `.gener8v/dependencies/dependency-map.md` (if available)
- System Context: `.gener8v/context.md` (if available — including its `## Repositories` table, which names every repository in the workspace and is the source of the root-relative paths this design cites)
- Flow maps: `.gener8v/flows/*.md` (if Flow Mapping has run — the current-state baseline a target design moves from)
- The repository itself, for the infrastructure and patterns the design assumes already exist
- `.gener8v/CONVENTIONS.md`

**Expects:** At minimum, one specification with numbered requirements — and its `## Non-Functional Requirements` (PREFIX-NFR-XXX), which set the measurable targets the infrastructure and risk sections must answer to. Richer design is possible when constraints, dependencies, and system context are available. Note which inputs were used in the Source Context section of the output.

**If input is missing or malformed:**
- If no specifications exist, stop and recommend running the Specification skill first
- If constraints or dependencies are missing, note "Not yet performed" in Source Context and proceed — flag that design decisions may need revisiting once these analyses exist
- If system context is missing, note this and flag any decisions that depend on technology stack or infrastructure knowledge as open questions

## Output

**Produces:** A technical design document
**Write to:**
- Per-capability design: `.gener8v/technical-design/[capability-area-slug].md`
- Cross-cutting system design: `.gener8v/technical-design/system-design.md`
**Creates directory:** `.gener8v/technical-design/` if it does not exist

Run this skill once per capability area that warrants technical design, or once for system-wide design that spans multiple capabilities. A single capability with complex internals warrants its own document; a simple capability may only need a section in the system-wide design.

## Output Format

Write the design in the shape of `assets/technical-design.md`. Read it before writing and follow it exactly. `scripts/gener8v-state.py` reads the first `**Status:**` line in the file as the design's approval state, so Source Context stays above the Architecture Decisions — a decision marked `**Status:** Superseded by AD-XXX` must never be the first. Lint flags any requirement or NFR ID the design cites that exists in no specification.

---

## Principles

### Decisions Over Descriptions
The primary value of this skill is recording decisions and their rationale — not describing a system in abstract terms. Every architecture decision should answer: what was the question, what did we decide, and why? A technical design without explicit decisions is just a diagram that no one can execute from.

### Justify With Alternatives
A decision without alternatives considered is just an assertion. Document what other approaches were viable and why they were rejected. This prevents relitigating decisions later and gives future maintainers context for when circumstances change.

### Design for the Requirements
Architecture should serve the requirements, not the other way around. Every component, every data model entity, and every interface should trace back to requirements it supports. If a design element exists for future hypothetical needs, call it out explicitly — don't smuggle it in as if it were required.

### Make Interfaces Explicit
The boundaries between components are where most integration issues occur. Define interfaces with enough specificity that two developers can independently build components on either side and have them work together. Input, output, and error cases — at minimum.

### Technical Debt Is a Choice
When a design makes an expedient choice that creates future maintenance burden, document it as a deliberate decision with rationale. "We chose X because Y, knowing that Z will need to change when [condition]." Undocumented shortcuts are accidents; documented ones are strategy.

### Constrained by Constraints
Technical decisions must respect the constraints identified by the Constraints skill. If a design decision conflicts with a constraint, either the design must change or the constraint must be challenged — don't silently ignore the tension.

## Process

0b. **Load the Existing Artifact**: If the output file already exists, read it first. Every existing ID and heading is kept; new items are allocated above the current maximum ID; anything no longer applicable is marked `**Status:** Withdrawn` in place rather than deleted. IDs are append-only (`CONVENTIONS.md` §4) — code and downstream documents reference them, and renumbering silently re-binds those references.

1. **Gather Inputs**: Read the relevant specifications, constraints, dependency map, and system context. Note which documents are available and which are missing.

1b. **Verify the Starting Point**: For every piece of infrastructure, library or pattern the design will build on because it "already exists" (a database extension, a queue, an auth middleware, a module layout), confirm it in the repository or `context.md` and cite the file. A design premised on infrastructure that is not there is a ticket-time surprise; make it an Open Technical Question now.

2. **Identify Decisions Needed**: Scan requirements and constraints for questions that require architectural answers: What technology? What pattern? What boundary? What trade-off?

3. **Make and Document Decisions**: For each decision point, evaluate options against requirements and constraints. Document the decision with full rationale and alternatives.

4. **Design Components**: Identify the major building blocks. Define what each does, what it depends on, and how others interact with it. When `context.md`'s `## Repositories` table lists several repositories, name the one each component lives in; every code path cited anywhere in the design is root-relative (`api/src/search/query.ts`), never relative to a single repository.

5. **Model Data**: Identify data entities, their structure, relationships, and sources. Align with requirements about what data the system captures, stores, and displays.

6. **Define Interfaces**: For each boundary between components (or between the system and external systems), define the contract: input, output, error handling.

7. **Identify Infrastructure**: Determine what infrastructure the design requires beyond application code — databases, queues, caches, external services, deployment targets. For each item, cite the NFR IDs it serves (the index that keeps latency under target, the log pipeline that makes a request traceable); an NFR no infrastructure item or component serves is a gap to name, not to leave implicit.

8. **Assess Technical Risks**: Identify where the design has uncertainty, where decisions depend on unverified assumptions, or where implementation complexity is high. State which NFR each risk threatens under *Related NFRs* — a risk that would miss a measurable target is the kind Ticket Breakdown most needs to see.

9. **Review Against Constraints**: Walk through each constraint and verify the design respects it. Flag any tensions.

10. **Flag Unknowns**: Technical questions that can't be answered without prototyping, vendor evaluation, or stakeholder input go to Open Technical Questions.

11. **Write as Draft, Record Approval**: Write the document with `**Status:** Draft` and `**Approved by:** pending`. The Architect approves technical design (`CONVENTIONS.md` §7). **Ask, do not wait.** Present the artifact and request approval before the session moves on to another area, another skill, or another run — an artifact left `Draft` because nobody was asked is indistinguishable in the record from one the user declined to approve. When the user approves in conversation, update both lines — `**Status:** Approved`, `**Approved by:** Architect — <name>, YYYY-MM-DD`. Approval never blocks the next stage; Audit raises a Warning (never a block) when a stage was produced from an unapproved upstream artifact.

## Example

A complete Search & Retrieval design for the Support Documentation Search System: two architecture decisions (AD-001 vector similarity, AD-002 PostgreSQL + pgvector), four components, one data entity, an interface contract, infrastructure and risks that cite SR-NFR-001 and SR-NFR-002, and a Draft approval line.
See `references/example.md` in this skill's directory.
Read it before producing your first artifact of this kind.

---

## Troubleshooting

- **The specification behind the design is still Draft.** Design anyway — approval never blocks the next stage — but record the specification's state in Source Context and ask for its approval before tickets are cut; Audit warns on a design produced from an unapproved specification.
- **An architecture decision contradicts the specification's wording.** Record the decision with the requirement under *Requirements Affected*; do not edit the specification to match — requirement text changes only through a change, with its `*(amended … by <change-slug>)*` tag. Ticket Breakdown turns the supersession into a Known Hazard on every ticket that implements the requirement.
- **A decision is reversed after tickets or code cite it.** Keep the old decision, marked `**Status:** Superseded by AD-XXX`, and add the replacement above the current maximum AD ID (Revisions); the design returns to Draft until the Architect approves again. The decision-level status stays below Source Context — the state script reads the first `**Status:**` line in the file as the design's approval.
- **Lint reports `technical-design/<file>.md references requirement IDs that exist in no specification`.** A *Requirements Affected*, *Requirements Served* or *Related NFRs* line cites a mistyped ID, or one from an area not yet specified. Correct it; a design element that serves no existing requirement is the hypothetical need Design for the Requirements says to call out.
- **The workspace holds several repositories but `context.md` has no `## Repositories` table.** Component paths cannot be made root-relative with confidence. Record the missing repository map as an Open Technical Question and cite only paths the repository itself confirms (Process step 1b); do not guess which repository a component lives in.

## Integration with Other Skills

**Upstream:**
- **Specification Skill**: Provides the requirements that drive design decisions
- **Constraints Skill**: Provides boundaries the design must respect
- **Dependencies Skill**: Provides sequencing and coupling information that shapes component boundaries

**Downstream:**
- **Ticket Breakdown Skill**: Uses architecture decisions, component boundaries, and interface contracts to create technically-informed tickets
- **Delivery / Code Review / Security Review**: follow and verify architecture decisions (AD-XXX)
- **Architecture Review Skill**: tests these decisions against the shipped code once it exists
- **Audit Skill**: Reviews technical design for completeness and consistency with specifications and constraints

## Revisions

- Re-run this skill when specifications or constraints change in ways that affect architectural decisions
- When re-running, review existing Architecture Decisions first — some may still hold, others may need updating
- Downstream ticket breakdowns that reference this design become potentially stale when the design changes
- If only one Architecture Decision changes, update the specific decision and its downstream references rather than regenerating the entire document; superseded decisions stay in the document marked `**Status:** Superseded by AD-XXX`
- An amended design goes back to `**Status:** Draft` with `**Approved by:** pending` until the Architect approves it again

## Notes

- This skill produces the only implementation-specific artifact in the pipeline — technology names, architecture patterns, and component designs are expected and appropriate here
- Not every capability area needs its own technical design — simple capabilities that follow established patterns can be covered by a section in the system-wide design
- Architecture Decisions (AD-XXX) are referenced by tickets the same way requirements (REQ-XXX) are — they provide traceability from "why this approach" to "what to build"
- If the team has an existing Architecture Decision Record (ADR) practice, this skill's output can feed into or replace that process
- System context (`.gener8v/context.md`) is especially valuable for this skill — without it, technology choices are made in a vacuum
