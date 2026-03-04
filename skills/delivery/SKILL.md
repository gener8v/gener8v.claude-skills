# Delivery Skill

## Purpose

Take a single ticket from a ticket breakdown and implement it. This skill operates in two phases: first producing an implementation plan for user approval, then executing the plan by writing actual code. It is the only skill in the pipeline that writes to the real codebase — all other skills produce markdown artifacts in `.gener8v/`. The delivery record captures what was planned, what was built, what decisions were made, and where the implementation diverged from the plan.

## When to Use

Use this skill when:
- A ticket from `.gener8v/tickets/` is ready for implementation (no unresolved blockers in its Depends On field)
- The user wants to implement a specific ticket
- All predecessor tickets (from the Depends On field) have been delivered
- The team is ready to move from planning artifacts to working code

## Input

**Source:** A single ticket from a ticket breakdown, plus all pipeline artifacts referenced in the ticket's Prior Art
**Read from:**
- Ticket breakdown: `.gener8v/tickets/[capability-area-slug].md`
- The specific ticket within that file (identified by TICKET-XXX)
- Prior Art as declared in the ticket (pipeline documents and predecessor ticket outputs)
- Technical Design: `.gener8v/technical-design/[capability-area-slug].md` or `.gener8v/technical-design/system-design.md` (if available)
- Constraints: `.gener8v/constraints/[capability-area-slug].md` (if available)
- System Context: `.gener8v/context.md` (if available)
- Predecessor delivery records: `.gener8v/delivery/*-delivery.md` (for dependent tickets)
- Existing codebase files referenced in Prior Art

**Expects:** A ticket with Summary, Requirements Covered, Prior Art, Acceptance Criteria, Output, Constraints, and Size fields. Predecessor tickets in the Depends On field should have delivery records.

**If input is missing or malformed:**
- If no ticket breakdown exists for the target capability area, stop and recommend running the Ticket Breakdown skill first
- If predecessor tickets have not been delivered, warn the user — the ticket's Prior Art may reference files that do not yet exist
- If technical design or constraints are missing, proceed but note the gap — implementation decisions may lack architectural context

## Output

**Produces:** Two things:
1. The actual code files declared in the ticket's Output section (written to the real codebase)
2. A delivery record documenting what was planned, built, and decided

**Write to:** `.gener8v/delivery/[capability-area-slug]-[ticket-id]-delivery.md`
**Creates directory:** `.gener8v/delivery/` if it does not exist
**Naming convention:** Combines the capability area slug with the lowercase ticket ID (e.g., `search-and-retrieval-ticket-001-delivery.md`)

The delivery record is the bridge between pipeline artifacts and the real codebase. Downstream skills (reviews, audits, orchestrate) read delivery records to locate implemented code.

## Output Format

Produce a markdown document with the following structure:

```markdown
# [Ticket ID]: [Ticket Title] — Delivery Record

## Ticket Reference

**Ticket:** [TICKET-XXX from capability-area-slug]
**Specification:** [Link to specification file]
**Requirements Covered:**
- [XX]-REQ-XXX: [Brief description]
- [XX]-REQ-XXX: [Brief description]

## Implementation Plan

[The plan as approved by the user in Phase 1. Preserved verbatim so
deviations can be compared against the original intent.]

### Planned Files

- [file path]: [what it will contain and why]
- [file path]: [what it will contain and why]

### How Acceptance Criteria Will Be Met

- [Criterion]: [How the plan addresses it]
- [Criterion]: [How the plan addresses it]

## Delivery Summary

**Status:** [Delivered / Partial / Blocked]
**Files Produced:**
- [file path]: [what was actually created or modified — brief description]
- [file path]: [what was actually created or modified — brief description]

## Acceptance Criteria Verification

- [x] [Criterion from ticket] — [how it was satisfied in the delivered code]
- [x] [Another criterion] — [how it was satisfied]
- [ ] [Unsatisfied criterion, if any] — [why not met, what is needed]

## Decisions Made

### DEL-001: [Decision title]

**Context:** [What prompted this decision during implementation]
**Decision:** [What was decided]
**Rationale:** [Why this choice over alternatives]
**Ticket Impact:** [How this affected the implementation vs. what the ticket specified]

### DEL-002: ...

## Deviations from Plan

[What changed from the approved implementation plan and why.
If nothing changed, state "None — implementation followed the approved plan."]

- [Deviation description]: [Why it was necessary and what impact it has on downstream tickets]

## Notes

[Implementation observations, warnings for downstream tickets,
performance considerations, or anything the next developer should know.]
```

---

## Principles

### Plan Before You Build
Never start writing code without presenting the implementation plan to the user first. The plan describes which files will be created or modified, what each will contain, and how acceptance criteria will be met. User approval is the gate between planning and execution. This prevents wasted effort and ensures alignment before code is written.

