# Technical Design Skill

## Purpose

Bridge the gap between functional specification and implementation. This skill translates requirements, constraints, and dependencies into architectural decisions, technology choices, component boundaries, and interface contracts. The output is the "how" that complements the specification's "what" — and directly informs ticket breakdown by giving developers a shared technical foundation before work begins.

## When to Use

Use this skill when:
- Specifications and constraints have been completed for one or more capability areas
- The team needs to agree on architecture and technology choices before writing code
- Multiple capability areas share infrastructure, data stores, or services that need coordinated design
- Technology choices materially affect ticket scope, sequencing, or sizing
- The gap between "what to build" and "how to build it" is large enough to warrant explicit decisions

Skip this skill when:
- The implementation approach is obvious and uncontested
- The team has an established architecture and the new work fits cleanly within it
- The scope is small enough that technical decisions can be made within individual tickets

## Input

**Source:** Specifications, Constraints analyses, Dependency Map, and optionally System Context
**Read from:**
- Specifications: `.gener8v/specifications/*.md`
- Constraints: `.gener8v/constraints/*.md` (if available)
- Dependency Map: `.gener8v/dependencies/dependency-map.md` (if available)
- System Context: `.gener8v/context.md` (if available)

**Expects:** At minimum, one specification with numbered requirements. Richer design is possible when constraints, dependencies, and system context are available. Note which inputs were used in the Source Context section of the output.

**If input is missing or malformed:**
- If no specifications exist, stop and recommend running the Specification skill first
- If constraints or dependencies are missing, note "Not yet performed" in Source Context and proceed — flag that design decisions may need revisiting once these analyses exist
- If system context is missing, note this and flag any decisions that depend on technology stack or infrastructure knowledge as open questions

## Output

**Produces:** A technical design document
**Write to:**
- Per-capability design: `.gener8v/technical-design/[capability-area-slug].md`
- Cross-cutting system design: `.gener8v/technical-design/system-design.md`
**Creates directory:** `.gener8v/technical-design/` if it does not exist

Run this skill once per capability area that warrants technical design, or once for system-wide design that spans multiple capabilities. A single capability with complex internals warrants its own document; a simple capability may only need a section in the system-wide design.

## Output Format

Produce a markdown document with the following structure:

```markdown
# [Capability Area or System Name] — Technical Design

## Overview

[2-3 sentences summarizing the key architectural approach and the most
significant decisions made.]

## Source Context

**Specifications Analyzed:** [List of specification files]
**Constraints Analysis:** [File path, or "Not yet performed"]
**Dependency Map:** [File path, or "Not yet performed"]
**System Context:** [File path, or "Not available"]

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
**Interfaces:**
- [Interface name]: [What it accepts and returns]
**Dependencies:** [Other components or external systems this relies on]
**Requirements Served:** [PREFIX-REQ-XXX IDs]

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

- [Requirement]: [Why needed, which decisions or components drive this]

## Technical Risks

- **TR-001**: [Risk statement]
  - *Likelihood:* [High / Medium / Low]
  - *Impact:* [What goes wrong if this risk materializes]
  - *Mitigation:* [How to reduce likelihood or impact]
  - *Related Constraints:* [Constraint IDs, if applicable]

## Open Technical Questions

- [ ] **TQ-001**: [Question that must be answered before or during implementation]

## Assumptions

- Assumption: [Technical assumption that, if wrong, would change the design]
```

---

## Principles

### Decisions Over Descriptions
The primary value of this skill is recording decisions and their rationale — not describing a system in abstract terms. Every architecture decision should answer: what was the question, what did we decide, and why? A technical design without explicit decisions is just a diagram that no one can execute from.

### Justify With Alternatives
A decision without alternatives considered is just an assertion. Document what other approaches were viable and why they were rejected. This prevents relitigating decisions later and gives future maintainers context for when circumstances change.

### Design for the Requirements
Architecture should serve the requirements, not the other way around. Every component, every data model entity, and every interface should trace back to requirements it supports. If a design element exists for future hypothetical needs, call it out explicitly — don't smuggle it in as if it were required.

### Make Interfaces Explicit
The boundaries between components are where most integration issues occur. Define interfaces with enough specificity that two developers can independently build components on either side and have them work together. Input, output, and error cases — at minimum.

