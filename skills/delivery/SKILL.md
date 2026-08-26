---
name: delivery
description: "Implement one ticket: reconcile its assumptions against the real codebase, get an implementation plan approved, write the code with @spec annotations, and keep the delivery record current from plan approval onward. The only skill that changes source code. Use when a ticket's dependencies are delivered and it is ready to build."
argument-hint: "<capability area> <TICKET-XXX> [in <change-slug>]"
disable-model-invocation: true
---
# Delivery Skill

**Invoked with:** `$ARGUMENTS`

If that is empty, ask the user which ticket (capability area + TICKET-XXX) to deliver before doing anything else. The ticket belongs to a change: when exactly one change is active (status `ready` or `in_delivery` in `pipeline-state.yaml`), default to it; when several are active and the argument does not name one (`in <change-slug>`), ask which. Never guess the target.

## Purpose

Take a single ticket from a ticket breakdown and implement it. This skill operates in three phases: first **reconciling** the ticket's stated assumptions against the actual codebase, then producing an **implementation plan** for user approval, then **executing** the plan by writing actual code. It is the only skill in the pipeline that writes to the real codebase — all other skills produce markdown artifacts in `.gener8v/`. The delivery record captures what was reconciled, what was planned, what was built, what decisions were made, and where the implementation diverged from the plan.

Reconciliation comes first because a ticket — however well-specified — encodes *assumptions* about the codebase it will build on: that a table or column exists, that a script or command is available, that a referenced document is present at the pinned version, that a predecessor's output is where it claims to be. When those assumptions are wrong, the most expensive outcome is discovering it mid-build (or worse, building confidently on top of the wrong foundation). Verifying them against ground truth *before* planning turns a runtime failure into a cheap pre-flight finding.

## When to Use

Use this skill when:
- A ticket file under `.gener8v/changes/<change-slug>/tickets/<capability-area-slug>/` is ready for implementation (no unresolved blockers in its Depends On field)
- The user wants to implement a specific ticket
- All predecessor tickets (from the Depends On field) have been delivered
- The team is ready to move from planning artifacts to working code

## Input

