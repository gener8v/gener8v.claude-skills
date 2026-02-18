# Ticket Breakdown Skill

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

**Source:** A Specification, plus the corresponding Constraints analysis, Dependency Map, and Technical Design
**Read from:**
- Specification: `.gener8v/specifications/[capability-area-slug].md`
- Constraints: `.gener8v/constraints/[capability-area-slug].md` (if available)
- Dependency Map: `.gener8v/dependencies/dependency-map.md` (if available)
- Technical Design: `.gener8v/technical-design/[capability-area-slug].md` or `.gener8v/technical-design/system-design.md` (if available)

**Expects:** At minimum, a Specification with numbered requirements ([PREFIX]-REQ-XXX). If Constraints, Dependency Map, or Technical Design files are not available, note "Not yet performed" in the Source Context section of the output and proceed without them.

**If input is missing or malformed:**
- If no specification exists for the target capability area, stop and recommend running the Specification skill first
- If constraints, dependencies, or technical design are missing, proceed but note the gap — tickets will lack constraint-informed criteria, dependency ordering, or architecture context respectively

## Output

**Produces:** A ticket breakdown for one capability area
**Write to:** `.gener8v/tickets/[capability-area-slug].md`
**Creates directory:** `.gener8v/tickets/` if it does not exist
**Naming convention:** Matches the specification filename (e.g., `search-and-retrieval.md`)

Run this skill once per Specification. The output is the final artifact in the pipeline — ready for implementation teams or task management tooling.

## Output Format

Produce a markdown document with the following structure:

```markdown
# [Capability Area Name] — Ticket Breakdown

## Overview

[2-3 sentences summarizing the breakdown. State total ticket count,
how they cluster, and any notable sequencing from the dependency analysis.]

## Source Context

**Specification:** [Title of the specification being decomposed]
**Constraints Analysis:** [Title, or "Not yet performed"]
**Dependency Map:** [Title, or "Not yet performed"]
**Technical Design:** [Title, or "Not yet performed"]

## Tickets

### TICKET-001: [Concise action-oriented title]

**Summary:** [1-2 sentences describing what this ticket accomplishes]

**Requirements Covered:**
- [XX]-REQ-001: [Brief description]
- [XX]-REQ-002: [Brief description]

**Prior Art:** [What to read/understand before starting. For tickets with
no dependencies, point to relevant pipeline documents. For tickets that
depend on other tickets, specify the files and directories produced by
those tickets that this work builds on.]
- Read: [file path — source file, config, module, or pipeline artifact]
- Understand: [what to look for in that file and why it matters]

**Acceptance Criteria:**
- [ ] [Observable, verifiable condition that must be true when complete]
- [ ] [Another condition]
- [ ] [Another condition]

**Output:**
- [File or directory this ticket produces or modifies, with enough
  detail that downstream tickets can locate the work]

**Constraints:**
- [Relevant constraint IDs and brief description, or "None identified"]

**Depends On:** [Other ticket IDs this is blocked by, or "None"]
**Blocks:** [Other ticket IDs this unblocks, or "None"]

**Size:** [Small / Medium / Large]

**Notes:** [Implementation hints, context, or warnings — optional]

---

### TICKET-002: [Title]

...

## Ticket Dependency Chain

[Visual representation of ticket ordering]

```
TICKET-001 ──→ TICKET-003 ──→ TICKET-005
TICKET-002 ──→ TICKET-004 ──┘
```

## Suggested Ordering

[Recommended implementation sequence with rationale]

1. **TICKET-001** — [Why first: foundational, unblocks others, etc.]
2. **TICKET-002** — [Can parallel with TICKET-001 because...]
3. ...

## Backlog Summary

| Ticket | Title | Size | Depends On | Status |
|--------|-------|------|------------|--------|
| TICKET-001 | [Title] | Small | None | Ready |
| TICKET-002 | [Title] | Medium | None | Ready |
| TICKET-003 | [Title] | Large | TICKET-001 | Blocked |
| ... | ... | ... | ... | ... |

**Total Tickets:** [Count]
**Ready to Start:** [Count of tickets with no unresolved dependencies]
```

---

## Principles

### One Ticket, One Outcome
Each ticket should produce a single, demonstrable outcome. If a ticket requires the developer to make unrelated decisions or produce multiple distinct artifacts, it should be split. The test: can you demo what this ticket accomplished in one sentence?