### Technical Debt Is a Choice
When a design makes an expedient choice that creates future maintenance burden, document it as a deliberate decision with rationale. "We chose X because Y, knowing that Z will need to change when [condition]." Undocumented shortcuts are accidents; documented ones are strategy.

### Constrained by Constraints
Technical decisions must respect the constraints identified by the Constraints skill. If a design decision conflicts with a constraint, either the design must change or the constraint must be challenged — don't silently ignore the tension.

## Process

1. **Gather Inputs**: Read the relevant specifications, constraints, dependency map, and system context. Note which documents are available and which are missing.

2. **Identify Decisions Needed**: Scan requirements and constraints for questions that require architectural answers: What technology? What pattern? What boundary? What trade-off?

3. **Make and Document Decisions**: For each decision point, evaluate options against requirements and constraints. Document the decision with full rationale and alternatives.

4. **Design Components**: Identify the major building blocks. Define what each does, what it depends on, and how others interact with it.

5. **Model Data**: Identify data entities, their structure, relationships, and sources. Align with requirements about what data the system captures, stores, and displays.

6. **Define Interfaces**: For each boundary between components (or between the system and external systems), define the contract: input, output, error handling.

7. **Identify Infrastructure**: Determine what infrastructure the design requires beyond application code — databases, queues, caches, external services, deployment targets.

8. **Assess Technical Risks**: Identify where the design has uncertainty, where decisions depend on unverified assumptions, or where implementation complexity is high.

9. **Review Against Constraints**: Walk through each constraint and verify the design respects it. Flag any tensions.

10. **Flag Unknowns**: Technical questions that can't be answered without prototyping, vendor evaluation, or stakeholder input go to Open Technical Questions.

## Example

### Input

Designing the "Search & Retrieval" capability from the Support Documentation Search System, using:
- Specification with requirements SR-REQ-001 through SR-REQ-010
- Constraints analysis with TC-001 (semantic search needed), TC-002 (stable identifiers needed)
- Dependency map showing dependency on Documentation Ingestion
- System context indicating the team uses Python, runs on AWS, and has experience with PostgreSQL

### Output

````markdown
# Search & Retrieval — Technical Design

## Overview

Search & Retrieval uses a vector similarity approach for semantic search, backed by PostgreSQL with pgvector. The design separates query processing, index management, and result ranking into distinct components with clear interfaces. The most significant decision is using pgvector over a dedicated vector database, trading peak performance for operational simplicity.

## Source Context

**Specifications Analyzed:** `.gener8v/specifications/search-and-retrieval.md`
**Constraints Analysis:** `.gener8v/constraints/search-and-retrieval.md`
**Dependency Map:** `.gener8v/dependencies/dependency-map.md`
**System Context:** `.gener8v/context.md`

## Architecture Decisions

### AD-001: Use vector similarity search for semantic matching

**Context:** SR-REQ-006 requires results even when query terminology differs from documentation. This rules out keyword-only search and requires some form of semantic understanding.
**Decision:** Use vector embeddings for both documentation chunks and queries, with cosine similarity for matching.
**Rationale:** Vector similarity handles terminology mismatch naturally without synonym dictionaries or manual mapping. Aligns with TC-001 from constraints analysis.
**Alternatives Considered:**
- Keyword search with synonym expansion — Fragile; requires manual maintenance of synonym lists
- Full LLM-based reranking — Higher latency and cost per query; overkill for initial scope
**Consequences:** Requires an embedding model for both indexing and query time. Index size grows with embedding dimensions. Quality depends on embedding model choice.
**Requirements Affected:** SR-REQ-004, SR-REQ-005, SR-REQ-006

### AD-002: Use PostgreSQL with pgvector extension

**Context:** Need a vector store for embeddings. Team already operates PostgreSQL in production.
**Decision:** Use pgvector extension in existing PostgreSQL infrastructure.
**Rationale:** Avoids introducing a new database technology. Team has PostgreSQL expertise and operational tooling. pgvector supports approximate nearest-neighbor search sufficient for expected scale.
**Alternatives Considered:**
- Dedicated vector database (Pinecone, Weaviate) — Better performance at scale, but adds operational complexity and a new vendor dependency
- Elasticsearch with vector search — Capable, but team lacks Elasticsearch experience
**Consequences:** Performance may become a concern at very high document volumes. Migration path to a dedicated vector store exists if needed.
**Requirements Affected:** SR-REQ-004, SR-REQ-005, SR-REQ-007

