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
- Tickets: `.gener8v/tickets/*.md`
- Delivery Records: `.gener8v/delivery/*.md`
- Code Reviews: `.gener8v/reviews/*-code-review.md`
- Quality Reviews: `.gener8v/reviews/*-quality-review.md`
- Security Reviews: `.gener8v/reviews/*-security-review.md`
- Delivered code files (for `@spec` annotation verification)

**Expects:** At least one artifact to exist. The skill adapts its checks based on what's available — auditing a PRD alone is valid, but auditing tickets without a specification is less useful and the skill will flag this.

## Output

**Produces:** An audit report with findings, plus interactive resolution of issues with the user
**Write to:** `.gener8v/audits/[scope]-audit.md`
**Creates directory:** `.gener8v/audits/` if it does not exist
**Naming convention:**
- Single-document audit: `[stage]-[slug]-audit.md` (e.g., `specification-search-and-retrieval-audit.md`)
- Cross-pipeline audit: `pipeline-audit.md`

After interactive resolution, the skill updates the source artifacts directly. The audit report captures what was found and what was changed.

## Audit Modes

### Single-Document Audit

Review one artifact in isolation for internal quality.

**Trigger:** User points to a specific file or stage
**Scope:** One document only

### Cross-Stage Audit

Trace consistency and coverage across multiple pipeline stages.

**Trigger:** User asks to audit the pipeline, or multiple stages have been completed
**Scope:** All available artifacts in `.gener8v/`

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
**Status:** [Open / Resolved / Deferred]
**Resolution:** [What was done, if resolved — filled in during interactive session]

---

### FIND-002: ...

## Coverage Matrix (Cross-Stage Audit only)

### Capability Area → Specification Coverage

| Capability Area (from PRD) | Spec | Constraints | Tech Design | Tickets | Delivered | CR | QR | SEC |
|---------------------------|------|-------------|-------------|---------|-----------|----|----|-----|
| [Area name] | Yes/No | Yes/No | Yes/No | Yes/No | [n/total] | [n/total] | [n/total] | [n/total] |

### Requirement Traceability

| Requirement | Specification | Ticket(s) | Covered |
|-------------|---------------|-----------|---------|
| REQ-001 | [slug].md | TICKET-001 | Yes |
| REQ-002 | [slug].md | — | **No** |

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

### Single-Document Checks

These apply when auditing any individual artifact.

#### PRD Checks
- [ ] Problem Context is present and describes current state + why it matters
- [ ] Goals use "the system should..." framing and are directional, not measurable
- [ ] Capability areas number between 3-7
- [ ] Each capability area has at least 2 functional requirements
- [ ] User scenarios reference capabilities defined in the document
- [ ] Out of Scope section exists and is non-empty
- [ ] Open Questions section exists
- [ ] No implementation-specific language (technology names, architecture patterns)
- [ ] Document is understandable without the original user prompt

#### Specification Checks
- [ ] Overview is understandable without reading the source PRD
- [ ] Source Context references the parent PRD and related capabilities
- [ ] Every requirement has a [PREFIX]-REQ-XXX identifier with a consistent prefix
- [ ] Requirement prefix is derived from the capability area name and is unique across specifications
- [ ] Every requirement is atomic (no "and" combining two behaviors)
- [ ] Every requirement is testable (no subjective language)
- [ ] Requirements use "the system should..." framing
- [ ] Edge cases table is present and non-empty
- [ ] Open Questions carry forward relevant items from the PRD
- [ ] No interface-specific language (button clicks, screen layouts)

#### Constraints Checks
- [ ] Every constraint has a rationale and impact
- [ ] Constraints are categorized correctly (Technical vs. Compliance vs. Integration vs. Operational)
- [ ] Constraint interactions table is present if 3+ constraints exist
- [ ] Risk flags exist for high-impact constraints
- [ ] No requirements masquerading as constraints
- [ ] Constraints reference specific REQ-XXX or capability areas in their impact

#### Dependencies Checks
- [ ] All capability areas from the PRD are represented
- [ ] Every dependency has direction, type (hard/soft), and nature
- [ ] No circular dependencies (or they are explicitly flagged)
- [ ] Dependency graph is present and matches the written dependencies
- [ ] Suggested sequence is consistent with the dependency graph
- [ ] Critical path is identified and rationale is provided
- [ ] Shared resources are documented with their coupling implications
- [ ] External dependencies are flagged as risk dependencies

