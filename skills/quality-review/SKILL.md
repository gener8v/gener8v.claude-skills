---
name: quality-review
description: "Review delivered code for engineering quality — organization, readability, error handling, tests, consistency with the codebase's patterns — independent of the specification. Use after a delivery in parallel with code-review and security-review, or on any files the user points at."
argument-hint: "<capability area> <TICKET-XXX> [in <change-slug>] | <files>"
---
# Quality Review Skill

**Invoked with:** `$ARGUMENTS`

If that is empty, ask the user which delivered ticket (or which files) to review before doing anything else. Never guess the target. The ticket lives in a change: when exactly one change is active (`active_changes` in `.gener8v/pipeline-state.yaml`), default to it; when several are and the argument does not say `in <change-slug>`, ask which change before doing anything else.

## Purpose

Review implemented code for engineering quality independent of pipeline artifacts. This skill does not care whether the code matches the spec — that is the Code Review skill's job. It cares whether the code is well-written, maintainable, testable, and follows sound engineering practices. It evaluates code organization, readability, error handling, test coverage, observability and operability, and adherence to established patterns in the codebase.

## When to Use

Use this skill when:
- A ticket has been delivered (a delivery record exists in `.gener8v/changes/<change-slug>/delivery/`)
- After or in parallel with Code Review
- When code quality standards need enforcement before merging
- When evaluating delivered code for maintainability concerns
- When onboarding new patterns or conventions and ensuring consistency

## Input

**Source:** Delivered code files
**Read from:**
- Delivery record: `.gener8v/changes/<change-slug>/delivery/<area-slug>-ticket-NNN-delivery.md` (for the file list)
- Actual code files listed in the delivery record's "Files Produced" section
- System Context: `.gener8v/context.md` (if available — for language, framework, convention expectations and the `## Repositories` table's verify commands for the repository the delivery changed)
- Conventions: `.gener8v/CONVENTIONS.md`
- Existing codebase files in the same directory or module (for pattern consistency checks)

**Expects:** Code files to exist. Does NOT require pipeline artifacts beyond the delivery record — this skill is intentionally pipeline-independent in its review criteria.

**If input is missing or malformed:**
- If no delivery record exists, the user can point directly to code files to review
- If system context is missing, the skill infers conventions from the existing codebase and notes reduced context in the report
- If the code files listed in the delivery record do not exist, stop and flag the issue

## Output

**Produces:** A quality review report with findings and interactive resolutions
**Write to:** `.gener8v/changes/<change-slug>/reviews/<area-slug>-ticket-NNN-quality-review.md`
**Creates directory:** `.gener8v/changes/<change-slug>/reviews/` if it does not exist
**Naming convention:** Matches the delivery record naming with `-quality-review` suffix

The report is written as soon as findings are drafted (all `Open`) and updated finding by finding during resolution. Approved code changes are applied in the resolution phase, re-verified, and recorded in the delivery record's `## Post-Review Amendments`.

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

### Tests Are First-Class Code — and Their Absence Is a Block
A ticket with testable acceptance criteria and no tests is `Changes Required`, not a suggestion: the delivery's Verification Run has nothing to run, so nothing about the ticket is proven. Review test code with the same rigor as production code. Tests that are brittle (tied to implementation details), unclear (test names that don't describe behavior), or incomplete (happy path only) are quality findings. Tests that test the framework instead of the behavior are quality findings.

### Two Phases, Two Runtimes
**Findings** (steps 1–13) can run in a fresh context — the shipped `quality-reviewer` agent, in parallel with the other two reviewers — because a reviewer who did not build the code has no reason to trust the builder's account of it. The findings phase writes the report with every finding `Status: Open` and a provisional verdict, and changes nothing else. **Resolution** (steps 14–16) runs in the main session with the user, one review at a time so three reviewers never edit the same file concurrently. Every approved change is re-verified and appended to the delivery record's `## Post-Review Amendments`; the report is updated per finding as it is resolved, and the final verdict is written last.

### Performance Is Contextual
Do not flag performance concerns without considering the actual usage context. An O(n^2) loop over a list that will never exceed 10 items is not a finding. A synchronous blocking call in a request handler that serves 10,000 concurrent users is. State the context that makes a performance concern relevant.

## Process

1. **Locate Code**: Read the delivery record to get the list of files produced. If no delivery record exists, use file paths provided directly by the user.

2. **Read All Code**: Read every delivered code file, including test files if present.

3. **Read System Context**: If `.gener8v/context.md` exists, read it for language, framework, and convention expectations, and take the verify commands for the repository the delivery changed from its `## Repositories` table.

4. **Read Surrounding Code**: Read existing code files in the same directory or module to understand established patterns, naming conventions, and error handling approaches.

