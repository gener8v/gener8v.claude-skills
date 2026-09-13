# [Ticket ID]: [Ticket Title] — Code Review

## Summary

[2-3 sentences: what was reviewed, overall assessment, finding count.]

**Delivery Record:** [file path]
**Files Reviewed:**
- [file path]
- [file path]

**Findings:** [Total count]
**Critical:** [Count] | **Issues:** [Count] | **Observations:** [Count]

## Traceability Check

### Acceptance Criteria Coverage

| Criterion | Satisfied | Evidence |
|-----------|-----------|----------|
| [Criterion text from ticket] | Yes / No / Partial | [File:line or function where this is demonstrated] |

### Requirement Coverage

| Requirement | Description | Code Location | Covered |
|-------------|-------------|---------------|---------|
| [XX]-REQ-XXX | [Brief description] | [file:line or function] | Yes / No / Partial |
| [XX]-NFR-XXX | [Measurable target] | [benchmark, test or lint that verifies it — or "not executable"] | Yes / No / Partial |

*[NFRs the ticket carries appear here like requirements. An NFR is Covered when the verification method the ticket names ran in the delivery record's Verification Run and met the target; one the record left Unverified is Partial and an Issue-level finding unless the ticket recorded it as non-executable.]*

### Constraint Compliance

| Constraint | Description | Respected | Evidence |
|------------|-------------|-----------|----------|
| [TC/CC/IC/OC]-XXX | [Brief description] | Yes / No / N/A | [How the code respects or violates] |

*[Omit this section if no constraints analysis exists. Note "Constraints analysis not available — constraint compliance not verified."]*

### Architecture Decision Adherence

| Decision | Description | Followed | Evidence |
|----------|-------------|----------|----------|
| AD-XXX | [Brief description] | Yes / No / Partial | [How the code aligns or diverges] |

*[Omit this section if no technical design exists. Note "Technical design not available — architecture adherence not verified."]*

### @spec Annotation Coverage

| Requirement | Expected Annotation | Code Location | Present |
|-------------|-------------------|---------------|---------|
| [XX]-REQ-XXX | `@spec [XX]-REQ-XXX` | [file:function] | Yes / No / Misplaced |

**Coverage:** [X of Y requirements annotated]
**Missing:** [List any requirements without `@spec` annotations — each is an Issue-level finding]
**Specification table:** [Does `## @spec Coverage` in the specification list these locations? Yes / No — a mismatch is an Issue-level finding]

### Verification Run

| Command (from delivery record) | Re-run exit | Matches record |
|--------------------------------|-------------|----------------|
| `pytest tests/search -q` | 0 | Yes |

*[A delivery record with no Verification Run, or one whose commands do not reproduce, is a Critical finding.]*

## Delivery Decisions Review

| Decision | Assessment | Notes |
|----------|------------|-------|
| DEL-XXX | [Reasonable / Questionable / Problematic] | [Why] |

## Findings

### CR-001: [Finding title]

**Severity:** [Critical / Issue / Observation]
**Location:** [root-relative path:line or function]
**Traces To:** [REQ-XXX, AD-XXX, constraint ID, or acceptance criterion]
**Description:** [What the problem is]
**Impact:** [What goes wrong if not addressed]
**Recommendation:** [Specific action to resolve]
**Status:** [Open / Resolved / Deferred → TICKET-NNN or reason / Dismissed]
**Resolution:** [What was done, if resolved — filled in during resolution]

---

### CR-002: ...

## Resolution Log

| Finding | Decision | Action Taken | File Updated |
|---------|----------|-------------|--------------|
| CR-001 | [User's decision] | [What was changed] | [File path, if applicable] |
| CR-002 | Deferred | — | — |

## Verdict

**Result:** [Approved / Approved with Notes / Changes Required]
**Unresolved Findings:** [Count and severity breakdown, if any]
**Notes:** [Any conditions on the approval or next steps]
