# gener8v Claude Skills

A structured pipeline for turning ideas into implementable work. Eight skills that take a user prompt from raw intent through requirements, specification, constraint analysis, dependency mapping, technical design, and ticket breakdown — with audit and orchestration skills that keep the pipeline on track. Each designed for LLM-driven execution.

## The Pipeline

```
Prompt → Planning → Specification → Constraints → Dependencies → Technical Design → Ticket Breakdown
            ↑             ↑              ↑              ↑               ↑                  ↑
            └─────────────┴──────────────┴──────────────┴───────────────┴──────────────────┘
                                              Audit

                                           Orchestrate
                                    (status + next steps at any point)
```

Each skill produces structured markdown that feeds into the next. The Audit skill can review any stage — or trace consistency across all of them. The Orchestrate skill reads the current state and guides you to what's next. Every skill is independently usable, but they're strongest as a sequence.

## Skills

### [Planning](./skills/planning/)

Transforms a user prompt into a structured Product Requirements Document (PRD). Groups work into 3-7 capability areas with functional requirements, user scenarios, scope boundaries, and open questions. Optionally captures system context for downstream skills.

**Input:** A user describing what they want built
**Output:** PRD + optional system context file

### [Specification](./skills/specification/)

Takes a single Capability Area from a PRD and produces a detailed functional specification. Enumerates atomic, testable requirements with namespaced IDs ([PREFIX]-REQ-XXX), defines behaviors and business rules, surfaces edge cases, and documents data requirements.

**Input:** One capability area from a Planning output
**Output:** Detailed spec with namespaced requirements, behaviors, edge cases

### [Constraints](./skills/constraints/)

Analyzes a PRD or Specification to surface what the system must operate within. Categorizes constraints as technical, compliance, integration, or operational — and maps how they interact with each other and the requirements. When system context is available, grounds analysis in the actual technology stack.

**Input:** A PRD or Specification (+ system context if available)
**Output:** Categorized constraints with rationale, impact mapping, and risk flags

### [Dependencies](./skills/dependencies/)

Maps dependencies between capability areas, external systems, and shared resources. Produces a dependency graph, sequencing analysis, parallelization opportunities, and critical path identification.

**Input:** A PRD with multiple capability areas, plus any Specifications and Constraints analyses
**Output:** Dependency map with suggested phasing and risk dependencies

### [Technical Design](./skills/technical-design/)

Bridges the gap between functional specification and implementation. Translates requirements, constraints, and dependencies into architecture decisions, technology choices, component boundaries, and interface contracts.

**Input:** Specifications + Constraints + Dependencies + system context
**Output:** Architecture decisions, component design, data model, interface contracts

### [Ticket Breakdown](./skills/ticket-breakdown/)

Decomposes a fully specified capability into implementable work items. Each ticket has acceptance criteria, requirement traceability, constraint awareness, relative sizing, and dependency ordering. When a Technical Design is available, tickets reference architecture decisions.

**Input:** A Specification, with Constraints, Dependencies, and Technical Design
**Output:** Ready-to-implement tickets with a backlog summary

### [Audit](./skills/audit/)

Reviews pipeline artifacts for gaps, inconsistencies, missing coverage, and unresolved ambiguity. Works interactively with the user to resolve findings. Checks include namespaced ID traceability, cross-stage coverage, staleness detection, and technical design consistency.

**Input:** Any artifact(s) in `.gener8v/`
**Output:** Audit report with findings + direct updates to source artifacts

### [Orchestrate](./skills/orchestrate/)

Reads the current state of `.gener8v/` and tells you where the pipeline stands and what to run next. Tracks coverage across capability areas, handles fan-out guidance (which areas still need specs, constraints, etc.), and adapts recommendations to project scale.

**Input:** Current state of `.gener8v/` directory
**Output:** Coverage matrix, pipeline stage, and ordered next steps

## Design Principles

- **Functional over technical** — describe what, not how (except where constraints and technical design are the focus)
- **Ambiguity becomes open questions** — never assume, always surface
- **Parseable by downstream agents** — structured output that LLMs can consume
- **Readable by non-technical stakeholders** — where possible
- **Independently usable** — each skill works standalone, even if strongest in sequence
- **Revision-aware** — every skill documents what triggers re-running and what becomes stale

## Scale Guidance

Not every project needs the full pipeline. Match the depth to the scope:

- **Light (1-2 capability areas, well-understood domain):** Planning → Specification → Ticket Breakdown. Skip Constraints, Dependencies, and Technical Design if the work is self-contained and the implementation approach is obvious.
- **Standard (3-5 areas, moderate complexity):** The full pipeline. Run each skill in sequence. Use Orchestrate to track progress.
- **Deep (6+ areas, complex or cross-team):** Run the full pipeline, but consider grouping related capability areas into sub-pipelines. Use Orchestrate heavily to manage fan-out. Run Audit at milestones, not just at the end.

## Project Structure

```
skills/
  planning/SKILL.md          # Prompt → PRD + system context
  specification/SKILL.md     # Capability area → detailed spec
  constraints/SKILL.md       # PRD or spec → constraint analysis
  dependencies/SKILL.md      # PRD + specs → dependency map
  technical-design/SKILL.md  # Specs + constraints → architecture decisions
  ticket-breakdown/SKILL.md  # Spec → implementable tickets
  audit/SKILL.md             # Any artifact(s) → audit report
  orchestrate/SKILL.md       # Pipeline status + next steps
.claude-plugin/
  plugin.json                # Plugin metadata
  marketplace.json           # Marketplace listing
```

Skills are discovered by convention: each subdirectory under `skills/` contains a `SKILL.md` that defines the skill's purpose, input/output, format, principles, and process.

### Pipeline Artifacts (`.gener8v/`)

When skills run, they produce artifacts in a `.gener8v/` directory in the project root:

```
.gener8v/
  prd.md                              # Planning output
  context.md                          # System context (optional)
  specifications/
    search-and-retrieval.md           # One per capability area
    results-presentation.md
  constraints/
    prd.md                            # PRD-level constraints
    search-and-retrieval.md           # Spec-level constraints
  dependencies/
    dependency-map.md                 # One per PRD
  technical-design/
    search-and-retrieval.md           # One per capability area
    system-design.md                  # Cross-cutting (optional)
  tickets/
    search-and-retrieval.md           # One per specification
  audits/
    pipeline-audit.md                 # Audit reports
```

## Installation

### Clone and Copy

```bash
git clone https://github.com/gener8v/gener8v.claude-skills.git
cp -r gener8v.claude-skills/skills/* ~/.claude/skills/
```

## License

[MIT](./LICENSE)

— gener8v
