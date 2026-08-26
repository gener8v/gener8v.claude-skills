---
name: audit
description: "Audit pipeline artifacts for gaps, inconsistencies, missing coverage and staleness — a single document, cross-stage traceability across .gener8v/, or reconciliation of a ticket or externally-authored plan against the real codebase (Go / Blocked) — then resolve findings interactively. Use before committing to a stage, at milestones, or before delivering a plan whose assumptions are unverified."
argument-hint: "[pipeline | <stage> <slug> | reconcile <ticket or plan>]"
---
# Audit Skill

## Purpose

Review pipeline artifacts for gaps, inconsistencies, missing coverage, and unresolved ambiguity — then work interactively with the user to resolve them. This skill acts as quality control across the entire pipeline. It can audit a single document in isolation or trace completeness across multiple stages. The goal is to catch problems before they compound downstream.

## When to Use

Use this skill when:
- A pipeline stage has been completed and needs review before proceeding
- Multiple stages have been completed and cross-stage consistency needs verification
- The user wants a second pass on a PRD, specification, or ticket breakdown before committing to it
- Open questions have accumulated across documents and need triage
- The team suspects something was missed but isn't sure where
- A ticket (or an externally-authored plan) is about to be delivered and its assumptions about the codebase need verification against ground truth *before* any code is written

## Input

**Source:** One or more pipeline artifacts from `.gener8v/`
**Read from:**
- Pipeline State: `.gener8v/pipeline-state.yaml` (for quick status overview before deep audit)
- PRD: `.gener8v/prd.md`
- System Context: `.gener8v/context.md`
- Specifications: `.gener8v/specifications/*.md`
- Constraints: `.gener8v/constraints/*.md`
- Dependency Map: `.gener8v/dependencies/dependency-map.md`
- Technical Design: `.gener8v/technical-design/*.md`
- Change briefs: `.gener8v/changes/*/change.md`
- Tickets: `.gener8v/changes/*/tickets/*/TICKET-*.md` — one ticket, one file — plus each directory's `backlog.md` (overview, dependency chain, suggested ordering)
- Delivery Records: `.gener8v/changes/*/delivery/*.md`
- Code Reviews: `.gener8v/changes/*/reviews/*-code-review.md`
- Quality Reviews: `.gener8v/changes/*/reviews/*-quality-review.md`
- Security Reviews: `.gener8v/changes/*/reviews/*-security-review.md`
- Legacy layout: a project whose `tickets/`, `delivery/` and `reviews/*-review.md` still sit at the top level of `.gener8v/` is read as the pseudo-change `initial` — audit it as one change and recommend the one-time migration from `CONVENTIONS.md` §2. Legacy ticket shape: a per-area ticket *file* (`tickets/<area-slug>.md` holding `### TICKET-NNN:` sections) is still read — audit it as the breakdown it is and recommend `gener8v-state.py split-tickets`
- Assessments: `.gener8v/reviews/*-owasp-top10-assessment.md`, `*-owasp-llm-top10-assessment.md`, `*-architecture-assessment.md`
- Flow maps: `.gener8v/flows/*.md`; Sweeps: `.gener8v/sweeps/*-sweep.md`; Brownfield checkpoints: `.gener8v/brownfield/*.md`
- Prior audits: `.gener8v/audits/*.md` (to carry deferred findings forward rather than re-raise them)
- Conventions: `.gener8v/CONVENTIONS.md` — the vocabularies and rules the checks in `references/checks.md` enforce
- `scripts/gener8v-state.py lint` output (plugin install) — prefix collisions, uncovered requirements and NFRs, missing ticket sections, missing `@spec` annotations, dangling references
- `scripts/gener8v-state.py metrics` output (plugin install) — rework rate, verification pass rate, deferred reviews, approvals pending; cite these as evidence for Warnings, never author them
- Delivered code files (for `@spec` annotation verification)

**Expects:** At least one artifact to exist. The skill adapts its checks based on what's available — auditing a PRD alone is valid, but auditing tickets without a specification is less useful and the skill will flag this.

