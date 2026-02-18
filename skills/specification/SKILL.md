# Specification Skill

## Purpose

Transform a single Capability Area from a Planning Skill PRD into a detailed functional specification. The specification enumerates all functional requirements, defines behaviors, describes edge cases, and surfaces decisions needed—all while remaining implementation-agnostic. The output is designed for downstream analysis (Constraints, Dependencies) and eventual decomposition into tickets.

## When to Use

Use this skill when:
- A Capability Area from a PRD needs detailed elaboration before implementation planning
- Stakeholders need to review and approve detailed requirements
- The scope of a capability area is ambiguous and needs explicit definition
- Preparing input for the Constraints, Dependencies, or Ticket Breakdown skills

## Input

**Source:** A single Capability Area from a Planning Skill PRD
**Read from:** `.gener8v/prd.md`
**Expects:** A PRD with `## Functional Capabilities` containing `### [Capability Area]` subsections. This skill operates on one capability area at a time.

## Output

**Produces:** A detailed functional specification for one capability area
**Write to:** `.gener8v/specifications/[capability-area-slug].md`
**Creates directory:** `.gener8v/specifications/` if it does not exist
**Naming convention:** Lowercase, hyphen-separated slug of the capability area name (e.g., `search-and-retrieval.md`, `documentation-ingestion.md`)

Run this skill once per capability area. A PRD with 5 capability areas produces 5 specification files.

## Output Format

Produce a markdown document with the following structure:

```markdown
# [Capability Area Name] Specification

## Overview

[2-3 sentences summarizing what this capability does and why it matters.
Should be understandable without reading the source PRD.]

## Source Context

**Parent PRD:** [Title of the PRD this capability came from]
**Related Capabilities:** [List other capability areas this interacts with]

## Functional Requirements

[Detailed enumeration of what the system should do. Group into logical
subsections. Each requirement should be atomic and testable.]

### [Subsection Name]

- **[XX]-REQ-001**: The system should [verb] [what] [conditions/context]
- **[XX]-REQ-002**: The system should...

[XX] is a 2-4 letter prefix derived from the capability area name
(e.g., SR for Search & Retrieval, DI for Documentation Ingestion).
This prefix ensures requirement IDs are unique across the project.

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
Requirements use [PREFIX]-REQ-XXX identifiers (e.g., SR-REQ-001 for Search & Retrieval). The prefix is derived from the capability area name — typically the first letter of each word or the first 2-4 letters. This ensures requirement IDs are unique across the entire project, preventing ambiguity when tickets, constraints, or audits reference requirements from different specifications.

## Process

0. **Validate Input**: Confirm `.gener8v/prd.md` exists and contains a `## Functional Capabilities` section with `###` subsections. If the PRD is missing, stop and recommend running the Planning skill. If the target capability area is not found in the PRD, inform the user and list the available areas.

1. **Extract Context**: Identify the Capability Area and its relationship to parent PRD and sibling capabilities.
2. **Expand Requirements**: Decompose each bullet into atomic, testable requirements.
3. **Define Behaviors**: Document business rules and conditional behaviors.
4. **Surface Edge Cases**: Identify boundary conditions, error states, unusual scenarios.
5. **Identify States**: Map valid states and transitions for stateful entities.
6. **Capture Data Needs**: List information to capture, store, or display.
7. **Document Interactions**: Describe interaction patterns without prescribing UI.
8. **Flag Unknowns**: Move ambiguity to Open Questions; document assumptions.
9. **Review for Completeness**: Ensure standalone understandability.

## Example

### Input

The "Search & Retrieval" capability area from the Support Documentation Search System PRD:

> ### Search & Retrieval
> - The system should accept natural language questions as input
> - The system should return relevant documentation excerpts ranked by relevance
> - The system should indicate the source document for each result
> - The system should handle questions even when exact terminology doesn't match

### Output

````markdown
# Search & Retrieval Specification

## Overview

Defines how support agents search documentation using natural language and receive ranked, source-attributed results. This capability is the core interaction point — agents pose questions and the system surfaces relevant documentation excerpts.

## Source Context

