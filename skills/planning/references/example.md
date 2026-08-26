# Planning — worked example

Planning writes two files for a first initiative: the living PRD at `.gener8v/prd.md` and the change brief at `.gener8v/changes/support-search/change.md`. The change slug `support-search` is derived from the change title "Support search" with the slug rule in `CONVENTIONS.md` §3.

## Input

> "I need a way for our support team to quickly find answers from our documentation when customers ask questions. Search over our docs is a must; nice result formatting can come second, and we don't need suggested replies yet."

## Output 1: `.gener8v/prd.md`

````markdown
# Support Documentation Search System

**Status:** Draft
**Approved by:** pending

## Problem Context

The support team currently searches documentation manually when responding to customer inquiries. This is time-consuming and leads to inconsistent answers. A system that surfaces relevant documentation quickly would improve response time and answer quality.

## Goals

- The system should reduce time spent searching for documentation
- The system should surface the most relevant information for a given question
- The system should be usable without training or specialized knowledge

## Functional Capabilities

### Search & Retrieval

- The system should accept natural language questions as input
- The system should return relevant documentation excerpts ranked by relevance
- The system should indicate the source document for each result
- The system should handle questions even when exact terminology doesn't match

### Results Presentation

- The system should display results in a scannable format
- The system should allow users to navigate to the full source document
- The system should highlight the most relevant portions of returned content

### Documentation Ingestion

- The system should process existing documentation in its current format
- The system should support updates when documentation changes
- The system should handle multiple documentation sources

## User Scenarios

**Scenario: Answering a Product Question**
A support agent receives a customer question about return policies. They type the question into the search system and immediately see three relevant excerpts from the returns documentation, with the most specific policy highlighted. They copy the relevant text into their response.

**Scenario: Handling an Unfamiliar Topic**
A new support agent encounters a technical question they've never seen. They search the system using the customer's exact wording. The system returns relevant results despite the terminology mismatch, helping the agent learn while responding accurately.

## Out of Scope

- This work does not include automated response generation (results are for agent reference)
- This work does not include customer-facing search
- This work does not include documentation authoring or editing capabilities
- Future consideration: suggested responses based on search results

## Open Questions

- [ ] What documentation sources should be included initially?
- [ ] Are there existing categories or tags in the documentation to leverage?
- [ ] Should search history or frequently accessed docs be surfaced?
- [ ] What is the expected query volume?

## Change Log

- 2026-08-26 — opened; capability areas Search & Retrieval, Results Presentation, Documentation Ingestion (Planning, change: support-search)
````

## Output 2: `.gener8v/changes/support-search/change.md`

````markdown
# Support search

**Status:** Draft
**Approved by:** pending
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
| Search & Retrieval | adds area | (pending specification) |
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
````

## What happens next

Specification runs once per affected area (`specification Search & Retrieval for support-search`) and replaces the pending cell with the IDs it allocated. After the Search & Retrieval pass the row reads:

```markdown
| Search & Retrieval | adds area | Adds SR-REQ-001..010, SR-NFR-001..002; Modifies —; Withdraws — |
```

and the brief's Change Log gains `2026-08-26 — SR specification amended: adds SR-REQ-001..010, SR-NFR-001..002 (Specification)`. Ticket Breakdown then reads the Priority Cut and writes `changes/support-search/tickets/search-and-retrieval.md`. When the Product Owner approves the PRD and the brief in conversation, both documents' `**Status:**` lines become `Approved` and `**Approved by:**` names them with the date.
