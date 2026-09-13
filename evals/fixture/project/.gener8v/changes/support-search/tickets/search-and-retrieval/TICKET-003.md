# TICKET-003: Implement relevance ranking

**Change:** support-search
**Capability Area:** Search & Retrieval (search-and-retrieval)
**Specification:** specifications/search-and-retrieval.md

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
