# Constraints Skill

## Purpose

Analyze a PRD or Specification to surface technical, compliance, integration, and operational constraints that will shape implementation decisions. Constraints are conditions the system must operate within—they are not requirements (what the system does) but boundaries (what the system must respect). The output informs downstream dependency mapping and ticket breakdown by making implicit limitations explicit before work begins.

## When to Use

Use this skill when:
- A PRD or Specification has been produced and needs constraint analysis before implementation planning
- Stakeholders need visibility into non-functional boundaries that affect feasibility
- The team needs to identify regulatory, security, or compliance obligations early
- Integration with existing systems introduces limitations that must be documented
- Preparing input for the Dependencies or Ticket Breakdown skills

## Input

**Source:** A PRD or a Specification (one or the other per invocation)
**Read from:**
- PRD-level analysis: `.gener8v/prd.md`
- Specification-level analysis: `.gener8v/specifications/[capability-area-slug].md`

**Expects:** A structured document with functional requirements or capability descriptions to analyze for constraints.

**Also reads (if available):**
- System Context: `.gener8v/context.md` — technology stack, infrastructure, team capabilities, and organizational constraints. When present, this file grounds the analysis in the actual environment rather than inference alone. If not available, note "System context not provided" in the output and flag any constraints that depend on technology or infrastructure knowledge as assumptions.

## Output

**Produces:** A constraints analysis document
**Write to:** `.gener8v/constraints/[source-slug].md`
**Creates directory:** `.gener8v/constraints/` if it does not exist
**Naming convention:**
- If analyzing the PRD: `prd.md`
- If analyzing a specification: matches the specification filename (e.g., `search-and-retrieval.md`)

A single constraints analysis can cover the PRD (broad) or one specification (deep). State which in the Source Context section of the output.

## Output Format

Produce a markdown document with the following structure:

```markdown
# [Source Document Title] — Constraints Analysis

## Overview

[2-3 sentences summarizing what was analyzed and the most significant
constraints discovered. Highlight any constraints that materially affect
scope or feasibility.]

## Source Context

**Analyzed Document:** [Title and type — PRD or Specification]
**Capability Areas Covered:** [List which capability areas this analysis spans]

## Technical Constraints

[Limitations imposed by technology, infrastructure, or engineering realities.]

- **TC-001**: [Constraint statement — what must be true or what cannot be done]
  - *Rationale:* [Why this constraint exists]
  - *Impact:* [Which requirements or capabilities this affects]

## Compliance & Regulatory Constraints

[Obligations imposed by law, regulation, industry standards, or policy.]

- **CC-001**: [Constraint statement]
  - *Rationale:* [Regulation, standard, or policy source]
  - *Impact:* [Which requirements or capabilities this affects]

## Integration Constraints

[Limitations imposed by external systems, APIs, third-party services,
or existing infrastructure the system must work with.]

- **IC-001**: [Constraint statement]
  - *Rationale:* [Why this constraint exists]
  - *Impact:* [Which requirements or capabilities this affects]

## Operational Constraints

[Limitations imposed by deployment, maintenance, support, scaling,
or organizational capacity.]

- **OC-001**: [Constraint statement]
  - *Rationale:* [Why this constraint exists]
  - *Impact:* [Which requirements or capabilities this affects]

## Constraint Interactions

[Document cases where constraints compound or conflict with each other.]

| Constraint | Interacts With | Nature of Interaction |
|------------|---------------|----------------------|
| [ID] | [ID] | [Reinforcing / Conflicting / Conditional] |

## Risk Flags

[Constraints that pose significant risk to feasibility, timeline, or scope.]

- **RF-001**: [Risk statement]
  - *Related Constraints:* [IDs]
  - *Severity:* [High / Medium / Low]
  - *Recommendation:* [Suggested action or investigation]

## Open Questions

- [ ] **OQ-001**: [Question requiring clarification to resolve a constraint]

## Assumptions

- Assumption: [Statement assumed to be true for this analysis]
```

---

## Principles

### Constraints Are Not Requirements
Requirements describe what the system does. Constraints describe what the system must operate within. "The system should support 1000 concurrent users" is a requirement. "The existing database infrastructure supports a maximum of 500 concurrent connections" is a constraint.

### Surface the Implicit
Many constraints are unstated in PRDs and Specifications because they are assumed. This skill's primary value is making the invisible visible—platform limitations, regulatory obligations, organizational policies, and integration boundaries that shape implementation but are rarely written down.

### Impact Over Inventory
Every constraint should connect to the requirements or capabilities it affects. A constraint without a stated impact is trivia, not analysis. Prioritize constraints that materially affect what can be built, how it can be built, or what risks exist.

### Categorize, Don't Bury
Organize constraints by type so that different stakeholders can quickly find what matters to them. Engineers scan Technical; legal reviews Compliance; ops reviews Operational. A flat list serves no one well.

### Flag Conflicts Early
When constraints interact—especially when they conflict—call this out explicitly. A compliance requirement that conflicts with a technical limitation is a risk that must be resolved before implementation, not discovered during it.

### Evidence-Based
Where possible, cite the source of a constraint (regulation name, API documentation, infrastructure spec, organizational policy). Constraints without rationale invite challenge and waste time in review.

## Process

0. **Validate Input**: Confirm the target document exists. If analyzing a specification, verify it contains numbered requirements. If the file is missing, stop and recommend the appropriate upstream skill. If `.gener8v/context.md` exists, read it for technology stack, infrastructure, and organizational context that grounds the analysis.

1. **Identify Source Material**: Determine whether analyzing a PRD (broader, multiple capabilities) or a Specification (single capability, more detail). Adjust depth accordingly.

