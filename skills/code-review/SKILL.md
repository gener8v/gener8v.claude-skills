---
name: code-review
description: "Review one delivered ticket against the pipeline: acceptance criteria, requirement coverage, constraints, architecture decisions and @spec annotations, producing traceability tables, findings and a verdict. Use after a delivery, in parallel with quality-review and security-review, when asked to 'review TICKET-003', 'check the delivery against the spec' or 'did we build what the ticket asked for'. Not for readability or tests on their own (quality-review), vulnerabilities (security-review), or code with no ticket behind it (quality-review on the files)."
argument-hint: "[capability area] [TICKET-XXX] [in change-slug]"
effort: xhigh
---

# Code Review Skill

**Invoked with:** `$ARGUMENTS`

If that is empty, ask the user which delivered ticket to review before doing anything else. Never guess the target. The ticket belongs to a change: when exactly one change is active (`active_changes` in `.gener8v/pipeline-state.yaml`), default to it; when several are active and the argument does not name one (`… in <change-slug>`), ask.

## Purpose

Review implemented code against pipeline artifacts to verify that a delivery satisfies its ticket, traces to requirements, respects constraints, and follows the technical design. This is a compliance-oriented review: does the code do what the pipeline says it should? It is the complement to the Quality Review skill — Code Review asks "did you build the right thing?" while Quality Review asks "did you build it well?"

## When to Use

Use this skill when:
- A ticket has been delivered (a delivery record exists in `.gener8v/changes/<change-slug>/delivery/`)
- Before marking a ticket as complete or merging code
- When verifying traceability from requirements through to implemented code
- When a delivery record shows deviations from the plan that need assessment
- After changes to specifications, constraints, or technical design that may affect already-delivered code

## Input

**Source:** A delivery record plus the delivered code files and the pipeline artifacts they trace to
**Change:** `[change-slug]` — from the argument (`in <change-slug>`) or the single active change
**Read from:**
- Delivery record: `.gener8v/changes/[change-slug]/delivery/[capability-area-slug]-[ticket-id]-delivery.md`
- Actual code files listed in the delivery record's "Files Produced" section — paths are root-relative; in a workspace with several repositories, the `## Repositories` table in `.gener8v/context.md` says which directory is which
- The source ticket: `.gener8v/changes/[change-slug]/tickets/[capability-area-slug]/TICKET-NNN.md` — one ticket, one file; `backlog.md` in the same directory gives the ordering context if needed
- Specification: `.gener8v/specifications/[capability-area-slug].md` (living — functional and non-functional requirements)
- Constraints: `.gener8v/constraints/prd.md` and `.gener8v/constraints/[capability-area-slug].md` (whichever exist)
- Technical Design: `.gener8v/technical-design/[capability-area-slug].md` or `.gener8v/technical-design/system-design.md` (if available)
- Conventions: `.gener8v/CONVENTIONS.md`

**Expects:** A completed delivery record with Files Produced listing actual file paths. The corresponding ticket must exist as its own `TICKET-NNN.md` in the change's `tickets/<area-slug>/` directory.

**If input is missing or malformed:**
- If no delivery record exists for the ticket, stop and recommend running the Delivery skill first
- If constraints or technical design are missing, proceed but note reduced review coverage — constraint compliance and architecture adherence sections will be marked "Not available"
- If code files listed in the delivery record do not exist, flag as a Critical finding

## Output

**Produces:** A code review report with findings and interactive resolutions
**Write to:** `.gener8v/changes/[change-slug]/reviews/[capability-area-slug]-[ticket-id]-code-review.md`
**Creates directory:** `.gener8v/changes/[change-slug]/reviews/` if it does not exist
**Naming convention:** Matches the delivery record naming with `-code-review` suffix

The report is written as soon as findings are drafted (all `Open`) and updated finding by finding during resolution, so a session that ends mid-review loses nothing. Approved code changes are applied in the resolution phase, re-verified, and recorded in the delivery record's `## Post-Review Amendments`.

## Output Format

Write the report in the shape of `assets/code-review-report.md` — Read it before writing and follow it exactly, headings and status lines included. `gener8v-state.py` parses its `**Result:**` line for the verdict and counts its `### CR-NNN` headings and `**Severity:**` lines for the metrics, so none of the three may be renamed or reformatted. Every code path in it — Files Reviewed, Code Location, Location — is root-relative to the workspace root (`api/src/search/query.ts`), never relative to a repository inside it.

---

## Principles

### Trace, Don't Opine
Every finding must trace to a specific pipeline artifact: a requirement, constraint, architecture decision, or acceptance criterion. "I don't like this approach" is not a code review finding. "This approach contradicts AD-002 which specifies X" is. The pipeline provides the objective standard; the review measures against it.

