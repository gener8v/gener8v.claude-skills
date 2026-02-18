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
- PRD: `.gener8v/prd.md`
- Specifications: `.gener8v/specifications/*.md`
- Constraints: `.gener8v/constraints/*.md`
- Dependency Map: `.gener8v/dependencies/dependency-map.md`
- Tickets: `.gener8v/tickets/*.md`

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

| Capability Area (from PRD) | Specification Exists | Constraints Exists | Tickets Exist |
|---------------------------|---------------------|-------------------|---------------|
| [Area name] | Yes / No | Yes / No | Yes / No |

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
- [ ] Every requirement has a REQ-XXX identifier
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

#### Ticket Checks
- [ ] Every requirement from the specification appears in at least one ticket
- [ ] Every ticket has a Prior Art section pointing to specific files
- [ ] Every ticket has an Output section describing what it produces
- [ ] Acceptance criteria are observable and verifiable
- [ ] No ticket is sized Large without a note on whether it should be split
- [ ] Dependency chain is acyclic
- [ ] Backlog summary table is present and accurate
- [ ] Ticket dependency chain visual matches the Depends On / Blocks fields

### Cross-Stage Checks

These apply when auditing across the pipeline.

- [ ] Every capability area in the PRD has a corresponding specification
- [ ] Every specification has a corresponding constraints analysis (or explicit deferral)
- [ ] The dependency map covers all capability areas in the PRD
- [ ] Every specification has a corresponding ticket breakdown
- [ ] Every REQ-XXX in specifications traces to at least one ticket
- [ ] Constraint IDs referenced in tickets exist in the constraints analysis
- [ ] Dependency IDs referenced in tickets exist in the dependency map
- [ ] Open questions are not duplicated across documents
- [ ] Open questions resolved in downstream documents are marked resolved upstream
- [ ] Ticket Prior Art paths reference files that earlier tickets declare in their Output sections
- [ ] No orphaned artifacts (files in `.gener8v/` that aren't referenced by anything)

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

### FIND-002: REQ-003 in search-and-retrieval specification uses subjective language

**Severity:** Warning
**Location:** `.gener8v/specifications/search-and-retrieval.md`, REQ-003
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

| Capability Area (from PRD) | Specification Exists | Constraints Exists | Tickets Exist |
|---------------------------|---------------------|-------------------|---------------|
| Search & Retrieval | Yes | Yes | Yes |
| Results Presentation | Yes | **No** | No |
| Documentation Ingestion | **No** | No | No |

### Requirement Traceability

| Requirement | Specification | Ticket(s) | Covered |
|-------------|---------------|-----------|---------|
| REQ-001 | search-and-retrieval.md | TICKET-001 | Yes |
| REQ-002 | search-and-retrieval.md | TICKET-003 | Yes |
| REQ-003 | search-and-retrieval.md | TICKET-004 | Yes |
| REQ-004 | search-and-retrieval.md | TICKET-002 | Yes |

## Resolution Log

| Finding | Decision | Action Taken | Artifact Updated |
|---------|----------|-------------|-----------------|
| FIND-001 | Approved | User will run Specification skill next | — |
| FIND-002 | Approved | Reworded REQ-003 to remove subjective language | `.gener8v/specifications/search-and-retrieval.md` |
| FIND-003 | Deferred | Will address after Documentation Ingestion specification is complete | — |
````

---

## Integration with Other Skills

**Upstream (audits output from):**
- **Planning Skill**: Audits PRD for structure, completeness, and technical leakage
- **Specification Skill**: Audits specifications for atomicity, testability, and traceability
- **Constraints Skill**: Audits constraints for categorization, rationale, and impact mapping
- **Dependencies Skill**: Audits dependency maps for completeness, circularity, and sequencing validity
- **Ticket Breakdown Skill**: Audits tickets for coverage, Prior Art/Output completeness, and acceptance criteria quality

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

## Notes

- This skill can be run at any point in the pipeline — it adapts to whatever artifacts exist
- Running a cross-stage audit with only a PRD produces limited findings (mostly "missing specification" gaps); this is expected and useful for planning next steps
- The skill does not generate missing artifacts — it identifies what's missing and recommends which skill to run
- Multiple audit reports can coexist in `.gener8v/audits/`; they are timestamped by content, not filename
- If the user has resolved open questions during an audit, update the source document's Open Questions section to reflect the resolution
