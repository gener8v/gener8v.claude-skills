# TICKET-004: Add source document attribution to results

**Change:** support-search
**Capability Area:** Search & Retrieval (search-and-retrieval)
**Specification:** specifications/search-and-retrieval.md

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
