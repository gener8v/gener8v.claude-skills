# Ticket Breakdown — worked example

### Input

Decomposing the "Search & Retrieval" area for the `support-search` change of the Support Documentation Search System.

The change brief (`.gener8v/changes/support-search/change.md`) lists the area as:

| Area | Kind | Requirements |
|------|------|--------------|
| Search & Retrieval | adds area | Adds SR-REQ-001..010, SR-NFR-001..002; Modifies —; Withdraws — |

and its Priority Cut puts query handling, search execution and the latency target under **Must** (SR-REQ-001..007, SR-NFR-001), and source attribution and request logging under **Should** (SR-REQ-008..010, SR-NFR-002).

The living specification (`.gener8v/specifications/search-and-retrieval.md`) carries:
- SR-REQ-001: Accept free-text natural language questions as search input
- SR-REQ-002: Accept queries of at least 500 characters
- SR-REQ-003: Reject empty or whitespace-only queries with a clear message
- SR-REQ-004: Return documentation excerpts that are relevant to the query
- SR-REQ-005: Rank results by relevance, with the most relevant result first
- SR-REQ-006: Return relevant results even when the query uses different terminology than the source documentation
- SR-REQ-007: Return results from all indexed documentation sources
- SR-REQ-008: Indicate the source document title for each result
- SR-REQ-009: Provide a stable reference to the source location for each result
- SR-REQ-010: Attribute results consistently regardless of documentation source
- SR-NFR-001: p95 search latency ≤ 800 ms at 50 concurrent users — verified by a k6 load test
- SR-NFR-002: Every search request is logged with a correlation id and duration — verified by a log-format test

With constraints TC-001 (semantic search needed for SR-REQ-006) and TC-002 (stable identifiers needed for SR-REQ-008, 009), dependency DEP-001 (requires indexed documentation from Documentation Ingestion), shared resources RES-001 (Document Index) and RES-002 (Source Reference Format), and architecture decisions AD-001 (vector similarity search) and AD-002 (PostgreSQL + pgvector).

### Output

Written to `.gener8v/changes/support-search/tickets/search-and-retrieval.md`:

````markdown
# Search & Retrieval — Ticket Breakdown

## Overview

Four tickets decomposed from the Search & Retrieval requirements the `support-search` change adds. The work forms a short dependency chain: query interface and search index setup can proceed in parallel, followed by ranking logic, then source attribution. Three Must tickets and one Should; 2 Small and 2 Medium. SR-NFR-002 (request logging, Should) is not covered by these four tickets — it is flagged as a gap and needs a ticket of its own, added above TICKET-004, before the change is complete.

## Source Context

**Change:** Support search (`changes/support-search/change.md`)
**Specification:** Search & Retrieval Specification
**Constraints Analysis:** Search & Retrieval Constraints Analysis
**Dependency Map:** Support Documentation Search System Dependency Map
**Technical Design:** Search & Retrieval Technical Design

## Tickets

### TICKET-001: Implement query input interface

**Summary:** Build the interface that accepts natural language questions from support agents, validates them, and passes them to the search pipeline.

**Priority:** Must
**Value:** A support agent can type a question in their own words and have it accepted for search.

**Requirements Covered:**
- SR-REQ-001: Accept free-text natural language questions as search input
- SR-REQ-002: Accept queries of at least 500 characters
- SR-REQ-003: Reject empty or whitespace-only queries with a clear message

**Prior Art:**
- Read: `.gener8v/specifications/search-and-retrieval.md` — SR-REQ-001..003 and the Query Handling behaviours (search-in-progress feedback)
- Read: `.gener8v/dependencies/dependency-map.md` — understand where this capability sits in the system

**Acceptance Criteria:**
- [ ] The system accepts free-text input of at least 500 characters
- [ ] The system passes the query text to the search pipeline without modification
- [ ] The system provides feedback that a search is in progress
- [ ] Empty or whitespace-only queries are rejected with a clear message

**Output:**
- `src/search/query-input.{ext}` — query input module exposing a function/method that accepts a string query, validates it, and returns it to the search pipeline
- `tests/search/query-input.test.{ext}` — proves the 500-character, pass-through and empty/whitespace criteria
- The query interface contract (function signature, input validation rules) that TICKET-003 will consume