**Source:** A single ticket from a ticket breakdown, plus all pipeline artifacts referenced in the ticket's Prior Art
**Read from:**
- Ticket: `.gener8v/changes/[change-slug]/tickets/[capability-area-slug]/TICKET-XXX.md` — one ticket, one file; there is no extraction step. Its `**Change:**`, `**Capability Area:**` and `**Specification:**` header lines confirm the target
- Backlog: `.gener8v/changes/[change-slug]/tickets/[capability-area-slug]/backlog.md` — the dependency chain and suggested ordering this ticket sits in
- Predecessor tickets (from the Depends On field): sibling `TICKET-XXX.md` files in the same directory
- Change brief: `.gener8v/changes/[change-slug]/change.md` — its Status (Draft or Approved) and Priority Cut
- Prior Art as declared in the ticket (pipeline documents and predecessor ticket outputs)
- Technical Design: `.gener8v/technical-design/[capability-area-slug].md` or `.gener8v/technical-design/system-design.md` (if available)
- Constraints: `.gener8v/constraints/prd.md` and `.gener8v/constraints/[capability-area-slug].md` (whichever exist — PRD-level constraints apply to every ticket)
- System Context: `.gener8v/context.md` (if available — its `## Repositories` table names each repository's directory and verify commands; its testing and build sections add detail)
- Conventions: `.gener8v/CONVENTIONS.md`
- Predecessor delivery records: `.gener8v/changes/[change-slug]/delivery/*-delivery.md` (for dependent tickets), including their `## Post-Review Amendments`
- Predecessor review reports: `.gener8v/changes/[change-slug]/reviews/*-{code,quality,security}-review.md` for every ticket in Depends On and for any predecessor whose Files Produced overlap this ticket's Output — findings deferred "to the next ticket" and accepted risks live there. Predecessors normally sit under the same change; a dependency on an earlier change's ticket is read from that change's directory
- Existing codebase files referenced in Prior Art

**Expects:** A ticket file opening with `# TICKET-XXX: title` and the three header lines, then Summary, Priority, Value, Requirements Covered, Prior Art, Acceptance Criteria, Output, Constraints, and Size fields. Predecessor tickets in the Depends On field should have delivery records.

**If input is missing or malformed:**
- If several changes are active and none is named, ask which one before reading anything
- If no `tickets/<capability-area-slug>/TICKET-XXX.md` exists for the target under the change, stop and recommend running the Ticket Breakdown skill first (`ticket-breakdown <area> for <change-slug>`)
- Legacy: if the area's tickets exist only as a per-area file `tickets/<capability-area-slug>.md` holding `### TICKET-NNN:` sections, recommend `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py" split-tickets` and deliver from the resulting ticket file — never from the legacy shape
- If predecessor tickets have not been delivered, warn the user — the ticket's Prior Art may reference files that do not yet exist
- If technical design or constraints are missing, proceed but note the gap — implementation decisions may lack architectural context

## Output

**Produces:** Two things:
1. The actual code files declared in the ticket's Output section (written to the real codebase)
2. A delivery record documenting what was planned, built, and decided

**Write to:** `.gener8v/changes/[change-slug]/delivery/[capability-area-slug]-[ticket-id]-delivery.md`
**Creates directory:** `.gener8v/changes/[change-slug]/delivery/` if it does not exist
**Naming convention:** Combines the capability area slug with the lowercase ticket ID (e.g., `search-and-retrieval-ticket-001-delivery.md`)

The delivery record is the bridge between pipeline artifacts and the real codebase. Downstream skills (reviews, audits, orchestrate) read delivery records to locate implemented code.

The record is **written early and updated as the delivery progresses** — first after reconciliation (`Status: Reconciled`), again the moment the plan is approved (`Status: In Progress`, plan preserved verbatim, a `## Progress` checklist), and finally when the code is verified (`Status: Delivered`). Nothing the user approved lives only in the conversation; a compaction or a new session resumes from the record.

Delivery also appends rows to the living specification's `## @spec Coverage` table (`.gener8v/specifications/[capability-area-slug].md`) for every requirement it annotated, with root-relative code locations — that section is promised by the Specification skill and this is the skill that keeps the promise.

## Output Format

Produce a markdown document with the following structure:

```markdown
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
```

---

## Principles

### Reconcile Against Ground Truth Before Planning
A ticket's assumptions are claims to verify, not facts to trust. Before drafting the implementation plan, check every assumption the ticket depends on against the actual repository: do the schema objects it references (tables, columns, enums, constraints) exist in the schema/migrations? Do the files, scripts, and commands it invokes exist? Is every document in Prior Art / Required Reading present at the pinned version? Did predecessor tickets actually produce the outputs this ticket builds on? Resolve from the code what the code can answer — and note where the answer closes an open question the ticket left for the user (e.g., a "Decision Point" that the existing schema already settles). If a *blocking* assumption is false (a required table is missing, a referenced script does not exist, a pinned doc is absent), stop and report — set delivery status to **Blocked** with the reconciliation findings, and do not proceed to planning. The "build-on-existing-schema" premise is the most common silent failure; verify it explicitly.

### Checkpoint the Record
The delivery record is not a report written at the end; it is the ticket's working memory. Reconciliation results go in as soon as they exist, the plan goes in the moment it is approved, progress is ticked as files land. If the context is compacted or the session ends mid-implementation, the next session opens the record and continues — it never has to reconstruct a plan the user already approved, and never re-asks for approval.

### Verified, Not Inspected
An acceptance criterion is satisfied when an executed check proves it — a test, a type-check, a build, a query — and the Verification Run records the command and its exit code. Reading the code and finding it plausible is not verification. A criterion with no executed evidence is recorded as Unverified, not ticked. The same rule covers the NFRs a ticket carries: where the specification's verification method is executable (a benchmark, a load test, a lint) it runs in the Verification Run; where it is not, the NFR is Unverified with what would verify it.

### Plan Before You Build
Never start writing code without presenting the implementation plan to the user first. The plan describes which files will be created or modified, what each will contain, and how acceptance criteria will be met. User approval is the gate between planning and execution. This prevents wasted effort and ensures alignment before code is written. The approval is recorded, not just given: the record carries `**Plan approved by:** Engineer — <name>, YYYY-MM-DD`. One person may hold every role; the record still names the role, so a reader knows which hat approved the plan.

### Prior Art Is Your Context Window
Read everything the ticket's Prior Art section points to before planning. For first tickets in a chain, this means pipeline documents (specifications, constraints, technical design). For later tickets, this means the actual code files produced by predecessor tickets plus their delivery records. Do not guess what predecessor tickets produced — read the actual files.

### Output Is Your Contract
The ticket's Output section declares what files this delivery produces. Downstream tickets reference those files in their Prior Art. Deliver exactly what was promised — same file paths, same exposed interfaces. If the implementation must diverge from the declared output, document the deviation and its impact on downstream tickets.

### Acceptance Criteria Are Done
A ticket is delivered when all acceptance criteria are satisfied. Not when the code compiles. Not when it looks right. Not when most criteria are met. Each criterion must be verifiable against the delivered code, and the delivery record must show how each was satisfied.

### Decisions Are First-Class
Implementation always surfaces decisions not anticipated by the ticket or technical design. A library choice, an error handling strategy, a data structure selection — these are implementation-time decisions that affect downstream work. Record every non-trivial decision with context and rationale using DEL-XXX IDs. These are the implementation-time equivalent of Architecture Decisions (AD-XXX).

### Deviations Are Expected, Not Failures
Real implementation often diverges from the plan. A dependency behaves differently than expected, an approach proves impractical, a better solution emerges during coding. The delivery record documents what changed and why. Deviations are information for downstream tickets and reviews, not defects.

### Annotate for Traceability
Every function, class, method, or handler that implements a requirement gets an `@spec` annotation comment linking it to the requirement IDs it satisfies. Use the language's native comment syntax:

```python
# @spec SR-REQ-001, SR-REQ-002
def process_query(text):
```

```typescript
// @spec SR-REQ-001, SR-REQ-002
function processQuery(text: string) {
```

Place annotations on the line immediately above the declaration. One annotation per code location, listing all requirement IDs implemented there. A requirement may appear in multiple annotations if it is implemented across multiple locations. These annotations make traceability greppable (`grep -r "@spec" src/`) and survive beyond the review phase — any developer can trace code back to requirements without consulting pipeline artifacts.

### Predecessors' Reviews Are Prior Art Too
A finding a review deferred "to the next ticket", and a risk it accepted on a file this ticket will edit, are part of this ticket's context. Read the predecessor reviews, list carried findings in the reconciliation table, and address or consciously carry each one.

### Stay in Your Lane
Only implement what this ticket specifies. Do not refactor adjacent code, add unrequested features, or "fix" things you notice in predecessor output. If something needs attention, note it in the delivery record — it belongs in a separate ticket. Scope discipline prevents one ticket from silently changing the foundation that other tickets depend on.

## Process

1. **Locate the Ticket**: Resolve the change — the one named in the argument, else the single active change, else ask. Open `.gener8v/changes/<change-slug>/tickets/<capability-area-slug>/TICKET-XXX.md` — the whole ticket is that one file; there is nothing to extract. Confirm that its `**Change:**`, `**Capability Area:**` and `**Specification:**` header lines match the target. Read the sibling `backlog.md` for the dependency chain and suggested ordering. Read the change brief for its Status and Priority Cut; a delivery started from a `Draft` brief proceeds, and the record's `**Change:**` line says so (Audit raises a Warning, never a block).

2. **Check Prerequisites**: Verify that all tickets listed in the Depends On field — sibling `TICKET-XXX.md` files in the same directory — have delivery records in `.gener8v/changes/<change-slug>/delivery/`. If any are missing, warn the user that Prior Art references may point to files that do not exist.

3. **Read Prior Art**: Follow every item in the ticket's Prior Art section. Read pipeline documents (specifications, constraints, technical design). Read predecessor delivery records and the actual code files they produced. Read system context if available.

4. **Read Technical Design**: If a technical design exists for this capability area, read it for architecture decisions (AD-XXX) that affect this ticket's implementation.

5. **Reconcile Ticket Assumptions Against Ground Truth**: Before planning, verify every assumption the ticket depends on against the actual repository. Read the schema/migrations to confirm referenced tables, columns, enums, and constraints exist; confirm that scripts and commands the ticket invokes are present; confirm every Prior Art / Required Reading document exists at the pinned version; confirm predecessor tickets produced the outputs declared in their Output sections; list findings the predecessor reviews deferred to this ticket or risks they accepted on files this ticket touches. Build the Pre-Flight Reconciliation table. Where the code answers a question the ticket left open (e.g., a Decision Point the existing schema already settles), record it as resolved rather than escalating it. **Write the delivery record now** — Ticket Reference and Pre-Flight Reconciliation, `Status: Reconciled` on a Go verdict. **Gate:** if any *blocking* assumption is false, set status to **Blocked**, report to the user, and stop — do not proceed to planning. Only a **Go** verdict continues.

6. **Draft Implementation Plan**: Produce a plan that covers:
   - Every file to be created or modified (aligned with the ticket's Output section)
   - What each file will contain (modules, functions, classes, configuration)
   - How each acceptance criterion will be satisfied
   - Any decisions or trade-offs identified during planning
   - Any constraints from the ticket that shape the implementation
   - The repository the code lands in, from `context.md`'s `## Repositories` table (`.` when there is one); a ticket that touches two repositories is two tickets unless the change is atomic, in which case the plan names both and the record will list both commits

7. **Present Plan to User**: Show the implementation plan and wait for explicit approval. The user may:
   - **Approve**: Proceed to implementation
   - **Modify**: Adjust the plan based on user feedback, then re-present
   - **Reject**: Do not proceed; discuss alternative approaches

   On approval, **append the plan verbatim to the delivery record**, record `**Plan approved by:** Engineer — <name>, YYYY-MM-DD`, add the `## Progress` checklist (one line per planned file), and set `Status: In Progress`. From this point the record — not the conversation — is the authority for what is being built.

8. **Implement**: Write the actual code files as described in the approved plan. Follow the technical design's architecture decisions. Respect constraints referenced in the ticket (PRD-level and area-level). Produce the files declared in the ticket's Output section — including the test files the ticket lists. Tick each file in `## Progress` as it lands.

9. **Add `@spec` Annotations**: For each function, class, method, or handler that implements a requirement from the ticket's Requirements Covered list, add an `@spec` annotation comment on the line immediately above the declaration. List all requirement IDs that the code location satisfies. If a requirement is implemented across multiple locations, annotate each one.

10. **Run Verification**: Execute the named repository's checks — tests, type-check, lint, build — using the Verify commands from its row in `context.md`'s `## Repositories` table or the repository's own scripts (`package.json` scripts, `Makefile`, `pyproject.toml`, CI configuration). Run every NFR check the ticket carries that is executable (a benchmark against a latency target, a log-format test, an accessibility lint) using the method the specification names. Record every command with its exit code in `## Verification Run`. A failing check is fixed or the delivery is `Partial`; it is never omitted. Set `**Verification:**` accordingly.

11. **Verify Acceptance Criteria**: Walk through each acceptance criterion from the ticket, including the verification method listed for each NFR it carries. Tick it only when an executed check from the Verification Run proves it, and cite that check. A criterion the code implements but no executed check covers is recorded as Unverified; a non-executable NFR is Unverified with what would verify it.

12. **Record Decisions**: Document any implementation decisions made during coding as DEL-XXX entries with context, decision, rationale, and ticket impact.

13. **Record Deviations**: Compare the delivered implementation against the approved plan. Document anything that changed and why. If the Output files differ from what the ticket declared, note the impact on downstream tickets.

14. **Finalize the Delivery Record**: Fill Delivery Summary, Acceptance Criteria Verification, Decisions, Deviations and `@spec` Annotations; set `Status: Delivered` (or `Partial`). Then append one row per annotated requirement to the living specification's `## @spec Coverage` table (create the section if it is absent), with root-relative code locations, so the specification shows where each requirement lives in code.

15. **Commit Together**: Commit in the repository named in the plan — the delivered code and the delivery record in the same commit (a branch per ticket is the recommended boundary; the record's file name is the natural commit subject). An atomic ticket spanning two repositories commits in each and the record lists both commits. Do not push or open a pull request unless the user asks. The three reviews are the pipeline's review of the change; a repository's own PR review, if any, sits on top of them.

## Example

A full delivery of `support-search/search-and-retrieval/TICKET-001` (query input, SR-REQ-001..003): the ticket as read from its own file, the plan presented for approval with its repository and approval line, and the finished record — reconciliation, verification run, criteria verification, a DEL decision and `@spec` annotations.

It is at `skills/delivery/references/example.md`.
Read it before producing your first artifact of this kind.

---

## Integration with Other Skills

**Upstream:**
- **Planning Skill**: Opens the change whose brief (`changes/<change-slug>/change.md`) scopes the ticket — its Priority Cut and approval status
- **Ticket Breakdown Skill**: Provides the ticket file that defines what to implement — summary, priority, value, requirements (REQ and NFR), Prior Art, acceptance criteria, output, constraints, and dependencies — and the area's `backlog.md` for ordering
- **Technical Design Skill**: Provides architecture decisions (AD-XXX) that guide implementation choices
- **Specification Skill**: Provides requirement detail referenced in Prior Art
- **Constraints Skill**: Provides constraints referenced in the ticket
- **Dependencies Skill**: Provides sequencing information consumed via ticket dependencies

**Downstream:**
- **Code Review Skill**: Reviews the delivered code against pipeline artifacts (acceptance criteria, requirements, constraints, architecture decisions)
- **Quality Review Skill**: Reviews the delivered code for engineering quality
- **Security Review Skill**: Reviews the delivered code for security vulnerabilities
- **Delivery Skill** (subsequent runs): Later tickets reference this delivery's output in their Prior Art and read this ticket's reviews for carried findings
- **Orchestrate / hooks**: read `Status`, `Verification` and `Reviews Deferred` from the record; a ticket is `done` only when Delivered, verified, and approved-or-deferred by every review

## Revisions

- A delivery record is written progressively during the delivery (Reconciled → In Progress → Delivered) and is append-only afterwards: reviews add `## Post-Review Amendments` entries; nothing above that section is rewritten
- If the ticket's requirements change after delivery, create a new ticket for the changes rather than modifying the delivery record
- If a review identifies issues, the fixes are applied in that review's resolution phase and recorded under `## Post-Review Amendments` (with re-verification), or a follow-up ticket is created
- Delivery records in `.gener8v/changes/<change-slug>/delivery/` are permanent artifacts for traceability

## Notes

- This skill is unique in the pipeline: it writes to the real codebase, not just `.gener8v/`
- The delivery record is the bridge between pipeline artifacts (all in `.gener8v/`) and actual code files
- One delivery per ticket — do not batch multiple tickets into a single delivery
- If a ticket is sized Large, consider whether it should have been split during Ticket Breakdown rather than delivering a monolithic implementation
- The `{ext}` placeholder in ticket Output sections should be resolved during implementation planning based on the system context and technology stack
- When system context (`.gener8v/context.md`) is available, use it to inform language, framework, and convention choices; its `## Repositories` table is where the plan's repository and the Verification Run's commands come from — in a workspace of several repositories every path in the record stays root-relative (`api/src/search/query.ts`)
- Delivery status values: **Reconciled** (pre-flight Go, plan not yet approved), **In Progress** (plan approved, code being written), **Delivered** (all acceptance criteria verified), **Partial** (some criteria met, others blocked), **Blocked** (cannot proceed — including a failed Pre-Flight Reconciliation: a missing table/column/script or an absent pinned document means the ticket is blocked before planning, with the reconciliation findings naming what must exist first)
- A project whose `tickets/`, `delivery/` and `reviews/*-review.md` still sit at the top level of `.gener8v/` is the legacy pseudo-change `initial`; read from there if that is where the ticket is, but never write a new record to the legacy location — Orchestrate recommends the one-time migration
- With the plugin installed, a `PreToolUse` hook reminds the model when source is edited while no delivery record is `In Progress`, and the `SessionStart` hook points a resumed or compacted session at the in-flight record
