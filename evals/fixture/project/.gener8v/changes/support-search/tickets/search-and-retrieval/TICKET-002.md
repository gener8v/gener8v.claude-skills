# TICKET-002: Configure search index for semantic matching

**Change:** support-search
**Capability Area:** Search & Retrieval (search-and-retrieval)
**Specification:** specifications/search-and-retrieval.md

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
