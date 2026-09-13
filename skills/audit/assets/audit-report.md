# Audit Report — [Scope Description]

## Summary

[2-3 sentences: what was audited, how many findings, severity breakdown.]

**Artifacts Audited:**
- [File path] ([stage name])
- ...

**Findings:** [Total count]
**Critical:** [Count] | **Gaps:** [Count] | **Warnings:** [Count] | **Suggestions:** [Count]

## Findings

### FIND-001: [Concise finding title]

**Severity:** [Critical / Gap / Warning / Suggestion]
**Location:** [File path and section where the issue exists]
**Description:** [What the problem is]
**Impact:** [What goes wrong downstream if this isn't addressed]
**Recommendation:** [Specific action to resolve]
**Status:** [Open / Resolved / Deferred / Dismissed]
**Resolution:** [What was done, if resolved — filled in during interactive session]

---

### FIND-002: ...

## Coverage Matrix (Cross-Stage Audit only)

### Capability Area → Specification Coverage

| Capability Area (from PRD) | Spec | Constraints | Tech Design | Tickets | Delivered | CR | QR | SEC |
|---------------------------|------|-------------|-------------|---------|-----------|----|----|-----|
| [Area name] | Yes/No | Yes/No | Yes/No | Yes/No | [n/total] | [n/total] | [n/total] | [n/total] |

### Change → Area Coverage

| Change | Status | Area | Requirements (brief) | Tickets | Delivered | Done |
|--------|--------|------|----------------------|---------|-----------|------|
| [change-slug] | [brief Status] | [Area name] | [Adds/Modifies/Withdraws IDs, or (pending specification)] | [count] | [n/total] | [n/total] |

### Requirement Traceability

| Requirement | Specification | Ticket(s) | Covered |
|-------------|---------------|-----------|---------|
| REQ-001 | [slug].md | [change-slug]/[area-slug]/TICKET-001 | Yes |
| REQ-002 | [slug].md | — | **No** |
| NFR-001 | [slug].md | — | **No** (Warning) |

### Open Questions Tally

| Source Document | Open Questions | Resolved | Unresolved |
|----------------|---------------|----------|------------|
| prd.md | [count] | [count] | [count] |
| specifications/[slug].md | [count] | [count] | [count] |
| ... | ... | ... | ... |

## Resolution Log

[Record of decisions made during the interactive session.]

| Finding | Decision | Action Taken | Artifact Updated |
|---------|----------|-------------|-----------------|
| FIND-001 | [User's decision] | [What was changed] | [File path] |
| FIND-002 | Deferred | — | — |