**Constraints:** None identified

**Known Hazards:** None identified

**Depends On:** None
**Blocks:** TICKET-003

**Size:** Small

---

### TICKET-002: Configure search index for semantic matching

**Summary:** Set up the search index to support semantic similarity matching, enabling results even when query terminology differs from document terminology, across every ingested source.

**Priority:** Must
**Value:** A question phrased differently from the documentation still finds the right page, whichever source it came from.

**Requirements Covered:**
- SR-REQ-006: Return relevant results even when the query uses different terminology than the source documentation
- SR-REQ-007: Return results from all indexed documentation sources

**Prior Art:**
- Read: `.gener8v/specifications/search-and-retrieval.md` — SR-REQ-006 and SR-REQ-007 for full requirement context
- Read: `.gener8v/constraints/search-and-retrieval.md` — TC-001 for semantic search constraint details
- Read: `.gener8v/dependencies/dependency-map.md` — RES-001 (Document Index shared resource) for index schema coordination with Documentation Ingestion
- Read: `.gener8v/technical-design/search-and-retrieval.md` — AD-001 (vector similarity) and AD-002 (PostgreSQL + pgvector) for the chosen index technology

**Acceptance Criteria:**
- [ ] The search index supports semantic similarity queries, not just keyword matching
- [ ] A query using synonyms or paraphrased terminology returns relevant results from documentation that uses different wording
- [ ] Index is populated from the output of the Documentation Ingestion pipeline and returns results from every ingested source
- [ ] The index is implemented on pgvector per AD-002

**Output:**
- `src/search/index.{ext}` — index configuration and schema definition
- `src/search/index-client.{ext}` — client module for querying the index, exposing a search function that accepts a query string and returns scored results
- `tests/search/index-client.test.{ext}` — proves the semantic-match and multi-source criteria against a seeded index
- Index schema documentation or contract that Documentation Ingestion will write to and TICKET-003 will read from

**Constraints:**
- TC-001: Semantic search capability required

**Known Hazards:**
- The index schema is a shared resource (RES-001) co-owned with Documentation Ingestion — confirm the agreed schema contract exists before defining the index; do not invent a schema unilaterally, and if the contract is not yet defined, surface it rather than guessing.

**Depends On:** None (index schema can be defined before ingestion is complete; integration testing requires DEP-001)
**Blocks:** TICKET-003

**Size:** Medium

**Notes:** Index schema should be coordinated with the Documentation Ingestion capability (RES-001 from Dependency Map). Define the schema contract early even if full content is not yet ingested.

---

### TICKET-003: Implement relevance ranking

**Summary:** Build the ranking logic that orders search results by relevance score so the most useful documentation appears first, within the latency target.

**Priority:** Must
**Value:** The most relevant excerpt is at the top of the list, and the answer arrives fast enough to use mid-call.

**Requirements Covered:**
- SR-REQ-004: Return documentation excerpts that are relevant to the query
- SR-REQ-005: Rank results by relevance, with the most relevant result first
- SR-NFR-001: p95 search latency ≤ 800 ms at 50 concurrent users

**Prior Art:**
- Read: TICKET-001 output at `src/search/query-input.{ext}` — understand the query interface contract (how queries arrive)
- Read: TICKET-002 output at `src/search/index-client.{ext}` — understand the index query interface (how raw results are returned and what fields are available, including relevance scores)
- Read: `.gener8v/specifications/search-and-retrieval.md` — SR-REQ-004, SR-REQ-005, SR-NFR-001 and the Result Ranking behaviours (deterministic tie ordering)

**Acceptance Criteria:**
- [ ] Results are returned in descending order of relevance score
- [ ] Each result includes the relevant excerpt, not the full document
- [ ] A query with multiple matches returns them in a consistent, repeatable order
- [ ] Results with identical relevance scores are ordered deterministically
- [ ] p95 search latency ≤ 800 ms at 50 concurrent users, verified by the k6 load test in `tests/load/search.js` run against a seeded index (SR-NFR-001)

**Output:**
- `src/search/ranking.{ext}` — ranking module that takes raw index results and returns ordered, excerpt-bearing results
- `tests/search/ranking.test.{ext}` — proves the ordering, excerpt and deterministic-tie criteria
- `tests/load/search.js` — k6 script that verifies SR-NFR-001
- A ranked result type/structure (with fields: excerpt, relevance score, source metadata) that TICKET-004 will extend with attribution