### Prior Art Is Your Context Window
Read everything the ticket's Prior Art section points to before planning. For first tickets in a chain, this means pipeline documents (specifications, constraints, technical design). For later tickets, this means the actual code files produced by predecessor tickets plus their delivery records. Do not guess what predecessor tickets produced — read the actual files.

### Output Is Your Contract
The ticket's Output section declares what files this delivery produces. Downstream tickets reference those files in their Prior Art. Deliver exactly what was promised — same file paths, same exposed interfaces. If the implementation must diverge from the declared output, document the deviation and its impact on downstream tickets.

### Acceptance Criteria Are Done
A ticket is delivered when all acceptance criteria are satisfied. Not when the code compiles. Not when it looks right. Not when most criteria are met. Each criterion must be verifiable against the delivered code, and the delivery record must show how each was satisfied.

### Decisions Are First-Class
Implementation always surfaces decisions not anticipated by the ticket or technical design. A library choice, an error handling strategy, a data structure selection — these are implementation-time decisions that affect downstream work. Record every non-trivial decision with context and rationale using DEL-XXX IDs. These are the implementation-time equivalent of Architecture Decisions (AD-XXX).

### Deviations Are Expected, Not Failures
Real implementation often diverges from the plan. A dependency behaves differently than expected, an approach proves impractical, a better solution emerges during coding. The delivery record documents what changed and why. Deviations are information for downstream tickets and reviews, not defects.

### Stay in Your Lane
Only implement what this ticket specifies. Do not refactor adjacent code, add unrequested features, or "fix" things you notice in predecessor output. If something needs attention, note it in the delivery record — it belongs in a separate ticket. Scope discipline prevents one ticket from silently changing the foundation that other tickets depend on.

## Process

1. **Locate the Ticket**: Read the ticket breakdown file and extract the target ticket. Confirm the ticket ID and capability area.

2. **Check Prerequisites**: Verify that all tickets listed in the Depends On field have delivery records in `.gener8v/delivery/`. If any are missing, warn the user that Prior Art references may point to files that do not exist.

3. **Read Prior Art**: Follow every item in the ticket's Prior Art section. Read pipeline documents (specifications, constraints, technical design). Read predecessor delivery records and the actual code files they produced. Read system context if available.

4. **Read Technical Design**: If a technical design exists for this capability area, read it for architecture decisions (AD-XXX) that affect this ticket's implementation.