### Acceptance Criteria Are the Contract
Acceptance criteria define "done." They must be observable and verifiable—not aspirational. A ticket without clear acceptance criteria is a ticket that will be argued about at review time.

**Good:** "Search returns results ranked by relevance score, with the highest-scoring result first."
**Avoid:** "Search works well and returns good results."

### Trace to Requirements
Every ticket should reference the requirements (REQ-XXX) it satisfies. Every requirement from the Specification should appear in at least one ticket. If a requirement has no ticket, it has been dropped—intentionally or accidentally. Both should be visible.

### Size Is Relative, Not Absolute
Size indicators (Small / Medium / Large) communicate relative complexity and scope, not duration. They help with planning and load balancing without the false precision of hour estimates.

- **Small**: Well-understood, limited scope, low uncertainty. A single focused work session.
- **Medium**: Clear scope but involves multiple components or moderate complexity. May surface minor unknowns.
- **Large**: Significant scope, multiple moving parts, or meaningful uncertainty. Consider whether it should be split further.

### Dependencies Flow Down
Ticket dependencies should reflect actual implementation order, informed by the Dependency Map. Do not create artificial dependencies based on assumed workflow. If two tickets are genuinely independent, they should be marked as such even if one "feels" like it should come first.

### Constraints Shape Acceptance Criteria
Constraints from the Constraints analysis should manifest as acceptance criteria or notes on relevant tickets. A compliance constraint becomes a testable condition. A technical constraint becomes a boundary the implementation must respect.

### Self-Contained Tickets
Each ticket should be understandable without reading every other ticket. Include enough context in the summary and acceptance criteria that a developer can pick it up and know what to build. Reference other tickets for dependency, not for comprehension.

### Prior Art Tells You Where to Look
Every ticket must include a **Prior Art** section that tells the implementing agent exactly what to read before starting. For tickets with no dependencies, this points to pipeline documents (specifications, constraints, dependency map). For tickets that depend on other tickets, this points to the specific files and modules those tickets produced. An LLM picking up TICKET-003 should never have to guess where TICKET-001's code lives.

### Output Tells Downstream Where to Find You
Every ticket must include an **Output** section that describes the files or directories the ticket produces or modifies. This is the contract between this ticket and any ticket that depends on it. Be specific: name the file path, describe what it exposes (function signatures, data structures, configuration), and note what downstream tickets will consume from it.

## Process

1. **Gather Inputs**: Collect the Specification, Constraints Analysis, and Dependency Map for the capability area. Note any open questions that remain unresolved.

2. **Identify Natural Boundaries**: Read through the Specification's requirements and look for natural groupings—subsections, data flows, interaction patterns, or state transitions that form coherent units of work.

3. **Draft Tickets**: For each boundary, create a ticket. Write the summary first, then map requirements, then define acceptance criteria.

4. **Define Prior Art**: For each ticket, identify what the implementing agent needs to read before starting. Point to pipeline artifacts (`.gener8v/` files) and, for dependent tickets, the specific source files and modules produced by predecessor tickets.

5. **Define Output**: For each ticket, specify what files or directories it produces or modifies. Name paths, describe exposed interfaces, and note what downstream tickets will consume. Use `{ext}` as a placeholder when the language/framework is not yet decided.

6. **Apply Constraints**: Review each ticket against the Constraints Analysis. Add relevant constraints as acceptance criteria or notes.

7. **Map Ticket Dependencies**: Using the Dependency Map and the requirements themselves, determine which tickets block which. Keep the graph as flat as possible—deep chains reduce parallelization.

8. **Size Tickets**: Assign relative size. If any ticket is Large, evaluate whether it can be split without creating artificial boundaries.

9. **Verify Coverage**: Check that every requirement from the Specification appears in at least one ticket. Check that no requirement is orphaned. Check that every ticket has Prior Art and Output sections.

10. **Determine Ordering**: Propose an implementation sequence based on dependencies, risk (build risky things first), and value (deliver demonstrable capability early).

11. **Build Summary Table**: Create the backlog summary with dependency status so "ready to start" tickets are immediately visible.

12. **Flag Gaps**: If open questions from upstream skills affect ticket definition, note them. If a ticket cannot be fully specified, say so and identify what is needed.

## Example

### Input

Decomposing the "Search & Retrieval" Specification with requirements:
- SR-REQ-001: Accept natural language questions as input
- SR-REQ-002: Return relevant documentation excerpts ranked by relevance
- SR-REQ-003: Indicate the source document for each result
- SR-REQ-004: Handle questions even when exact terminology doesn't match

