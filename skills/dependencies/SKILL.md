---
name: dependencies
description: "Map dependencies between capability areas, external systems and shared resources into .gener8v/dependencies/dependency-map.md, with phased sequencing, parallelization opportunities and the critical path. Use when a PRD has more than one capability area and implementation order must be decided, such as 'what order should we build these in', 'what is the critical path' or 'what can run in parallel'. Not for the constraints on one area (constraints) or ordering tickets inside one area (ticket-breakdown)."
---

# Dependencies Skill

## Purpose

Map dependencies between capability areas, external systems, shared resources, and sequencing requirements for a PRD or set of Specifications. The output is a dependency graph (in structured markdown) that reveals what must come before what, what shares state or infrastructure, and where parallel work is possible. This skill exists to prevent the most common planning failure: starting work on something that is blocked by something else no one identified.

## When to Use

Use this skill when:
- A PRD has multiple capability areas that may depend on each other
- Specifications reference shared data, systems, or behaviors that create coupling
- Implementation sequencing needs to be determined before ticket breakdown
- The team needs to identify the critical path through a body of work
- External system dependencies need to be documented for coordination
- Preparing input for the Ticket Breakdown skill

## Input

**Source:** The PRD, plus any available Specifications and Constraints analyses
**Read from:**
- PRD: `.gener8v/prd.md`
- Specifications: `.gener8v/specifications/*.md` (all available)
- Constraints: `.gener8v/constraints/*.md` (all available, if produced)

**Expects:** At minimum, a PRD with multiple capability areas. Richer analysis is possible when Specifications and Constraints documents are also available. The skill should note in Source Context which documents were analyzed.

## Output

**Produces:** A dependency map covering all capability areas in the PRD
**Write to:** `.gener8v/dependencies/dependency-map.md`
**Creates directory:** `.gener8v/dependencies/` if it does not exist

One dependency map per PRD. If the project scope changes significantly (e.g., new capability areas added), regenerate this file.

## Output Format

Write the map in the shape of `assets/dependency-map.md`. Read it before writing and follow it exactly. `scripts/gener8v-state.py` reads only the `**Status:**` line in Source Context — a map that is not Approved counts toward approvals pending — so the rest of the structure is for its readers: Technical Design and Ticket Breakdown cite its `DEP-`, `EXT-`, `RES-` and `RD-` IDs.

---

## Principles

### Hard vs. Soft Dependencies
A **hard dependency** means work cannot begin without the dependency being satisfied. A **soft dependency** means work can begin but cannot be completed, or would benefit significantly from the dependency being available. This distinction directly affects sequencing—hard dependencies are immovable; soft dependencies create options.

### Dependencies Are Directional
"A depends on B" is not the same as "A and B are related." Every dependency should state which capability needs something and which capability provides it. Bidirectional dependencies (A needs B and B needs A) are circular and must be resolved—flag them explicitly.

### Surface Coupling, Not Just Sequence
Shared resources, shared data models, and shared infrastructure create coupling even when there is no strict ordering requirement. Two capabilities that both write to the same data store may not have a sequencing dependency, but they have a coordination dependency that affects implementation.

### Critical Path Clarity
The critical path is the longest chain of hard dependencies. It determines the minimum sequential effort regardless of team size or parallelization. Identifying it early prevents the illusion that "more people" can compress a timeline that is dependency-bound.

### External Dependencies Are the Highest Risk
Dependencies on teams, systems, or decisions outside the project's control are the most common source of delays. Treat every external dependency as a risk until confirmed otherwise.

### Minimize Assumptions About Order
Do not impose sequencing that the dependencies don't require. If two capabilities are genuinely independent, say so—even if convention or intuition suggests one "should" come first. Unnecessary sequencing wastes parallelization opportunities.

## Process

0. **Validate Input**: Confirm `.gener8v/prd.md` exists and contains multiple capability areas. If the PRD is missing, stop and recommend running the Planning skill. If only one capability area exists, note that internal dependency analysis is not applicable but external dependencies may still be relevant. Read any available specifications and constraints to enrich the analysis.

0b. **Load the Existing Artifact**: If the output file already exists, read it first. Every existing ID and heading is kept; new items are allocated above the current maximum ID; anything no longer applicable is marked `**Status:** Withdrawn` in place rather than deleted. IDs are append-only (`CONVENTIONS.md` §4) — code and downstream documents reference them, and renumbering silently re-binds those references.

1. **Inventory Capability Areas**: List all capability areas from the PRD and any Specifications produced.

2. **Identify Internal Dependencies**: For each capability area, ask: "What does this need from other capability areas before it can start or complete?" Document each dependency with direction, type, and nature.

3. **Identify External Dependencies**: For each capability area, ask: "What does this need from outside the project?" Include systems, APIs, teams, decisions, and resources.

