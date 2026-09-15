# Search & Retrieval — Backlog (support-search)

## Overview

Four tickets decomposed from the Search & Retrieval requirements the `support-search` change adds. The work forms a short dependency chain: query interface and search index setup can proceed in parallel, followed by ranking logic, then source attribution. Three Must tickets and one Should; 2 Small and 2 Medium. SR-NFR-002 (request logging, Should) is not covered by these four tickets — it is flagged as a gap and needs a ticket of its own, added above TICKET-004, before the change is complete.

## Source Context

**Specification:** Search & Retrieval Specification · **Constraints Analysis:** Search & Retrieval Constraints Analysis · **Dependency Map:** Support Documentation Search System Dependency Map · **Technical Design:** Search & Retrieval Technical Design
**Change brief:** changes/support-search/change.md (Priority Cut applied)

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
