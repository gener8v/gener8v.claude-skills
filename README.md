# gener8v Claude Skills

A structured pipeline for turning ideas into delivered, reviewed code. Fourteen skills that take a user prompt from raw intent through requirements, specification, constraint analysis, dependency mapping, technical design, ticket breakdown, implementation, and code review — with audit and orchestration skills that keep the pipeline on track. Works for greenfield and brownfield projects alike. Each designed for LLM-driven execution.

## The Pipeline

```
                         Setup (bootstrap pipeline + CLAUDE.md)
                                        │
               ┌────────────────────────┴────────────────────────┐
               ▼                                                 ▼
Greenfield: Planning                              Brownfield: Brownfield
               │                                  (maps existing code into
               ▼                                   pipeline artifacts)
         Specification → Constraints → Dependencies → Technical Design → Ticket Breakdown
               ↑             ↑              ↑              ↑               ↑
               └─────────────┴──────────────┴──────────────┴───────────────┘
                                              Audit

                                    ┌─→ Code Review
Ticket Breakdown → Delivery ────────┼─→ Quality Review
                                    └─→ Security Review
                                    (run in parallel after delivery)

                                           Orchestrate
                              (status + pipeline-state.yaml at any point)
```

Each skill produces structured markdown that feeds into the next. The Delivery skill is unique — it writes real code files (with `@spec` annotations for traceability) and a delivery record. The three review skills (Code Review, Quality Review, Security Review) can run in parallel after delivery, each evaluating the code from a different perspective. The Audit skill can review any stage — or trace consistency across all of them. The Orchestrate skill reads the current state, writes a machine-readable `pipeline-state.yaml`, and guides you to what's next. Every skill is independently usable, but they're strongest as a sequence.

## Skills

### [Setup](./skills/setup/)

Bootstraps the gener8v pipeline in a project. Creates the `.gener8v/` directory structure, initializes `pipeline-state.yaml`, and patches the project's `CLAUDE.md` with pipeline activation directives so the workflow activates automatically on every session and code change.

**Input:** A project directory
**Output:** `.gener8v/` directory structure + `CLAUDE.md` with pipeline directives

### [Planning](./skills/planning/)

Transforms a user prompt into a structured Product Requirements Document (PRD). Groups work into 3-7 capability areas with functional requirements, user scenarios, scope boundaries, and open questions. Optionally captures system context for downstream skills.

**Input:** A user describing what they want built
**Output:** PRD + optional system context file

### [Brownfield](./skills/brownfield/)

Maps an existing codebase into the gener8v pipeline. Works bottom-up: reads the code, derives specifications with requirement IDs, synthesizes a PRD, and adds `@spec` annotations to existing source files. After brownfield onboarding, the project has a complete artifact set and is ready for any downstream skill.

**Input:** An existing codebase with working code
**Output:** System context + specifications + PRD + `@spec` annotations in source code

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

### [Delivery](./skills/delivery/)

Takes a single ticket and implements it in two phases: first producing an implementation plan for user approval, then writing the actual code. The only skill that writes to the real codebase. Embeds `@spec` annotations in delivered code to link functions and classes back to their requirement IDs. Produces a delivery record tracking what was planned, built, decided, and where the implementation diverged from the plan.

**Input:** A ticket from Ticket Breakdown, with Prior Art, Technical Design, and Constraints
**Output:** Real code files (with `@spec` annotations) + delivery record with acceptance criteria verification

### [Code Review](./skills/code-review/)

Reviews implemented code against pipeline artifacts. Verifies that the delivery satisfies its ticket's acceptance criteria, traces to requirements, respects constraints, follows the technical design, and includes correct `@spec` annotations. Produces traceability tables and findings with interactive resolution.

**Input:** A delivery record + delivered code + pipeline artifacts (ticket, spec, constraints, technical design)
**Output:** Code review report with traceability tables, `@spec` annotation coverage, and verdict

### [Quality Review](./skills/quality-review/)

Reviews implemented code for engineering quality independent of pipeline artifacts. Evaluates code organization, readability, error handling, test coverage, and adherence to established patterns. Does not check whether the code matches the spec — that is Code Review's job.

**Input:** Delivered code files (+ system context for calibration)
**Output:** Quality review report with ratings, findings, and verdict

### [Security Review](./skills/security-review/)

Performs an OWASP-informed, code-level security review. Checks for injection vulnerabilities, authentication gaps, data exposure, misconfigurations, dependency vulnerabilities, and cryptographic issues. Attack scenarios required for Medium+ findings. Compliance constraints (CC-XXX) violations are auto-Critical.

**Input:** Delivered code files (+ constraints for compliance, technical design for auth patterns)
**Output:** Security review report with OWASP-referenced findings and verdict

### [Audit](./skills/audit/)

Reviews pipeline artifacts for gaps, inconsistencies, missing coverage, and unresolved ambiguity. Works interactively with the user to resolve findings. Covers the full pipeline: PRD structure, specification atomicity, constraint categorization, dependency completeness, technical design rationale, ticket coverage, delivery record verification, code review traceability, quality review completeness, and security review OWASP compliance. Cross-stage checks trace requirements from specification through delivery and verify that review verdicts are consistent.

