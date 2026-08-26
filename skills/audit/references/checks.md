# Audit — checks

The complete check lists for the Audit skill. Open this file at Process step 3 and apply every group that
matches the artifacts in scope. Vocabularies, ID rules and the change-set layout come from
`.gener8v/CONVENTIONS.md`; when a check here and that file disagree, CONVENTIONS wins and this file has a bug.

## Single-Document Checks

These apply when auditing any individual artifact.

### PRD Checks
- [ ] Problem Context is present and describes current state + why it matters
- [ ] Goals use "the system should..." framing and are directional, not measurable
- [ ] Capability areas number between 3-7
- [ ] Each capability area has at least 2 functional requirements
- [ ] User scenarios reference capabilities defined in the document
- [ ] Out of Scope section exists and is non-empty
- [ ] Open Questions section exists
- [ ] No implementation-specific language (technology names, architecture patterns)
- [ ] Document is understandable without the original user prompt
- [ ] `**Status:**` is `Draft` or `Approved` and `**Approved by:**` names the Product Owner (or says `pending`)
- [ ] A PRD amended by a later change has a Change Log entry for the amendment; earlier content was amended in place, not regenerated

### Change Brief Checks (`changes/<change-slug>/change.md`)
- [ ] Header carries `**Status:**` (`Draft` / `Approved` / `In Delivery` / `Complete` / `Abandoned`), `**Approved by:**` (Product Owner, or `pending`), `**Opened:**` and `**Slug:**`
- [ ] `**Slug:**` equals the directory name and follows the slug rule (`CONVENTIONS.md` §3)
- [ ] `## Why`, `## Outcome`, `## Affected Capability Areas`, `## Priority Cut`, `## Out of Scope`, `## Open Questions` and `## Change Log` are all present
- [ ] Affected Capability Areas is a table with Area, Kind and Requirements columns; every Area names a capability area from the PRD (or is marked `adds area`)
- [ ] Every Requirements cell is either `(pending specification)` or lists Adds / Modifies / Withdraws with real requirement and NFR IDs
- [ ] Priority Cut has a non-empty **Must** line — a change with no must-have is not worth opening
- [ ] Change Log records the opening and every specification amendment made for this change
- [ ] Declared `**Status:**` agrees with the working status `pipeline-state.yaml` derives (`In Delivery` with no delivery record, or `Complete` with an undone ticket, is a Warning)

### Specification Checks
- [ ] Overview is understandable without reading the source PRD
- [ ] Source Context references the parent PRD and related capabilities
- [ ] Source Context carries `**Requirement prefix:**`, `**Status:**` (`Draft` / `Approved`) and `**Approved by:**` (Product Owner, or `pending`)
- [ ] Every requirement has a [PREFIX]-REQ-XXX identifier with a consistent prefix
- [ ] Requirement prefix is derived from the capability area name and is unique across specifications
- [ ] Every requirement is atomic (no "and" combining two behaviors)
- [ ] Every requirement is testable (no subjective language)
- [ ] Requirements use "the system should..." framing
- [ ] `## Non-Functional Requirements` is present after Functional Requirements (or explicitly states that this area has none, and why)
- [ ] Every NFR has a [PREFIX]-NFR-XXX identifier, names a measurable target, and says `**verified by:**` with a concrete method (benchmark script, load test, lint, audit query)
- [ ] An NFR whose target cannot be measured or whose verification method is missing is recorded as an Open Question, not left as a bare statement
- [ ] Every requirement or NFR introduced by a change carries the change tag (`*(must · change: <change-slug>)*`); every amended one carries `*(amended YYYY-MM-DD by <change-slug>)*`; baseline (Brownfield) items carry no tag
- [ ] Edge cases table is present and non-empty
- [ ] Open Questions carry forward relevant items from the PRD
- [ ] No interface-specific language (button clicks, screen layouts)
- [ ] Once any requirement is delivered, `## @spec Coverage` is present and its locations are root-relative

