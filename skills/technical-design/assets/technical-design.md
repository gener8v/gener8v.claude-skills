# [Capability Area or System Name] — Technical Design

## Overview

[2-3 sentences summarizing the key architectural approach and the most
significant decisions made.]

## Source Context

**Specifications Analyzed:** [List of specification files]
**Constraints Analysis:** [File path, or "Not yet performed"]
**Dependency Map:** [File path, or "Not yet performed"]
**System Context:** [File path, or "Not available"]
**Status:** [Draft / Approved]
**Approved by:** [Architect — name, YYYY-MM-DD — or "pending"]

## Architecture Decisions

### AD-001: [Decision Title]

**Context:** [Why this decision needs to be made — what tension or trade-off exists]
**Decision:** [What was decided]
**Rationale:** [Why this option over alternatives]
**Alternatives Considered:**
- [Alternative A] — [Why rejected]
- [Alternative B] — [Why rejected]
**Consequences:** [What this decision enables and what it constrains going forward]
**Requirements Affected:** [PREFIX-REQ-XXX IDs this decision shapes]

### AD-002: ...

## Component Design

### [Component Name]

**Responsibility:** [What this component does — one sentence]
**Repository:** [Directory from `context.md`'s `## Repositories` table — required when the workspace has several repositories, omit for a single repository]
**Interfaces:**
- [Interface name]: [What it accepts and returns]
**Dependencies:** [Other components or external systems this relies on]
**Requirements Served:** [PREFIX-REQ-XXX and PREFIX-NFR-XXX IDs]

## Data Model

### [Entity or Data Store Name]

**Purpose:** [Why this data exists]
**Key Fields:**
- [field]: [type/description]
**Relationships:** [How this relates to other data entities]
**Source:** [Where this data comes from — user input, external system, derived]

## Interface Contracts (if applicable)

### [Interface Name]

**Between:** [Component A] ↔ [Component B]
**Purpose:** [What this interface enables]
**Input:** [What is provided]
**Output:** [What is returned]
**Error Cases:** [How failures are communicated]

## Infrastructure Requirements

- [Requirement]: [Why needed — which decisions or components drive this, and which PREFIX-NFR-XXX targets it serves]

## Technical Risks

- **TR-001**: [Risk statement]
  - *Likelihood:* [High / Medium / Low]
  - *Impact:* [What goes wrong if this risk materializes — name the NFR that would be missed]
  - *Mitigation:* [How to reduce likelihood or impact]
  - *Related Constraints:* [Constraint IDs, if applicable]
  - *Related NFRs:* [PREFIX-NFR-XXX IDs this risk threatens, or "—"]

## Open Technical Questions

- [ ] **TQ-001**: [Question that must be answered before or during implementation]

## Assumptions

- Assumption: [Technical assumption that, if wrong, would change the design]
