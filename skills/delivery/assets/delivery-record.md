# [Ticket ID]: [Ticket Title] — Delivery Record

## Ticket Reference

**Ticket:** [<change-slug>/<capability-area-slug>/TICKET-XXX]
**Change:** [`.gener8v/changes/<change-slug>/change.md` — and its Status at the time delivery started]
**Specification:** [Link to specification file]
**Requirements Covered:**
- [XX]-REQ-XXX: [Brief description]
- [XX]-REQ-XXX: [Brief description]
- [XX]-NFR-XXX: [Brief description — and the verification method the ticket names for it]

## Pre-Flight Reconciliation

**Verdict:** [Go / Blocked]

| Assumption (from ticket) | Expected | Found in repo | Status |
|--------------------------|----------|---------------|--------|
| [e.g., table `document_index` exists] | present | not in schema.ts or migrations | ❌ Blocking |
| [e.g., `scripts/build-index.sh` exists] | present | absent | ❌ Blocking |
| [e.g., Prior Art document present at the pinned version] | v1.4 | v1.2 in repo | ❌ Blocking |
| [e.g., `documents.source_ref` nullable] | nullable | NOT NULL (`api/src/db/schema.ts:NNNN`) | ⚠️ Resolves a Decision Point → Path A |
| [e.g., predecessor TICKET-002 output exists] | `api/src/search/index-client.ts` | present | ✅ |
| [Carried finding: `<change-slug>/<capability-area-slug>-ticket-001-code-review/CR-001` deferred to this ticket] | addressed here | — | 🔁 Carried — see Implementation Plan |

**Resolved from ground truth (not escalated):** [Open questions / Decision Points the ticket left for the user that the code already answers, with evidence — e.g., "PDF approach: repo already depends on `pdfkit`, so the jsPDF-vs-Puppeteer choice is moot."]

**Blocking findings:** [If Verdict is Blocked, what must exist before this ticket can be delivered, and which skill/action produces it. If Go, state "None."]

## Implementation Plan

**Repository:** [directory from `context.md`'s `## Repositories` table — `.` for a single repository; its verify commands and the commit belong to it. An atomic ticket that must touch two repositories names both.]
**Plan approved by:** [Engineer — <name>, YYYY-MM-DD — or `pending` until Phase 2 approval]

[The plan as approved by the user in Phase 2. Preserved verbatim so
deviations can be compared against the original intent. Written the moment it is approved.]

### Planned Files

- [root-relative file path]: [what it will contain and why]
- [root-relative file path]: [what it will contain and why]

### How Acceptance Criteria Will Be Met

- [Criterion]: [How the plan addresses it — and which test will prove it]
- [Criterion]: [How the plan addresses it]

## Progress

[One line per planned file, updated as each lands. This is what a resumed session reads first.]

- [x] `src/search/query_input.py` — written, annotated
- [ ] `tests/search/test_query_input.py` — pending

## Delivery Summary

**Status:** [Reconciled / In Progress / Delivered / Partial / Blocked]
**Verification:** [passed / failed / not run]
**Reviews Deferred:** [none — or `quality, security — <reason>` when the scale decision defers a review; the ticket can still reach done]
**Files Produced:**
- [root-relative file path]: [what was actually created or modified — brief description]
- [root-relative file path]: [what was actually created or modified — brief description]

## Verification Run

[The commands actually executed, verbatim, with exit codes. Sourced from the named repository's Verify commands in `context.md`'s `## Repositories` table (or its testing and build sections) or the repository's own scripts. Includes every NFR check the ticket carries that is executable — a benchmark, a load test, an accessibility lint. "Tests pass" without a command and an exit code is not verification.]

| Command | Exit | Evidence |
|---------|------|----------|
| `pytest tests/search -q` | 0 | 6 passed |
| `ruff check src/search` | 0 | — |
| `mypy src/search` | 0 | — |

## Acceptance Criteria Verification

- [x] [Criterion from ticket] — [the executed test or command that proves it, from the Verification Run]
- [x] [Another criterion] — [how it was satisfied]
- [ ] [Unverified criterion] — [it is implemented but no executed check covers it; say what would]
- [ ] [XX]-NFR-XXX [non-executable NFR] — Unverified; [what would verify it — the method the specification names, and who runs it]
- [ ] [Unsatisfied criterion, if any] — [why not met, what is needed]

## Decisions Made

### DEL-001: [Decision title]

**Context:** [What prompted this decision during implementation]
**Decision:** [What was decided]
**Rationale:** [Why this choice over alternatives]
**Ticket Impact:** [How this affected the implementation vs. what the ticket specified]

### DEL-002: ...

## Deviations from Plan

[What changed from the approved implementation plan and why.
If nothing changed, state "None — implementation followed the approved plan."]

- [Deviation description]: [Why it was necessary and what impact it has on downstream tickets]

## @spec Annotations

| Requirement | Code Location | Annotation |
|-------------|---------------|------------|
| [XX]-REQ-XXX | [root-relative file:function or class] | `@spec [XX]-REQ-XXX` |

[Any requirements that could not be annotated, with explanation.]

## Notes

[Implementation observations, warnings for downstream tickets,
performance considerations, or anything the next developer should know.]

## Post-Review Amendments

[Appended by the review skills during interactive resolution. One entry per applied change:
finding ID (qualified, e.g. `support-search/search-and-retrieval-ticket-001-code-review/CR-002`), what changed, files touched, re-verification result. "None" until a review changes something.]
