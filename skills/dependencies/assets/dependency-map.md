# [PRD or Project Title] — Dependency Map

## Overview

[2-3 sentences summarizing the dependency landscape. Call out the total
number of capability areas analyzed, the most coupled areas, and whether
a clear critical path exists.]

## Source Context

**Analyzed Documents:** [List PRD and/or Specifications analyzed]
**Capability Areas:** [Enumerate all capability areas in scope]
**Status:** [Draft / Approved]
**Approved by:** [Architect — name, YYYY-MM-DD — or "pending"]

## Internal Dependencies

[Dependencies between capability areas within the same PRD.]

### [Capability Area A] → [Capability Area B]

- **DEP-001**: [What A needs from B, or what must be true about B before A can proceed]
  - *Type:* [Hard / Soft]
  - *Nature:* [Data / Behavior / Infrastructure / Shared Resource]
  - *Detail:* [Specific requirements, data flows, or shared state involved]

## External Dependencies

[Dependencies on systems, services, teams, or resources outside the PRD scope.]

- **EXT-001**: [Capability Area] depends on [External System/Team/Resource]
  - *Type:* [Hard / Soft]
  - *Nature:* [API / Data Source / Service / Team / Decision]
  - *Detail:* [What is needed, current availability, known limitations]
  - *Related Constraints:* [Constraint IDs from Constraints analysis, if applicable — qualified by their home document, e.g. `search-and-retrieval/IC-001`]

## Shared Resources

[Data stores, services, infrastructure, or concepts that multiple
capability areas depend on. These are coupling points.]

- **RES-001**: [Shared Resource Name]
  - *Used By:* [List of capability areas]
  - *Nature:* [Data Store / Service / Configuration / Concept]
  - *Implication:* [Why this coupling matters for sequencing or coordination]

## Sequencing Analysis

### Dependency Graph

[Text-based representation of the dependency flow.]

```
[Capability A] ──→ [Capability C] ──→ [Capability E]
                         ↑
[Capability B] ──────────┘

[Capability D] (independent)
```

### Suggested Sequence

[Ordered list of capability areas based on dependency analysis.]

1. **Phase 1** (no dependencies): [Capability areas that can start immediately]
2. **Phase 2** (depends on Phase 1): [Capability areas unblocked by Phase 1 completion]
3. **Phase 3** (depends on Phase 2): [Capability areas unblocked by Phase 2 completion]

### Parallelization Opportunities

- [Capability A] and [Capability D] have no shared dependencies and can proceed in parallel
- [Capability B] and [Capability C] share [resource] but only [specific aspect], allowing partial overlap

### Critical Path

[The longest chain of dependent capabilities that determines minimum
sequential duration.]

[Capability X] → [Capability Y] → [Capability Z]

*Rationale:* [Why this is the critical path — what makes each link necessary]

## Risk Dependencies

[Dependencies that are uncertain, fragile, or outside the team's control.]

- **RD-001**: [Dependency statement]
  - *Risk:* [What happens if this dependency is not met]
  - *Mitigation:* [Suggested approach to reduce risk]

## Open Questions

- [ ] **OQ-001**: [Question that affects dependency mapping]

## Assumptions

- Assumption: [Statement assumed to be true for this analysis]
