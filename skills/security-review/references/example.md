# Security Review — worked example

## Input

Reviewing the delivery of `support-search/search-and-retrieval/TICKET-002` — "Configure search index for semantic matching" — for Search & Retrieval in the change `support-search` (the only active change, so `/security-review Search & Retrieval TICKET-002` needs no `in …` clause).

- Ticket: `.gener8v/changes/support-search/tickets/search-and-retrieval/TICKET-002.md`
- Delivery record: `.gener8v/changes/support-search/delivery/search-and-retrieval-ticket-002-delivery.md`
- Delivered code (root-relative; a single repository): `src/search/index.py` and `src/search/index_client.py`
- Constraints: `.gener8v/constraints/search-and-retrieval.md` — CC-001 (access controls if documentation holds PII)
- Technical design: `.gener8v/technical-design/search-and-retrieval.md` — AD-001 vector similarity, AD-002 PostgreSQL + pgvector

Report written to `.gener8v/changes/support-search/reviews/search-and-retrieval-ticket-002-security-review.md`.

## Output — findings phase (abbreviated)

````markdown
# TICKET-002: Configure search index for semantic matching — Security Review

## Summary

Reviewed two files delivered for TICKET-002. The code handles search index configuration and querying. One Medium finding related to the database connection string. One Informational finding regarding query logging. Overall security posture is adequate for the current scope.

**Files Reviewed:**
- `src/search/index.py`
- `src/search/index_client.py`

**Findings:** 2
**Critical:** 0 | **High:** 0 | **Medium:** 1 | **Low:** 0 | **Informational:** 1

## Security Assessment

### Input Validation

**Status:** Adequate
**Notes:** Query text passed to the search function is parameterized in the database query — no SQL injection vector. Vector embedding is generated via API call with the query string; the API client handles encoding.

### Authentication & Authorization

**Status:** Not Applicable
**Notes:** This module does not handle user authentication or authorization. Access control is expected at a higher layer.

### Data Protection

**Status:** Gaps Found
**Notes:** The database connection string is constructed from environment variables, but the fallback default includes a placeholder password (see SEC-001).

### Configuration Security

**Status:** Gaps Found
**Notes:** Fallback connection string in code (see SEC-001).

## Findings

### SEC-001: Database connection string with fallback default

**Severity:** Medium
**Category:** Misconfiguration
**OWASP Reference:** A02:2025 Security Misconfiguration
**Location:** `src/search/index.py:12`
**Description:** The database connection string is read from `DATABASE_URL` environment variable with a fallback default of `postgresql://search:search_dev@localhost:5432/search_db`. While the default points to localhost, committing default credentials normalizes the pattern of credentials in source code.
**Attack Scenario:** A developer or CI system runs the code without setting the environment variable. The code connects with the default credentials. If the default database exists and is accessible, the code operates with unintended credentials. In a deployment misconfiguration, the default could leak into production.
**Impact:** Unauthorized database access in misconfigured environments. Credential exposure in source code.
**Recommendation:** Remove the fallback default. Raise an error if `DATABASE_URL` is not set. Fail explicitly rather than falling back to hardcoded credentials.
**Compliance Impact:** None
**Status:** Open

---

### SEC-002: Search queries logged at DEBUG level

**Severity:** Informational
**Category:** Logging
**OWASP Reference:** N/A
**Location:** `src/search/index_client.py:28`
**Description:** User search queries are logged at DEBUG level. Search queries may contain sensitive information depending on the domain (e.g., employee names, case numbers, internal project details).
**Attack Scenario:** N/A (Informational)
**Impact:** Potential exposure of sensitive query content in log files if DEBUG logging is enabled in production.
**Recommendation:** Ensure DEBUG logging is disabled in production. Consider whether search queries should be logged at all, or logged with redaction.
**Compliance Impact:** None
**Status:** Open

## Verdict

**Result:** Approved with Notes
**Unresolved Critical/High:** 0
**Accepted Risks:** 0
**Notes:** SEC-001 should be addressed before production deployment. SEC-002 is informational and depends on logging configuration in production.
````

## Output — after resolution (excerpt)

The user removed the fallback connection string for SEC-001 (re-verified, appended to the delivery record's `## Post-Review Amendments`) and accepted SEC-002 as a risk. The two findings and the closing sections now read:

````markdown
### SEC-001: Database connection string with fallback default

…
**Status:** Resolved
**Resolution:** Fallback removed; `index.py` now raises `ConfigurationError` when `DATABASE_URL` is unset. Verification Run re-executed and passed; recorded in `search-and-retrieval-ticket-002-delivery.md` `## Post-Review Amendments`.

---

### SEC-002: Search queries logged at DEBUG level

…
**Status:** Accepted Risk
**Risk accepted by:** Security — J. Okafor, 2026-08-26
**Resolution:** DEBUG logging is disabled in every deployed environment by the shared logging configuration, and query logging at DEBUG is needed for local relevance tuning. Revisit if documentation sources holding PII are indexed (CC-001).

## Resolution Log

| Finding | Decision | Action Taken | Risk Accepted | File Updated |
|---------|----------|-------------|---------------|--------------|
| SEC-001 | Fix | Removed fallback connection string; fail fast on missing `DATABASE_URL` | No | `src/search/index.py` |
| SEC-002 | Accepted Risk | — | Yes | — |

## Verdict

**Result:** Approved
**Unresolved Critical/High:** 0
**Accepted Risks:** 1 — SEC-002, DEBUG-level query logging (compensating control: DEBUG disabled in deployed environments)
**Notes:** Re-run this review if documentation sources holding PII are indexed; SEC-002's acceptance is conditional on CC-001 not applying.
````

Referenced from another document, these findings are `support-search/search-and-retrieval-ticket-002-security-review/SEC-001` and `…/SEC-002`.