## Output

**Produces:** An audit report with findings, plus interactive resolution of issues with the user
**Write to:** `.gener8v/audits/[scope]-audit-YYYY-MM-DD.md`
**Creates directory:** `.gener8v/audits/` if it does not exist
**Naming convention:**
- Single-document audit: `[stage]-[slug]-audit-YYYY-MM-DD.md` (e.g., `specification-search-and-retrieval-audit-2026-08-26.md`)
- Cross-pipeline audit: `pipeline-audit-YYYY-MM-DD.md`

Audits are never overwritten: each run writes a new dated file and its Summary states which earlier findings (by `FIND-XXX` and file) were still open, now resolved, or newly raised.

After interactive resolution, the skill updates the source artifacts directly. The audit report captures what was found and what was changed.

## Audit Modes

### Single-Document Audit

Review one artifact in isolation for internal quality.

**Trigger:** User points to a specific file or stage
**Scope:** One document only

### Cross-Stage Audit

Trace consistency and coverage across multiple pipeline stages.

**Trigger:** User asks to audit the pipeline, or multiple stages have been completed
**Scope:** All available artifacts in `.gener8v/`, including every change under `changes/`

### Reconciliation Audit (artifact vs. reality)

Verify that an artifact's claims about the codebase are actually true — not whether the artifacts agree with *each other* (that is Cross-Stage), but whether they agree with the *repository*. This catches the failure the other modes can't: a perfectly self-consistent plan built on a false premise ("builds on existing schema," "table X exists," "script Y runs the checks").

**Trigger:** A ticket or externally-authored plan is about to be delivered; or the user asks whether a plan is actually executable against the current code
**Scope:** One or more tickets or plans + the live codebase (schema, migrations, scripts, source files, referenced documents)
**Output verdict:** **Go** (assumptions hold) or **Blocked** (named assumptions are false, with what must exist first)

## Output Format

Produce a markdown document with the following structure:

```markdown
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
```

---

## Checks

The full check lists live in `references/checks.md` — open it at Process step 3 and apply every group that matches the artifacts in scope. The groups:

**Single-document** (one group per artifact kind)
- **PRD** — structure, directional goals, 3–7 areas, no technology leakage, Status/Approved-by
- **Change brief** — header fields and Slug, the seven sections, Affected Capability Areas table, non-empty Must cut, declared Status vs derived
- **Specification** — atomic and testable requirements, unique prefix, NFR section with measurable targets and a verification method, change and amended tags, Status/Approved-by, `@spec Coverage`
- **Constraints** — rationale and impact, categories, interactions, no requirements (or NFR targets) masquerading as constraints, Architect approval
- **Dependencies** — direction/type/nature, no cycles, graph matches prose, critical path, shared resources
- **Technical Design** — AD-XXX completeness, requirement and NFR citations, constraint compliance, repository named per component in a workspace, Architect approval
- **Tickets** — one `TICKET-NNN.md` per ticket with the three header lines, `backlog.md` present, no ticket living only as a heading in another file; scope matches the brief, Priority and Value present, Prior Art/Output root-relative, Known Hazards, acceptance criteria and NFR verification, `backlog.md` Backlog Summary Priority column, ordering respects priority
- **Delivery Record** — acceptance criteria, Files Produced exist and are root-relative, plan approved by Engineer, repository and verify commands, `@spec`, Status/Verification vocabularies, Pre-Flight, Verification Run with NFR checks, Post-Review Amendments
- **Code Review** — acceptance and requirement (incl. NFR) coverage, `@spec` coverage, finding traceability, verdict vocabulary, deferrals matched by Known Hazards
- **Quality Review** — all five categories rated, Test Coverage cites commands, verdict vocabulary
- **Security Review** — four categories, attack scenarios, OWASP 2025, CC-XXX violations Critical, Risk accepted by Security, Accepted Risks counted
- **Assessments** — every category or thesis assessed, qualified references, tickets named for code changes
- **Flow Map** — validator exits 0, edges and nodes complete, Unknowns honest, prose matches diagram
- **Defect Sweep** — Scope, proof per DS-XXX, Swept and clean, fix-now findings mapped to tickets