### Constraints Checks
- [ ] Every constraint has a rationale and impact
- [ ] Constraints are categorized correctly (Technical vs. Compliance vs. Integration vs. Operational)
- [ ] Constraint interactions table is present if 3+ constraints exist
- [ ] Risk flags exist for high-impact constraints
- [ ] No requirements masquerading as constraints — a measurable target belongs in the specification's NFR section, not here
- [ ] Constraints reference specific REQ-XXX or capability areas in their impact
- [ ] Source Context carries `**Status:**` and `**Approved by:**` (Architect, or `pending`)

### Dependencies Checks
- [ ] Source Context carries `**Status:**` and `**Approved by:**` (Architect — name, date — or `pending`)
- [ ] All capability areas from the PRD are represented
- [ ] Every dependency has direction, type (hard/soft), and nature
- [ ] No circular dependencies (or they are explicitly flagged)
- [ ] Dependency graph is present and matches the written dependencies
- [ ] Suggested sequence is consistent with the dependency graph
- [ ] Critical path is identified and rationale is provided
- [ ] Shared resources (RES-XXX) are documented with their coupling implications
- [ ] External dependencies are flagged as risk dependencies

### Technical Design Checks
- [ ] Every Architecture Decision (AD-XXX) has context, decision, rationale, and alternatives considered
- [ ] Components trace back to requirements they serve; in a workspace, each component names the repository it lives in
- [ ] Interface contracts specify input, output, and error cases
- [ ] Design respects constraints identified in the Constraints analysis
- [ ] Technical risks are identified with likelihood, impact, and mitigation
- [ ] Infrastructure Requirements and Technical Risks cite the NFR IDs they serve
- [ ] Data model entities have clear purpose, structure, and relationships
- [ ] Assumptions are documented and falsifiable
- [ ] Source Context carries `**Status:**` and `**Approved by:**` (Architect, or `pending`)

### Ticket Checks (`changes/<change-slug>/tickets/<area-slug>.md`)
- [ ] Every requirement the change brief adds or modifies for this area appears in at least one ticket (the whole specification only when the brief says so)
- [ ] Every ticket has `**Priority:**` (`Must` / `Should` / `Could`) and `**Value:**` (one sentence) directly under Summary
- [ ] Every ticket has a Prior Art section pointing to specific files
- [ ] Every ticket has an Output section describing what it produces
- [ ] Prior Art and Output paths are root-relative (`api/src/search/query.ts`), never relative to a repository inside the workspace
- [ ] Every ticket has a Known Hazards section (populated, or explicitly "None identified" — an absent section means the hazard scan was skipped)
- [ ] Each listed hazard names a resolution ("so do X"), not just a worry
- [ ] Acceptance criteria are observable and verifiable
- [ ] NFR IDs in Requirements Covered are matched by a verification method under Acceptance Criteria
- [ ] No ticket is sized Large without a note on whether it should be split
- [ ] Dependency chain is acyclic
- [ ] Backlog summary table is present, accurate, and has a Priority column
- [ ] Suggested Ordering never places a `Could` ticket before a `Must` ticket unless a dependency forces it
- [ ] Ticket dependency chain visual matches the Depends On / Blocks fields
- [ ] When a Technical Design exists, tickets reference relevant Architecture Decisions

