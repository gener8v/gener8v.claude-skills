# Brownfield — worked example

This example onboards an existing Support Documentation Search System that was built without
pipeline artifacts. It shows every phase's output in abbreviated form: the reconnaissance with its
Repositories table, the capability groupings, one as-is specification with approval lines and a
populated `@spec Coverage`, the synthesized PRD, the `@spec` annotations in source, and what the
first change afterwards looks like. Everything written here is a living baseline; no
`changes/<change-slug>/` directory is created.

## Input

A workspace directory containing two repositories:

- `api/` — a TypeScript service (Node.js, Fastify) exposing a `/search` endpoint, backed by
  PostgreSQL with pgvector; ingestion jobs under `api/src/ingest/` pull from three documentation
  sources
- `web/` — a React application (TypeScript, Vite) that support agents use to search
- No formal requirements or design documents
- A README in each repository with setup instructions; a k6 load-test script in `api/load/`
- `.gener8v/` does not exist

## Output (abbreviated)

### Phase 1 — Reconnaissance summary → `.gener8v/brownfield/reconnaissance.md`

> **Project:** Support documentation search — TypeScript workspace, two repositories
> **API:** Fastify on Node 20, PostgreSQL 16 + pgvector, OpenAI-compatible embeddings client
> **Web:** React 18, TypeScript, Vite
> **Jobs:** Ingestion runs as a scheduled Fastify plugin (`api/src/ingest/scheduler.ts`)
> **Tests:** Vitest in both repositories — ~55% coverage in `api/`, ~30% in `web/`; k6 load test in `api/load/search.js` with a p95 ≤ 800 ms threshold
> **Documentation:** Two READMEs with setup steps, no architecture docs
> **Notable:** 2 route groups (`search`, `admin/ingest`), 4 database tables (`documents`, `chunks`, `sources`, `search_log`), 3 ingestion adapters (Confluence, help-center scrape, Markdown repo)
>
> **Repositories**
>
> | Directory | Purpose | Language / build | Verify commands |
> |-----------|---------|------------------|-----------------|
> | `api/` | Search API and documentation ingestion | TypeScript / npm | `npm test`, `npm run lint`, `npm run typecheck` |
> | `web/` | Agent-facing search UI | TypeScript (React) / npm | `npm test`, `npm run lint` |

The user confirms the summary and adds that the help-center scrape adapter is "fragile and not
really supported". That note goes into the reconnaissance file and later becomes an Open Question
on the Documentation Ingestion specification.

### Phase 2 — System context → `.gener8v/context.md`

The `## Repositories` table above is carried into `context.md` verbatim, followed by the technology
stack, the architecture (a single API process with an in-process scheduler; the web app talks to it
over JSON), conventions, external integrations (Confluence REST API, the legacy help center, the
embeddings provider), build/deployment and testing sections.

### Phase 3 — Capability groupings (one of several proposed) → `.gener8v/brownfield/capability-areas.md`

> **Option A: By user capability** *(selected)*
> 1. **Search & Retrieval** (`SR`) — accept a question, run the vector query, rank results (`api/src/search/`, `api/src/db/chunks.ts`)
> 2. **Results Presentation** (`RP`) — render results, source titles and links, loading and error states (`web/src/pages/Search.tsx`, `web/src/components/Results.tsx`)
> 3. **Documentation Ingestion** (`DI`) — pull, chunk, embed and index documents from three sources (`api/src/ingest/`, `api/src/db/documents.ts`)
>
> **Option B: By data flow** — Ingestion Pipeline, Index, Query Path, Presentation
> **Option C: By integration surface** — Confluence Sync, Help-Center Sync, Markdown Sync, Search API, Web Client

The user selects Option A. The approved list — name, slug, requirement prefix, summary, key code
locations (root-relative), touchpoints — is written to `capability-areas.md` before Phase 4 starts.

### Phase 4 — Specification (abbreviated, one area) → `.gener8v/specifications/search-and-retrieval.md`

````markdown
# Search & Retrieval Specification

## Overview

Support agents submit a natural-language question and receive ranked documentation excerpts drawn from every indexed source. This is the as-is behaviour of `api/src/search/`; it describes what the code does today.

## Source Context

**Parent PRD:** (synthesized in Phase 5)
**Requirement prefix:** SR
**Status:** Draft
**Approved by:** pending
**Related Capabilities:** Results Presentation, Documentation Ingestion

## Functional Requirements

### Query Processing

- **SR-REQ-001**: The system accepts free-text natural language questions as search input
- **SR-REQ-002**: The system accepts queries of at least 500 characters (the request schema caps input at 2,000)
- **SR-REQ-003**: The system rejects an empty query with the message "Enter a question to search"; a whitespace-only query is trimmed to empty *after* validation and returns an empty result set instead of the message (see OQ-001)

### Search Execution

- **SR-REQ-004**: The system returns documentation excerpts that are relevant to the query
- **SR-REQ-005**: The system ranks results by relevance, with the most relevant result first
- **SR-REQ-006**: The system returns relevant results when the query uses different terminology than the source documentation (vector similarity over embeddings)
- **SR-REQ-007**: The system returns results from all indexed documentation sources, not just a single source

### Source Attribution

- **SR-REQ-008**: The system indicates the source document title for each result
- **SR-REQ-009**: The system provides a stable reference to the source location for each result
- **SR-REQ-010**: The system attributes results consistently regardless of which documentation source they originate from

## Non-Functional Requirements