5. **Draft Implementation Plan**: Produce a plan that covers:
   - Every file to be created or modified (aligned with the ticket's Output section)
   - What each file will contain (modules, functions, classes, configuration)
   - How each acceptance criterion will be satisfied
   - Any decisions or trade-offs identified during planning
   - Any constraints from the ticket that shape the implementation

6. **Present Plan to User**: Show the implementation plan and wait for explicit approval. The user may:
   - **Approve**: Proceed to implementation
   - **Modify**: Adjust the plan based on user feedback, then re-present
   - **Reject**: Do not proceed; discuss alternative approaches

7. **Implement**: Write the actual code files as described in the approved plan. Follow the technical design's architecture decisions. Respect constraints referenced in the ticket. Produce the files declared in the ticket's Output section.

8. **Verify Acceptance Criteria**: Walk through each acceptance criterion from the ticket and verify the delivered code satisfies it. For each criterion, note the specific evidence (file, function, behavior) that demonstrates satisfaction.

9. **Record Decisions**: Document any implementation decisions made during coding as DEL-XXX entries with context, decision, rationale, and ticket impact.

10. **Record Deviations**: Compare the delivered implementation against the approved plan. Document anything that changed and why. If the Output files differ from what the ticket declared, note the impact on downstream tickets.

11. **Write Delivery Record**: Save the delivery record to `.gener8v/delivery/[capability-area-slug]-[ticket-id]-delivery.md`.

## Example

### Input

Delivering TICKET-001 from the Search & Retrieval ticket breakdown: "Implement query input interface"

The ticket specifies:
- **Requirements Covered:** SR-REQ-001 (Accept natural language questions as input)
- **Prior Art:** Read `.gener8v/specifications/search-and-retrieval.md`, read `.gener8v/dependencies/dependency-map.md`
- **Acceptance Criteria:** Accepts free-text input of 500+ characters, passes query to search pipeline unmodified, provides in-progress feedback, rejects empty/whitespace queries
- **Output:** `src/search/query-input.{ext}` — query input module
- **Constraints:** None identified
- **Depends On:** None

### Output

#### Phase 1 — Implementation Plan (presented to user)

> **Plan for TICKET-001: Implement query input interface**
>
> **Files to create:**
> - `src/search/query_input.py` — Query input module with `process_query()` function
>
> **Approach:**
> - Define a `process_query(text: str) -> str` function that validates input and returns the cleaned query
> - Validate: reject empty strings, whitespace-only strings, and strings exceeding 10,000 characters
> - Return the query text unmodified (no normalization, no trimming beyond whitespace rejection)
> - Raise `ValueError` with descriptive messages for invalid input
>
> **Acceptance Criteria Mapping:**
> - "Accepts free-text input of 500+ characters" → No upper limit below 10,000; any string up to that length is accepted
> - "Passes query to search pipeline unmodified" → `process_query` returns the input string as-is after validation
> - "Provides in-progress feedback" → Returns a status indicator alongside the query; upstream caller uses this for UI feedback
> - "Rejects empty/whitespace queries" → `ValueError` raised with clear message

#### Phase 2 — Delivery Record

````markdown
# TICKET-001: Implement query input interface — Delivery Record

## Ticket Reference

**Ticket:** TICKET-001 from search-and-retrieval
**Specification:** `.gener8v/specifications/search-and-retrieval.md`
**Requirements Covered:**
- SR-REQ-001: Accept natural language questions as input

## Implementation Plan

[Plan as approved above — preserved verbatim]

### Planned Files

- `src/search/query_input.py`: Query input module with validation and passthrough

### How Acceptance Criteria Will Be Met

- Free-text input of 500+ characters: No restrictive upper limit; tested with 500+ char input
- Passes query unmodified: Returns input string as-is after validation
- In-progress feedback: Returns status indicator for upstream caller
- Rejects empty/whitespace: Raises ValueError with descriptive message

## Delivery Summary

**Status:** Delivered
**Files Produced:**
- `src/search/query_input.py`: Query input module exposing `process_query(text: str) -> QueryResult` with input validation

## Acceptance Criteria Verification

- [x] The system accepts free-text input of at least 500 characters — `process_query` accepts any string up to 10,000 characters; tested with 1,000-character input
- [x] The system passes the query text to the search pipeline without modification — `process_query` returns the original text in `QueryResult.query` without transformation
- [x] The system provides feedback that a search is in progress — `QueryResult` includes a `status` field set to `"processing"`
- [x] Empty or whitespace-only queries are rejected with a clear message — `ValueError("Query must not be empty or whitespace-only")` raised

## Decisions Made

### DEL-001: Use dataclass for query result instead of plain tuple

**Context:** The ticket's Output section describes "a function/method that accepts a string query and returns it to the search pipeline." Need to decide what the return type looks like.
**Decision:** Return a `QueryResult` dataclass with `query` and `status` fields instead of a plain string.
**Rationale:** Downstream tickets (TICKET-003) need both the query text and metadata. A dataclass is self-documenting and extensible without breaking the interface.
**Ticket Impact:** Output contract is slightly richer than specified — downstream Prior Art references will find a `QueryResult` type instead of a bare string.

## Deviations from Plan

None — implementation followed the approved plan.

## Notes

- The 10,000 character upper limit is a safety bound, not a requirement. If downstream needs change, this can be adjusted without affecting the interface contract.
- TICKET-003 should import `QueryResult` from this module for type consistency.
````

---

## Integration with Other Skills

**Upstream:**
- **Ticket Breakdown Skill**: Provides the ticket that defines what to implement — summary, requirements, Prior Art, acceptance criteria, output, constraints, and dependencies
- **Technical Design Skill**: Provides architecture decisions (AD-XXX) that guide implementation choices
- **Specification Skill**: Provides requirement detail referenced in Prior Art
- **Constraints Skill**: Provides constraints referenced in the ticket
- **Dependencies Skill**: Provides sequencing information consumed via ticket dependencies

**Downstream:**
- **Code Review Skill**: Reviews the delivered code against pipeline artifacts (acceptance criteria, requirements, constraints, architecture decisions)
- **Quality Review Skill**: Reviews the delivered code for engineering quality
- **Security Review Skill**: Reviews the delivered code for security vulnerabilities
- **Delivery Skill** (subsequent runs): Later tickets reference this delivery's output in their Prior Art

## Revisions

- A delivery record is not revised after creation — it captures a point-in-time implementation
- If the ticket's requirements change after delivery, create a new ticket for the changes rather than modifying the delivery record
- If a code review or quality review identifies issues, the fixes are a new delivery action (either amending the code with a note in the delivery record, or creating a follow-up ticket)
- Delivery records in `.gener8v/delivery/` are permanent artifacts for traceability

## Notes

- This skill is unique in the pipeline: it writes to the real codebase, not just `.gener8v/`
- The delivery record is the bridge between pipeline artifacts (all in `.gener8v/`) and actual code files
- One delivery per ticket — do not batch multiple tickets into a single delivery
- If a ticket is sized Large, consider whether it should have been split during Ticket Breakdown rather than delivering a monolithic implementation
- The `{ext}` placeholder in ticket Output sections should be resolved during implementation planning based on the system context and technology stack
- When system context (`.gener8v/context.md`) is available, use it to inform language, framework, and convention choices
- Delivery status values: **Delivered** (all acceptance criteria met), **Partial** (some criteria met, others blocked), **Blocked** (cannot proceed due to missing prerequisites or unresolved questions)
