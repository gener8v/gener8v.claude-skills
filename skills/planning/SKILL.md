# Planning Skill

## Purpose

Transform a user prompt into a structured Product Requirements Document (PRD) that describes the functional capabilities needed to satisfy the request. The output is designed for downstream decomposition by LLM agents into phases, detailed specifications, and tickets.

## When to Use

Use this skill when:
- A user describes a new feature, product, or system they want built
- A user has a problem statement that needs translation into requirements
- Work needs to be scoped before technical planning begins

## Input

**Source:** User prompt (natural language description of what they want built)
**Location:** Provided directly by the user in conversation. No file input required.

## Output

**Produces:** A Product Requirements Document (PRD) in markdown
**Write to:** `.gener8v/prd.md` in the project root
**Creates directory:** `.gener8v/` if it does not exist

The output file is the single entry point for all downstream skills. Downstream skills reference this path to locate the PRD.

### System Context (Optional)

After producing the PRD, ask the user whether they want to provide system context — information about their existing technology stack, infrastructure, team capabilities, and organizational constraints. If provided, write to `.gener8v/context.md` as freeform markdown.

This file is not required for the pipeline to proceed, but significantly improves the quality of Constraints analysis and Technical Design. Without it, those skills infer constraints from functional documents alone.

## Output Format

Produce a markdown document with the following structure:

```markdown
# [Descriptive Title]

## Problem Context

[2-4 sentences describing the problem or opportunity this work addresses.
What is the current state? Why does this matter?]

## Goals

[Bulleted list of 2-5 high-level outcomes this work should achieve.
These are directional, not measurable criteria.]

- The system should...
- The system should...

## Functional Capabilities

[Group capabilities into logical areas. Each area will be further defined
by downstream skills. Use "the system should..." framing.]

### [Capability Area 1]

- The system should [verb] [what] [context/condition if needed]
- The system should...

### [Capability Area 2]

- The system should...

## User Scenarios

[2-4 narrative scenarios that illustrate how the capabilities come together.
These ground the requirements in realistic usage patterns.]

**Scenario: [Title]**
[Brief narrative of a user accomplishing something with the system]

## Out of Scope

[Explicitly list what this work does NOT include. This prevents scope creep
and clarifies boundaries for downstream planning.]

- This work does not include...
- Future consideration: ...

## Open Questions

[Capture ambiguity, unknowns, and decisions that need stakeholder input.
These should be resolved before or during detailed specification.]

- [ ] Question about...
- [ ] Decision needed on...
```

---

## Principles

### Functional Over Technical
Describe **what** the system should do, not **how** it should be implemented. Avoid mentioning specific technologies, architectures, or implementation approaches unless they are explicit constraints from the user.

**Good:** "The system should allow users to upload documents and extract key information automatically."

**Avoid:** "The system should use S3 for storage and call an LLM API to parse PDFs."

### Balanced Granularity
Break work into major capability areas (typically 3-7) that are meaningful but not exhaustive. Each area should be substantial enough to warrant its own detailed specification pass, but not so broad that it obscures important distinctions.

### Capture Ambiguity Explicitly
When the user prompt is vague or leaves room for interpretation, do not assume. Instead:
1. Make a reasonable interpretation for the PRD
2. Document the assumption in Open Questions
3. Flag decisions that need stakeholder input

### Scope Boundaries
Be explicit about what is out of scope. This is especially important for:
- Adjacent features that seem related but aren't requested
- Future phases or enhancements
- Integrations or dependencies not mentioned

## Process

1. **Parse Intent**: Read the user prompt and identify the core problem or outcome they're seeking.

2. **Identify Capability Areas**: What major functional areas does this work span? Group related capabilities together.

3. **Draft Capabilities**: For each area, enumerate what the system should do using clear, testable statements.

4. **Ground in Scenarios**: Write 2-4 user scenarios that demonstrate the capabilities working together.

5. **Define Boundaries**: Explicitly list what's out of scope to prevent future confusion.

6. **Surface Unknowns**: Capture any ambiguity, missing information, or decisions needed as open questions.

7. **Review for Technical Leakage**: Scan the document and remove any implementation-specific language.

## Example

### Input
> "I need a way for our support team to quickly find answers from our documentation when customers ask questions."

### Output

````markdown
# Support Documentation Search System

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
````

---

## Integration with Other Skills

This skill produces output that feeds into:
- **Specification Skill**: Takes each Capability Area and produces detailed functional specifications
- **Constraints Skill**: Analyzes the PRD for technical, compliance, or integration constraints
- **Dependencies Skill**: Maps dependencies between capability areas and external systems
- **Technical Design Skill**: Translates specifications and constraints into architecture decisions
- **Ticket Breakdown Skill**: Decomposes specified capabilities into implementable work items
- **Orchestrate Skill**: Reads the PRD to determine pipeline status and next steps

## Revisions

- Re-running this skill overwrites `.gener8v/prd.md` — all downstream artifacts (specifications, constraints, dependencies, technical designs, tickets) become potentially stale
- If the change is limited to one capability area, consider updating the PRD manually and re-running only the affected downstream skills
- If capability areas are added or removed, the Orchestrate skill can identify which downstream artifacts need to be created or are now orphaned
- System context (`.gener8v/context.md`) does not need to be regenerated when the PRD changes unless the project scope shifts significantly

## Notes

- Do not include time estimates; these are determined during ticket breakdown
- Do not include acceptance criteria; these are defined during specification
- Keep the document readable by non-technical stakeholders
- The PRD should be understandable without access to the original prompt
