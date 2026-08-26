# Delivery — worked example

## Input

Delivering `support-search/search-and-retrieval/TICKET-001` — "Implement query input interface" — from `.gener8v/changes/support-search/tickets/search-and-retrieval.md`. One change (`support-search`) is active, so it is the default and the argument did not need to name it.

The ticket specifies:
- **Priority:** Must
- **Value:** A support agent can type a question in their own words and have it accepted for search
- **Requirements Covered:** SR-REQ-001 (accept free-text natural language questions as search input), SR-REQ-002 (accept queries of at least 500 characters), SR-REQ-003 (reject empty or whitespace-only queries with a clear message)
- **Prior Art:** Read `.gener8v/specifications/search-and-retrieval.md`, read `.gener8v/dependencies/dependency-map.md`
- **Acceptance Criteria:** Accepts free-text input of 500+ characters, passes query to search pipeline unmodified, provides in-progress feedback, rejects empty/whitespace queries
- **Output:** `src/search/query-input.{ext}` — query input module; `tests/search/query-input.test.{ext}` — proves the 500-character, pass-through and empty/whitespace criteria
- **Constraints:** None identified
- **Depends On:** None

`.gener8v/context.md`'s `## Repositories` table has one row: `| . | Search API | Python / uv | pytest -q; ruff check src tests |`. The change brief `.gener8v/changes/support-search/change.md` is `Approved` (Product Owner).

## Output

### Phase 2 — Implementation Plan (presented to user)