With constraints TC-001 (semantic search needed for SR-REQ-004) and TC-002 (stable identifiers needed for SR-REQ-003), and dependency DEP-001 (requires indexed documentation from Documentation Ingestion).

### Output

````markdown
# Search & Retrieval — Ticket Breakdown

## Overview

Four tickets decomposed from the Search & Retrieval specification. The work forms a short dependency chain: query interface and search index setup can proceed in parallel, followed by ranking logic, then source attribution. Total of 2 Small, 1 Medium, and 1 Medium ticket.

## Source Context

**Specification:** Search & Retrieval Specification
**Constraints Analysis:** Search & Retrieval Constraints Analysis
**Dependency Map:** Support Documentation Search System Dependency Map

## Tickets

### TICKET-001: Implement query input interface

**Summary:** Build the interface that accepts natural language questions from support agents and passes them to the search pipeline.

**Requirements Covered:**
- SR-REQ-001: Accept natural language questions as input

**Prior Art:**
- Read: `.gener8v/specifications/search-and-retrieval.md` — SR-REQ-001 for full requirement context
- Read: `.gener8v/dependencies/dependency-map.md` — understand where this capability sits in the system

**Acceptance Criteria:**
- [ ] The system accepts free-text input of at least 500 characters
- [ ] The system passes the query text to the search pipeline without modification
- [ ] The system provides feedback that a search is in progress
- [ ] Empty or whitespace-only queries are rejected with a clear message

**Output:**
- `src/search/query-input.{ext}` — query input module exposing a function/method that accepts a string query and returns it to the search pipeline
- The query interface contract (function signature, input validation rules) that TICKET-003 will consume

**Constraints:** None identified

**Depends On:** None
**Blocks:** TICKET-003

**Size:** Small

---

### TICKET-002: Configure search index for semantic matching

**Summary:** Set up the search index to support semantic similarity matching, enabling results even when query terminology differs from document terminology.

**Requirements Covered:**
- SR-REQ-004: Handle questions even when exact terminology doesn't match

**Prior Art:**
- Read: `.gener8v/specifications/search-and-retrieval.md` — SR-REQ-004 for full requirement context
- Read: `.gener8v/constraints/search-and-retrieval.md` — TC-001 for semantic search constraint details
- Read: `.gener8v/dependencies/dependency-map.md` — SR-001 (Document Index shared resource) for index schema coordination with Documentation Ingestion

**Acceptance Criteria:**
- [ ] The search index supports semantic similarity queries, not just keyword matching
- [ ] A query using synonyms or paraphrased terminology returns relevant results from documentation that uses different wording
- [ ] Index is populated from the output of the Documentation Ingestion pipeline

**Output:**
- `src/search/index.{ext}` — index configuration and schema definition
- `src/search/index-client.{ext}` — client module for querying the index, exposing a search function that accepts a query string and returns scored results
- Index schema documentation or contract that Documentation Ingestion will write to and TICKET-003 will read from

**Constraints:**
- TC-001: Semantic search capability required

**Depends On:** None (index schema can be defined before ingestion is complete; integration testing requires DEP-001)
**Blocks:** TICKET-003

**Size:** Medium

**Notes:** Index schema should be coordinated with the Documentation Ingestion capability (SR-001 from Dependency Map). Define the schema contract early even if full content is not yet ingested.

---

### TICKET-003: Implement relevance ranking

**Summary:** Build the ranking logic that orders search results by relevance score so the most useful documentation appears first.

**Requirements Covered:**
- SR-REQ-002: Return relevant documentation excerpts ranked by relevance

**Prior Art:**
- Read: TICKET-001 output at `src/search/query-input.{ext}` — understand the query interface contract (how queries arrive)
- Read: TICKET-002 output at `src/search/index-client.{ext}` — understand the index query interface (how raw results are returned and what fields are available, including relevance scores)
- Read: `.gener8v/specifications/search-and-retrieval.md` — SR-REQ-002 for full requirement context

**Acceptance Criteria:**
- [ ] Results are returned in descending order of relevance score
- [ ] Each result includes the relevant excerpt, not the full document
- [ ] A query with multiple matches returns them in a consistent, repeatable order
- [ ] Results with identical relevance scores are ordered deterministically

**Output:**
- `src/search/ranking.{ext}` — ranking module that takes raw index results and returns ordered, excerpt-bearing results
- A ranked result type/structure (with fields: excerpt, relevance score, source metadata) that TICKET-004 will extend with attribution