**Constraints:** None identified

**Known Hazards:**
- AD-001 fixes the ranking basis as the stored vector similarity score — rank on the score the index returns, NOT on a recomputed similarity; a second scoring pass is what breaks the SR-NFR-001 budget.

**Depends On:** TICKET-001, TICKET-002
**Blocks:** TICKET-004

**Size:** Medium

---

### TICKET-004: Add source document attribution to results

**Summary:** Attach source document identification and navigation references to each search result so agents can trace results back to their origin.

**Priority:** Should
**Value:** An agent can see which document an excerpt came from and open it, whichever source it lives in.

**Requirements Covered:**
- SR-REQ-008: Indicate the source document title for each result
- SR-REQ-009: Provide a stable reference to the source location for each result
- SR-REQ-010: Attribute results consistently regardless of documentation source

**Prior Art:**
- Read: TICKET-003 output at `src/search/ranking.{ext}` — understand the ranked result structure that this ticket extends with source attribution fields
- Read: TICKET-002 output at `src/search/index-client.{ext}` — understand what source metadata is available from the index
- Read: `.gener8v/constraints/search-and-retrieval.md` — TC-002 for stable identifier constraint details
- Read: `.gener8v/dependencies/dependency-map.md` — RES-002 (Source Reference Format) for the shared contract with Documentation Ingestion and Results Presentation

**Acceptance Criteria:**
- [ ] Each result carries the title of the source document
- [ ] Each result includes a stable reference that identifies the source location
- [ ] Source references resolve to the correct document in the source system
- [ ] Results from different documentation sources are attributed consistently

**Output:**
- Modified `src/search/ranking.{ext}` (or new `src/search/attribution.{ext}`) — extends ranked results with source document title and stable reference link
- `tests/search/attribution.test.{ext}` — proves title, stable-reference and cross-source consistency criteria
- The final search result type/structure consumed by the Results Presentation capability

**Constraints:**
- TC-002: Stable, addressable identifiers required from ingestion

**Known Hazards:**
- Spec conflict: SR-REQ-009 says "stable reference" and TC-002 says "addressable identifier"; whether a reference may be a plain URL is decided by RES-002 — implement per the RES-002 contract, and if RES-002 is still undefined, surface it in the delivery record's Decisions rather than picking a format silently.

**Depends On:** TICKET-003
**Blocks:** None

**Size:** Small

**Notes:** Source reference format depends on RES-002 (shared resource contract with Documentation Ingestion and Results Presentation). Verify format is defined before implementation.

## Ticket Dependency Chain

```
TICKET-001 ──→ TICKET-003 ──→ TICKET-004
TICKET-002 ──┘
```

## Suggested Ordering

1. **TICKET-001** and **TICKET-002** — Both Must, no dependencies, can start in parallel. TICKET-002 carries more uncertainty (semantic index setup, RES-001 contract) so starting early reduces risk.
2. **TICKET-003** — Must; unblocked once query interface and index are available. Core search value and the latency target are delivered here.
3. **TICKET-004** — Should; final layer, adds traceability to results. Lower risk, clear scope, and correctly last: nothing Must depends on it.

## Backlog Summary

| Ticket | Title | Priority | Size | Depends On | Status |
|--------|-------|----------|------|------------|--------|
| TICKET-001 | Implement query input interface | Must | Small | None | Ready |
| TICKET-002 | Configure search index for semantic matching | Must | Medium | None | Ready |
| TICKET-003 | Implement relevance ranking | Must | Medium | TICKET-001, TICKET-002 | Blocked |
| TICKET-004 | Add source document attribution to results | Should | Small | TICKET-003 | Blocked |

**Total Tickets:** 4
**Ready to Start:** 2

*Status here is as of this breakdown. Live status (delivered, reviewed, done) is derived from delivery records and reviews into `.gener8v/pipeline-state.yaml`; this table is not updated as tickets progress.*
````

From any other document these tickets are referenced qualified — `support-search/search-and-retrieval/TICKET-003` — because TICKET-001 in another change's breakdown is a different ticket.