4. **Identify Shared Resources**: Scan for data stores, services, configuration, or concepts referenced by multiple capability areas. These are coupling points even without explicit dependencies.

5. **Build the Dependency Graph**: Arrange capability areas based on their dependencies. Identify independent nodes, chains, and clusters.

6. **Determine Sequencing**: Propose phases based on the dependency graph. Group capabilities that can start simultaneously in the same phase.

7. **Identify Parallelization**: Call out which capabilities can proceed concurrently and any partial overlaps.

8. **Trace the Critical Path**: Find the longest chain of hard dependencies. This is the minimum sequential effort.

9. **Assess Risk Dependencies**: Flag dependencies that are uncertain, controlled by external parties, or have known fragility.

10. **Flag Unknowns**: Document questions that affect dependency analysis as Open Questions.

11. **Record Approval**: Write `**Status:** Draft` and `**Approved by:** pending` in Source Context. **Ask, do not wait.** Present the artifact and request approval before the session moves on to another area, another skill, or another run — an artifact left `Draft` because nobody was asked is indistinguishable in the record from one the user declined to approve. When the user approves the map in conversation, set `**Status:** Approved` and record `**Approved by:** Architect — <name>, YYYY-MM-DD` (`CONVENTIONS.md` §7). Approval never blocks downstream skills; the record simply says which hat approved the sequencing.

## Example

A full dependency map for the Support Documentation Search System — three capability areas, hard and soft internal dependencies, external dependencies tied to qualified constraint IDs, two shared resources, and a linear critical path with parallelization notes.

See `references/example.md` (relative to this skill's directory). Read it before producing your first dependency map.

---

## Troubleshooting

- **Two areas depend on each other.** A cycle has no valid sequence; do not break it by picking an order. Record both `DEP-` entries, flag the cycle as a Risk Dependency, and name what would resolve it — typically a shared contract both areas build against, recorded as a `RES-` entry, or one area's requirements split across phases. A sequence drawn through an unresolved cycle hides the real blocker (Notes).
- **Two areas write the same data and neither specification says which owns it.** Record a `RES-` entry with both areas under *Used By*, and an Open Question. Ownership is a component boundary, decided in Technical Design; the map makes the coupling visible, it does not settle it.
- **The dependency order conflicts with the change brief's Priority Cut.** The map orders by dependency only (Notes): a Must area that hard-depends on a Could area still waits for it. State the conflict under Sequencing Analysis instead of reordering phases; Ticket Breakdown weighs priority against the order, and the Product Owner decides whether the Could area moves up the cut.
- **Re-running after areas were added or specifications landed.** Load the existing map first (Process step 0b). Rewriting the analysis is fine; renumbering is not — tickets cite `DEP-`, `EXT-` and `RES-` IDs, so existing IDs stay, new ones go above the maximum, and a dependency that no longer holds is marked `**Status:** Withdrawn` in place.
- **Orchestrate recommends a dependency map for a small project.** The recommendation is marked optional for light scope. Run the map when areas share data or depend on an external system; otherwise Orchestrate's scale step lists it as skipped with the reason, and Ticket Breakdown proceeds without it.

## Integration with Other Skills

**Upstream:**
- **Planning Skill**: Provides the PRD with capability areas to analyze
- **Specification Skill**: Provides detailed requirements that reveal data flows and coupling
- **Constraints Skill**: Provides constraints that may create or influence dependencies (especially Integration and Technical constraints)

**Downstream:**
- **Technical Design Skill**: Uses dependency information to inform component boundaries and interface design
- **Ticket Breakdown Skill**: Uses sequencing and dependency information to order work items and define blockers

## Revisions

- Re-run this skill when capability areas are added, removed, or significantly changed in the PRD
- Re-run when new specifications or constraints reveal dependencies not visible from the PRD alone
- The dependency map is a single file covering the entire PRD — partial updates are possible but full regeneration is safer when multiple areas change
- Downstream tickets that reference dependency IDs (DEP-XXX, EXT-XXX, RES-XXX) become potentially stale when the dependency map changes; IDs are append-only
- Shared resources use the `RES-` prefix (not `SR-`, which collides with a requirement prefix such as Search & Retrieval's `SR-REQ-XXX`)

## Notes

- Analyze at the PRD level for sequencing across capability areas; analyze at the Specification level for finer-grained dependencies within a capability
- Circular dependencies are a red flag—if found, document them explicitly and recommend resolution before proceeding
- The suggested sequence is based on dependencies only, not effort or priority; the Ticket Breakdown skill incorporates this alongside other factors
- This skill does not assign work to teams or individuals
- Update the dependency map if new Specifications or Constraints analyses materially change the landscape
