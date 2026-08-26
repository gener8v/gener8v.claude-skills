# Audit — worked example

### Input

User asks: "Audit the pipeline" with the following artifacts available:
- `.gener8v/prd.md`
- `.gener8v/changes/support-search/change.md`
- `.gener8v/specifications/search-and-retrieval.md`
- `.gener8v/specifications/results-presentation.md`
- `.gener8v/specifications/documentation-ingestion.md` (missing)
- `.gener8v/constraints/search-and-retrieval.md`
- `.gener8v/dependencies/dependency-map.md`
- `.gener8v/changes/support-search/tickets/search-and-retrieval.md`

### Output (abbreviated)

````markdown
# Audit Report — Cross-Pipeline Audit

## Summary

Audited 7 artifacts across 5 pipeline stages and one change (`support-search`). The pipeline is partially complete with 8 findings: 1 critical, 3 gaps, 3 warnings, 1 suggestion. The most significant issue is a missing specification for the Documentation Ingestion capability area, which blocks constraint analysis and ticket breakdown for that area. No earlier audit exists, so every finding is newly raised.

**Artifacts Audited:**
- `.gener8v/prd.md` (Planning)
- `.gener8v/changes/support-search/change.md` (Planning — change brief)
- `.gener8v/specifications/search-and-retrieval.md` (Specification)
- `.gener8v/specifications/results-presentation.md` (Specification)
- `.gener8v/constraints/search-and-retrieval.md` (Constraints)
- `.gener8v/dependencies/dependency-map.md` (Dependencies)
- `.gener8v/changes/support-search/tickets/search-and-retrieval.md` (Ticket Breakdown)

**Findings:** 8
**Critical:** 1 | **Gaps:** 3 | **Warnings:** 3 | **Suggestions:** 1

## Findings

### FIND-001: Missing specification for Documentation Ingestion

**Severity:** Critical
**Location:** `.gener8v/specifications/` (expected: `documentation-ingestion.md`)
**Description:** The PRD defines three capability areas but only two have specifications. Documentation Ingestion has no specification, and the `support-search` change brief still says `(pending specification)` for it.
**Impact:** Cannot produce constraints analysis, dependency detail, or tickets for this capability area. The dependency map references it (DEP-001) but the analysis is based on PRD-level detail only.
**Recommendation:** Run `/specification Documentation Ingestion for support-search`.
**Status:** Open

---

### FIND-002: SR-REQ-008 in search-and-retrieval specification uses subjective language

**Severity:** Warning
**Location:** `.gener8v/specifications/search-and-retrieval.md`, SR-REQ-008
**Description:** "The system should indicate the source document for each result in a user-friendly way" — "user-friendly" is not testable.
**Impact:** Acceptance criteria derived from this requirement (TICKET-004) may be ambiguous.
**Recommendation:** Reword to: "The system should indicate the source document title for each result." The stable location reference is already SR-REQ-009.
**Status:** Open

---

### FIND-003: No constraints analysis for results-presentation

**Severity:** Gap
**Location:** `.gener8v/constraints/` (expected: `results-presentation.md`)
**Description:** Results Presentation has a specification but no constraints analysis.
**Impact:** Tickets for this area will lack constraint-informed acceptance criteria.
**Recommendation:** Run the Constraints skill on the Results Presentation specification, or explicitly defer with a note in the ticket breakdown.
**Status:** Open

---

### FIND-004: Tickets cut from a Draft specification

**Severity:** Warning
**Location:** `.gener8v/changes/support-search/tickets/search-and-retrieval.md`; `.gener8v/specifications/search-and-retrieval.md` Source Context
**Description:** The Search & Retrieval specification is `**Status:** Draft` (`**Approved by:** pending`) but four tickets have already been cut from it.
**Impact:** If the Product Owner changes the priority cut on approval, TICKET-001..004 carry stale scope. Not a block — the record simply says so.
**Recommendation:** Have the Product Owner approve the specification (the Specification skill flips the Status and Approved-by lines) before TICKET-001 enters delivery.
**Status:** Open

---

*[Interactive session begins — user resolves each finding...]*

## Coverage Matrix

### Capability Area → Specification Coverage

| Capability Area (from PRD) | Spec | Constraints | Tech Design | Tickets | Delivered | CR | QR | SEC |
|---------------------------|------|-------------|-------------|---------|-----------|----|----|-----|
| Search & Retrieval | Yes (Draft) | Yes | **No** | Yes | 0/4 | 0/4 | 0/4 | 0/4 |
| Results Presentation | Yes (Draft) | **No** | No | No | — | — | — | — |
| Documentation Ingestion | **No** | No | No | No | — | — | — | — |

### Change → Area Coverage

| Change | Status | Area | Requirements (brief) | Tickets | Delivered | Done |
|--------|--------|------|----------------------|---------|-----------|------|
| support-search | Approved | Search & Retrieval | Adds SR-REQ-001..010, SR-NFR-001..002 | 4 | 0/4 | 0/4 |
| support-search | Approved | Results Presentation | Adds RP-REQ-001..005 | — | — | — |
| support-search | Approved | Documentation Ingestion | (pending specification) | — | — | — |

### Requirement Traceability

| Requirement | Specification | Ticket(s) | Covered |
|-------------|---------------|-----------|---------|
| SR-REQ-001 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-001 | Yes |
| SR-REQ-002 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-001 | Yes |
| SR-REQ-003 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-001 | Yes |
| SR-REQ-004 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-003 | Yes |
| SR-REQ-005 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-003 | Yes |
| SR-REQ-006 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-002 | Yes |
| SR-REQ-007 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-002 | Yes |
| SR-REQ-008 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-004 | Yes |
| SR-REQ-009 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-004 | Yes |
| SR-REQ-010 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-004 | Yes |
| SR-NFR-001 | search-and-retrieval.md | support-search/search-and-retrieval/TICKET-003 | Yes |
| SR-NFR-002 | search-and-retrieval.md | — | **No** (Warning — see FIND-006) |

## Resolution Log

| Finding | Decision | Action Taken | Artifact Updated |
|---------|----------|-------------|-----------------|
| FIND-001 | Approved | User will run the Specification skill next | — |
| FIND-002 | Approved | Reworded SR-REQ-008 to remove subjective language; appended `*(amended 2026-08-26 by support-search)*` | `.gener8v/specifications/search-and-retrieval.md` |
| FIND-003 | Deferred | Will address after Documentation Ingestion specification is complete | — |
| FIND-004 | Approved | Product Owner approved the specification in session; Status and Approved-by lines updated | `.gener8v/specifications/search-and-retrieval.md` |
````
