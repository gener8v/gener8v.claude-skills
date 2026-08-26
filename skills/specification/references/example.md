# Specification — worked example

The canonical pipeline example: the **Search & Retrieval** area of the *Support Documentation Search
System*, specified for the first change, `support-search`. It shows the priority and change tags on
requirements, the Non-Functional Requirements section, the approval lines in Source Context, and the
change-brief update the skill makes after writing.

## Input

Invoked as `/specification Search & Retrieval for support-search`.

The "Search & Retrieval" capability area from `.gener8v/prd.md`:

> ### Search & Retrieval
> - The system should accept natural language questions as input
> - The system should return relevant documentation excerpts ranked by relevance
> - The system should indicate the source document for each result
> - The system should handle questions even when exact terminology doesn't match

The change brief `.gener8v/changes/support-search/change.md`, as Planning left it — its Priority Cut
puts query input, the semantic index, relevance ranking and the latency target under **Must** and source
attribution and request logging under **Should**, and its Affected Capability Areas row for this area reads:

> | Search & Retrieval | adds area | (pending specification) |

## Output — `.gener8v/specifications/search-and-retrieval.md`

````markdown
# Search & Retrieval Specification

## Overview

Defines how support agents search documentation using natural language and receive ranked, source-attributed results. This capability is the core interaction point — agents pose questions and the system surfaces relevant documentation excerpts.

## Source Context

**Parent PRD:** Support Documentation Search System
**Requirement prefix:** SR
**Status:** Draft
**Approved by:** pending
**Related Capabilities:** Results Presentation, Documentation Ingestion

## Functional Requirements

### Query Processing

- **SR-REQ-001** *(must · change: support-search)*: The system should accept free-text natural language questions as search input
- **SR-REQ-002** *(must · change: support-search)*: The system should accept queries of at least 500 characters
- **SR-REQ-003** *(must · change: support-search)*: The system should reject empty or whitespace-only queries with a clear message

### Search Execution

- **SR-REQ-004** *(must · change: support-search)*: The system should return documentation excerpts that are relevant to the query
- **SR-REQ-005** *(must · change: support-search)*: The system should rank results by relevance, with the most relevant result first
- **SR-REQ-006** *(must · change: support-search)*: The system should return relevant results even when the query uses different terminology than the source documentation
- **SR-REQ-007** *(must · change: support-search)*: The system should return results from all indexed documentation sources, not just a single source

### Source Attribution

- **SR-REQ-008** *(should · change: support-search)*: The system should indicate the source document title for each result
- **SR-REQ-009** *(should · change: support-search)*: The system should provide a stable reference to the source location for each result
- **SR-REQ-010** *(should · change: support-search)*: The system should attribute results consistently regardless of which documentation source they originate from

## Non-Functional Requirements

- **SR-NFR-001** *(must · change: support-search)*: p95 search latency ≤ 800 ms at 50 concurrent users — **verified by:** k6 load test against the search endpoint, run in the Delivery verification step
- **SR-NFR-002** *(should · change: support-search)*: Every search request is logged with a correlation id and its duration — **verified by:** a log-format test that submits a query and asserts both fields are present in the emitted log record

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

## Change brief update — `.gener8v/changes/support-search/change.md`

After writing the specification, the skill replaces the pending cell in the brief's Affected
Capability Areas table and appends a Change Log line:

```markdown
| Area | Kind | Requirements |
|------|------|--------------|
| Search & Retrieval | adds area | Adds SR-REQ-001..010, SR-NFR-001..002; Modifies —; Withdraws — |
| Results Presentation | adds area | (pending specification) |
| Documentation Ingestion | adds area | (pending specification) |
```

```markdown
## Change Log
- 2026-08-26 — opened (Planning)
- 2026-08-26 — SR specification amended: adds SR-REQ-001..010, SR-NFR-001..002 (Specification)
```

## Approval

When the Product Owner approves the specification in conversation, the skill updates the two Source
Context lines in place:

```markdown
**Status:** Approved
**Approved by:** Product Owner — A. Reviewer, 2026-08-27
```