**Cross-stage**
- **Coverage** — area → spec → constraints → design; brief areas → ticket breakdowns
- **Change Traceability** — every change has a brief, brief Requirements column matches the spec's change tags, ticket scope follows the brief, qualified references carry the change segment, legacy layout flagged
- **Approvals** — Warning (never a block) when tickets came from a Draft specification or delivery started under a Draft change brief; approval lines name a role and date
- **Traceability** — every REQ and NFR in a ticket, unique prefixes, constraint/dependency/AD references exist, Prior Art points at declared Output
- **Delivery Traceability** — records per ticket under the same change, Files Produced vs Output, predecessors delivered first, qualified DEL/CR/QR/SEC references, `@spec` in code
- **Review Traceability** — three reviews or an explicit deferral, criteria match, CC-XXX references exist, verdicts agree with `pipeline-state.yaml`, deferred findings become Known Hazards
- **Root-Relative Paths** — every code path in every artifact is workspace-root-relative and, in a workspace, starts with a repository from `context.md`
- **Consistency** — open questions not duplicated, resolved upstream, no orphans (standalone artifacts are not orphans)
- **Staleness** — downstream documents reference current upstream IDs, IDs append-only, amended requirements flagged for re-review

**Ground-truth reconciliation** (Reconciliation Audit)
- **Schema & Data Model** · **Files, Scripts & Commands** · **Referenced Documents** · **Decision Closure** — artifacts vs the actual codebase; each failure is at least a Gap, Critical if it blocks delivery

---

## Severity Levels

- **Critical**: Blocks downstream work or produces incorrect output. Must be resolved before proceeding. Examples: missing capability area with no specification, circular dependency, requirement with no ticket coverage.
- **Gap**: Something is missing that should be present but doesn't block immediate progress. Should be resolved before implementation. Examples: empty edge cases table, missing constraints analysis for a specification, open question that affects ticket scope.
- **Warning**: Potential issue that may cause problems later. Worth reviewing but can proceed. Examples: subjective language in a requirement, a Large ticket that might benefit from splitting, a soft dependency not reflected in sequencing.
- **Suggestion**: Improvement opportunity. Non-blocking. Examples: reworded requirement for clarity, additional user scenario, constraint that could be more specific.

## Process

1. **Determine Scope**: Identify which artifacts exist in `.gener8v/` and whether this is a single-document, cross-stage, or reconciliation audit. A reconciliation audit also needs access to the live codebase, not just `.gener8v/`.

2. **Read Artifacts**: Load all in-scope documents and `CONVENTIONS.md`. Note which expected artifacts are missing. Read prior audits so deferred findings are carried forward, not re-raised. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py" lint` when available and treat each line as a candidate finding; run `… metrics` for a cross-stage audit and keep the numbers as evidence for Warnings. For a reconciliation audit, also read the codebase ground truth the artifacts reference — schema/migrations, scripts, and the cited documents.

3. **Run Checks**: Open `references/checks.md` and apply every group that matches the artifacts in scope. For cross-stage audits, run single-document checks first, then cross-stage checks — including the Change Traceability and Approvals groups for every change under `changes/`. For reconciliation audits, run the Ground-Truth Reconciliation checks against the codebase and produce a Go / Blocked verdict.

4. **Draft Findings**: For each failed check, create a finding with severity, location, description, impact, and recommendation.

5. **Present to User**: Share the findings with the user, starting with Critical items. For each finding:
   - Explain the issue clearly
   - Propose a specific fix
   - Ask the user to approve, modify, or defer

6. **Resolve Interactively**: Work through findings with the user:
   - **Approve**: Apply the recommended change to the source artifact
   - **Modify**: User provides direction; apply their preferred fix
   - **Defer**: Mark the finding as deferred with a note on why
   - **Dismiss**: User determines this is not an issue; mark as dismissed with rationale

