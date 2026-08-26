---
name: orchestrate
description: "Report where the gener8v pipeline stands — coverage matrix per capability area, ticket-level delivery and review status with verdicts, current stage — regenerate .gener8v/pipeline-state.yaml, and recommend the exact next skills and targets. Use at session start, after any pipeline skill, or when asked 'what's next' or 'where are we'."
---
# Orchestrate Skill

## Purpose

Assess the current state of the pipeline and guide the user to the next step. Everything that can be decided by looking at which files exist and what their status lines say is decided by `scripts/gener8v-state.py`, deterministically; this skill adds the judgement a script cannot — scale, correctness risk, what to defer, when a sweep or an assessment is due — and presents the result. It is the entry point for anyone resuming work or unsure where the pipeline stands.

## When to Use

Use this skill when:
- Starting a new session (the plugin's SessionStart hook injects the summary automatically; run Orchestrate for the full matrix and recommendations)
- A skill has just completed and the next step is unclear
- Resuming work after a break or a context compaction
- Multiple capability areas exist and it's unclear which have been fully processed
- The user asks "what's next?" or "where are we?"

## Input

**Source:** All artifacts in `.gener8v/`
**Read from:**
- `.gener8v/pipeline-state.yaml` (regenerated first — see Process step 1)
- `.gener8v/prd.md`, `.gener8v/context.md`, `.gener8v/CONVENTIONS.md`
- `.gener8v/changes/<change-slug>/change.md` for each change the state file lists (declared status, Priority Cut, Open Questions)
- The metrics the script derives (`gener8v-state.py metrics`; it also reads `.gener8v/runs.jsonl`, the run log the hooks append — no skill writes it)
- Any artifact the judgement layer needs to open (a delivery record's Verification Run, a sweep's Verdict, an assessment's Coverage Summary)

**Expects:** Nothing. Orchestrate adapts to whatever exists — including an empty directory, a `.gener8v/` that holds only standalone artifacts, or a project that has never been set up.

## Output

**Produces:** Two things:
1. A pipeline status assessment presented to the user, with specific next-step recommendations
2. A fresh `.gener8v/pipeline-state.yaml`

**Write to:** `.gener8v/pipeline-state.yaml` — by running the generator. Under a copied install (no `${CLAUDE_PLUGIN_ROOT}`), write it by hand in the Pipeline State Format below, following the same rules the script implements.
**Delivery:** Status assessment is presented directly to the user in conversation. The YAML state file is written silently.

## Process

1. **Regenerate State**: Run the deterministic generator and read its summary:
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py" state
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py" summary
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py" lint
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py" metrics
   ```
   If the script is unavailable, perform the same scan by hand — inventory every file below, parse the `**Status:**` line of each artifact, the `**Result:**` line of each review and the `**Priority:**` line of each ticket, derive ticket and change status from the vocabulary in `CONVENTIONS.md` §5, and write the YAML yourself:
   - PRD `prd.md`; System Context `context.md`; Brownfield checkpoints `brownfield/*.md`
   - Living artifacts: Specifications (count `REQ` and `NFR` IDs), Constraints (`constraints/prd.md` and per-area), Dependency map, Technical design (per-area and `system-design.md`) — read each **Status** line; a `Draft` PRD, specification, constraints file (PRD-level or per-area), dependency map or technical design (per-area or system) counts towards `approvals_pending`, together with unapproved change briefs — exactly what the script counts
   - Change briefs `changes/<change-slug>/change.md` — read **Status** and the Affected Capability Areas table; a Requirements cell still saying `(pending specification)` means Specification has not run for that area in this change
   - Tickets `changes/<change-slug>/tickets/<area-slug>/TICKET-NNN.md` (one ticket, one file; `backlog.md` alongside) — read each ticket's **Priority** and **Depends On**; a ticket carrying `**Status:** Withdrawn` at the top is not counted
   - Delivery records `changes/<change-slug>/delivery/<area-slug>-ticket-NNN-delivery.md` — read **Status** and **Verification**, and any **Reviews Deferred** line
   - Reviews `changes/<change-slug>/reviews/<area-slug>-ticket-NNN-{code,quality,security}-review.md` — read **Result**
   - Legacy layout: top-level `tickets/`, `delivery/` and `reviews/*-review.md` are read as the pseudo-change `initial`; a legacy per-area ticket *file* (`tickets/<area-slug>.md` holding `### TICKET-NNN:` sections) is read with a warning that names `gener8v-state.py split-tickets --remove`
   - Assessments `reviews/*-owasp-top10-assessment.md`, `*-owasp-llm-top10-assessment.md`, `*-architecture-assessment.md`
   - Flow maps `flows/*.md`; Sweeps `sweeps/*-sweep.md`; Audits `audits/*.md`

2. **Read the State**: Open `.gener8v/pipeline-state.yaml`. The living coverage per capability area (with the changes touching each), the `changes:` map (each change's declared and working status, areas, pending specification/breakdown, ticket statuses, `done` flags and progress), `active_changes`, `approvals_pending`, stage, warnings and the deterministic next steps are already there. Do not recompute them. Keep the `metrics` output alongside; it is derived on demand and not written to the state file.

3. **Detect the Situation** — the cases a file scan cannot label:
   - **Not started, has source code** → recommend Setup then Brownfield (not Planning). Decide by looking at the working tree, not at `.gener8v/`.
   - **Not started, no source** → Setup then Planning.
   - **Standalone artifacts only** (`sweeps/`, `flows/`, assessments, no `prd.md`) → say so, list them, and recommend Setup + the right entry point; these artifacts are kept.
   - **Brownfield-onboarded** (specifications carry populated `## @spec Coverage` sections and no change has tickets) → the code already exists; the next step is Planning to open the first change, then Constraints / Dependencies / Technical Design *for that new work* — never "deliver" what is already implemented.
   - **Brownfield mid-run** (`brownfield/*.md` exists, specs incomplete, or specs exist without `prd.md`) → resume Brownfield at the first phase whose output is missing.
   - **Specified, no change opened** (specifications exist, `changes:` is empty, not brownfield-onboarded) → Planning opens a change; Ticket Breakdown needs a change brief to cut from.
   - **Legacy layout** (`cross_cutting.legacy_layout: true`; the pseudo-change `initial` appears in `changes:`) → recommend the one-time migration, run inside `.gener8v/`: `git mv tickets delivery changes/initial/ && mkdir -p changes/initial/reviews && git mv reviews/*-review.md changes/initial/reviews/`. Do it before any new delivery; no skill writes to the legacy locations.
   - **Legacy ticket file** (a warning says `tickets/<area-slug>.md holds several tickets in one file`; `areas_detail.<area-slug>.legacy_file` is set) → recommend `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gener8v-state.py" split-tickets --remove`, which gives each ticket its own `TICKET-NNN.md` and writes `backlog.md`. Do it before delivering from that area; no skill writes the per-area file any more.
   - **Several changes active** (`active_changes` lists more than one) → every per-ticket recommendation names its change (`… in <change-slug>` for Delivery and the reviews, `… for <change-slug>` for Specification and Ticket Breakdown), because those skills will ask otherwise. With exactly one active change those skills default to it and the suffix may be dropped.
   - **Declared status disagrees** (a warning such as "declared Complete but n ticket(s) are not done" or "still Draft but has tickets") → the fix is on the brief: the Product Owner approves it, or its `**Status:**` line is corrected. Do not edit it silently.
   - **In-flight delivery** (a delivery record `In Progress` or `Reconciled`) → resuming that ticket comes before anything else.
   - **Changes required** (any ticket `changes_required`) → resolving those review findings comes before new deliveries.

4. **Apply Scale and Risk**: Count capability areas and read the PRD for correctness-risk signals (data integrity, tenant isolation, money, credentials, compliance):
   - **1–2 areas**: the Light path — Constraints, Dependencies and Technical Design are optional; say which to skip and why. A review may be deferred with a reason recorded in the delivery record.
   - **3–5 areas**: the full pipeline; recommend parallel specification passes; note where constraints or technical design can be batched.
   - **6+ areas**: recommend grouping related areas or splitting into sub-pipelines; track at ticket level.
   - Regardless of count, an area that carries a correctness-critical invariant gets the deep treatment on that area (full specification, technical design, all three reviews) — say which area and why.

5. **Recommend the Periodic and Standalone Work** when its trigger is met:
   - **Defect Sweep** when three or more deliveries have landed in one capability area since its last sweep, or before a launch over the surface the launch exposes
   - **OWASP Top 10 Review** after the first delivery that touches authentication, configuration or external input; **OWASP LLM Top 10 Review** when `context.md` names an LLM client, RAG or agent surface
   - **Architecture Review** at milestone boundaries or when technical-design decisions have accumulated without being tested against shipped code
   - **Security re-check** when the last security review's dependency audit is older than the project's release cadence
   - **Audit** at milestones — not only at the end

6. **Read the Metrics**: `gener8v-state.py metrics` derives ticket counts by priority, verdict distribution and finding counts per review kind, rework rate (tickets amended after review ÷ tickets reviewed), verification pass rate, deferred reviews, sweep findings, approvals pending, lead time per ticket (from git, when history exists) and session count (from `runs.jsonl`). Nothing is authored; the numbers are evidence for Recommendations. Patterns worth naming: a rework rate around one in three or higher ("3 of 5 reviewed tickets needed rework — consider Technical Design before the next breakdown"); `not run` verification on delivered tickets (deliveries are being called Delivered without their checks); `no_priority` above zero (those tickets go back to Ticket Breakdown); a median lead time that keeps growing inside one change (the tickets are too large); many deferred reviews on an area that carries a correctness-critical invariant.

7. **Order the Next Steps**: Start from the script's `next_steps` (it already puts in-flight work, `changes_required` and missing reviews first, then ready tickets Must → Should → Could, then each change's pending specification and breakdown), then apply steps 3–6: remove steps the scale decision skips (say "skipped: <reason>" rather than silently dropping them), add the periodic work whose trigger is met, and mark what can run in parallel. Per-ticket targets carry their change (`search-and-retrieval TICKET-003 in support-search`); keep the suffix whenever more than one change is active.

8. **Present Status**: Show the living coverage matrix, the changes table, stage, approvals pending, warnings from the script (orphaned specs, prefix collisions, declared-status disagreements, legacy layout, lint errors), the metrics block, and the ordered recommendations.

## Status Format

Present the status to the user in this structure:

```markdown
## Pipeline Status: [PRD Title]

**Stage:** [stage] · **Capability Areas:** [n] · **Changes:** [n] (active: [slugs, or none]) · **Approvals pending:** [n] · **System Context:** [Available / Not provided]
**Situation:** [one line from Process step 3, if any applies]

### Coverage (living)

| Capability Area | Spec | REQ / NFR | Constraints | Tech Design | Changes |
|----------------|------|-----------|-------------|-------------|---------|
| [Area name]    | ✓ Approved / ✓ Draft / ✗ | [n] / [n] | ✓/✗ | ✓/✗ | [change slugs touching it, or —] |

**Cross-cutting:** dependency map ✓/✗ · PRD constraints ✓/✗ · system design ✓/✗ · flows [n] · sweeps [n] · assessments [n] · audits [n]

### Changes

| Change | Declared | Working | Areas | Tickets | Delivered | Done | CR | QR | SEC |
|--------|----------|---------|-------|---------|-----------|------|----|----|-----|
| [slug] | [Draft / Approved / In Delivery / Complete / Abandoned] | [planned / ready / in_delivery / complete / abandoned] | [n] ([n] pending spec, [n] pending breakdown) | [n] | [n/total] | [n/total] | [n/total] | [n/total] | [n/total] |

*Delivered/Done/CR/QR/SEC count tickets. CR/QR/SEC count reviews with an Approved-variant verdict or an explicit deferral; a review that came back Changes Required is shown as `!`. A legacy top-level layout appears as the change `initial`.*

### Attention

- [Tickets in changes_required, in_progress, blocked_delivery — qualified as `<change-slug>/<area-slug>/TICKET-NNN`; declared-status disagreements; approvals pending, by artifact and role; lint errors; warnings]

### Next Steps

1. **[Skill]** on [target] — [why this is next]
2. **[Skill]** on [target] — [can run in parallel with step 1]

### Skipped for this scale

- [Skill] — [why it is not needed here]

### Metrics

tickets [done]/[total] (Must [n] · Should [n] · Could [n] · no priority [n]) · verdicts code [approved/notes/changes] · quality [a/n/c] · security [a/n/c] · findings [n] · rework [amended]/[reviewed] · verification passed [n] / failed [n] / not run [n] · reviews deferred [n] · sweeps [n] ([n] findings) · lead time median [d] days ([n] samples) · sessions [n]

### Recommendations

- [Scale, risk, periodic work, pipeline health — cite the metric or warning behind each]
```

## Pipeline State Format

`scripts/gener8v-state.py` writes `.gener8v/pipeline-state.yaml` in this shape (schema version 4). When writing it by hand, produce the same shape. The example is the state of the Support Documentation Search System with its first change, `support-search`, in delivery.

```yaml
# gener8v pipeline state — GENERATED by gener8v-state.py; do not edit by hand.
generated: "2026-08-26T12:48:59Z"
schema_version: 4
stage: delivering
prd_title: Support Documentation Search System
system_context: true
has_source: true
active_changes: [support-search]
approvals_pending: 1
capability_areas:
  search-and-retrieval:
    name: "Search & Retrieval"
    specification: specifications/search-and-retrieval.md
    approved: true
    requirements: 10
    nfrs: 2
    constraints: constraints/search-and-retrieval.md
    technical_design: technical-design/search-and-retrieval.md   # still Draft — counted in approvals_pending
    changes: [support-search]
  results-presentation:
    name: Results Presentation
    specification: null
    approved: null
    requirements: 0
    nfrs: 0
    constraints: null
    technical_design: null
    changes: [support-search]
  documentation-ingestion:
    # … same fields, changes: [support-search]
changes:
  support-search:
    brief: changes/support-search/change.md
    legacy: false
    title: Support search
    declared_status: In Delivery
    approved: true
    areas: [search-and-retrieval, results-presentation, documentation-ingestion]
    areas_detail:
      search-and-retrieval:
        tickets_dir: changes/support-search/tickets/search-and-retrieval
        backlog: changes/support-search/tickets/search-and-retrieval/backlog.md
        ticket_count: 4                # withdrawn tickets are not counted
        legacy_file: null              # set when tickets/search-and-retrieval.md (legacy) still exists
    pending_specification: [results-presentation, documentation-ingestion]
    pending_breakdown: [results-presentation, documentation-ingestion]
    deliveries:
      search-and-retrieval/TICKET-001:
        title: Implement query input interface
        priority: Must
        status: reviewed
        done: true
        ticket_file: changes/support-search/tickets/search-and-retrieval/TICKET-001.md
        depends_on: []
        requirements: [SR-REQ-001, SR-REQ-002, SR-REQ-003]
        delivery: changes/support-search/delivery/search-and-retrieval-ticket-001-delivery.md
        delivery_status: Delivered
        verification: passed
        code_review: changes/support-search/reviews/search-and-retrieval-ticket-001-code-review.md
        quality_review: changes/support-search/reviews/search-and-retrieval-ticket-001-quality-review.md
        security_review: null
        reviews_deferred: [security]
        verdicts:
          code: Approved with Notes
          quality: Approved
        amended_after_review: false
      search-and-retrieval/TICKET-002:
        title: Configure search index for semantic matching
        priority: Must
        status: in_progress
        done: false
        ticket_file: changes/support-search/tickets/search-and-retrieval/TICKET-002.md
        depends_on: []
        requirements: [SR-REQ-006, SR-REQ-007]
        delivery: changes/support-search/delivery/search-and-retrieval-ticket-002-delivery.md
        delivery_status: In Progress
        verification: not run
        code_review: null
        quality_review: null
        security_review: null
        reviews_deferred: []
        verdicts: {}
        amended_after_review: false
      search-and-retrieval/TICKET-003:
        title: Implement relevance ranking
        priority: Must
        status: blocked
        done: false
        ticket_file: changes/support-search/tickets/search-and-retrieval/TICKET-003.md
        depends_on: [TICKET-001, TICKET-002]
        requirements: [SR-NFR-001, SR-REQ-004, SR-REQ-005]
        delivery: null
        # … remaining fields null / empty
      search-and-retrieval/TICKET-004:
        title: Add source document attribution to results
        priority: Should
        status: blocked
        # …
    progress: { total: 4, delivered: 1, reviewed: 1, done: 1, changes_required: 0 }
    status: in_delivery
    stage: delivering
  initial:                       # present only on a legacy layout
    brief: null
    legacy: true
    title: Initial (legacy layout)
    # … same fields as any change
cross_cutting:
  dependency_map: null
  system_design: null
  prd_constraints: null
  brownfield_checkpoints: []
  audits: []
  flows: []
  sweeps: [sweeps/search-sweep.md]
  assessments: [reviews/support-search-system-owasp-top10-assessment.md]
  legacy_layout: false
next_steps:
  - skill: delivery
    target: search-and-retrieval TICKET-002 in support-search
    reason: Delivery record is In Progress — resume from its Implementation Plan and Progress checklist
  - skill: specification
    target: Results Presentation
    reason: No specification for this capability area
  - skill: specification
    target: Documentation Ingestion
    reason: No specification for this capability area
  - skill: specification
    target: results-presentation for support-search
    reason: The change brief lists this area with requirements pending specification
  - skill: specification
    target: documentation-ingestion for support-search
    reason: The change brief lists this area with requirements pending specification
  - skill: dependencies
    target: PRD
    reason: Multiple capability areas and no dependency map (optional for light scope)
warnings: []
totals: { areas: 3, specs: 1, changes: 1, tickets_total: 4, delivered: 1, reviewed: 1, done: 1, changes_required: 0 }
prd_approved: true
```

Field definitions:
- **generated**: ISO 8601 timestamp. Derived files may be regenerated freely; the timestamp is informational.
- **schema_version**: bump when the shape changes so CI gates can pin it.
- **stage**: `not_started`, `planning_complete`, `specifying`, `analyzing`, `designing`, `breaking_down`, `ready_for_delivery`, `delivering`, `delivered`, `reviewing`, `reviewed`, `audited`. When a change is active the stage is that change's stage; otherwise it is the earliest incomplete living phase — which is why a project can be `specifying` while every change is complete. The matrix and the changes table show the detail.
- **has_source**: whether the working tree holds source code — the input to the Setup-then-Brownfield versus Setup-then-Planning decision.
- **active_changes**: the changes whose working status is `ready` or `in_delivery`. With exactly one, the per-ticket skills default to it; with several, the script warns and every per-ticket target names its change.
- **approvals_pending**: the PRD, specifications, per-area constraints and per-area technical designs, and change briefs whose `**Status:**` is not `Approved` (the script does not read the Status of `constraints/prd.md`, `system-design.md` or the dependency map). Which ones is visible from each entry's `approved` field.
- **capability_areas**: living coverage — specification (with `approved`, `requirements` and `nfrs` counts), constraints, technical design — and `changes`, the slugs of every change that touches the area. Tickets no longer live here.
- **changes**: one entry per `changes/<change-slug>/` (plus `initial` when the legacy layout is present, marked `legacy: true`). `declared_status` is what the brief says; `status` is the working status the script derives (`planned` · `ready` · `in_delivery` · `complete` · `abandoned`) and a warning names any disagreement. `areas` come from the brief's Affected Capability Areas table and from the ticket directories; `pending_specification` lists areas whose Requirements cell still says pending, `pending_breakdown` areas with no ticket directory (or an empty one) yet. `deliveries` is keyed `<area-slug>/TICKET-NNN` because ticket numbering restarts per area within a change.
- **areas_detail** (per change, per area): `tickets_dir` (`changes/<change-slug>/tickets/<area-slug>`), `backlog` (its `backlog.md`, or `null` when missing — lint warns), `ticket_count` (withdrawn tickets excluded) and `legacy_file` — the legacy per-area file `tickets/<area-slug>.md` when one still exists; the script reads it with a warning that names `gener8v-state.py split-tickets --remove`, and ignores it once the directory exists.
- **priority / requirements** (per delivery): copied from the ticket's `**Priority:**` and `**Requirements Covered:**` lines; the script orders ready tickets Must → Should → Could and its lint warns on a ticket with no priority.
- **ticket_file** (per delivery): the ticket's own file, root-relative under `.gener8v/` — what Delivery and the reviews open, and where a review appends a Known Hazard when it defers a finding to that ticket.
- **ticket status**: `blocked` (a dependency is not delivered) · `ready` · `reconciled` · `in_progress` · `partial` · `blocked_delivery` (pre-flight reconciliation failed) · `delivered` (Status Delivered, reviews outstanding) · `changes_required` (any review `Changes Required`) · `reviewed` (every review approved or deferred).
- **done**: `delivered` ∧ verification `passed` ∧ every review approved-or-deferred. This — not the existence of files — is what a CI gate reads.
- **delivery_status / verification / verdicts / reviews_deferred**: copied from the artifacts' status lines so nothing that Delivery or a review recorded is lost at this hand-off.
- **amended_after_review** (per delivery): whether the record's `## Post-Review Amendments` holds an entry — the input to the rework rate that `metrics` reports.
- **progress** (per change): ticket counts; a change is `complete` when `done` equals `total`.
- **cross_cutting**: artifacts that span capability areas, including the standalone ones (flows, sweeps, assessments) and `legacy_layout`.
- **next_steps**: the deterministic recommendations; Orchestrate's judgement layer refines them in conversation and may write nothing back.
- **warnings**: orphaned specifications, PRD without capability areas, Brownfield mid-run, legacy layout, a legacy per-area ticket file (the warning names `gener8v-state.py split-tickets --remove`), several active changes, a change naming an area the PRD lacks, declared-status disagreements, etc.

Metrics are not part of this file. `gener8v-state.py metrics` prints them on demand (YAML on stdout) from the same scan plus the review reports, git history and `runs.jsonl`.

---

## Principles

### Regex First, Model Second
Inventorying a directory and reading status lines is a script's job. The model's attention goes to what the script cannot know: whether a two-area project deserves technical design, whether an area carries a correctness-critical invariant, whether a sweep is due. Under a copied install the model performs the scan itself — by the same rules, so the file is the same either way.

### Status, Not Judgment — but Verdicts Are Status
This skill does not evaluate whether artifacts are good; that is Audit's job. But a delivery record's `Blocked`, a review's `Changes Required` and a failed verification are *status* that the artifacts recorded on purpose, and losing them at the hand-off is the failure the pipeline exists to prevent. They are carried into the state file and into the recommendations.

### Specific Over Vague
"Run the Specification skill on the Documentation Ingestion capability area" is useful. "You need more specifications" is not. Every recommendation names the skill and the target.

### Respect Optional Steps — Visibly
Constraints, Technical Design and Dependencies can be skipped for simple projects, and a review can be deferred with a recorded reason. Skipped steps are listed as skipped with the reason, so a resumed session does not re-recommend them, and a deferral recorded in a delivery record lets the ticket reach `done`.

### Fan-Out Awareness
Skills that run per capability area create fan-out; delivery and reviews create more — each ticket is a delivery and up to three reviews. Make it explicit: "3 of 5 capability areas have specifications. Run Specification on: Area D, Area E." "support-search · Search & Retrieval: 2/4 tickets delivered. Next: deliver TICKET-003 (Must; unblocked by TICKET-001, TICKET-002)." The three reviews' findings phases can run in parallel as the shipped reviewer agents; their resolution phases run one at a time in the main session.

### Delivery-Stage Guidance
When a change is in delivery, track at ticket level inside that change: resume anything in flight first, clear `changes_required` before starting new work, then deliver the next `ready` ticket (Must before Should before Could), then run the three reviews, then — once all verdicts are approved or deferred — the next ready ticket. A change is complete when every ticket under it is done; the next piece of work is a new change opened by Planning, and the living specifications are amended for it, never regenerated.

### Scale-Aware, Risk-Aware
A 2-area project and a 12-area project need different approaches, and so do a CRUD screen and a tenant-isolation invariant inside the same project. Never give the same advice regardless of scale or risk.

## Integration with Other Skills

This skill reads output from every other skill and writes only the state file. It is a coordination tool, not a pipeline stage. The plugin's `SessionStart` hook runs the same generator and injects the summary at the start of every session, resume and compaction, so a session never starts blind even when nobody runs Orchestrate.

## Revisions

- Re-run at any time; the state is regenerated from the artifacts, so there is nothing to keep in sync
- When the artifact layout changes (a new artifact class, a new status value), update `scripts/gener8v-state.py`, this skill's Pipeline State Format and `CONVENTIONS.md` together and bump `schema_version`

## Notes

- Orchestrate and Audit are complementary: Orchestrate tracks completeness and recorded status; Audit tracks quality
- `pipeline-state.yaml` is machine-readable. A CI gate reads `done` per ticket (see README "CI gate"), never the existence of review files
- The state file is derived; it need not be committed, and a PostToolUse hook regenerates it after every write under `.gener8v/` when the plugin is installed
- `gener8v-state.py lint` reports prefix collisions across specifications, requirements and NFRs with no ticket, NFRs with no verification method, tickets missing required sections (Priority and Value included), a ticket directory with no `backlog.md`, a legacy per-area ticket file (it names `split-tickets`), delivered requirements with no `@spec` annotation in source, dangling requirement references, and change briefs whose deltas have no matching change tag in the specification — surface its output under **Attention**
- Every number in the status comes from `gener8v-state.py metrics` (or the same arithmetic done by hand over the artifacts); Orchestrate never asks anyone to record a metric