#### Technical Design Checks
- [ ] Every Architecture Decision (AD-XXX) has context, decision, rationale, and alternatives considered
- [ ] Components trace back to requirements they serve
- [ ] Interface contracts specify input, output, and error cases
- [ ] Design respects constraints identified in the Constraints analysis
- [ ] Technical risks are identified with likelihood, impact, and mitigation
- [ ] Data model entities have clear purpose, structure, and relationships
- [ ] Assumptions are documented and falsifiable

#### Ticket Checks
- [ ] Every requirement from the specification appears in at least one ticket
- [ ] Every ticket has a Prior Art section pointing to specific files
- [ ] Every ticket has an Output section describing what it produces
- [ ] Acceptance criteria are observable and verifiable
- [ ] No ticket is sized Large without a note on whether it should be split
- [ ] Dependency chain is acyclic
- [ ] Backlog summary table is present and accurate
- [ ] Ticket dependency chain visual matches the Depends On / Blocks fields
- [ ] When a Technical Design exists, tickets reference relevant Architecture Decisions

#### Delivery Record Checks
- [ ] Ticket reference is valid (ticket exists in the ticket breakdown)
- [ ] All acceptance criteria from the ticket are addressed (marked satisfied or explicitly unsatisfied with reason)
- [ ] Files Produced lists specific file paths
- [ ] Every file listed in Files Produced actually exists in the codebase
- [ ] Implementation Plan section is present (evidence of two-phase plan-then-implement process)
- [ ] DEL-XXX decisions have context, decision, and rationale
- [ ] Deviations from plan are documented (or explicitly "None")
- [ ] Requirements Covered matches the source ticket's Requirements Covered
- [ ] `@spec` Annotations section is present with a mapping of requirements to code locations
- [ ] Every requirement in Requirements Covered has at least one `@spec` annotation in the delivered code

#### Code Review Checks
- [ ] Every acceptance criterion from the ticket appears in the Acceptance Criteria Coverage table
- [ ] Every requirement from the ticket appears in the Requirement Coverage table
- [ ] `@spec` Annotation Coverage table is present and shows all requirements annotated (or missing annotations flagged as findings)
- [ ] All CR-XXX findings have traceability to a pipeline artifact (REQ-XXX, AD-XXX, constraint ID, or acceptance criterion)
- [ ] Verdict is present
- [ ] Critical findings are resolved or have documented rationale for deferral

#### Quality Review Checks
- [ ] All four quality assessment categories (Code Organization, Readability, Error Handling, Test Coverage) are rated
- [ ] QR-XXX findings have category, severity, and recommendation
- [ ] Verdict is present

#### Security Review Checks
- [ ] All four security assessment categories (Input Validation, Auth/Authz, Data Protection, Configuration Security) are addressed
- [ ] SEC-XXX findings with Medium+ severity have attack scenarios
- [ ] OWASP references are present where applicable
- [ ] Critical/High findings are resolved or have explicit risk acceptance with rationale
- [ ] Compliance constraint (CC-XXX) violations are flagged at Critical severity
- [ ] Verdict is present

### Cross-Stage Checks

These apply when auditing across the pipeline.

#### Coverage
- [ ] Every capability area in the PRD has a corresponding specification
- [ ] Every specification has a corresponding constraints analysis (or explicit deferral)
- [ ] The dependency map covers all capability areas in the PRD
- [ ] Technical design exists for capability areas with non-trivial architecture (or explicit deferral)
- [ ] Every specification has a corresponding ticket breakdown

#### Traceability
- [ ] Every [PREFIX]-REQ-XXX in specifications traces to at least one ticket
- [ ] Requirement ID prefixes are unique across specifications (no two specs use the same prefix)
- [ ] Constraint IDs referenced in tickets exist in the constraints analysis
- [ ] Dependency IDs referenced in tickets exist in the dependency map
- [ ] Architecture Decision IDs (AD-XXX) referenced in tickets exist in the technical design
- [ ] Ticket Prior Art paths reference files that earlier tickets declare in their Output sections

#### Delivery Traceability
- [ ] Every ticket in a completed ticket breakdown has a corresponding delivery record
- [ ] Delivery record file paths (Files Produced) match the ticket's Output section (or deviations are documented)
- [ ] Predecessor tickets referenced in Depends On have delivery records before dependent tickets are delivered
- [ ] DEL-XXX decision IDs are unique across delivery records
- [ ] `@spec` annotations in delivered code reference requirement IDs that exist in the corresponding specification
- [ ] Every requirement in a delivered specification has at least one `@spec` annotation in the codebase (`grep -r "@spec" src/`)

