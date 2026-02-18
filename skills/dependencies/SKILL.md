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

Produce a markdown document with the following structure:

```markdown
# [PRD or Project Title] — Dependency Map

## Overview

[2-3 sentences summarizing the dependency landscape. Call out the total
number of capability areas analyzed, the most coupled areas, and whether
a clear critical path exists.]

## Source Context

**Analyzed Documents:** [List PRD and/or Specifications analyzed]
**Capability Areas:** [Enumerate all capability areas in scope]

## Internal Dependencies

[Dependencies between capability areas within the same PRD.]

### [Capability Area A] → [Capability Area B]

- **DEP-001**: [What A needs from B, or what must be true about B before A can proceed]
  - *Type:* [Hard / Soft]
  - *Nature:* [Data / Behavior / Infrastructure / Shared Resource]
  - *Detail:* [Specific requirements, data flows, or shared state involved]

## External Dependencies

[Dependencies on systems, services, teams, or resources outside the PRD scope.]

- **EXT-001**: [Capability Area] depends on [External System/Team/Resource]
  - *Type:* [Hard / Soft]
  - *Nature:* [API / Data Source / Service / Team / Decision]
  - *Detail:* [What is needed, current availability, known limitations]
  - *Related Constraints:* [Constraint IDs from Constraints analysis, if applicable]

## Shared Resources

[Data stores, services, infrastructure, or concepts that multiple
capability areas depend on. These are coupling points.]

- **SR-001**: [Shared Resource Name]
  - *Used By:* [List of capability areas]
  - *Nature:* [Data Store / Service / Configuration / Concept]
  - *Implication:* [Why this coupling matters for sequencing or coordination]

## Sequencing Analysis

### Dependency Graph

[Text-based representation of the dependency flow.]

```
[Capability A] ──→ [Capability C] ──→ [Capability E]
                         ↑
[Capability B] ──────────┘

[Capability D] (independent)
```

### Suggested Sequence

[Ordered list of capability areas based on dependency analysis.]

1. **Phase 1** (no dependencies): [Capability areas that can start immediately]
2. **Phase 2** (depends on Phase 1): [Capability areas unblocked by Phase 1 completion]
3. **Phase 3** (depends on Phase 2): [Capability areas unblocked by Phase 2 completion]

### Parallelization Opportunities

- [Capability A] and [Capability D] have no shared dependencies and can proceed in parallel
- [Capability B] and [Capability C] share [resource] but only [specific aspect], allowing partial overlap

### Critical Path

[The longest chain of dependent capabilities that determines minimum
sequential duration.]

[Capability X] → [Capability Y] → [Capability Z]

*Rationale:* [Why this is the critical path — what makes each link necessary]

## Risk Dependencies

[Dependencies that are uncertain, fragile, or outside the team's control.]

- **RD-001**: [Dependency statement]
  - *Risk:* [What happens if this dependency is not met]
  - *Mitigation:* [Suggested approach to reduce risk]

## Open Questions

- [ ] **OQ-001**: [Question that affects dependency mapping]

## Assumptions

- Assumption: [Statement assumed to be true for this analysis]
```

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

## Example

### Input

Analyzing the Support Documentation Search System PRD with three capability areas:
- Search & Retrieval
- Results Presentation
- Documentation Ingestion

### Output

````markdown
# Support Documentation Search System — Dependency Map

## Overview

Three capability areas with a clear linear critical path. Documentation Ingestion is the foundational dependency—both Search & Retrieval and Results Presentation require ingested content to function. Results Presentation depends on Search & Retrieval for the result set it displays. No circular dependencies exist.

## Source Context

**Analyzed Documents:** Support Documentation Search System PRD, Search & Retrieval Specification
**Capability Areas:** Search & Retrieval, Results Presentation, Documentation Ingestion

## Internal Dependencies

### Search & Retrieval → Documentation Ingestion

- **DEP-001**: Search & Retrieval requires indexed documentation to search against
  - *Type:* Hard
  - *Nature:* Data
  - *Detail:* Search queries operate on an index built from ingested documentation. Without ingestion, there is nothing to search.

### Results Presentation → Search & Retrieval

- **DEP-002**: Results Presentation requires a result set to display
  - *Type:* Hard
  - *Nature:* Data / Behavior
  - *Detail:* Presentation layer consumes ranked results with source attribution from Search & Retrieval. The display format depends on the result structure.