**Parent PRD:** Support Documentation Search System
**Related Capabilities:** Results Presentation, Documentation Ingestion

## Functional Requirements

### Query Processing

- **SR-REQ-001**: The system should accept free-text natural language questions as search input
- **SR-REQ-002**: The system should accept queries of at least 500 characters
- **SR-REQ-003**: The system should reject empty or whitespace-only queries with a clear message

### Search Execution

- **SR-REQ-004**: The system should return documentation excerpts that are relevant to the query
- **SR-REQ-005**: The system should rank results by relevance, with the most relevant result first
- **SR-REQ-006**: The system should return relevant results even when the query uses different terminology than the source documentation
- **SR-REQ-007**: The system should return results from all indexed documentation sources, not just a single source

### Source Attribution

- **SR-REQ-008**: The system should indicate the source document title for each result
- **SR-REQ-009**: The system should provide a stable reference to the source location for each result
- **SR-REQ-010**: The system should attribute results consistently regardless of which documentation source they originate from

## Behaviors & Rules

### Query Handling

- When a query is submitted, the system should begin processing and indicate that a search is in progress
- When no results meet the relevance threshold, the system should indicate that no relevant documentation was found rather than returning low-quality results
- If the search service is unavailable, the system should communicate the issue clearly rather than returning empty results silently

### Result Ranking

- When multiple results have identical relevance scores, the system should order them deterministically
- When a result excerpt spans a section boundary in the source document, the system should include enough context to be understandable

## Edge Cases & Error Handling

| Scenario | Expected Behavior |
|----------|-------------------|
| Query is a single word | The system should attempt the search and return results if any are relevant |
| Query is in a different language than the documentation | The system should return whatever results match; no translation is expected |
| Source document has been deleted since indexing | The system should still return the excerpt but indicate the source may be unavailable |
| Query matches hundreds of documents | The system should return a bounded set of the most relevant results |
| Documentation contains duplicate content across sources | The system should return results from each source independently; deduplication is not required |

## Data Requirements

- The system should have access to an index of documentation content built by the Documentation Ingestion capability
- The system should store relevance scores with sufficient precision to produce consistent ordering
- The system should capture the source document title and location reference at index time

## User Interactions

- The user should be able to submit a search by providing a natural language question
- The system should provide feedback that a search is in progress after submission
- The user should be able to distinguish between "no results found" and "search failed"

## Open Questions

- [ ] **OQ-001**: Should there be a maximum number of results returned per query?
- [ ] **OQ-002**: Should the system support follow-up queries that refine previous results?
- [ ] **OQ-003**: What relevance threshold should separate "returned" from "not relevant enough"?
- [ ] **OQ-004**: Should search history be preserved within a session? (Carried from PRD)

## Assumptions

- Assumption: Documentation is indexed and available before search is used (dependency on Documentation Ingestion)
- Assumption: Queries are in the same language as the documentation
- Assumption: The relevance ranking algorithm is determined during implementation, not specified here
````

---

## Integration with Other Skills

**Upstream:**
- **Planning Skill**: Provides the Capability Area that this skill elaborates

**Downstream:**
- **Constraints Skill**: Analyzes for technical, compliance, or operational constraints
- **Dependencies Skill**: Maps dependencies between capabilities and external systems
- **Technical Design Skill**: Translates requirements into architecture decisions and component design
- **Ticket Breakdown Skill**: Decomposes requirements into implementable work items

## Revisions

- Re-running this skill overwrites the specification file for the target capability area
- Downstream artifacts that reference this specification's requirements (constraints, technical designs, tickets) become potentially stale
- If requirements are renumbered, all downstream references to the old IDs must be updated
- If the PRD's capability area description changes, compare the new and existing specification to determine whether a full regeneration or targeted update is appropriate

## Notes

- Generate one specification per Capability Area; do not combine multiple areas
- Requirements should be numbered sequentially within each specification, using the capability area prefix
- Open Questions from source PRD relevant to this capability should be carried forward
- This skill does not define acceptance criteria—that occurs during Ticket Breakdown
- Keep specifications under ~2000 words; split complex capabilities if needed
