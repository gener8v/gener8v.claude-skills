# Code Review Skill

## Purpose

Review implemented code against pipeline artifacts to verify that a delivery satisfies its ticket, traces to requirements, respects constraints, and follows the technical design. This is a compliance-oriented review: does the code do what the pipeline says it should? It is the complement to the Quality Review skill — Code Review asks "did you build the right thing?" while Quality Review asks "did you build it well?"

## When to Use

Use this skill when:
- A ticket has been delivered (a delivery record exists in `.gener8v/delivery/`)
- Before marking a ticket as complete or merging code
- When verifying traceability from requirements through to implemented code
- When a delivery record shows deviations from the plan that need assessment
- After changes to specifications, constraints, or technical design that may affect already-delivered code

## Input

**Source:** A delivery record plus the delivered code files and the pipeline artifacts they trace to
**Read from:**
- Delivery record: `.gener8v/delivery/[capability-area-slug]-[ticket-id]-delivery.md`
- Actual code files listed in the delivery record's "Files Produced" section
- The source ticket: `.gener8v/tickets/[capability-area-slug].md`
- Specification: `.gener8v/specifications/[capability-area-slug].md`
- Constraints: `.gener8v/constraints/[capability-area-slug].md` (if available)
- Technical Design: `.gener8v/technical-design/[capability-area-slug].md` or `.gener8v/technical-design/system-design.md` (if available)

**Expects:** A completed delivery record with Files Produced listing actual file paths. The corresponding ticket must exist in the ticket breakdown.

**If input is missing or malformed:**
- If no delivery record exists for the ticket, stop and recommend running the Delivery skill first
- If constraints or technical design are missing, proceed but note reduced review coverage — constraint compliance and architecture adherence sections will be marked "Not available"
- If code files listed in the delivery record do not exist, flag as a Critical finding

## Output

**Produces:** A code review report with findings and interactive resolutions
**Write to:** `.gener8v/reviews/[capability-area-slug]-[ticket-id]-code-review.md`
**Creates directory:** `.gener8v/reviews/` if it does not exist
**Naming convention:** Matches the delivery record naming with `-code-review` suffix

After interactive resolution, the skill may update delivered code files if the user approves changes. The review report captures all findings and their resolutions.

## Output Format

Produce a markdown document with the following structure:

```markdown
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

## Delivery Decisions Review

| Decision | Assessment | Notes |
|----------|------------|-------|
| DEL-XXX | [Reasonable / Questionable / Problematic] | [Why] |

## Findings

### CR-001: [Finding title]

**Severity:** [Critical / Issue / Observation]
**Location:** [file:line or function]
**Traces To:** [REQ-XXX, AD-XXX, constraint ID, or acceptance criterion]
**Description:** [What the problem is]
**Impact:** [What goes wrong if not addressed]
**Recommendation:** [Specific action to resolve]
**Status:** [Open / Resolved / Deferred]
**Resolution:** [What was done, if resolved — filled in during interactive session]

---

### CR-002: ...

## Resolution Log

| Finding | Decision | Action Taken | File Updated |
|---------|----------|-------------|--------------|
| CR-001 | [User's decision] | [What was changed] | [File path, if applicable] |
| CR-002 | Deferred | — | — |

## Verdict

**Result:** [Approved / Approved with Observations / Changes Required]
**Unresolved Findings:** [Count and severity breakdown, if any]
**Notes:** [Any conditions on the approval or next steps]
```

---

## Principles

### Trace, Don't Opine
Every finding must trace to a specific pipeline artifact: a requirement, constraint, architecture decision, or acceptance criterion. "I don't like this approach" is not a code review finding. "This approach contradicts AD-002 which specifies X" is. The pipeline provides the objective standard; the review measures against it.

### The Ticket Is the Contract
The ticket defines what should have been built. Review against the ticket, not against what you think should have been built. If the ticket is wrong — missing requirements, insufficient acceptance criteria, flawed approach — that is an Audit finding on the ticket, not a Code Review finding on the code.

### Coverage Is Binary
Either an acceptance criterion is satisfied or it is not. Either a requirement is covered or it is not. Partial coverage is documented as "Partial" with specifics, not rounded up to "Yes." The traceability tables are the core deliverable of this review — they must be precise.

### Interactive Resolution
Like the Audit skill, findings are presented to the user for resolution. For each finding, the user may:
- **Approve**: Apply the recommended change to the code
- **Modify**: Provide a different fix; apply their preferred approach
- **Defer**: Mark as deferred with rationale
- **Dismiss**: Determine this is not an issue; mark with rationale

The skill updates code files when the user approves changes.

### Severity Reflects Pipeline Impact
- **Critical**: Acceptance criteria not met, requirement not covered, or code contradicts a constraint or architecture decision. Blocks approval.
- **Issue**: Partial coverage, minor divergence from architecture decision, or constraint not fully respected — but core functionality is present. Should be addressed.
- **Observation**: Minor divergence that does not affect correctness or traceability. Worth noting but does not block.

## Process

1. **Locate Delivery**: Read the delivery record for the target ticket. Extract the list of files produced, the ticket reference, and any DEL-XXX decisions.

2. **Read Delivered Code**: Read all code files listed in the delivery record's Files Produced section.

3. **Gather Pipeline Context**: Read the source ticket, specification, constraints (if available), and technical design (if available) for the capability area.

4. **Check Acceptance Criteria**: For each acceptance criterion in the ticket, examine the delivered code for evidence of satisfaction. Record the evidence (file, line, function, behavior) or note its absence.

5. **Check Requirement Coverage**: For each requirement the ticket covers (from the Requirements Covered field), verify the code implements it. Identify the specific code location that serves each requirement.