### Delivery Record Checks (`changes/<change-slug>/delivery/<area-slug>-ticket-NNN-delivery.md`)
- [ ] Ticket reference is valid (ticket exists in the ticket breakdown under the same change)
- [ ] All acceptance criteria from the ticket are addressed (marked satisfied or explicitly unsatisfied with reason)
- [ ] Files Produced lists specific, root-relative file paths
- [ ] Every file listed in Files Produced actually exists in the codebase
- [ ] Implementation Plan section is present (evidence of two-phase plan-then-implement process) and names the repository it changes
- [ ] `**Plan approved by:** Engineer — <name>, YYYY-MM-DD` is recorded before the record reaches `In Progress`
- [ ] DEL-XXX decisions have context, decision, and rationale
- [ ] Deviations from plan are documented (or explicitly "None")
- [ ] Requirements Covered matches the source ticket's Requirements Covered
- [ ] `@spec` Annotations section is present with a mapping of requirements to code locations
- [ ] Every requirement in Requirements Covered has at least one `@spec` annotation in the delivered code
- [ ] `**Status:**` is `Delivered` before any review report exists for the ticket (a `Blocked`, `Partial`, `Reconciled` or `In Progress` record with reviews is a Critical finding)
- [ ] `## Pre-Flight Reconciliation` is present with a Go/Blocked verdict and lists carried findings from predecessor reviews
- [ ] `## Verification Run` lists the executed commands with exit codes (the repository's verify commands from `context.md`'s Repositories table), `**Verification:**` matches them, and every ticked acceptance criterion cites an executed check
- [ ] Every NFR the ticket carries is either checked in the Verification Run or marked Unverified with what would verify it
- [ ] The specification's `## @spec Coverage` table has a row for every requirement this record annotated
- [ ] `## Post-Review Amendments` is present ("None" or one entry per review-applied change with re-verification)

### Code Review Checks
- [ ] Every acceptance criterion from the ticket appears in the Acceptance Criteria Coverage table
- [ ] Every requirement and NFR from the ticket appears in the Requirement Coverage table
- [ ] `@spec` Annotation Coverage table is present and shows all requirements annotated (or missing annotations flagged as findings)
- [ ] All CR-XXX findings have traceability to a pipeline artifact (REQ-XXX, NFR-XXX, AD-XXX, constraint ID, or acceptance criterion) and root-relative Location fields
- [ ] Verdict uses the shared vocabulary (Approved / Approved with Notes / Changes Required) and every finding has a Status before the verdict is anything but provisional
- [ ] Critical findings are resolved or have documented rationale for deferral; a finding `Deferred → TICKET-NNN` has a matching Known Hazard on that ticket

### Quality Review Checks
- [ ] All five quality assessment categories (Code Organization, Readability, Error Handling, Test Coverage, Observability & Operability) are rated
- [ ] QR-XXX findings have category, severity, recommendation and a root-relative Location
- [ ] Test Coverage rating cites executed commands; testable acceptance criteria with no tests is Critical, not a Concern
- [ ] Verdict uses the shared vocabulary (Approved / Approved with Notes / Changes Required)

### Security Review Checks
- [ ] All four security assessment categories (Input Validation, Auth/Authz, Data Protection, Configuration Security) are addressed
- [ ] SEC-XXX findings with Medium+ severity have attack scenarios and a root-relative Location
- [ ] OWASP references are present where applicable
- [ ] Critical/High findings are resolved or have explicit risk acceptance with rationale
- [ ] Every `Accepted Risk` finding carries `**Risk accepted by:** Security — <name>, YYYY-MM-DD`
- [ ] Compliance constraint (CC-XXX) violations — PRD-level or area-level — are flagged at Critical severity
- [ ] OWASP references use the 2025 edition
- [ ] Verdict uses the shared vocabulary (Approved / Approved with Notes / Changes Required) and `**Accepted Risks:**` is counted

### Assessment Checks (OWASP Top 10, OWASP LLM Top 10, Architecture)
- [ ] Every category (A01–A10 / LLM01–LLM10) or thesis is assessed — "Not applicable" states what was checked and why
- [ ] Findings from per-ticket security reviews are referenced with qualified IDs (`<change-slug>/<report-slug>/SEC-XXX`), not restated
- [ ] New findings are numbered within the assessment and Medium+ findings carry an attack scenario
- [ ] Findings the assessment says need code changes name the ticket that will carry them (or that no ticket exists yet)

### Flow Map Checks
- [ ] `scripts/validate-flows.sh` exits 0 (compilation is the hard gate)
- [ ] Every edge states payload, mechanism and cadence; every node carries a reliability class
- [ ] An `## Unknowns` section exists and is honest — evidence gaps are listed, not smoothed over
- [ ] The prose and the diagram agree

