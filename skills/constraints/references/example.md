# Constraints — worked example

### Input

Analyzing the "Search & Retrieval" Specification (`.gener8v/specifications/search-and-retrieval.md`) from the Support Documentation Search System PRD, which includes requirements such as:
- SR-REQ-001: The system should accept free-text natural language questions as search input
- SR-REQ-006: The system should return relevant results even when the query uses different terminology than the source documentation
- SR-REQ-008: The system should indicate the source document title for each result
- SR-REQ-009: The system should provide a stable reference to the source location for each result

and non-functional requirements such as SR-NFR-001 (p95 search latency ≤ 800 ms at 50 concurrent users). Those are targets and stay in the specification; this analysis surfaces the boundaries the system must operate within to reach them.

### Output

Written to `.gener8v/constraints/search-and-retrieval.md`:

````markdown
# Search & Retrieval — Constraints Analysis

## Overview

Analysis of the Search & Retrieval specification surfaces constraints primarily around existing documentation infrastructure and data handling obligations. The most significant constraint is that documentation currently spans multiple formats and systems with no unified access layer.

## Source Context

**Analyzed Document:** Search & Retrieval Specification (from Support Documentation Search System PRD)
**Capability Areas Covered:** Search & Retrieval
**Status:** Draft
**Approved by:** pending

## Technical Constraints

- **TC-001**: Natural language matching (SR-REQ-006) requires semantic search capability beyond keyword matching
  - *Rationale:* Terminology mismatch handling implies vector similarity or equivalent approach
  - *Impact:* SR-REQ-006, Documentation Ingestion capability

- **TC-002**: Source document linking (SR-REQ-008, SR-REQ-009) requires documentation to retain stable, addressable identifiers
  - *Rationale:* Deep links break if source systems reorganize content without redirects
  - *Impact:* SR-REQ-008, SR-REQ-009, Results Presentation capability

## Compliance & Regulatory Constraints

- **CC-001**: If documentation contains customer data examples, search results must respect data access controls
  - *Rationale:* Support documentation sometimes includes sanitized customer scenarios that may contain PII
  - *Impact:* SR-REQ-004, SR-REQ-007

## Integration Constraints

- **IC-001**: Existing documentation spans Confluence, PDF manuals, and a legacy help center with no unified API
  - *Rationale:* Each source has different access patterns and update mechanisms
  - *Impact:* Documentation Ingestion capability, SR-REQ-009 (source linking varies by system)

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

Once the Architect approves the analysis in conversation, the two Source Context lines become `**Status:** Approved` and `**Approved by:** Architect — <name>, YYYY-MM-DD`. Downstream documents cite these entries qualified by source, e.g. `search-and-retrieval/TC-001`.