7. **Update Source Artifacts**: Apply approved changes directly to the `.gener8v/` files. Do not create separate "fixed" copies.

8. **Write Audit Report**: Write the report as soon as findings are drafted (step 4), every finding `Open`, and update each finding's Status and Resolution Log row as it is decided in steps 5–7 — a session that ends mid-audit loses nothing. The dated file name means the previous audit's Resolution Log is never overwritten.

9. **Summarize**: Present a final summary — what was found, what was resolved, what remains open.

## Example

A cross-pipeline audit of the Support Documentation Search System with one change (`support-search`): a missing specification, a subjective requirement, a Draft-specification Warning, the per-change coverage view and the Resolution Log. See `references/example.md`. Read it before producing your first artifact of this kind.

---

## Integration with Other Skills

**Upstream (audits output from):**
- **Planning Skill**: Audits PRD for structure, completeness, and technical leakage; audits change briefs for format, priority cut, and requirement deltas that match the specification's change tags
- **Specification Skill**: Audits specifications for atomicity, testability, namespacing, NFR verifiability, change tags, and traceability
- **Constraints Skill**: Audits constraints for categorization, rationale, and impact mapping
- **Dependencies Skill**: Audits dependency maps for completeness, circularity, and sequencing validity
- **Technical Design Skill**: Audits architecture decisions for completeness, constraint compliance, and requirement traceability
- **Ticket Breakdown Skill**: Audits tickets for coverage of the change brief's scope, Priority and Value, Prior Art/Output completeness, and acceptance criteria quality
- **Delivery Skill**: Audits delivery records for acceptance criteria verification, file existence, plan approval, decision documentation, and deviation tracking
- **Code Review Skill**: Audits code reviews for traceability completeness, finding quality, and verdict consistency
- **Quality Review Skill**: Audits quality reviews for assessment completeness and finding quality
- **Security Review Skill**: Audits security reviews for OWASP compliance, attack scenario presence, risk acceptance documentation, and compliance constraint coverage

**Downstream:**
- This skill modifies source artifacts directly during interactive resolution
- Audit reports are reference documents; no other skill consumes them as input

## Principles

### Write First, Resolve Second
The report exists before the first finding is discussed. Decisions the user makes are written into the file as they are made, not remembered until the end.

### Interactive, Not Automated
This skill does not silently fix problems. Every finding is presented to the user with a recommendation. The user decides: approve, modify, defer, or dismiss. The skill is a partner in quality, not an autonomous corrector.

### Start with Critical, End with Suggestions
Present findings in severity order. Critical issues must be addressed before the pipeline can proceed reliably. Suggestions are opportunities, not obligations.

### Trace Across Stages
The highest-value checks are cross-stage: does every requirement have a ticket? Does every ticket's Prior Art point to real output from a real predecessor? Single-document quality matters, but pipeline consistency is where gaps hide.

### Fix in Place
When the user approves a fix, update the source artifact. Do not create parallel "fixed" or "v2" copies. The pipeline should always have one source of truth per artifact.

### Audit Reports Are Records, Not Artifacts
The audit report documents what was found and decided. It is not consumed by downstream skills. It exists for the user's reference and for traceability of decisions.

## Revisions

- Audit reports capture a point-in-time assessment — they do not auto-update when source artifacts change
- After significant pipeline changes, re-run the audit to get a current assessment
- Previous audit reports remain in `.gener8v/audits/` for reference; file names carry the date so nothing is ever overwritten
- The Orchestrate skill tracks completeness (what exists); the Audit skill tracks quality (is it good) — they are complementary

## Notes

- This skill can be run at any point in the pipeline — it adapts to whatever artifacts exist
- Running a cross-stage audit with only a PRD produces limited findings (mostly "missing specification" gaps); this is expected and useful for planning next steps
- The skill does not generate missing artifacts — it identifies what's missing and recommends which skill to run
- Multiple audit reports coexist in `.gener8v/audits/`, dated in the file name; the newest states which earlier findings are still open
- If the user has resolved open questions during an audit, update the source document's Open Questions section to reflect the resolution