### Defect Sweep Checks
- [ ] `## Scope` says what was swept and what was deliberately not
- [ ] Every DS-XXX names a breaking circumstance and carries proof (a failing test, a query, a reproduction), or is labelled a hypothesis
- [ ] `## Swept and clean` names the classes run
- [ ] The Verdict maps fix-now findings to tickets under a named change

## Cross-Stage Checks

These apply when auditing across the pipeline.

### Coverage
- [ ] Every capability area in the PRD has a corresponding specification
- [ ] Every specification has a corresponding constraints analysis (or explicit deferral)
- [ ] The dependency map covers all capability areas in the PRD
- [ ] Technical design exists for capability areas with non-trivial architecture (or explicit deferral)
- [ ] Every area a change brief lists under Affected Capability Areas has a ticket breakdown at `changes/<change-slug>/tickets/<area-slug>.md` once its Requirements cell is filled (a cell still `(pending specification)` is a Gap against Specification, not Ticket Breakdown)

### Change Traceability
- [ ] Every directory under `changes/` has a `change.md`; every change brief's `**Slug:**` matches its directory
- [ ] The Requirements column of the brief's Affected Capability Areas matches the specification's change tags: every ID tagged `change: <change-slug>` in a living specification is listed in the brief's row for that area, and every ID the brief lists carries that tag in the specification (Adds ↔ new tag, Modifies ↔ amended tag, Withdraws ↔ `**Status:** Withdrawn`)
- [ ] A ticket breakdown covers only requirements its change brief adds or modifies for that area, unless the brief says otherwise
- [ ] Qualified references across documents carry the change segment (`<change-slug>/<area-slug>/TICKET-003`, `<change-slug>/<area-slug>-ticket-003-code-review/CR-002`)
- [ ] A project whose `tickets/`, `delivery/` and `reviews/*-review.md` still sit at the top level is read as the pseudo-change `initial` — raise a Suggestion to migrate once (`CONVENTIONS.md` §2); a *new* artifact written to a legacy location is a Gap

### Approvals
- [ ] Tickets were cut from an `Approved` specification — tickets under a `Draft` specification are a Warning, never a block
- [ ] Delivery started under an `Approved` (or `In Delivery`) change brief — a delivery record under a `Draft` brief is a Warning
- [ ] Every `**Approved by:**` / `**Plan approved by:**` / `**Risk accepted by:**` line names a role from `CONVENTIONS.md` §7 and a date; `approvals_pending` in `pipeline-state.yaml` matches the count of `pending` `**Approved by:**` lines on the artifacts the script reads (PRD, specifications, per-area constraints and technical designs, change briefs)

### Traceability
- [ ] Every [PREFIX]-REQ-XXX in specifications traces to at least one ticket
- [ ] Every [PREFIX]-NFR-XXX in specifications traces to at least one ticket (a Warning, not a Gap — some NFRs are verified system-wide)
- [ ] Requirement ID prefixes are unique across specifications (no two specs use the same prefix; none is a reserved prefix or segment from `CONVENTIONS.md` §3)
- [ ] Constraint IDs referenced in tickets exist in the constraints analysis (PRD-level or area-level); references across documents are qualified by source (`prd/TC-001`)
- [ ] Dependency IDs referenced in tickets exist in the dependency map
- [ ] Architecture Decision IDs (AD-XXX) referenced in tickets exist in the technical design
- [ ] Ticket Prior Art paths reference files that earlier tickets declare in their Output sections

### Delivery Traceability
- [ ] Every ticket in a completed ticket breakdown has a corresponding delivery record under the same change
- [ ] Delivery record file paths (Files Produced) match the ticket's Output section (or deviations are documented)
- [ ] Predecessor tickets referenced in Depends On have delivery records before dependent tickets are delivered
- [ ] DEL-XXX and SEC/CR/QR-XXX references made outside their home document are qualified (`TICKET-003/DEL-001`, `<change-slug>/<report-slug>/SEC-002`) — numbering restarts per document by design
- [ ] `@spec` annotations in delivered code reference requirement IDs that exist in the corresponding specification
- [ ] Every requirement in a delivered specification has at least one `@spec` annotation in the codebase (`grep -r "@spec"` across every repository under the workspace root)