**Constraints:** None identified

**Depends On:** TICKET-001, TICKET-002
**Blocks:** TICKET-004

**Size:** Medium

---

### TICKET-004: Add source document attribution to results

**Summary:** Attach source document identification and navigation references to each search result so agents can trace results back to their origin.

**Requirements Covered:**
- SR-REQ-003: Indicate the source document for each result

**Prior Art:**
- Read: TICKET-003 output at `src/search/ranking.{ext}` — understand the ranked result structure that this ticket extends with source attribution fields
- Read: TICKET-002 output at `src/search/index-client.{ext}` — understand what source metadata is available from the index
- Read: `.gener8v/constraints/search-and-retrieval.md` — TC-002 for stable identifier constraint details
- Read: `.gener8v/dependencies/dependency-map.md` — SR-002 (Source Reference Format) for the shared contract with Documentation Ingestion and Results Presentation

**Acceptance Criteria:**
- [ ] Each result displays the title of the source document
- [ ] Each result includes a stable reference that identifies the source location
- [ ] Source references resolve to the correct document in the source system
- [ ] Results from different documentation sources are attributed consistently

**Output:**
- Modified `src/search/ranking.{ext}` (or new `src/search/attribution.{ext}`) — extends ranked results with source document title and stable reference link
- The final search result type/structure consumed by the Results Presentation capability

**Constraints:**
- TC-002: Stable, addressable identifiers required from ingestion

**Depends On:** TICKET-003
**Blocks:** None

**Size:** Small

**Notes:** Source reference format depends on SR-002 (shared resource contract with Documentation Ingestion and Results Presentation). Verify format is defined before implementation.

## Ticket Dependency Chain

```
TICKET-001 ──→ TICKET-003 ──→ TICKET-004
TICKET-002 ──┘
```

## Suggested Ordering

1. **TICKET-001** and **TICKET-002** — No dependencies, can start in parallel. TICKET-002 carries more uncertainty (semantic search setup) so starting early reduces risk.
2. **TICKET-003** — Unblocked once query interface and index are available. Core search value is delivered here.
3. **TICKET-004** — Final layer; adds traceability to results. Lower risk, clear scope.

## Backlog Summary

| Ticket | Title | Size | Depends On | Status |
|--------|-------|------|------------|--------|
| TICKET-001 | Implement query input interface | Small | None | Ready |
| TICKET-002 | Configure search index for semantic matching | Medium | None | Ready |
| TICKET-003 | Implement relevance ranking | Medium | TICKET-001, TICKET-002 | Blocked |
| TICKET-004 | Add source document attribution to results | Small | TICKET-003 | Blocked |

**Total Tickets:** 4
**Ready to Start:** 2
````

---

## Integration with Other Skills

**Upstream:**
- **Planning Skill**: Provides the PRD that defines capability areas
- **Specification Skill**: Provides the detailed requirements that are decomposed into tickets
- **Constraints Skill**: Provides constraints that shape acceptance criteria and surface implementation boundaries
- **Dependencies Skill**: Provides sequencing information and external dependency awareness
- **Technical Design Skill**: Provides architecture decisions, component boundaries, and interface contracts that inform ticket scope and Prior Art references

**Downstream:**
- This is the final skill in the pipeline. Output is consumed by implementation teams or further task management tooling.

## Revisions

- Re-run this skill when the source specification, constraints, dependencies, or technical design change in ways that affect ticket scope or ordering
- When re-running, compare with the existing ticket breakdown — some tickets may survive unchanged while others need updating
- If only a single requirement changes, consider updating the affected ticket(s) rather than regenerating the entire breakdown
- If the technical design introduces new architecture decisions, tickets may need new acceptance criteria or Prior Art references

## Notes

- Generate one ticket breakdown per Specification; do not combine multiple capability areas into one breakdown
- If a requirement spans multiple tickets, note this and ensure acceptance criteria collectively cover the full requirement
- Large tickets should prompt reconsideration—can they be split without creating artificial boundaries?
- Open questions from upstream skills that affect ticket definition should be listed; do not invent acceptance criteria to fill gaps left by unresolved questions
- This skill does not assign tickets to individuals or teams
- This skill does not estimate duration—size indicators communicate relative scope only
- When a Technical Design is available, tickets should reference Architecture Decisions (AD-XXX) in their notes or constraints, and Prior Art should point to technical design documents alongside specifications
