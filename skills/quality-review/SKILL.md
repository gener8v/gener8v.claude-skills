# Quality Review Skill

## Purpose

Review implemented code for engineering quality independent of pipeline artifacts. This skill does not care whether the code matches the spec — that is the Code Review skill's job. It cares whether the code is well-written, maintainable, testable, and follows sound engineering practices. It evaluates code organization, readability, error handling, test coverage, and adherence to established patterns in the codebase.

## When to Use

Use this skill when:
- A ticket has been delivered (a delivery record exists in `.gener8v/delivery/`)
- After or in parallel with Code Review
- When code quality standards need enforcement before merging
- When evaluating delivered code for maintainability concerns
- When onboarding new patterns or conventions and ensuring consistency

## Input

**Source:** Delivered code files
**Read from:**
- Delivery record: `.gener8v/delivery/[capability-area-slug]-[ticket-id]-delivery.md` (for the file list)
- Actual code files listed in the delivery record's "Files Produced" section
- System Context: `.gener8v/context.md` (if available — for language, framework, and convention expectations)
- Existing codebase files in the same directory or module (for pattern consistency checks)

**Expects:** Code files to exist. Does NOT require pipeline artifacts beyond the delivery record — this skill is intentionally pipeline-independent in its review criteria.

**If input is missing or malformed:**
- If no delivery record exists, the user can point directly to code files to review
- If system context is missing, the skill infers conventions from the existing codebase and notes reduced context in the report
- If the code files listed in the delivery record do not exist, stop and flag the issue

## Output

**Produces:** A quality review report with findings and interactive resolutions
**Write to:** `.gener8v/reviews/[capability-area-slug]-[ticket-id]-quality-review.md`
**Creates directory:** `.gener8v/reviews/` if it does not exist
**Naming convention:** Matches the delivery record naming with `-quality-review` suffix

After interactive resolution, the skill may update delivered code files if the user approves changes. The review report captures all findings and their resolutions.

## Output Format

Produce a markdown document with the following structure:

```markdown
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
testing, test quality and maintainability]

## Findings

### QR-001: [Finding title]

**Category:** [Readability / Error Handling / Naming / DRY / SOLID / Performance / Maintainability / Testing / Patterns]
**Severity:** [Critical / Concern / Suggestion]
**Location:** [file:line or function]
**Description:** [What the issue is — specific, not aesthetic]
**Impact:** [Why this matters for maintainability, reliability, or performance]
**Recommendation:** [Specific improvement with example if helpful]
**Status:** [Open / Resolved / Deferred]
**Resolution:** [What was done, if resolved — filled in during interactive session]

---

### QR-002: ...

## Resolution Log

| Finding | Decision | Action Taken | File Updated |
|---------|----------|-------------|--------------|
| QR-001 | [User's decision] | [What was changed] | [File path] |
| QR-002 | Deferred | — | — |

## Verdict

**Result:** [Approved / Approved with Suggestions / Improvements Required]
**Unresolved Findings:** [Count and severity breakdown, if any]
```

---

## Principles

### Quality Is Objective, Not Aesthetic
Findings must identify concrete engineering concerns: missing error handling, naming that obscures intent, duplicated logic, untested edge cases, functions too complex to reason about. "I would have done it differently" is not a finding. "This function has a cyclomatic complexity of 15 with 6 nested conditionals" is.

### Context-Sensitive Standards
A prototype and a production service have different quality bars. A CLI script and a shared library have different expectations. Use system context (`.gener8v/context.md`) when available to calibrate. Examine the existing codebase to understand established patterns. Do not demand enterprise patterns in a proof-of-concept or library-grade polish in an internal tool.

### Readability Over Cleverness
Code is read far more often than it is written. Prefer findings that improve readability even at the cost of conciseness. A three-line conditional is better than a one-line ternary that requires three re-reads to parse. Name things for the reader who will debug this at 2am.

### Patterns Over Rules
Check for consistency with the codebase's existing patterns before flagging deviations from textbook best practices. A codebase that consistently uses one error handling pattern should not be told to switch mid-stream. Pattern consistency within a project trumps theoretical ideals.

### SOLID Is a Lens, Not a Law
Use SOLID principles as diagnostic tools to identify potential problems, not as a checklist that must be fully satisfied. Flag Single Responsibility violations only when a module is doing so many things that changes in one area risk breaking another. Flag Open/Closed violations only when extension points are clearly needed. Do not flag SOLID "violations" in code that is simple, clear, and unlikely to change.