2. **Scan for Technical Constraints**: Review requirements for implied infrastructure needs, performance boundaries, platform limitations, data volume assumptions, and technology prerequisites.

3. **Scan for Compliance Constraints**: Identify data handling requirements (PII, PHI, PCI), accessibility obligations, industry regulations, and organizational policies that apply.

4. **Scan for Integration Constraints**: Identify external systems, APIs, data sources, or services the system must interact with. Document their known limitations, availability, and interface requirements.

5. **Scan for Operational Constraints**: Consider deployment environment, support model, scaling expectations, maintenance windows, monitoring needs, and organizational capacity to operate the system.

6. **Map Interactions**: Review constraints pairwise for reinforcement, conflict, or conditional relationships.

7. **Assess Risk**: Identify constraints that pose the highest risk to feasibility or scope. Assign severity and recommend action.

8. **Flag Unknowns**: Where a constraint is suspected but not confirmed, document as an Open Question rather than stating it as fact.

9. **Review for Completeness**: Ensure each constraint has rationale and impact. Remove constraints that don't connect to the analyzed document.

## Example

### Input

Analyzing the "Search & Retrieval" Specification from the Support Documentation Search System PRD, which includes requirements such as:
- SR-REQ-001: The system should accept natural language questions as input
- SR-REQ-003: The system should indicate the source document for each result
- SR-REQ-004: The system should handle questions even when exact terminology doesn't match

### Output

````markdown
# Search & Retrieval — Constraints Analysis

## Overview

Analysis of the Search & Retrieval specification surfaces constraints primarily around existing documentation infrastructure and data handling obligations. The most significant constraint is that documentation currently spans multiple formats and systems with no unified access layer.

## Source Context

**Analyzed Document:** Search & Retrieval Specification (from Support Documentation Search System PRD)
**Capability Areas Covered:** Search & Retrieval

## Technical Constraints

- **TC-001**: Natural language matching (SR-REQ-004) requires semantic search capability beyond keyword matching
  - *Rationale:* Terminology mismatch handling implies vector similarity or equivalent approach
  - *Impact:* SR-REQ-004, Documentation Ingestion capability

- **TC-002**: Source document linking (SR-REQ-003) requires documentation to retain stable, addressable identifiers
  - *Rationale:* Deep links break if source systems reorganize content without redirects
  - *Impact:* SR-REQ-003, Results Presentation capability

## Compliance & Regulatory Constraints

- **CC-001**: If documentation contains customer data examples, search results must respect data access controls
  - *Rationale:* Support documentation sometimes includes sanitized customer scenarios that may contain PII
  - *Impact:* SR-REQ-001, SR-REQ-003

## Integration Constraints

- **IC-001**: Existing documentation spans Confluence, PDF manuals, and a legacy help center with no unified API
  - *Rationale:* Each source has different access patterns and update mechanisms
  - *Impact:* Documentation Ingestion capability, SR-REQ-003 (source linking varies by system)

- **IC-002**: The legacy help center does not support programmatic content extraction
  - *Rationale:* No API; content is rendered server-side with no export function
  - *Impact:* Documentation Ingestion capability

## Operational Constraints

- **OC-001**: The support team operates 24/7; system downtime for index updates must be zero or near-zero
  - *Rationale:* Support agents rely on search during active customer interactions
  - *Impact:* Documentation Ingestion capability (update mechanism)

## Constraint Interactions

| Constraint | Interacts With | Nature of Interaction |
|------------|---------------|----------------------|
| IC-001 | TC-002 | Conflicting — multiple source systems make stable linking harder |
| IC-002 | OC-001 | Conditional — workaround for legacy extraction may require scheduled batch jobs |

## Risk Flags

- **RF-001**: Legacy help center extraction (IC-002) may require screen scraping or manual export
  - *Related Constraints:* IC-002, OC-001
  - *Severity:* Medium
  - *Recommendation:* Investigate legacy system capabilities; consider excluding from initial scope

## Open Questions

- [ ] **OQ-001**: Does the organization have data classification policies that affect which documentation can be indexed?
- [ ] **OQ-002**: Are there SLAs for search availability that constrain the update mechanism?

## Assumptions

- Assumption: Confluence and PDF sources have API or export access available
- Assumption: Documentation does not contain classified or restricted content beyond potential PII
````

---

## Integration with Other Skills

**Upstream:**
- **Planning Skill**: Provides the PRD that may be analyzed at a high level, and optionally `.gener8v/context.md` for system context
- **Specification Skill**: Provides the detailed specification that is the primary input

**Downstream:**
- **Dependencies Skill**: Uses constraints to identify external dependencies and sequencing impacts
- **Technical Design Skill**: Uses constraints as boundaries that architecture decisions must respect
- **Ticket Breakdown Skill**: Uses constraints to scope work items and define acceptance criteria boundaries

## Revisions

- Re-run this skill when the source specification or PRD changes in ways that affect constraints
- Re-run when system context (`.gener8v/context.md`) is created or updated, as new technology or infrastructure information may reveal constraints not previously identified
- Downstream technical designs and tickets that reference constraint IDs become potentially stale when constraints change
- If only new constraints are added (existing IDs unchanged), downstream artifacts may only need additive updates rather than full regeneration

## Notes

- A single constraints analysis can cover a PRD (broad, lighter touch) or a Specification (focused, deeper analysis); state which in Source Context
- Not every category will have constraints for every analysis; omit empty sections rather than forcing entries
- Constraints should be revisited if the source PRD or Specification changes materially
- This skill does not recommend solutions—it surfaces the problem space for decision-makers
- When a constraint clearly blocks a requirement, flag it as a Risk rather than burying it in the category list
- When system context is available, constraints should be grounded in specific technology and infrastructure details rather than generic assumptions