## Component Design

### Query Processor

**Responsibility:** Accept natural language queries, validate input, generate query embeddings
**Interfaces:**
- `process_query(text: str) -> QueryEmbedding`: Validates input and returns embedding vector
**Dependencies:** Embedding model service
**Requirements Served:** SR-REQ-001, SR-REQ-002, SR-REQ-003

### Search Index

**Responsibility:** Store document embeddings and perform similarity searches
**Interfaces:**
- `search(embedding: vector, limit: int) -> list[RawResult]`: Returns nearest matches with scores
**Dependencies:** PostgreSQL with pgvector
**Requirements Served:** SR-REQ-004, SR-REQ-006, SR-REQ-007

### Result Ranker

**Responsibility:** Order raw results by relevance, attach source attribution, return bounded result set
**Interfaces:**
- `rank(results: list[RawResult]) -> list[RankedResult]`: Returns ordered, attributed results
**Dependencies:** Query Processor (for query context), Search Index (for raw results)
**Requirements Served:** SR-REQ-005, SR-REQ-008, SR-REQ-009, SR-REQ-010

## Data Model

### DocumentChunk

**Purpose:** Stores a searchable segment of documentation with its embedding
**Key Fields:**
- `id`: Unique identifier
- `content`: Text excerpt
- `embedding`: Vector representation
- `source_title`: Title of the source document
- `source_ref`: Stable URI/path to the source location
- `source_system`: Which documentation system this came from
**Relationships:** Many chunks per source document
**Source:** Created by Documentation Ingestion capability

## Infrastructure Requirements

- PostgreSQL instance with pgvector extension enabled
- Embedding model access (API or self-hosted) for query-time embedding generation
- Sufficient storage for embedding vectors (dimensionality × document count × 4 bytes)

## Technical Risks

- **TR-001**: pgvector query performance at scale is unproven for this team
  - *Likelihood:* Low (expected document volume is modest)
  - *Impact:* Search latency degrades, affecting user experience
  - *Mitigation:* Benchmark with representative data volume early; define performance threshold
  - *Related Constraints:* TC-001

## Open Technical Questions

- [ ] **TQ-001**: Which embedding model should be used? (Affects quality, latency, and cost)
- [ ] **TQ-002**: What chunk size produces the best search results? (Requires experimentation)
- [ ] **TQ-003**: Should the system support hybrid search (vector + keyword) for improved precision?

## Assumptions

- Assumption: pgvector is available or can be enabled on the existing PostgreSQL instance
- Assumption: Query volume is low enough that embedding generation per query is acceptable latency
- Assumption: A single embedding model is sufficient for all documentation sources
````

---

## Integration with Other Skills

**Upstream:**
- **Specification Skill**: Provides the requirements that drive design decisions
- **Constraints Skill**: Provides boundaries the design must respect
- **Dependencies Skill**: Provides sequencing and coupling information that shapes component boundaries

**Downstream:**
- **Ticket Breakdown Skill**: Uses architecture decisions, component boundaries, and interface contracts to create technically-informed tickets
- **Audit Skill**: Reviews technical design for completeness and consistency with specifications and constraints

## Revisions

- Re-run this skill when specifications or constraints change in ways that affect architectural decisions
- When re-running, review existing Architecture Decisions first — some may still hold, others may need updating
- Downstream ticket breakdowns that reference this design become potentially stale when the design changes
- If only one Architecture Decision changes, update the specific decision and its downstream references rather than regenerating the entire document

## Notes

- This skill produces the only implementation-specific artifact in the pipeline — technology names, architecture patterns, and component designs are expected and appropriate here
- Not every capability area needs its own technical design — simple capabilities that follow established patterns can be covered by a section in the system-wide design
- Architecture Decisions (AD-XXX) are referenced by tickets the same way requirements (REQ-XXX) are — they provide traceability from "why this approach" to "what to build"
- If the team has an existing Architecture Decision Record (ADR) practice, this skill's output can feed into or replace that process
- System context (`.gener8v/context.md`) is especially valuable for this skill — without it, technology choices are made in a vacuum
