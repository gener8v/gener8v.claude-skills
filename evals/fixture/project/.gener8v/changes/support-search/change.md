# Support search

**Status:** Approved
**Approved by:** Product Owner, 2026-08-27
**Opened:** 2026-08-26
**Slug:** support-search

## Why
Support agents answer customer questions by searching documentation by hand, which is slow and produces inconsistent answers. Three documentation sources exist and none of them is searchable from one place. Response time and answer consistency are the support team's current top complaints, so a search capability is the first initiative on this product.

## Outcome
- A support agent can type a customer's question in natural language and see relevant documentation excerpts, most relevant first
- Every result names its source document and links to it
- Results come from all indexed documentation sources, and the index can be refreshed when documentation changes
- Results are scannable, with the most relevant portion of each excerpt highlighted

## Affected Capability Areas

| Area | Kind | Requirements |
|------|------|--------------|
| Search & Retrieval | adds area | SR-REQ-001–SR-REQ-010 |
| Results Presentation | adds area | (pending specification) |
| Documentation Ingestion | adds area | (pending specification) |

## Priority Cut
- **Must:** natural-language search over the initial documentation sources, with results ranked by relevance and matching despite terminology differences, fast enough to use during a live customer conversation (the latency target is set in Specification); ingestion of the initial sources into a searchable index
- **Should:** source document indicated for every result with a stable reference to it; every search request logged so operators can trace it; navigation from a result to the full source document; index updates when documentation changes
- **Could / later:** highlighting the most relevant portion of each excerpt; search history or frequently accessed documents

## Out of Scope
- Automated response generation and suggested replies
- Customer-facing search
- Documentation authoring or editing

## Open Questions
- [ ] **OQ-001**: Which documentation sources are in the initial index? (Carried from PRD)
- [ ] **OQ-002**: What query volume should the first release handle? (Carried from PRD; becomes an NFR target in Specification)

## Change Log
- 2026-08-26 — opened (Planning)
