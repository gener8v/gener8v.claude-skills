# Quality Review — worked example

### Input

Reviewing the delivery of TICKET-001 from Search & Retrieval, "Implement query input interface", in the change `support-search` (the only active change, so it is the default).

- Ticket: `.gener8v/changes/support-search/tickets/search-and-retrieval.md` — TICKET-001 covers SR-REQ-001, SR-REQ-002, SR-REQ-003
- Delivery record: `.gener8v/changes/support-search/delivery/search-and-retrieval-ticket-001-delivery.md` — Files Produced: `src/search/query_input.py`, `tests/search/test_query_input.py`; Verification Run: `pytest tests/search/test_query_input.py -q` (exit 0, 4 passed), `ruff check src/search tests/search` (exit 0)
- `.gener8v/context.md`'s `## Repositories` table names the verify commands; all paths below are root-relative

### Output (abbreviated)

Written to `.gener8v/changes/support-search/reviews/search-and-retrieval-ticket-001-quality-review.md`.

````markdown
# TICKET-001: Implement query input interface — Quality Review

## Summary

Reviewed two files delivered for TICKET-001. Code organization and readability are strong; error handling is adequate with one suggestion. Tests exist for every acceptance criterion and pass, but the module's own safety bound (the 10,000-character upper limit introduced by DEL-001) is untested — one Concern. Two findings total.

**Files Reviewed:**
- `src/search/query_input.py`
- `tests/search/test_query_input.py`

**Findings:** 2
**Critical:** 0 | **Concerns:** 1 | **Suggestions:** 1

## Quality Assessment

### Code Organization

**Rating:** Strong
**Notes:** Single module with clear responsibility. `QueryResult` dataclass and `process_query` function are well-separated. No unnecessary abstractions.

### Readability

**Rating:** Strong
**Notes:** Clear naming, concise functions, self-documenting code. The validation logic reads naturally.

### Error Handling

**Rating:** Adequate
**Notes:** `ValueError` raised for invalid input with descriptive messages. The 10,000-character upper limit raises the same `ValueError` type as empty input — callers cannot distinguish between "too short" and "too long" without parsing the message string.

### Test Coverage

**Rating:** Adequate
**Notes:** Re-ran the delivery record's Verification Run: `pytest tests/search/test_query_input.py -q` → 4 passed (exit 0); `ruff check src/search tests/search` → exit 0. One test per acceptance criterion — `test_accepts_long_input` (SR-REQ-002, 1,000 characters), `test_passes_query_through` (SR-REQ-001), `test_rejects_empty` and `test_rejects_whitespace` (SR-REQ-003). Tests assert on behaviour, not on implementation details, and their names describe it. The 10,000-character upper bound has no test (QR-001).

### Observability & Operability

**Rating:** Adequate
**Notes:** Validation failures raise with a message the caller can surface directly. The module does not log or emit metrics, which is appropriate for a pure validation function — request logging with a correlation id (SR-NFR-002) belongs to the search request handler that calls it, not here. Nothing to flag.

## Findings

### QR-001: Upper-bound rejection is untested

**Category:** Testing
**Severity:** Concern
**Location:** `tests/search/test_query_input.py` (expected: a test for the 10,000-character bound in `src/search/query_input.py:18-20`)
**Description:** `process_query` rejects inputs longer than 10,000 characters (DEL-001 in the delivery record calls this a safety bound, not a requirement). No test exercises it: a change that removed or mis-typed the bound would pass the suite.
**Impact:** The one behaviour in this module that is not traced to a requirement is also the one with no automated check. Regressions in the bound will not be caught.
**Recommendation:** Add `test_rejects_over_length` (10,001 characters → `ValueError`) and `test_accepts_at_bound` (exactly 10,000 → accepted) so the bound is pinned in the same suite as the criteria.
**Status:** Open

---

### QR-002: Same exception type for different validation failures

**Category:** Error Handling
**Severity:** Suggestion
**Location:** `src/search/query_input.py:18-20`
**Description:** Both empty input and over-length input raise `ValueError`. Callers cannot programmatically distinguish between the two failure modes without string matching.
**Impact:** Minor — current consumers may not need to distinguish, but it limits future flexibility.
**Recommendation:** Consider distinct error messages at minimum, or a custom exception subclass if callers will need to branch on failure type.
**Status:** Open

## Verdict

**Result:** Approved with Notes
**Unresolved Findings:** 1 Concern, 1 Suggestion
````

Referenced from another document, the first finding is `support-search/search-and-retrieval-ticket-001-quality-review/QR-001`.

Had the delivery shipped without `tests/search/test_query_input.py`, Test Coverage would be **Not Present**, QR-001 would be **Critical** ("No tests delivered — the acceptance criteria are unproven") and the verdict **Changes Required**: testable criteria with no tests is a block, not a suggestion.