6. **Check Constraint Compliance**: For each constraint referenced in the ticket (or relevant to the capability area), verify the code respects it. Note how the constraint is honored or violated.

7. **Check Architecture Adherence**: For each relevant architecture decision (AD-XXX) from the technical design, verify the code follows it. Note alignment or divergence.

8. **Check `@spec` Annotations**: For each requirement the ticket covers, verify that an `@spec` annotation exists in the delivered code at the appropriate location. Check that annotations are correctly placed (on the line above the implementing function/class/method), list the right requirement IDs, and that no requirements are missing annotations. Missing annotations are Issue-level findings — traceability must survive in the code, not just in pipeline artifacts.

9. **Review Delivery Decisions**: Examine each DEL-XXX decision in the delivery record. Assess whether the decision was reasonable given the context, and whether it introduced risks or downstream impact.

10. **Review Deviations**: If the delivery record lists deviations from the approved plan, assess their impact on traceability and downstream tickets.

11. **Draft Findings**: For each issue discovered, create a finding with severity, location, traceability reference, description, impact, and recommendation.

12. **Present to User**: Share findings starting with Critical, then Issues, then Observations. For each finding, explain the issue, its pipeline trace, and the recommended fix. Work through interactive resolution.

13. **Apply Approved Changes**: Update code files for findings the user approves.

14. **Write Report**: Save the code review report to `.gener8v/reviews/`.

## Example

### Input

Reviewing the delivery of TICKET-001 from Search & Retrieval: "Implement query input interface"

Delivery record at `.gener8v/delivery/search-and-retrieval-ticket-001-delivery.md` shows:
- Files Produced: `src/search/query_input.py`
- Requirements Covered: SR-REQ-001
- Acceptance Criteria: 4 criteria, all marked satisfied
- Decisions: DEL-001 (QueryResult dataclass)

### Output (abbreviated)

````markdown
# TICKET-001: Implement query input interface — Code Review

## Summary

Reviewed delivery of TICKET-001 against the Search & Retrieval specification and ticket. One file reviewed. All acceptance criteria are satisfied. One observation regarding the DEL-001 decision's downstream impact. No critical or issue-level findings.

**Delivery Record:** `.gener8v/delivery/search-and-retrieval-ticket-001-delivery.md`
**Files Reviewed:**
- `src/search/query_input.py`

**Findings:** 1
**Critical:** 0 | **Issues:** 0 | **Observations:** 1

## Traceability Check

### Acceptance Criteria Coverage

| Criterion | Satisfied | Evidence |
|-----------|-----------|----------|
| Accepts free-text input of 500+ characters | Yes | `process_query()` accepts strings up to 10,000 chars; no lower bound enforced beyond non-empty |
| Passes query to search pipeline unmodified | Yes | `QueryResult.query` returns input string without transformation (line 24) |
| Provides in-progress feedback | Yes | `QueryResult.status` set to `"processing"` (line 25) |
| Rejects empty/whitespace queries | Yes | `ValueError` raised at line 18 for empty/whitespace input |

### Requirement Coverage

| Requirement | Description | Code Location | Covered |
|-------------|-------------|---------------|---------|
| SR-REQ-001 | Accept natural language questions as input | `src/search/query_input.py:process_query()` | Yes |

## Delivery Decisions Review

| Decision | Assessment | Notes |
|----------|------------|-------|
| DEL-001 | Reasonable | QueryResult dataclass is a clean interface for downstream consumers. TICKET-003 Prior Art should reference this type. |

## Findings

### CR-001: QueryResult type not exported in module __init__

**Severity:** Observation
**Location:** `src/search/query_input.py`
**Traces To:** TICKET-001 Output section ("exposing a function/method that accepts a string query")
**Description:** The ticket's Output section says downstream tickets will consume the query interface contract. The `QueryResult` type is defined but not explicitly exported — downstream imports will need to reference the internal module path.
**Impact:** Minor inconvenience for TICKET-003 implementation; not a correctness issue.
**Recommendation:** Add `QueryResult` to the module's public API or note the import path in the delivery record's Notes section.
**Status:** Open

## Verdict

**Result:** Approved with Observations
**Unresolved Findings:** 1 Observation
**Notes:** All acceptance criteria satisfied. All requirements covered. CR-001 is a minor export concern that can be addressed during TICKET-003 delivery.
````

---

## Integration with Other Skills

**Upstream:**
- **Delivery Skill**: Provides the delivery record and code files to review
- **Ticket Breakdown Skill**: Provides the ticket (acceptance criteria, requirements, constraints, dependencies)
- **Specification Skill**: Provides requirement detail for traceability verification
- **Constraints Skill**: Provides constraints for compliance verification
- **Technical Design Skill**: Provides architecture decisions for adherence verification

**Downstream:**
- **Audit Skill**: Can include code review findings in cross-stage consistency checks
- Code review reports are reference documents — no other skill consumes them as direct input

## Revisions

- Code review reports capture a point-in-time assessment — they do not auto-update when code changes
- If code is modified after review (e.g., from quality or security review findings), the code review remains valid for its original scope but may warrant re-running
- Previous code review reports remain in `.gener8v/reviews/` for reference
- If the underlying specification or constraints change, re-run the code review to verify continued compliance

## Notes

- Run this skill after Delivery, before marking a ticket as complete
- This skill can run in parallel with Quality Review and Security Review — they review different aspects of the same code
- The traceability tables (acceptance criteria, requirements, constraints, architecture decisions) are the primary output — findings are secondary
- A delivery with zero findings but incomplete traceability tables is a worse outcome than one with findings and complete tables
- This skill does not evaluate code quality, performance, or security — those are the responsibilities of Quality Review and Security Review respectively
- If the delivery record shows a "Partial" or "Blocked" status, the code review should note which acceptance criteria could not be verified and why