### The Ticket Is the Contract
The ticket defines what should have been built. Review against the ticket, not against what you think should have been built. If the ticket is wrong — missing requirements, insufficient acceptance criteria, flawed approach — that is an Audit finding on the ticket, not a Code Review finding on the code.

### Coverage Is Binary
Either an acceptance criterion is satisfied or it is not. Either a requirement is covered or it is not. Partial coverage is documented as "Partial" with specifics, not rounded up to "Yes." The traceability tables are the core deliverable of this review — they must be precise.

### Two Phases, Two Runtimes
**Findings** (steps 1–11) can run in a fresh context — the shipped `code-reviewer` agent, in parallel with the other two reviewers — because a reviewer who did not build the code has no reason to trust the builder's account of it. The findings phase writes the report with every finding `Status: Open` and a provisional verdict, and changes nothing else. **Resolution** (steps 12–14) runs in the main session with the user, one review at a time so three reviewers never edit the same file concurrently. Every approved change is re-verified and appended to the delivery record's `## Post-Review Amendments`; the report is updated per finding as it is resolved, and the final verdict is written last.

### Interactive Resolution
Like the Audit skill, findings are presented to the user for resolution. For each finding, the user may:
- **Approve**: Apply the recommended change to the code
- **Modify**: Provide a different fix; apply their preferred approach
- **Defer**: Mark as `Deferred → TICKET-NNN` (and append a Known Hazard to that ticket's own file, `.gener8v/changes/<change-slug>/tickets/<area-slug>/TICKET-NNN.md`, so its implementer sees it) or `Deferred → <reason>`
- **Dismiss**: Determine this is not an issue; mark `Dismissed` with rationale

The skill updates code files when the user approves changes, re-runs the delivery record's Verification Run, and appends the change to `## Post-Review Amendments`.

### Severity Reflects Pipeline Impact
- **Critical**: Acceptance criteria not met, requirement not covered, or code contradicts a constraint or architecture decision. Blocks approval.
- **Issue**: Partial coverage, minor divergence from architecture decision, or constraint not fully respected — but core functionality is present. Should be addressed.
- **Observation**: Minor divergence that does not affect correctness or traceability. Worth noting but does not block.

## Process

1. **Locate Delivery**: Resolve the change (the argument's `in <change-slug>`, or the single active one), then read the delivery record at `.gener8v/changes/<change-slug>/delivery/`. Extract the list of files produced, the ticket reference, and any DEL-XXX decisions.

2. **Read Delivered Code**: Read all code files listed in the delivery record's Files Produced section.

3. **Gather Pipeline Context**: Read the source ticket file `.gener8v/changes/<change-slug>/tickets/<area-slug>/TICKET-NNN.md`, the living specification (functional and non-functional requirements), constraints (if available), and technical design (if available) for the capability area.

4. **Check Acceptance Criteria**: For each acceptance criterion in the ticket, examine the delivered code for evidence of satisfaction. Record the evidence (file, line, function, behavior) or note its absence.

5. **Check Requirement Coverage**: For each requirement the ticket covers (from the Requirements Covered field), verify the code implements it. Identify the specific code location that serves each requirement. NFR IDs in that field are checked the same way: find the verification method the ticket's acceptance criteria name, confirm it ran in the Verification Run and met the target, and record the verifying artifact as the Code Location.

6. **Check Constraint Compliance**: For each constraint referenced in the ticket (or relevant to the capability area), verify the code respects it. Note how the constraint is honored or violated.

7. **Check Architecture Adherence**: For each relevant architecture decision (AD-XXX) from the technical design, verify the code follows it. Note alignment or divergence.

8. **Check `@spec` Annotations**: For each requirement the ticket covers, verify that an `@spec` annotation exists in the delivered code at the appropriate location. Check that annotations are correctly placed (on the line above the implementing function/class/method), list the right requirement IDs, and that no requirements are missing annotations. Missing annotations are Issue-level findings — traceability must survive in the code, not just in pipeline artifacts. Then open the specification's `## @spec Coverage` table and confirm it lists the same locations; a missing or stale row is an Issue-level finding.

8b. **Re-run the Verification**: Execute the commands in the delivery record's `## Verification Run` and confirm the exit codes match. A record with no Verification Run, a `Status` other than `Delivered`, or commands that no longer pass is a Critical finding — the review is of code that was never proven.

9. **Review Delivery Decisions**: Examine each DEL-XXX decision in the delivery record. Assess whether the decision was reasonable given the context, and whether it introduced risks or downstream impact.

10. **Review Deviations**: If the delivery record lists deviations from the approved plan, assess their impact on traceability and downstream tickets.

11. **Draft Findings and Write the Report**: For each issue discovered, create a finding with severity, location, traceability reference, description, impact, and recommendation. Write the full report to `.gener8v/changes/<change-slug>/reviews/` now, every finding `Open`, verdict provisional. *(End of the findings phase — when run as the `code-reviewer` agent, stop here and return the report path, verdict and counts.)*

12. **Present to User**: Share findings starting with Critical, then Issues, then Observations. For each finding, explain the issue, its pipeline trace, and the recommended fix. Work through interactive resolution, updating the finding's Status/Resolution and the Resolution Log row in the report as each is decided.

13. **Apply Approved Changes**: Update code files for findings the user approves, re-run the Verification Run, and append each change to the delivery record's `## Post-Review Amendments`.

14. **Write the Verdict**: Set the final `**Result:**` last, once every finding has a status.

## Example

The worked example reviews `support-search/search-and-retrieval/TICKET-001` (query input, SR-REQ-001..003) end to end: input, traceability tables, `@spec` and verification checks, one Observation-level finding and its verdict.
It lives at `references/example.md` next to this file.
Read it before producing your first artifact of this kind.

---

## Troubleshooting

- **No delivery record matches the argument.** Record names use the area slug, not its display name — `search-and-retrieval-ticket-003-delivery.md` for `Search & Retrieval TICKET-003` — and sit under the ticket's change. With several changes active and no `in <change-slug>`, the wrong change was searched: ask. With no record in any change, the ticket was never delivered; stop and recommend Delivery.
- **Orchestrate still lists the code review as missing after the report was written.** The state script opens exactly `.gener8v/changes/<change-slug>/reviews/<area-slug>-ticket-nnn-code-review.md` — area slug, lowercase `ticket-nnn`, inside the ticket's change. A report named `TICKET-003-code-review.md`, filed under another change, or written to the top-level `.gener8v/reviews/` (system assessments only) is invisible to it. Move or rename the file; never leave two copies.
- **The ticket exists only as a section of `tickets/<area-slug>.md`.** That is the legacy per-area file, read as change `initial` when the whole layout is legacy. Review against the section, and recommend `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py split-tickets --remove` in the Verdict's Notes: a deferral appends its Known Hazard to the ticket's own file, and until the split there is none.
- **A Verification Run command fails for a reason outside the code** — a service that is not running, a variable the record expects. It is still Critical under step 8b: nothing about the ticket is proven from where the reviewer stands. Say which failure it was, so resolution fixes the environment or the record's command rather than the code.
- **The `code-reviewer` agent returned without a report path.** The findings phase ends at step 11 by writing the report; an agent that stops at its turn limit returns partial output instead. Resolution needs a report with every finding `Open` — resume or re-launch the agent on the same ticket, or run steps 1–11 in the main session, before starting step 12.

## Integration with Other Skills

**Upstream:**
- **Delivery Skill**: Provides the delivery record and code files to review
- **Ticket Breakdown Skill**: Provides the ticket (acceptance criteria, requirements, constraints, dependencies)
- **Specification Skill**: Provides requirement detail for traceability verification
- **Constraints Skill**: Provides constraints for compliance verification
- **Technical Design Skill**: Provides architecture decisions for adherence verification

**Downstream:**
- **Audit Skill**: Can include code review findings in cross-stage consistency checks
- **Delivery Skill** (later tickets): reads this report for findings deferred to a named ticket
- **Orchestrate**: reads the `**Result:**` line; `Changes Required` holds the ticket at `changes_required`

## Revisions

- Code review reports capture a point-in-time assessment — they do not auto-update when code changes
- If code is modified after review (e.g., from quality or security review findings), the code review remains valid for its original scope but may warrant re-running
- Previous code review reports remain in `.gener8v/changes/<change-slug>/reviews/` for reference
- If the underlying specification or constraints change, re-run the code review to verify continued compliance

## Notes

- Run this skill after Delivery, before marking a ticket as complete
- The findings phase can run in parallel with Quality Review and Security Review (as the three reviewer agents); resolution phases run one at a time
- Verdict vocabulary is shared by all three reviews: Approved / Approved with Notes / Changes Required (see `CONVENTIONS.md` §5)
- The traceability tables (acceptance criteria, requirements, constraints, architecture decisions) are the primary output — findings are secondary
- A delivery with zero findings but incomplete traceability tables is a worse outcome than one with findings and complete tables
- This skill does not evaluate code quality, performance, or security — those are the responsibilities of Quality Review and Security Review respectively
- If the delivery record shows a "Partial" or "Blocked" status, the code review should note which acceptance criteria could not be verified and why
