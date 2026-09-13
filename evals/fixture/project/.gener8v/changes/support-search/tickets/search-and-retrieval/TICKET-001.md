# TICKET-001: Implement query input interface

**Change:** support-search
**Capability Area:** Search & Retrieval (search-and-retrieval)
**Specification:** specifications/search-and-retrieval.md

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
