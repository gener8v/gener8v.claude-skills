# Technical Design — worked example

### Input

Designing the "Search & Retrieval" capability from the Support Documentation Search System, using:
- Specification with requirements SR-REQ-001 through SR-REQ-010 and non-functional requirements SR-NFR-001 (p95 search latency ≤ 800 ms at 50 concurrent users, verified by a k6 load test) and SR-NFR-002 (every search request logged with a correlation id and duration, verified by a log-format test)
- Constraints analysis with TC-001 (semantic search needed), TC-002 (stable identifiers needed), OC-001 (24/7 support, near-zero downtime for index updates)
- Dependency map showing DEP-001 (Search & Retrieval → Documentation Ingestion, hard) and the shared resource RES-001 (Document Index)
- System context indicating the team uses Python, runs on AWS, has experience with PostgreSQL, and works in a single repository

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
**Status:** Draft
**Approved by:** pending

## Architecture Decisions

### AD-001: Use vector similarity search for semantic matching

**Context:** SR-REQ-006 requires results even when query terminology differs from documentation. This rules out keyword-only search and requires some form of semantic understanding.
**Decision:** Use vector embeddings for both documentation chunks and queries, with cosine similarity for matching.
**Rationale:** Vector similarity handles terminology mismatch naturally without synonym dictionaries or manual mapping. Aligns with search-and-retrieval/TC-001 from the constraints analysis.
**Alternatives Considered:**
- Keyword search with synonym expansion — Fragile; requires manual maintenance of synonym lists
- Full LLM-based reranking — Higher latency and cost per query; overkill for initial scope and puts SR-NFR-001 at risk
**Consequences:** Requires an embedding model for both indexing and query time. Index size grows with embedding dimensions. Quality depends on embedding model choice.
**Requirements Affected:** SR-REQ-004, SR-REQ-005, SR-REQ-006

### AD-002: Use PostgreSQL with pgvector extension

**Context:** Need a vector store for embeddings. Team already operates PostgreSQL in production (`infra/terraform/rds.tf`, `src/db/session.py`).
**Decision:** Use pgvector extension in existing PostgreSQL infrastructure.
**Rationale:** Avoids introducing a new database technology. Team has PostgreSQL expertise and operational tooling. pgvector supports approximate nearest-neighbor search sufficient for expected scale.
**Alternatives Considered:**
- Dedicated vector database (Pinecone, Weaviate) — Better performance at scale, but adds operational complexity and a new vendor dependency
- Elasticsearch with vector search — Capable, but team lacks Elasticsearch experience
**Consequences:** Performance may become a concern at very high document volumes. Migration path to a dedicated vector store exists if needed.
**Requirements Affected:** SR-REQ-004, SR-REQ-005, SR-REQ-007, SR-NFR-001

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
**Dependencies:** PostgreSQL with pgvector; populated by Documentation Ingestion (RES-001 Document Index)
**Requirements Served:** SR-REQ-004, SR-REQ-006, SR-REQ-007

### Result Ranker

**Responsibility:** Order raw results by relevance, attach source attribution, return bounded result set
**Interfaces:**
- `rank(results: list[RawResult]) -> list[RankedResult]`: Returns ordered, attributed results
**Dependencies:** Query Processor (for query context), Search Index (for raw results)
**Requirements Served:** SR-REQ-005, SR-REQ-008, SR-REQ-009, SR-REQ-010

### Search Request Logger

**Responsibility:** Attach a correlation id to every search request and emit one structured log line with the id, query length, result count and duration
**Interfaces:**
- `log_search(correlation_id: str, query_len: int, result_count: int, duration_ms: int) -> None`: Emits the structured record
**Dependencies:** Application logging pipeline
**Requirements Served:** SR-NFR-002

## Data Model

### DocumentChunk

**Purpose:** Stores a searchable segment of documentation with its embedding
**Key Fields:**
- `id`: Unique identifier
- `content`: Text excerpt
- `embedding`: Vector representation
- `source_title`: Title of the source document
- `source_ref`: Stable URI/path to the source location (search-and-retrieval/TC-002)
- `source_system`: Which documentation system this came from
**Relationships:** Many chunks per source document
**Source:** Created by Documentation Ingestion capability

## Interface Contracts

### Search API

**Between:** Results Presentation ↔ Query Processor / Result Ranker
**Purpose:** The single entry point Results Presentation calls to run a search
**Input:** `query: str` (non-blank; at least 500 characters accepted, SR-REQ-002), `limit: int` (default 10)
**Output:** Ordered `list[RankedResult]`, each with `excerpt`, `score`, `source_title`, `source_ref`, `source_system`; the response carries the request's correlation id
**Error Cases:** Empty or whitespace-only query → `400` with a message the caller can show (SR-REQ-003); embedding service unavailable → `503`, logged with the correlation id

## Infrastructure Requirements

- PostgreSQL instance with pgvector extension enabled: driven by AD-002; the HNSW index it provides is what keeps SR-NFR-001 reachable at 50 concurrent users
- Embedding model access (API or self-hosted) for query-time embedding generation: driven by AD-001; its round-trip time is the largest single contributor to SR-NFR-001's latency budget
- Sufficient storage for embedding vectors (dimensionality × document count × 4 bytes): driven by AD-001 and the Search Index component
- Structured application logging with per-request correlation ids: serves SR-NFR-002; also the evidence the k6 run for SR-NFR-001 reads duration from
- Index rebuilds run against a shadow table and swap atomically: serves search-and-retrieval/OC-001 (near-zero downtime for index updates)

## Technical Risks

- **TR-001**: pgvector query performance at scale is unproven for this team
  - *Likelihood:* Low (expected document volume is modest)
  - *Impact:* Search latency degrades; SR-NFR-001 (p95 ≤ 800 ms) is missed
  - *Mitigation:* Benchmark with representative data volume early using the SR-NFR-001 k6 load test; decide index parameters (HNSW `m`, `ef_search`) from the results
  - *Related Constraints:* search-and-retrieval/TC-001
  - *Related NFRs:* SR-NFR-001
- **TR-002**: Embedding service latency is outside the team's control
  - *Likelihood:* Medium
  - *Impact:* Query-time embedding dominates the latency budget under load; SR-NFR-001 fails while the rest of the pipeline is within target
  - *Mitigation:* Measure embedding round-trip separately in the load test (the per-request duration log from SR-NFR-002 is how the split is observed); cache embeddings for repeated queries; keep a self-hosted fallback model as an option (TQ-001)
  - *Related Constraints:* —
  - *Related NFRs:* SR-NFR-001

## Open Technical Questions

- [ ] **TQ-001**: Which embedding model should be used? (Affects quality, latency, cost, and whether SR-NFR-001 is achievable with a hosted API)
- [ ] **TQ-002**: What chunk size produces the best search results? (Requires experimentation)
- [ ] **TQ-003**: Should the system support hybrid search (vector + keyword) for improved precision?

## Assumptions

- Assumption: pgvector is available or can be enabled on the existing PostgreSQL instance (confirmed: `infra/terraform/rds.tf` provisions PostgreSQL 16; the extension is not yet enabled, so the first index ticket must carry the `CREATE EXTENSION vector` migration)
- Assumption: Query volume is low enough that embedding generation per query is acceptable latency
- Assumption: A single embedding model is sufficient for all documentation sources
````