> **Plan for support-search/search-and-retrieval/TICKET-001: Implement query input interface**
>
> **Repository:** `.` (the single repository in `context.md`'s Repositories table)
>
> **Files to create:**
> - `src/search/query_input.py` — Query input module with `process_query()` function
> - `tests/search/test_query_input.py` — One test per acceptance criterion
>
> **Approach:**
> - Define a `process_query(text: str) -> str` function that validates input and returns the cleaned query
> - Validate: reject empty strings, whitespace-only strings, and strings exceeding 10,000 characters
> - Return the query text unmodified (no normalization, no trimming beyond whitespace rejection)
> - Raise `ValueError` with descriptive messages for invalid input
>
> **Acceptance Criteria Mapping:**
> - "Accepts free-text input of 500+ characters" (SR-REQ-002) → No upper limit below 10,000; any string up to that length is accepted
> - "Passes query to search pipeline unmodified" (SR-REQ-001) → `process_query` returns the input string as-is after validation
> - "Provides in-progress feedback" → Returns a status indicator alongside the query; upstream caller uses this for UI feedback
> - "Rejects empty/whitespace queries" (SR-REQ-003) → `ValueError` raised with clear message
>
> **Verification:** `pytest tests/search/test_query_input.py -q` and `ruff check src/search tests/search`, from the repository's Verify commands. This ticket carries no NFR; SR-NFR-001's load test runs under TICKET-003.

### Phase 3 — Delivery Record (as finalized after execution)

Written to `.gener8v/changes/support-search/delivery/search-and-retrieval-ticket-001-delivery.md`.

````markdown
# TICKET-001: Implement query input interface — Delivery Record

## Ticket Reference

**Ticket:** support-search/search-and-retrieval/TICKET-001
**Change:** `.gener8v/changes/support-search/change.md` — Approved when delivery started
**Specification:** `.gener8v/specifications/search-and-retrieval.md`
**Requirements Covered:**
- SR-REQ-001: Accept free-text natural language questions as search input
- SR-REQ-002: Accept queries of at least 500 characters
- SR-REQ-003: Reject empty or whitespace-only queries with a clear message

## Pre-Flight Reconciliation

**Verdict:** Go

| Assumption (from ticket) | Expected | Found in repo | Status |
|--------------------------|----------|---------------|--------|
| `src/search/` package exists | present | present (`src/search/__init__.py`) | ✅ |
| pytest configured | present | `pyproject.toml [tool.pytest.ini_options]` | ✅ |

**Resolved from ground truth (not escalated):** None.
**Blocking findings:** None.

## Implementation Plan

**Repository:** `.` (single repository — `context.md` Repositories table)
**Plan approved by:** Engineer — Alex Rivera, 2026-08-28

[Plan as approved above — preserved verbatim]

### Planned Files

- `src/search/query_input.py`: Query input module with validation and passthrough
- `tests/search/test_query_input.py`: One test per acceptance criterion

### How Acceptance Criteria Will Be Met

- Free-text input of 500+ characters (SR-REQ-002): No restrictive upper limit; `test_accepts_long_input` sends a 1,000-character query
- Passes query unmodified (SR-REQ-001): Returns input string as-is after validation
- In-progress feedback: Returns status indicator for upstream caller
- Rejects empty/whitespace (SR-REQ-003): Raises ValueError with descriptive message

## Progress

- [x] `src/search/query_input.py` — written, annotated
- [x] `tests/search/test_query_input.py` — written

## Delivery Summary

**Status:** Delivered
**Verification:** passed
**Reviews Deferred:** none
**Files Produced:**
- `src/search/query_input.py`: Query input module exposing `process_query(text: str) -> QueryResult` with input validation
- `tests/search/test_query_input.py`: Four tests, one per acceptance criterion

## Verification Run

| Command | Exit | Evidence |
|---------|------|----------|
| `pytest tests/search/test_query_input.py -q` | 0 | 4 passed |
| `ruff check src/search tests/search` | 0 | — |

No NFR is covered by this ticket (SR-NFR-001 is verified under TICKET-003).

## Acceptance Criteria Verification

- [x] The system accepts free-text input of at least 500 characters (SR-REQ-002) — `test_accepts_long_input` (1,000-character input) passes
- [x] The system passes the query text to the search pipeline without modification (SR-REQ-001) — `test_passes_through_unmodified` asserts `QueryResult.query` equals the original text
- [x] The system provides feedback that a search is in progress — `test_status_processing` asserts `QueryResult.status == "processing"`
- [x] Empty or whitespace-only queries are rejected with a clear message (SR-REQ-003) — `test_rejects_empty` and `test_rejects_whitespace` assert `ValueError("Query must not be empty or whitespace-only")`

## Decisions Made

### DEL-001: Use dataclass for query result instead of plain tuple

**Context:** The ticket's Output section describes "a function/method that accepts a string query and returns it to the search pipeline." Need to decide what the return type looks like.
**Decision:** Return a `QueryResult` dataclass with `query` and `status` fields instead of a plain string.
**Rationale:** Downstream tickets (TICKET-003) need both the query text and metadata. A dataclass is self-documenting and extensible without breaking the interface.
**Ticket Impact:** Output contract is slightly richer than specified — downstream Prior Art references will find a `QueryResult` type instead of a bare string.

## Deviations from Plan

None — implementation followed the approved plan.

## @spec Annotations

| Requirement | Code Location | Annotation |
|-------------|---------------|------------|
| SR-REQ-001 | `src/search/query_input.py:process_query()` | `@spec SR-REQ-001, SR-REQ-002` |
| SR-REQ-002 | `src/search/query_input.py:process_query()` | `@spec SR-REQ-001, SR-REQ-002` |
| SR-REQ-003 | `src/search/query_input.py:_reject_blank()` | `@spec SR-REQ-003` |

All requirements annotated.

## Notes

- The 10,000 character upper limit is a safety bound, not a requirement. If downstream needs change, this can be adjusted without affecting the interface contract.
- TICKET-003 should import `QueryResult` from this module for type consistency.

## Post-Review Amendments

None.
````

### Rows appended to the living specification

Appended to the two-column `## @spec Coverage` table in `.gener8v/specifications/search-and-retrieval.md` (locations root-relative; the delivering ticket, `support-search/search-and-retrieval/TICKET-001`, is named by this record, not by the table):

```markdown
| SR-REQ-001 | `src/search/query_input.py:process_query()` |
| SR-REQ-002 | `src/search/query_input.py:process_query()` |
| SR-REQ-003 | `src/search/query_input.py:_reject_blank()` |
```

The code and the record were committed together in the repository named in the plan (`.`), subject `search-and-retrieval-ticket-001-delivery`.
