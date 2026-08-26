# Dependencies — worked example

### Input

Analyzing the Support Documentation Search System PRD with three capability areas:
- Search & Retrieval
- Results Presentation
- Documentation Ingestion

### Output

````markdown
# Support Documentation Search System — Dependency Map

## Overview

Three capability areas with a clear linear critical path. Documentation Ingestion is the foundational dependency—both Search & Retrieval and Results Presentation require ingested content to function. Results Presentation depends on Search & Retrieval for the result set it displays. No circular dependencies exist.

## Source Context

**Analyzed Documents:** Support Documentation Search System PRD, Search & Retrieval Specification, Search & Retrieval Constraints
**Capability Areas:** Search & Retrieval, Results Presentation, Documentation Ingestion
**Status:** Draft
**Approved by:** pending

## Internal Dependencies

### Search & Retrieval → Documentation Ingestion

- **DEP-001**: Search & Retrieval requires indexed documentation to search against
  - *Type:* Hard
  - *Nature:* Data
  - *Detail:* Search queries operate on an index built from ingested documentation. Without ingestion, there is nothing to search.

### Results Presentation → Search & Retrieval

- **DEP-002**: Results Presentation requires a result set to display
  - *Type:* Hard
  - *Nature:* Data / Behavior
  - *Detail:* Presentation layer consumes ranked results with source attribution from Search & Retrieval. The display format depends on the result structure.

### Results Presentation → Documentation Ingestion

- **DEP-003**: Source document navigation requires stable links established during ingestion
  - *Type:* Soft
  - *Nature:* Data
  - *Detail:* "Navigate to full source" functionality requires addressable source references. Presentation can be built against a mock interface, but end-to-end testing requires real ingested references.

## External Dependencies

- **EXT-001**: Documentation Ingestion depends on Confluence API access
  - *Type:* Hard
  - *Nature:* API
  - *Detail:* Confluence is a primary documentation source. API credentials and permission scope needed.
  - *Related Constraints:* search-and-retrieval/IC-001

- **EXT-002**: Documentation Ingestion depends on legacy help center content extraction
  - *Type:* Hard
  - *Nature:* Data Source
  - *Detail:* Legacy system has no API (search-and-retrieval/IC-002). Extraction method must be determined.
  - *Related Constraints:* search-and-retrieval/IC-002, search-and-retrieval/RF-001

- **EXT-003**: Compliance review of indexable content
  - *Type:* Soft
  - *Nature:* Decision
  - *Detail:* Data classification policies may restrict which documentation can be indexed (search-and-retrieval/OQ-001 from the Constraints analysis). Can proceed with known-safe content initially.

## Shared Resources

- **RES-001**: Document Index
  - *Used By:* Documentation Ingestion (writes), Search & Retrieval (reads)
  - *Nature:* Data Store
  - *Implication:* Index schema decisions in Ingestion directly constrain Search capabilities. These teams (or skill passes) must agree on index structure early.

- **RES-002**: Source Reference Format
  - *Used By:* Documentation Ingestion (produces), Results Presentation (consumes)
  - *Nature:* Data Contract
  - *Implication:* How sources are identified during ingestion determines how Presentation links back to them. Format must be defined before either capability is complete.

## Sequencing Analysis

### Dependency Graph

```
[Documentation Ingestion] ──→ [Search & Retrieval] ──→ [Results Presentation]
         ↑                                                       │
         └──────────── (soft: source references) ────────────────┘
```

### Suggested Sequence

1. **Phase 1**: Documentation Ingestion — no internal dependencies; can begin immediately once external dependencies (EXT-001, EXT-002) are resolved
2. **Phase 2**: Search & Retrieval — requires index from Phase 1
3. **Phase 3**: Results Presentation — requires result set from Phase 2

### Parallelization Opportunities

- Results Presentation interface design can proceed in parallel with Phases 1-2 using mock data, though integration testing requires real results
- Search & Retrieval query logic can be developed against a test index while full ingestion proceeds
- Source reference format (RES-002) should be defined early to unblock parallel interface work

### Critical Path

Documentation Ingestion → Search & Retrieval → Results Presentation

*Rationale:* Each step produces the data the next step consumes. This is a strictly linear chain for full integration, though partial parallel work is possible with mocks.

## Risk Dependencies

- **RD-001**: Legacy help center extraction method is undefined (EXT-002)
  - *Risk:* If no programmatic extraction is possible, Documentation Ingestion scope increases significantly or legacy content is excluded
  - *Mitigation:* Investigate extraction options in Phase 1; define fallback scope that excludes legacy content

- **RD-002**: Compliance review timeline is unknown (EXT-003)
  - *Risk:* Content restrictions discovered late could invalidate index design or reduce system utility
  - *Mitigation:* Begin with documentation known to be unrestricted; run compliance review in parallel

## Open Questions

- [ ] **OQ-001**: Can index updates be incremental, or must the full index be rebuilt on documentation changes?
- [ ] **OQ-002**: Is there an existing document identifier system, or must one be created during ingestion?

## Assumptions

- Assumption: Confluence API access can be provisioned within the project timeline
- Assumption: The document index is a single shared resource, not per-source
````