**Input:** Any artifact(s) in `.gener8v/`
**Output:** Audit report with findings + direct updates to source artifacts

### [Orchestrate](./skills/orchestrate/)

Reads the current state of `.gener8v/` and tells you where the pipeline stands and what to run next. Writes a persistent `pipeline-state.yaml` with machine-readable state that other tools and CI/CD pipelines can query. Tracks coverage across capability areas through the full lifecycle — from specification through delivery and reviews. In the delivery stage, shifts to ticket-level tracking with per-ticket delivery and review status. Recommends running Code Review, Quality Review, and Security Review in parallel after each delivery.

**Input:** Current state of `.gener8v/` directory
**Output:** `pipeline-state.yaml` + coverage matrix (including Delivered/CR/QR/SEC columns), pipeline stage, and ordered next steps

## Design Principles

- **Functional over technical** — describe what, not how (except where constraints and technical design are the focus)
- **Ambiguity becomes open questions** — never assume, always surface
- **Parseable by downstream agents** — structured output that LLMs can consume
- **Readable by non-technical stakeholders** — where possible
- **Independently usable** — each skill works standalone, even if strongest in sequence
- **Revision-aware** — every skill documents what triggers re-running and what becomes stale
- **Traceable to the code** — `@spec` annotations embed requirement IDs directly in source code, making traceability greppable and permanent
- **Brownfield-ready** — existing codebases are first-class citizens, not afterthoughts

## Scale Guidance

Not every project needs the full pipeline. Match the depth to the scope:

- **Light (1-2 capability areas, well-understood domain):** Planning → Specification → Ticket Breakdown → Delivery → Reviews. Skip Constraints, Dependencies, and Technical Design if the work is self-contained and the implementation approach is obvious. Reviews can be selective — Security Review may be sufficient for low-risk code.
- **Standard (3-5 areas, moderate complexity):** The full pipeline through Delivery and all three Reviews. Run each skill in sequence. Use Orchestrate to track progress. Run all three reviews in parallel after each delivery.
- **Deep (6+ areas, complex or cross-team):** Run the full pipeline, but consider grouping related capability areas into sub-pipelines. Use Orchestrate heavily to manage fan-out. Run Audit at milestones, not just at the end. Delivery creates significant fan-out (each ticket is a delivery + 3 reviews), so track at the ticket level.

## Project Structure

```
skills/
  setup/SKILL.md             # Bootstrap pipeline + CLAUDE.md directives
  planning/SKILL.md          # Prompt → PRD + system context
  brownfield/SKILL.md        # Existing code → pipeline artifacts + @spec annotations
  specification/SKILL.md     # Capability area → detailed spec
  constraints/SKILL.md       # PRD or spec → constraint analysis
  dependencies/SKILL.md      # PRD + specs → dependency map
  technical-design/SKILL.md  # Specs + constraints → architecture decisions
  ticket-breakdown/SKILL.md  # Spec → implementable tickets
  delivery/SKILL.md          # Ticket → implemented code (with @spec) + delivery record
  code-review/SKILL.md       # Delivery → pipeline traceability + @spec verification
  quality-review/SKILL.md    # Delivery → engineering quality review
  security-review/SKILL.md   # Delivery → OWASP security review
  audit/SKILL.md             # Any artifact(s) → audit report
  orchestrate/SKILL.md       # Pipeline status + pipeline-state.yaml
.claude-plugin/
  plugin.json                # Plugin metadata
  marketplace.json           # Marketplace listing
```

Skills are discovered by convention: each subdirectory under `skills/` contains a `SKILL.md` that defines the skill's purpose, input/output, format, principles, and process.

### Pipeline Artifacts (`.gener8v/`)

When skills run, they produce artifacts in a `.gener8v/` directory in the project root:

```
.gener8v/
  pipeline-state.yaml                 # Machine-readable pipeline state (auto-generated by Orchestrate)
  prd.md                              # Planning output (or Brownfield synthesis)
  context.md                          # System context (optional, or from Brownfield)
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
  delivery/
    search-and-retrieval-ticket-001-delivery.md  # One per ticket delivered
  reviews/
    search-and-retrieval-ticket-001-code-review.md     # Pipeline traceability + @spec coverage
    search-and-retrieval-ticket-001-quality-review.md   # Engineering quality
    search-and-retrieval-ticket-001-security-review.md  # OWASP security
  audits/
    pipeline-audit.md                 # Audit reports
```

## Getting Started

### Greenfield (new project)

```bash
/setup          # Bootstrap pipeline + CLAUDE.md directives
/planning       # Create PRD from your idea
/orchestrate    # See what's next
```

### Brownfield (existing code)

```bash
/setup          # Bootstrap pipeline + CLAUDE.md directives
/brownfield     # Map existing code into pipeline artifacts
/orchestrate    # See what's next
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