- **SR-NFR-001**: p95 search latency ≤ 800 ms at 50 concurrent users — **verified by:** the k6 load test in `api/load/search.js`, whose threshold encodes this target
- **SR-NFR-002**: Every search request is logged with a correlation id and its duration — **verified by:** `api/test/search/logging.test.ts`, which asserts both fields on the emitted record

## Behaviors & Rules

- Results are limited to the top 20 chunks by cosine similarity; there is no relevance threshold — a query that matches nothing well still returns 20 results
- ...

## Open Questions

- [ ] **OQ-001**: Whitespace-only queries bypass the empty-query message (SR-REQ-003). The user has flagged this as a bug; the specification records the current behaviour until a change fixes it
- [ ] **OQ-002**: No relevance threshold exists — is "20 results regardless of quality" intended?

## @spec Coverage

| Requirement | Code Location(s) |
|-------------|------------------|
| SR-REQ-001 | `api/src/search/query.ts:parseQuery` |
| SR-REQ-002 | `api/src/search/schema.ts:searchRequestSchema` |
| SR-REQ-003 | `api/src/search/query.ts:parseQuery` |
| SR-REQ-004 | `api/src/search/retrieve.ts:retrieveChunks` |
| SR-REQ-005 | `api/src/search/rank.ts:rankResults` |
| SR-REQ-006 | `api/src/search/retrieve.ts:retrieveChunks`, `api/src/search/embed.ts:embedQuery` |
| SR-REQ-007 | `api/src/db/chunks.ts:queryAllSources` |
| SR-REQ-008 | `api/src/search/attribute.ts:attachSource` |
| SR-REQ-009 | `api/src/search/attribute.ts:attachSource` |
| SR-REQ-010 | Emergent — each ingestion adapter writes the same `sources` row shape (`api/src/ingest/*/adapter.ts`); no single location enforces it |
| SR-NFR-001 | `api/load/search.js` (threshold) |
| SR-NFR-002 | `api/src/search/routes.ts:searchHandler` |
````

The user **approves** the specification with one correction (the 2,000-character cap in SR-REQ-002
was 1,000 in an older schema still referenced by the README — the code wins). Source Context becomes:

```markdown
**Status:** Approved
**Approved by:** Product Owner — A. Reviewer, 2026-08-26
```

Baseline requirements carry no priority or change tag. Compare the Specification skill's worked
example, where the same ten requirements are introduced by the `support-search` change and each
line carries `*(must · change: support-search)*` — that tag names the change that introduced the
requirement, and the brownfield baseline was introduced by none.

### Phase 5 — PRD (abbreviated) → `.gener8v/prd.md`

```markdown
# Support Documentation Search System

**Status:** Draft
**Approved by:** pending

## Problem Context

Support agents answer customer questions from documentation spread across Confluence, a legacy help center and a Markdown repository. Before this system, finding the right page meant searching each source separately with exact keywords. The system indexes all three sources and answers natural-language questions with ranked, source-attributed excerpts.

## Goals

- Agents find the relevant documentation from one search box, regardless of source or wording
- Every result names its source document and links to a stable location
- New and changed documentation is searchable without manual re-indexing

## Functional Capabilities

### Search & Retrieval
Accepts natural-language questions, retrieves and ranks excerpts across all indexed sources. See `specifications/search-and-retrieval.md` (SR-REQ-001..010, SR-NFR-001..002).

### Results Presentation
Renders ranked results with source title and link, loading and error states. See `specifications/results-presentation.md`.

### Documentation Ingestion
Pulls, chunks, embeds and indexes documents from three sources on a schedule. See `specifications/documentation-ingestion.md`.

## Out of Scope

- Answer generation — the system returns excerpts, it does not compose answers
- Search across customer tickets or chat transcripts

## Open Questions

- [ ] **OQ-001**: The help-center scrape adapter is described by the team as unsupported; is that source still in scope? (Carried from reconnaissance; see documentation-ingestion/OQ-001)
```

On approval, `**Status:** Approved` / `**Approved by:** Product Owner — A. Reviewer, 2026-08-26`
replace the two lines, and `**Parent PRD:** Support Documentation Search System` is back-filled into
every specification written in Phase 4.

### Phase 6 — `@spec` annotations

```typescript
// api/src/search/query.ts

// @spec SR-REQ-001, SR-REQ-003
export function parseQuery(raw: string): ParsedQuery {
  ...
}
```

```typescript
// api/src/search/rank.ts

// @spec SR-REQ-005
export function rankResults(chunks: ScoredChunk[]): RankedResult[] {
  ...
}
```

```typescript
// api/src/search/routes.ts

// @spec SR-NFR-002
export async function searchHandler(req: FastifyRequest, reply: FastifyReply) {
  ...
}
```

The annotation summary presented to the user lists eleven annotated IDs and one of the twelve that
could not be tied to a single location (SR-REQ-010 — recorded as emergent in `@spec Coverage`).

## What happens next

Onboarding wrote living artifacts only. The first initiative — say, fixing OQ-001 and adding a
relevance threshold — starts with `/planning`, which amends `prd.md` in place (with a `## Change
Log` entry) and opens `changes/search-relevance-v2/change.md`. Specification then amends
`specifications/search-and-retrieval.md`: SR-REQ-003 gains `*(amended 2026-09-02 by
search-relevance-v2)*` with the corrected text, and a new `- **SR-REQ-011** *(must · change:
search-relevance-v2)*: …` is appended above the current maximum. Ticket Breakdown writes one file
per ticket under `changes/search-relevance-v2/tickets/search-and-retrieval/` (`TICKET-001.md`, … plus
`backlog.md`), and Delivery runs `api/`'s verify commands from the Repositories table. Nothing from
onboarding is regenerated.