#### Review Traceability
- [ ] Every delivery record has corresponding code review, quality review, and security review reports (or explicit deferral documented)
- [ ] Code review acceptance criteria table matches the source ticket's acceptance criteria
- [ ] Security review compliance findings trace to constraint IDs (CC-XXX) that exist in the constraints analysis
- [ ] Review verdicts are consistent — a "Changes Required" code review should block deployment regardless of other review outcomes

#### Consistency
- [ ] Open questions are not duplicated across documents
- [ ] Open questions resolved in downstream documents are marked resolved upstream
- [ ] Constraint impacts reference requirement IDs that exist in the corresponding specification
- [ ] No orphaned artifacts (files in `.gener8v/` that aren't referenced by anything)

#### Staleness
- [ ] Specifications still align with the current PRD capability area descriptions
- [ ] Constraints analyses reflect the current specification requirements (not outdated IDs)
- [ ] Tickets reference requirement IDs that still exist in the current specification
- [ ] Technical design decisions are consistent with current constraints
- [ ] Delivery records reference tickets that still exist in the current ticket breakdown
- [ ] Code reviews reference acceptance criteria that still exist in the current tickets

---

## Severity Levels

- **Critical**: Blocks downstream work or produces incorrect output. Must be resolved before proceeding. Examples: missing capability area with no specification, circular dependency, requirement with no ticket coverage.
- **Gap**: Something is missing that should be present but doesn't block immediate progress. Should be resolved before implementation. Examples: empty edge cases table, missing constraints analysis for a specification, open question that affects ticket scope.
- **Warning**: Potential issue that may cause problems later. Worth reviewing but can proceed. Examples: subjective language in a requirement, a Large ticket that might benefit from splitting, a soft dependency not reflected in sequencing.
- **Suggestion**: Improvement opportunity. Non-blocking. Examples: reworded requirement for clarity, additional user scenario, constraint that could be more specific.

## Process

1. **Determine Scope**: Identify which artifacts exist in `.gener8v/` and whether this is a single-document or cross-stage audit.

2. **Read Artifacts**: Load all in-scope documents. Note which expected artifacts are missing.

3. **Run Checks**: Apply the relevant check lists systematically. For cross-stage audits, run single-document checks first, then cross-stage checks.

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

8. **Write Audit Report**: Save the audit report with all findings and their resolutions.

9. **Summarize**: Present a final summary — what was found, what was resolved, what remains open.

## Example

### Input

User asks: "Audit the pipeline" with the following artifacts available:
- `.gener8v/prd.md`
- `.gener8v/specifications/search-and-retrieval.md`
- `.gener8v/specifications/results-presentation.md`
- `.gener8v/specifications/documentation-ingestion.md` (missing)
- `.gener8v/constraints/search-and-retrieval.md`
- `.gener8v/dependencies/dependency-map.md`
- `.gener8v/tickets/search-and-retrieval.md`

### Output (abbreviated)

````markdown
# Audit Report — Cross-Pipeline Audit

## Summary

Audited 5 artifacts across 4 pipeline stages. The pipeline is partially complete with 7 findings: 1 critical, 3 gaps, 2 warnings, 1 suggestion. The most significant issue is a missing specification for the Documentation Ingestion capability area, which blocks constraint analysis and ticket breakdown for that area.

**Artifacts Audited:**
- `.gener8v/prd.md` (Planning)
- `.gener8v/specifications/search-and-retrieval.md` (Specification)
- `.gener8v/specifications/results-presentation.md` (Specification)
- `.gener8v/constraints/search-and-retrieval.md` (Constraints)
- `.gener8v/dependencies/dependency-map.md` (Dependencies)
- `.gener8v/tickets/search-and-retrieval.md` (Ticket Breakdown)

**Findings:** 7
**Critical:** 1 | **Gaps:** 3 | **Warnings:** 2 | **Suggestions:** 1

## Findings

### FIND-001: Missing specification for Documentation Ingestion

**Severity:** Critical
**Location:** `.gener8v/specifications/` (expected: `documentation-ingestion.md`)
**Description:** The PRD defines three capability areas but only two have specifications. Documentation Ingestion has no specification.
**Impact:** Cannot produce constraints analysis, dependency detail, or tickets for this capability area. The dependency map references it but the analysis is based on PRD-level detail only.
**Recommendation:** Run the Specification skill on the Documentation Ingestion capability area.
**Status:** Open

---

### FIND-002: SR-REQ-003 in search-and-retrieval specification uses subjective language

**Severity:** Warning
**Location:** `.gener8v/specifications/search-and-retrieval.md`, SR-REQ-003
**Description:** "The system should indicate the source document for each result in a user-friendly way" — "user-friendly" is not testable.
**Impact:** Acceptance criteria derived from this requirement may be ambiguous.
**Recommendation:** Reword to: "The system should indicate the source document title and location for each result."
**Status:** Open

---

### FIND-003: No constraints analysis for results-presentation

**Severity:** Gap
**Location:** `.gener8v/constraints/` (expected: `results-presentation.md`)
**Description:** Results Presentation has a specification but no constraints analysis.
**Impact:** Tickets for this area will lack constraint-informed acceptance criteria.
**Recommendation:** Run the Constraints skill on the Results Presentation specification, or explicitly defer with a note in the ticket breakdown.
**Status:** Open

---

*[Interactive session begins — user resolves each finding...]*

## Coverage Matrix

### Capability Area → Specification Coverage

| Capability Area (from PRD) | Spec | Constraints | Tech Design | Tickets |
|---------------------------|------|-------------|-------------|---------|
| Search & Retrieval | Yes | Yes | **No** | Yes |
| Results Presentation | Yes | **No** | No | No |
| Documentation Ingestion | **No** | No | No | No |

### Requirement Traceability

| Requirement | Specification | Ticket(s) | Covered |
|-------------|---------------|-----------|---------|
| SR-REQ-001 | search-and-retrieval.md | TICKET-001 | Yes |
| SR-REQ-002 | search-and-retrieval.md | TICKET-003 | Yes |
| SR-REQ-003 | search-and-retrieval.md | TICKET-004 | Yes |
| SR-REQ-004 | search-and-retrieval.md | TICKET-002 | Yes |

## Resolution Log

| Finding | Decision | Action Taken | Artifact Updated |
|---------|----------|-------------|-----------------|
| FIND-001 | Approved | User will run Specification skill next | — |
| FIND-002 | Approved | Reworded SR-REQ-003 to remove subjective language | `.gener8v/specifications/search-and-retrieval.md` |
| FIND-003 | Deferred | Will address after Documentation Ingestion specification is complete | — |
````

---

## Integration with Other Skills

**Upstream (audits output from):**
- **Planning Skill**: Audits PRD for structure, completeness, and technical leakage
- **Specification Skill**: Audits specifications for atomicity, testability, namespacing, and traceability
- **Constraints Skill**: Audits constraints for categorization, rationale, and impact mapping
- **Dependencies Skill**: Audits dependency maps for completeness, circularity, and sequencing validity
- **Technical Design Skill**: Audits architecture decisions for completeness, constraint compliance, and requirement traceability
- **Ticket Breakdown Skill**: Audits tickets for coverage, Prior Art/Output completeness, and acceptance criteria quality
- **Delivery Skill**: Audits delivery records for acceptance criteria verification, file existence, decision documentation, and deviation tracking
- **Code Review Skill**: Audits code reviews for traceability completeness, finding quality, and verdict consistency
- **Quality Review Skill**: Audits quality reviews for assessment completeness and finding quality
- **Security Review Skill**: Audits security reviews for OWASP compliance, attack scenario presence, risk acceptance documentation, and compliance constraint coverage

**Downstream:**
- This skill modifies source artifacts directly during interactive resolution
- Audit reports are reference documents; no other skill consumes them as input

## Principles

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
- Previous audit reports remain in `.gener8v/audits/` for reference; they are not overwritten unless the scope is identical
- The Orchestrate skill tracks completeness (what exists); the Audit skill tracks quality (is it good) — they are complementary

## Notes

- This skill can be run at any point in the pipeline — it adapts to whatever artifacts exist
- Running a cross-stage audit with only a PRD produces limited findings (mostly "missing specification" gaps); this is expected and useful for planning next steps
- The skill does not generate missing artifacts — it identifies what's missing and recommends which skill to run
- Multiple audit reports can coexist in `.gener8v/audits/`; they are timestamped by content, not filename
- If the user has resolved open questions during an audit, update the source document's Open Questions section to reflect the resolution
