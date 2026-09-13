# [Ticket ID]: [Ticket Title] — Quality Review

## Summary

[2-3 sentences: what was reviewed, overall quality assessment, finding count by severity.]

**Files Reviewed:**
- [file path]
- [file path]

**Findings:** [Total count]
**Critical:** [Count] | **Concerns:** [Count] | **Suggestions:** [Count]

## Quality Assessment

### Code Organization

**Rating:** [Strong / Adequate / Needs Improvement]
**Notes:** [Assessment of module structure, file organization, separation of concerns,
single responsibility adherence]

### Readability

**Rating:** [Strong / Adequate / Needs Improvement]
**Notes:** [Assessment of naming conventions, code clarity, function length,
cognitive complexity, self-documenting code]

### Error Handling

**Rating:** [Strong / Adequate / Needs Improvement]
**Notes:** [Assessment of error handling completeness, consistent patterns,
meaningful error messages, appropriate propagation]

### Test Coverage

**Rating:** [Strong / Adequate / Needs Improvement / Not Present]
**Notes:** [Assessment of test presence, coverage of key paths, edge case
testing, test quality and maintainability. Include the executed result: which commands were run and their exit codes.]

### Observability & Operability

**Rating:** [Strong / Adequate / Needs Improvement]
**Notes:** [Assessment of logging (what is logged, at what level, with what
context), metrics and health signals, and error surfaces — whether a failure
in this code is visible, attributable and actionable to whoever operates it]

## Findings

### QR-001: [Finding title]

**Category:** [Readability / Error Handling / Naming / DRY / SOLID / Performance / Maintainability / Testing / Patterns / Observability]
**Severity:** [Critical / Concern / Suggestion]
**Location:** [root-relative path:line or function — e.g. `api/src/search/query.ts:42`]
**Description:** [What the issue is — specific, not aesthetic]
**Impact:** [Why this matters for maintainability, reliability, or performance]
**Recommendation:** [Specific improvement with example if helpful]
**Status:** [Open / Resolved / Deferred → TICKET-NNN or reason / Dismissed]
**Resolution:** [What was done, if resolved — filled in during resolution]

---

### QR-002: ...

## Resolution Log

| Finding | Decision | Action Taken | File Updated |
|---------|----------|-------------|--------------|
| QR-001 | [User's decision] | [What was changed] | [File path] |
| QR-002 | Deferred | — | — |

## Verdict

**Result:** [Approved / Approved with Notes / Changes Required]
**Unresolved Findings:** [Count and severity breakdown, if any]