5. **Assess Code Organization**: Evaluate module structure, separation of concerns, file organization. Check whether responsibilities are clearly delineated. Check import structure and dependency direction.

6. **Assess Readability**: Evaluate naming conventions (variables, functions, classes, files). Check function length and cognitive complexity. Look for self-documenting code vs. code that requires extensive comments to understand.

7. **Assess Error Handling**: Check for missing error handling on operations that can fail. Check for swallowed errors (catch-and-ignore). Verify error messages are meaningful and actionable. Check for consistent error handling patterns.

8. **Assess Test Coverage**: Run the project's test, lint and type-check commands (from the `## Repositories` table in `context.md` for the repository the delivery changed, or the repository's scripts when the table is absent) and record the results. Check for test presence. Evaluate coverage of key code paths, edge cases, and error conditions. Assess test quality — are tests testing behavior or implementation? Are test names descriptive? Testable acceptance criteria with no tests is a Critical finding.

9. **Assess Observability & Operability**: Check what the code logs, at what level and with what context (identifiers, durations, causes). Check whether failures are visible to an operator — not swallowed, not logged as noise — and whether metrics or health signals exist where the surrounding code provides them. Rate it like the other four categories; calibrate to the codebase's existing logging and metrics patterns rather than demanding instrumentation the project does not use.

10. **Check DRY**: Identify duplicated logic that should be extracted. Distinguish between coincidental similarity (leave alone) and actual duplication (extract).

11. **Check Patterns**: Verify consistency with the codebase's established patterns. Flag deviations that introduce inconsistency without justification.

12. **Check Performance**: Identify obvious performance concerns in context. Consider the actual usage patterns and data volumes.

13. **Draft Findings and Write the Report**: Create findings with category, severity, root-relative location, and specific recommendations. Write the full report to `.gener8v/changes/<change-slug>/reviews/` now, every finding `Open`, verdict provisional. *(End of the findings phase — when run as the `quality-reviewer` agent, stop here and return the report path, verdict and counts.)*

14. **Present to User**: Share findings starting with Critical, then Concerns, then Suggestions. Work through interactive resolution — fix, defer or dismiss — updating each finding in the report as it is decided. A finding deferred to a named ticket (`Deferred → TICKET-NNN`) also gets a Known Hazard appended to that ticket in its breakdown file, so the implementer sees it (`CONVENTIONS.md` §2).

15. **Apply Approved Changes**: Update code files for findings the user approves, re-run the delivery record's Verification Run, and append each change to the delivery record's `## Post-Review Amendments`.

16. **Write the Verdict**: Set the final `**Result:**` last.

## Example

A quality review of `support-search/search-and-retrieval/TICKET-001` (query input interface) — one delivered file, no tests, five rated categories, a Critical finding that blocks the ticket and a Suggestion, written under `changes/support-search/reviews/`. The full worked example is in `references/example.md` (relative to this skill's directory). Read it before producing your first artifact of this kind.

---

## Integration with Other Skills

**Upstream:**
- **Delivery Skill**: Provides the delivery record (file list) and the delivered code to review

**Downstream:**
- **Audit Skill**: Can include quality review ratings in cross-stage assessments
- **Delivery Skill** (later tickets): reads this report for findings deferred to a named ticket
- **Orchestrate**: reads the `**Result:**` line; `Changes Required` holds the ticket at `changes_required`

**Parallel:**
- **Code Review Skill**: Reviews the same code for pipeline traceability — different concern, can run in parallel
- **Security Review Skill**: Reviews the same code for vulnerabilities — different concern, can run in parallel

## Revisions

- Quality review reports capture a point-in-time assessment — they do not auto-update when code changes
- If code is modified after review (e.g., from code review or security review findings), the quality review remains valid for its original scope
- Previous quality review reports remain in `.gener8v/changes/<change-slug>/reviews/` for reference
- If the codebase's patterns or conventions change significantly, earlier quality reviews may be less relevant

## Notes

- This skill is intentionally pipeline-independent — it evaluates engineering quality, not specification compliance
- The only pipeline artifacts it reads are the delivery record (for the file list), `pipeline-state.yaml` (to find the active change) and optionally system context (for calibration and verify commands)
- The findings phase runs after Delivery, in parallel with Code Review and Security Review (as the reviewer agents); resolution phases run one at a time
- Verdict vocabulary is shared by all three reviews: Approved / Approved with Notes / Changes Required
- Quality standards should match the project's maturity and purpose — do not over-engineer a prototype or under-engineer a production service
- When reviewing test code, apply the same quality lens as production code — tests are not second-class artifacts
- If no delivery record exists, this skill can still be used by pointing it directly at code files — it degrades gracefully