### Tests Are First-Class Code
Review test code with the same rigor as production code. Tests that are brittle (tied to implementation details), unclear (test names that don't describe behavior), or incomplete (happy path only) are quality findings. Tests that test the framework instead of the behavior are quality findings.

### Performance Is Contextual
Do not flag performance concerns without considering the actual usage context. An O(n^2) loop over a list that will never exceed 10 items is not a finding. A synchronous blocking call in a request handler that serves 10,000 concurrent users is. State the context that makes a performance concern relevant.

## Process

1. **Locate Code**: Read the delivery record to get the list of files produced. If no delivery record exists, use file paths provided directly by the user.

2. **Read All Code**: Read every delivered code file, including test files if present.

3. **Read System Context**: If `.gener8v/context.md` exists, read it for language, framework, and convention expectations.

4. **Read Surrounding Code**: Read existing code files in the same directory or module to understand established patterns, naming conventions, and error handling approaches.

5. **Assess Code Organization**: Evaluate module structure, separation of concerns, file organization. Check whether responsibilities are clearly delineated. Check import structure and dependency direction.

6. **Assess Readability**: Evaluate naming conventions (variables, functions, classes, files). Check function length and cognitive complexity. Look for self-documenting code vs. code that requires extensive comments to understand.

7. **Assess Error Handling**: Check for missing error handling on operations that can fail. Check for swallowed errors (catch-and-ignore). Verify error messages are meaningful and actionable. Check for consistent error handling patterns.

8. **Assess Test Coverage**: Check for test presence. Evaluate coverage of key code paths, edge cases, and error conditions. Assess test quality — are tests testing behavior or implementation? Are test names descriptive?

9. **Check DRY**: Identify duplicated logic that should be extracted. Distinguish between coincidental similarity (leave alone) and actual duplication (extract).

10. **Check Patterns**: Verify consistency with the codebase's established patterns. Flag deviations that introduce inconsistency without justification.

11. **Check Performance**: Identify obvious performance concerns in context. Consider the actual usage patterns and data volumes.

12. **Draft Findings**: Create findings with category, severity, location, and specific recommendations.

13. **Present to User**: Share findings starting with Critical, then Concerns, then Suggestions. Work through interactive resolution.

14. **Apply Approved Changes**: Update code files for findings the user approves.

15. **Write Report**: Save to `.gener8v/reviews/`.

## Example

### Input

Reviewing the delivery of TICKET-001 from Search & Retrieval: "Implement query input interface"

Delivered code at `src/search/query_input.py`.

### Output (abbreviated)

````markdown
# TICKET-001: Implement query input interface — Quality Review

## Summary

Reviewed one file delivered for TICKET-001. Code organization and readability are strong. Error handling is adequate with one suggestion for improvement. No tests were delivered with this ticket. Two findings total.

**Files Reviewed:**
- `src/search/query_input.py`

**Findings:** 2
**Critical:** 0 | **Concerns:** 1 | **Suggestions:** 1

## Quality Assessment

### Code Organization

**Rating:** Strong
**Notes:** Single module with clear responsibility. QueryResult dataclass and process_query function are well-separated. No unnecessary abstractions.

### Readability

**Rating:** Strong
**Notes:** Clear naming, concise functions, self-documenting code. The validation logic reads naturally.

### Error Handling

**Rating:** Adequate
**Notes:** ValueError raised for invalid input with descriptive messages. The 10,000-character upper limit raises the same ValueError type as empty input — callers cannot distinguish between "too short" and "too long" without parsing the message string.

### Test Coverage

**Rating:** Not Present
**Notes:** No test file was delivered with this ticket. The ticket's acceptance criteria are testable and should have corresponding tests.

## Findings

### QR-001: No tests delivered

**Category:** Testing
**Severity:** Concern
**Location:** `src/search/` (expected: `tests/search/test_query_input.py` or similar)
**Description:** The ticket's acceptance criteria define four testable conditions, but no test file was delivered.
**Impact:** Acceptance criteria are verified manually in the delivery record but are not automated. Regressions will not be caught.
**Recommendation:** Add a test file covering: valid input passthrough, empty string rejection, whitespace-only rejection, boundary length handling.
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

**Result:** Approved with Suggestions
**Unresolved Findings:** 1 Concern, 1 Suggestion
````

---

## Integration with Other Skills

**Upstream:**
- **Delivery Skill**: Provides the delivery record (file list) and the delivered code to review

**Downstream:**
- **Audit Skill**: Can include quality review ratings in cross-stage assessments
- Quality review reports are reference documents — no other skill consumes them as direct input

**Parallel:**
- **Code Review Skill**: Reviews the same code for pipeline traceability — different concern, can run in parallel
- **Security Review Skill**: Reviews the same code for vulnerabilities — different concern, can run in parallel

## Revisions

- Quality review reports capture a point-in-time assessment — they do not auto-update when code changes
- If code is modified after review (e.g., from code review or security review findings), the quality review remains valid for its original scope
- Previous quality review reports remain in `.gener8v/reviews/` for reference
- If the codebase's patterns or conventions change significantly, earlier quality reviews may be less relevant

## Notes

- This skill is intentionally pipeline-independent — it evaluates engineering quality, not specification compliance
- The only pipeline artifact it reads is the delivery record (for the file list) and optionally system context (for calibration)
- Run this skill after Delivery, in parallel with Code Review and Security Review
- Quality standards should match the project's maturity and purpose — do not over-engineer a prototype or under-engineer a production service
- When reviewing test code, apply the same quality lens as production code — tests are not second-class artifacts
- If no delivery record exists, this skill can still be used by pointing it directly at code files — it degrades gracefully