### Results Presentation → Documentation Ingestion

- **DEP-003**: Source document navigation requires stable links established during ingestion
  - *Type:* Soft
  - *Nature:* Data
  - *Detail:* "Navigate to full source" functionality requires addressable source references. Presentation can be built against a mock interface, but end-to-end testing requires real ingested references.

## External Dependencies

- **EXT-001**: Documentation Ingestion depends on Confluence API access
  - *Type:* Hard
  - *Nature:* API
  - *Detail:* Confluence is a primary documentation source. API credentials and permission scope needed.
  - *Related Constraints:* IC-001

- **EXT-002**: Documentation Ingestion depends on legacy help center content extraction
  - *Type:* Hard
  - *Nature:* Data Source
  - *Detail:* Legacy system has no API (IC-002). Extraction method must be determined.
  - *Related Constraints:* IC-002, RF-001

- **EXT-003**: Compliance review of indexable content
  - *Type:* Soft
  - *Nature:* Decision
  - *Detail:* Data classification policies may restrict which documentation can be indexed (OQ-001 from Constraints analysis). Can proceed with known-safe content initially.

## Shared Resources

- **SR-001**: Document Index
  - *Used By:* Documentation Ingestion (writes), Search & Retrieval (reads)
  - *Nature:* Data Store
  - *Implication:* Index schema decisions in Ingestion directly constrain Search capabilities. These teams (or skill passes) must agree on index structure early.

- **SR-002**: Source Reference Format
  - *Used By:* Documentation Ingestion (produces), Results Presentation (consumes)
  - *Nature:* Data Contract
  - *Implication:* How sources are identified during ingestion determines how Presentation links back to them. Format must be defined before either capability is complete.

## Sequencing Analysis

### Dependency Graph

```
[Documentation Ingestion] ──→ [Search & Retrieval] ──→ [Results Presentation]
         ↑                                                       │
         └──────────── (soft: source references) ────────────────┘
```

### Suggested Sequence

1. **Phase 1**: Documentation Ingestion — no internal dependencies; can begin immediately once external dependencies (EXT-001, EXT-002) are resolved
2. **Phase 2**: Search & Retrieval — requires index from Phase 1
3. **Phase 3**: Results Presentation — requires result set from Phase 2

### Parallelization Opportunities

- Results Presentation interface design can proceed in parallel with Phases 1-2 using mock data, though integration testing requires real results
- Search & Retrieval query logic can be developed against a test index while full ingestion proceeds
- Source reference format (SR-002) should be defined early to unblock parallel interface work

### Critical Path

Documentation Ingestion → Search & Retrieval → Results Presentation

*Rationale:* Each step produces the data the next step consumes. This is a strictly linear chain for full integration, though partial parallel work is possible with mocks.

## Risk Dependencies

- **RD-001**: Legacy help center extraction method is undefined (EXT-002)
  - *Risk:* If no programmatic extraction is possible, Documentation Ingestion scope increases significantly or legacy content is excluded
  - *Mitigation:* Investigate extraction options in Phase 1; define fallback scope that excludes legacy content

- **RD-002**: Compliance review timeline is unknown (EXT-003)
  - *Risk:* Content restrictions discovered late could invalidate index design or reduce system utility
  - *Mitigation:* Begin with documentation known to be unrestricted; run compliance review in parallel

## Open Questions

- [ ] **OQ-001**: Can index updates be incremental, or must the full index be rebuilt on documentation changes?
- [ ] **OQ-002**: Is there an existing document identifier system, or must one be created during ingestion?

## Assumptions

- Assumption: Confluence API access can be provisioned within the project timeline
- Assumption: The document index is a single shared resource, not per-source
````

---

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
- Downstream tickets that reference dependency IDs (DEP-XXX, EXT-XXX) become potentially stale when the dependency map changes

## Notes

- Analyze at the PRD level for sequencing across capability areas; analyze at the Specification level for finer-grained dependencies within a capability
- Circular dependencies are a red flag—if found, document them explicitly and recommend resolution before proceeding
- The suggested sequence is based on dependencies only, not effort or priority; the Ticket Breakdown skill incorporates this alongside other factors
- This skill does not assign work to teams or individuals
- Update the dependency map if new Specifications or Constraints analyses materially change the landscape
