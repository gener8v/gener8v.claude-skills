# gener8v Claude Skills

A structured pipeline for turning ideas into implementable work. Six skills that take a user prompt from raw intent through requirements, specification, constraint analysis, dependency mapping, and ticket breakdown — with an audit skill that catches gaps at any stage. Each designed for LLM-driven execution.

## The Pipeline

```
Prompt → Planning → Specification → Constraints → Dependencies → Ticket Breakdown
            ↑             ↑              ↑              ↑               ↑
            └─────────────┴──────────────┴──────────────┴───────────────┘
                                       Audit
```

Each skill produces structured markdown that feeds into the next. The Audit skill can review any stage — or trace consistency across all of them. Every skill is independently usable, but they're strongest as a sequence.

## Skills

### [Planning](./skills/planning/)

Transforms a user prompt into a structured Product Requirements Document (PRD). Groups work into 3-7 capability areas with functional requirements, user scenarios, scope boundaries, and open questions.

**Input:** A user describing what they want built
**Output:** PRD with capability areas ready for specification

### [Specification](./skills/specification/)

Takes a single Capability Area from a PRD and produces a detailed functional specification. Enumerates atomic, testable requirements (REQ-XXX), defines behaviors and business rules, surfaces edge cases, and documents data requirements.

**Input:** One capability area from a Planning output
**Output:** Detailed spec with numbered requirements, behaviors, edge cases

### [Constraints](./skills/constraints/)

Analyzes a PRD or Specification to surface what the system must operate within. Categorizes constraints as technical, compliance, integration, or operational — and maps how they interact with each other and the requirements.

**Input:** A PRD or Specification
**Output:** Categorized constraints with rationale, impact mapping, and risk flags

### [Dependencies](./skills/dependencies/)

Maps dependencies between capability areas, external systems, and shared resources. Produces a dependency graph, sequencing analysis, parallelization opportunities, and critical path identification.

**Input:** A PRD with multiple capability areas, plus any Specifications and Constraints analyses
**Output:** Dependency map with suggested phasing and risk dependencies

### [Ticket Breakdown](./skills/ticket-breakdown/)

Decomposes a fully specified capability into implementable work items. Each ticket has acceptance criteria, requirement traceability, constraint awareness, relative sizing, and dependency ordering.

**Input:** A Specification, with Constraints and Dependencies analyses
**Output:** Ready-to-implement tickets with a backlog summary

### [Audit](./skills/audit/)

Reviews pipeline artifacts for gaps, inconsistencies, missing coverage, and unresolved ambiguity. Works interactively with the user to resolve findings — approving fixes, modifying recommendations, or deferring issues. Can audit a single document or trace completeness across the entire pipeline.

**Input:** Any artifact(s) in `.gener8v/`
**Output:** Audit report with findings + direct updates to source artifacts

## Design Principles

- **Functional over technical** — describe what, not how (except where constraints are the focus)
- **Ambiguity becomes open questions** — never assume, always surface
- **Parseable by downstream agents** — structured output that LLMs can consume
- **Readable by non-technical stakeholders** — where possible
- **Independently usable** — each skill works standalone, even if strongest in sequence

## Project Structure

```
skills/
  planning/SKILL.md        # Prompt → PRD
  specification/SKILL.md   # Capability area → detailed spec
  constraints/SKILL.md     # PRD or spec → constraint analysis
  dependencies/SKILL.md    # PRD + specs → dependency map
  ticket-breakdown/SKILL.md # Spec → implementable tickets
  audit/SKILL.md           # Any artifact(s) → audit report
.claude-plugin/
  plugin.json              # Plugin metadata
  marketplace.json         # Marketplace listing
```

Skills are discovered by convention: each subdirectory under `skills/` contains a `SKILL.md` that defines the skill's purpose, input/output, format, principles, and process.

## Installation

### Clone and Copy

```bash
git clone https://github.com/gener8v/gener8v.claude-skills.git
cp -r gener8v.claude-skills/skills/* ~/.claude/skills/
```

## License

[MIT](./LICENSE)

— gener8v