### Review Traceability
- [ ] Every delivery record has corresponding code review, quality review, and security review reports under the same change, or a `**Reviews Deferred:**` line naming the deferred review and the reason
- [ ] Code review acceptance criteria table matches the source ticket's acceptance criteria
- [ ] Security review compliance findings trace to constraint IDs (CC-XXX) that exist in the constraints analysis
- [ ] Review verdicts are consistent with `pipeline-state.yaml`: a `Changes Required` verdict from any review leaves the ticket `changes_required`, and a ticket is `done` only when Delivered, verified, and approved-or-deferred by every review
- [ ] Findings a review deferred to a named ticket appear as Known Hazards on that ticket, and the ticket's delivery record lists them as carried findings

### Root-Relative Paths
- [ ] Every code path in every artifact — ticket Output and Prior Art, delivery Files Produced, `@spec Coverage` locations, review Location fields — is relative to the workspace root, and in a workspace begins with a directory listed in `context.md`'s Repositories table
- [ ] A delivery record's Verification Run uses the verify commands of the repository it names

### Consistency
- [ ] Open questions are not duplicated across documents
- [ ] Open questions resolved in downstream documents are marked resolved upstream
- [ ] Constraint impacts reference requirement IDs that exist in the corresponding specification
- [ ] No orphaned pipeline artifacts (a specification, constraints file, ticket breakdown or delivery record that no PRD area, change brief or ticket refers to; a `changes/<change-slug>/` directory with no brief). Standalone artifacts — `flows/`, `sweeps/`, `reviews/*-assessment.md`, `brownfield/`, `CONVENTIONS.md`, `pipeline-state.yaml`, `runs.jsonl` — are expected and are not orphans

### Staleness
- [ ] Specifications still align with the current PRD capability area descriptions
- [ ] Constraints analyses reflect the current specification requirements (not outdated IDs)
- [ ] Tickets reference requirement IDs that still exist in the current specification
- [ ] Technical design decisions are consistent with current constraints
- [ ] Delivery records reference tickets that still exist in the current ticket breakdown
- [ ] Code reviews reference acceptance criteria that still exist in the current tickets
- [ ] IDs are append-only: no requirement, NFR, constraint, decision or ticket ID has been renumbered or reused since the earliest delivery record; withdrawn items remain in place marked Withdrawn
- [ ] Every requirement an `@spec` annotation points at still says what it said when its delivery record was written (an amended statement means the code needs re-review — flag it)

## Ground-Truth Reconciliation Checks

These apply in a Reconciliation Audit — they check artifacts against the **actual codebase**, not against other artifacts. Each failure is at minimum a Gap, and Critical if it blocks delivery.

### Schema & Data Model
- [ ] Every table, column, enum, and constraint a ticket assumes is present in the schema/migrations (read `shared/schema.ts`, `migrations/`, or the project's equivalent — do not trust the spec's claim)
- [ ] Where a spec asserts "builds on existing schema," the schema objects actually exist; if they are net-new (never in any migration), that is flagged as an unbuilt prerequisite, not drift
- [ ] Live database state matches the committed schema where verifiable (note when only the committed source was checked, not a live DB)

### Files, Scripts & Commands
- [ ] Every script or command a ticket/plan invokes (gate scripts, build steps, seeds) exists and is runnable from the repository the ticket names
- [ ] Every file a ticket declares as Prior Art or predecessor Output actually exists at the stated root-relative path

### Referenced Documents
- [ ] Every document a ticket cites (spec, decision log, data dictionary) is present in the working context
- [ ] Each is present at the *pinned version* — a stale version (repo has v1.2, ticket pins v1.4) is a finding
- [ ] Version pins are internally consistent (a document is not pinned to two different versions across artifacts)

### Decision Closure
- [ ] Open questions / "Decision Points" the ticket leaves for the user are checked against the code first — any the code already settles are recorded as resolved (with evidence) rather than escalated
