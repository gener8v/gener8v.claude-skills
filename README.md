# gener8v Claude Skills

A structured pipeline for turning ideas into delivered, reviewed code. Nineteen skills take a user prompt from raw intent through requirements, specification, constraint analysis, dependency mapping, technical design, ticket breakdown, implementation, and review — with audit, orchestration, and a small runtime (hooks, agents, scripts) that keep the pipeline's state in front of every session. Works for greenfield and brownfield projects alike, for one initiative or many, in one repository or a workspace of several. Each skill is designed for LLM-driven execution.

## The Pipeline

```
                         Setup (bootstrap: .gener8v/, CONVENTIONS.md, state, CLAUDE.md)
                                        │
               ┌────────────────────────┴────────────────────────┐
               ▼                                                 ▼
Greenfield: Planning                              Brownfield: Brownfield
  (amends prd.md, opens a change)                 (maps existing code into the living baseline)
               │                                                 │
               ▼                                                 ▼
         Specification → Constraints → Dependencies → Technical Design      living artifacts,
               ↑             ↑              ↑              ↑                amended in place,
               └─────────────┴──────────────┴──────────────┘                IDs append-only
                                              Audit

   changes/<change-slug>/                          ┌─→ Code Review      ┐  findings phase runs in parallel
   change.md → Ticket Breakdown → Delivery ────────┼─→ Quality Review   │  (reviewer agents, fresh context);
                                                   └─→ Security Review  ┘  resolution runs with the user

              System-level assessments (any time code exists)
              OWASP Top 10 Review · OWASP LLM Top 10 Review · Architecture Review

              Standalone (no PRD, ticket or spec required)
              Flow Mapping — current-state data flows, as diagrams that compile
              Defect Sweep — sweep a subsystem's perimeter, in a fresh context

                                           Orchestrate
                    (status, pipeline-state.yaml, metrics and next steps — also injected at session start)
```

Two kinds of artifact. **Living** artifacts — the PRD, specifications, constraints, dependencies, technical design — describe the product and are amended in place; their IDs are append-only because code carries `@spec` annotations that point at them. **Change** artifacts — a change brief, tickets, delivery records, reviews — belong to one initiative and live under `.gener8v/changes/<change-slug>/`. Planning opens a change; Specification amends the living specifications and records the deltas in the brief; Ticket Breakdown, Delivery and the reviews work inside the change. A second initiative is a second change, not an overwrite.

The Delivery skill is unique — it writes real code files (with `@spec` annotations for traceability), keeps its delivery record current from reconciliation onward, and runs the project's tests before it calls anything delivered. The three review skills each have a findings phase, which can run in parallel as fresh-context agents, and a resolution phase, which runs with the user. The Audit skill can review any stage — or trace consistency across all of them. The Orchestrate skill regenerates a machine-readable `pipeline-state.yaml` from the artifacts and guides you to what's next. Every skill is independently usable, but they're strongest as a sequence.

## Skills

### [Setup](./skills/setup/)

Bootstraps the gener8v pipeline in a project. Creates the `.gener8v/` directory structure (including `changes/`), installs `.gener8v/CONVENTIONS.md` (the rules every skill follows), generates `pipeline-state.yaml`, and adds a short `## gener8v Pipeline` section to the project's `CLAUDE.md` — replaced in place on re-run, never duplicated.

**Input:** A project directory
**Output:** `.gener8v/` structure + `CONVENTIONS.md` + `pipeline-state.yaml` + `CLAUDE.md` directives

### [Planning](./skills/planning/)

Transforms a user prompt into a structured Product Requirements Document (PRD) and opens a change. Groups work into 3-7 capability areas with functional requirements, user scenarios, scope boundaries, and open questions; the change brief (`changes/<slug>/change.md`) records why, the intended outcome, the affected areas, and the priority cut — what is Must, Should, and Could. When a PRD already exists, amends it in place and records a Change Log entry rather than overwriting the baseline.

**Input:** A user describing what they want built
**Output:** PRD (created or amended) + change brief + optional system context file

### [Brownfield](./skills/brownfield/)

Maps an existing codebase into the gener8v pipeline. Works bottom-up: reads the code, derives specifications with requirement IDs, synthesizes a PRD, and adds `@spec` annotations to existing source files. Each phase's approved output is checkpointed to `.gener8v/brownfield/` so an interrupted run resumes instead of restarting. Records the repository (or repositories, for a workspace) in `context.md`. The first feature afterwards is a change like any other.

**Input:** An existing codebase with working code
**Output:** System context + specifications + PRD + `@spec` annotations in source code

### [Specification](./skills/specification/)

Takes a single Capability Area from a PRD and produces a detailed functional specification. Enumerates atomic, testable requirements with namespaced IDs ([PREFIX]-REQ-XXX), non-functional requirements with measurable targets and a named verification method ([PREFIX]-NFR-XXX), behaviors and business rules, edge cases, and data requirements. Requirements introduced by a change carry the change's tag; IDs are append-only, so a re-run amends and never renumbers. Writes the requirement deltas back into the change brief.

**Input:** One capability area from a PRD, for a change
**Output:** Detailed spec with namespaced requirements, NFRs, behaviors, edge cases

### [Constraints](./skills/constraints/)

Analyzes a PRD or Specification to surface what the system must operate within. Categorizes constraints as technical, compliance, integration, or operational — and maps how they interact with each other and the requirements. Constraints are boundaries; the specification's NFRs are targets. When system context is available, grounds analysis in the actual technology stack; where the repository can confirm a constraint, cites it.

**Input:** A PRD or Specification (+ system context if available)
**Output:** Categorized constraints with rationale, impact mapping, and risk flags

### [Dependencies](./skills/dependencies/)

Maps dependencies between capability areas, external systems, and shared resources. Produces a dependency graph, sequencing analysis, parallelization opportunities, and critical path identification.

**Input:** A PRD with multiple capability areas, plus any Specifications and Constraints analyses
**Output:** Dependency map with suggested phasing and risk dependencies

### [Technical Design](./skills/technical-design/)

Bridges the gap between functional specification and implementation. Translates requirements, constraints, and dependencies into architecture decisions, technology choices, component boundaries, and interface contracts — after verifying that the infrastructure it builds on actually exists. Infrastructure requirements and technical risks cite the NFRs they serve.

**Input:** Specifications + Constraints + Dependencies + system context (+ flow maps if present)
**Output:** Architecture decisions, component design, data model, interface contracts

### [Ticket Breakdown](./skills/ticket-breakdown/)

Decomposes a fully specified capability — for one change — into implementable work items, **one ticket per file**. Each ticket has a Priority (Must / Should / Could) and a one-line Value, acceptance criteria, requirement and NFR traceability, constraint awareness, Prior Art (verified to exist), an Output contract that includes the tests, Known Hazards, relative sizing, and dependency ordering; `backlog.md` alongside carries the overview, dependency chain and suggested ordering. Also the path by which sweep findings, deferred review findings and flagged bugs become tickets.

**Input:** A Specification and the change brief, with Constraints, Dependencies, and Technical Design
**Output:** `changes/<slug>/tickets/<area>/TICKET-NNN.md` (one per ticket) + `backlog.md`

### [Delivery](./skills/delivery/)

Takes a single ticket and implements it in three phases: reconciling the ticket's assumptions against the real codebase, producing an implementation plan for Engineer approval, then writing the code. The only skill that writes source on a ticket. Writes the delivery record at reconciliation, again at plan approval (`In Progress`, with a progress checklist), and finally after a recorded Verification Run — tests, lint, type-check, build, NFR checks where executable — so nothing the user approved lives only in the conversation. Names the repository it changes, embeds `@spec` annotations and appends the specification's `@spec Coverage` rows.

**Input:** A ticket from a change, with Prior Art, Technical Design, Constraints, and predecessor reviews
**Output:** Real code files (with `@spec` annotations) + a delivery record with verification evidence

### [Code Review](./skills/code-review/)

Reviews implemented code against pipeline artifacts. Verifies that the delivery satisfies its ticket's acceptance criteria, traces to requirements and NFRs, respects constraints, follows the technical design, includes correct `@spec` annotations, and that its Verification Run reproduces. Produces traceability tables and findings; resolution is interactive.

**Input:** A delivery record + delivered code + pipeline artifacts (ticket, spec, constraints, technical design)
**Output:** Code review report with traceability tables, `@spec` annotation coverage, and verdict

### [Quality Review](./skills/quality-review/)

Reviews implemented code for engineering quality independent of pipeline artifacts. Evaluates code organization, readability, error handling, test coverage (by running the tests), observability and operability, and adherence to established patterns. Does not check whether the code matches the spec — that is Code Review's job.

**Input:** Delivered code files (+ system context for calibration)
**Output:** Quality review report with ratings, findings, and verdict

### [Security Review](./skills/security-review/)

Performs an OWASP-informed, code-level security review. Checks for injection vulnerabilities, authentication gaps, data exposure, misconfigurations, dependency vulnerabilities, and cryptographic issues. Attack scenarios required for Medium+ findings. Compliance constraints (CC-XXX) violations are auto-Critical; risk acceptance is recorded with the Security role's name.

**Input:** Delivered code files (+ constraints for compliance, technical design for auth patterns)
**Output:** Security review report with OWASP-referenced findings and verdict

### [OWASP Top 10 Review](./skills/owasp-top10-review/)

Framework-coverage complement to Security Review. Walks all ten OWASP Top 10:2025 categories top-down — assessing posture in each, mapping the per-ticket security reviews' findings onto the taxonomy, and verifying the categories a bottom-up pass tends to miss (insecure deserialization, security-event logging, fail-open error handling, SSRF). Where Security Review finds bugs, this proves coverage and surfaces missed categories.

**Input:** Codebase + IaC/CI + existing security reviews (optional)
**Output:** OWASP Top 10:2025 coverage assessment with a category matrix and re-ranked priorities

### [OWASP LLM Top 10 Review](./skills/owasp-llm-top10-review/)

Category-by-category assessment of an AI/LLM application against the OWASP Top 10 for LLM Applications 2025. Covers risks the web Top 10 misses: prompt injection (direct and indirect via retrieved content), sensitive-information disclosure through model I/O, data/model poisoning, improper output handling, excessive agency, system-prompt leakage, and unbounded consumption (denial-of-wallet).

**Input:** LLM orchestration code (prompts, clients, retrieval, telemetry, cost) + existing security reviews (optional)
**Output:** OWASP LLM Top 10:2025 assessment with a category matrix, findings, and positive controls

### [Architecture Review](./skills/architecture-review/)

Adversarial, code-grounded review of an existing system's architecture. Asks three questions in order: is it real (do the architecture decisions match the running code), is it right for a system of this nature, and what are its inherent limitations — with every "better decision" proven against the actual code as a runnable sketch, never a vendor reflex.

**Input:** The codebase + whatever architecture intent exists (ADRs, technical design, prior reviews)
**Output:** `.gener8v/reviews/[system]-architecture-assessment.md` with theses, a reality audit, and prioritised recommendations

### [Flow Mapping](./skills/flow-mapping/)

Turns current-state data-flow findings into Mermaid diagrams that compile, read clearly, and state their own maturity. Pairs a deterministic validator (`scripts/validate-flows.sh` — compilation via `mmdc`, plus structural lints for unlabelled edges, missing reliability classes, absent cadence, and oversized graphs) with an LLM review pass for what a lint cannot decide.

Asserts what *is*, evidenced — flows nobody described go in an explicit **Unknowns** list rather than into the diagram. Current-state only; not for future-state architecture proposals.

**Input:** `data-flow` / `system-map` / `integration-map` deliverables, flow triples, or interview evidence
**Output:** `.gener8v/flows/[domain-slug].md` per domain — prose, Mermaid diagrams, reliability classes, and Unknowns. Gate: the validator must exit 0.

**Requires:** `npx` (Node). Fetches `@mermaid-js/mermaid-cli@11` on first run — the only skill with an external runtime dependency.

### [Defect Sweep](./skills/defect-sweep/)

Searches existing code for defects nobody is looking for. Unlike the review skills, it is not anchored to a delivery — it takes a subsystem and sweeps its **perimeter** for known defect classes: inherited defaults, sibling writers, incomplete gates, fail-open error paths, silent truncation, stale assertions, identity confusion, time-based inference, unasked authorization, and over-serving the client. Every finding names a circumstance in which something breaks and carries proof.

Building and sweeping are different modes, so the skill forks into the `defect-sweeper` agent — a fresh context that has not read the builder's reasoning. Findings to fix now become tickets in the active change.

**Input:** A subsystem, named by directory, feature or entry point (no `.gener8v/` artifacts required)
**Output:** `.gener8v/sweeps/[subsystem-slug]-sweep.md` — findings ordered by consequence, classes swept clean, and a verdict that names the tickets to raise

### [Audit](./skills/audit/)

Reviews pipeline artifacts for gaps, inconsistencies, missing coverage, and unresolved ambiguity. Works interactively with the user to resolve findings, writing the report first and updating it as decisions are made. Covers the full pipeline — PRD through reviews, plus change briefs, flow maps, sweeps and assessments — with cross-stage checks that trace requirements from specification through delivery, verify review verdicts against `pipeline-state.yaml`, confirm IDs have never been renumbered, and warn when a stage was produced from an unapproved upstream. A reconciliation mode checks a ticket or externally-authored plan against the real codebase (Go / Blocked). The check lists live in `references/checks.md`.

**Input:** Any artifact(s) in `.gener8v/`
**Output:** Dated audit report with findings + direct updates to source artifacts

### [Orchestrate](./skills/orchestrate/)

Reports where the pipeline stands and what to run next. The inventory is deterministic — `scripts/gener8v-state.py` scans `.gener8v/`, reads every change brief, delivery record and review verdict, and writes `pipeline-state.yaml` — and the skill adds the judgement: scale, correctness risk, what to defer, when a sweep or an assessment is due. Reports per change, orders ready tickets by priority, shows the derived metrics, and recommends the one-time migration for a legacy layout.

**Input:** Current state of `.gener8v/`
**Output:** `pipeline-state.yaml` + per-change coverage, stage, metrics, and ordered next steps

## Runtime

The skills are prose; a few things need to be mechanical. The plugin ships:

- **`hooks/hooks.json`** — three hooks, active only when the project has a `.gener8v/` directory:
  - `SessionStart` (startup, resume, clear, compact): regenerates `pipeline-state.yaml`, injects a compact summary with next steps, and appends a line to `runs.jsonl`. After a compaction it also points the session at any delivery record that is `In Progress`. Nobody has to remember to run `/orchestrate`.
  - `PreToolUse` on Write/Edit: denies hand-edits to `pipeline-state.yaml` (it is generated), and adds a one-line reminder when source is edited while no delivery is in progress. It does not block — reviews, Brownfield and trivial fixes legitimately touch source.
  - `PostToolUse` on Write/Edit: regenerates the state file after any write under `.gener8v/` and logs the write to `runs.jsonl`.
- **`agents/`** — `code-reviewer`, `quality-reviewer`, `security-reviewer` (the findings phase of each review, safe to run in parallel because they only write their report) and `defect-sweeper` (the fresh pass Defect Sweep forks into).
- **`scripts/gener8v-state.py`** — `state` writes the YAML (schema version 4: living coverage per area, one entry per change with its tickets, active changes, approvals pending); `summary` prints what the hook injects; `lint` reports prefix collisions, requirements and NFRs in no ticket, tickets missing required sections, a ticket directory with no `backlog.md`, a legacy per-area ticket file, delivered requirements with no `@spec` annotation, dangling references, and change briefs that disagree with the specifications; `metrics` derives verdict distributions, finding counts, rework rate, verification pass rate, deferred reviews, approvals pending, sweep findings, lead time (from git) and session counts (from `runs.jsonl`); `split-tickets` turns a legacy per-area ticket file into the one-file-per-ticket directory plus `backlog.md` (`--remove` deletes the original). Python 3, no dependencies.
- **`scripts/check-install.sh`** — reports drift between the repository and a copied `~/.claude/skills/` install (and, once the plugin is installed, which copies still linger).
- **`skills/flow-mapping/scripts/validate-flows.sh`** — the Flow Mapping gate.
- **`skills/*/references/`** — worked examples (one canonical project across every skill), Audit's check lists, Defect Sweep's defect classes, and the conventions Setup installs. Loaded when a skill needs them, not on every invocation.

Running the script by hand (the hooks and Orchestrate do this for you):

```bash
S="$HOME/.claude/plugins/cache/gener8v-claude-skills/gener8v/$(ls "$HOME/.claude/plugins/cache/gener8v-claude-skills/gener8v" | sort -V | tail -1)/scripts/gener8v-state.py"
python3 "$S" summary            # what the SessionStart hook injects
python3 "$S" state              # rewrite .gener8v/pipeline-state.yaml
python3 "$S" lint               # exit 1 on an ERROR (prefix collision, uncovered requirement, brief/spec mismatch)
python3 "$S" metrics            # derived metrics, YAML on stdout
python3 "$S" state --json       # the state as JSON, for CI
python3 "$S" split-tickets      # migrate per-area ticket files to one file per ticket (--remove deletes the originals)
```

**Requirements.** Python 3.8+ for the hooks and the state script (without it the hooks stay silent and Orchestrate scans by hand); Node with `npx` for Flow Mapping's validator; git, if you want lead-time metrics.

Periodic work — sweeps over high-consequence subsystems, dependency-vulnerability re-checks, posture reviews at milestones — is a good use of a scheduled routine (`/schedule`) or a cron-driven session. Orchestrate names the triggers; the cadence is the project's decision, so the plugin ships no schedule.

## Design Principles

- **Functional over technical** — describe what, not how (except where constraints and technical design are the focus)
- **Ambiguity becomes open questions** — never assume, always surface
- **Verify against ground truth before escalating** — when code, schema, config, or an existing artifact can answer a question, read it and answer it; surface to the user only what genuinely remains undecided. A plan's stated premises ("builds on existing schema," "table X already exists," "script Y runs the checks") are claims to verify, not facts to trust
- **Verified, not inspected** — a ticket is delivered when an executed check proves each acceptance criterion and the delivery record says which command and exit code; reading the code and finding it plausible is not verification
- **The record, not the conversation** — anything the user approved is written to `.gener8v/` the moment it is approved; a compaction or a new session resumes from the file
- **Living artifacts are amended; changes are added** — specifications describe the product and are never regenerated; each initiative is a change with its own tickets, deliveries and reviews
- **One ticket, one file** — a ticket is a single action item that is read, delivered and reviewed alone, so it lives in its own `TICKET-NNN.md`, self-describing, next to its delivery record and reviews
- **IDs are append-only** — requirement, constraint, decision and ticket IDs are never renumbered or reused; code carries `@spec` annotations that point at them
- **Priorities and targets are explicit** — every ticket says Must, Should or Could and what the user gets; every non-functional requirement names a measurable target and how it is verified
- **Roles are named** — the record says which hat approved what (Product Owner, Architect, Engineer, Security), and the reviewer is never the builder's context
- **Regex first, model second** — inventories, slugs, coverage, status and metrics are computed by scripts; the model's attention goes to judgement
- **Parseable by downstream agents** — structured output that LLMs can consume; vocabularies shared across skills (`CONVENTIONS.md`)
- **Readable by non-technical stakeholders** — where possible
- **Independently usable** — each skill works standalone, even if strongest in sequence
- **Revision-aware** — every skill documents what triggers re-running and what becomes stale
- **Traceable to the code** — `@spec` annotations embed requirement IDs directly in source code, making traceability greppable and permanent
- **Brownfield-ready** — existing codebases are first-class citizens, not afterthoughts

## Scale Guidance

Not every project needs the full pipeline. Match the depth to the scope:

- **Light (1-2 capability areas, well-understood domain):** Planning → Specification → Ticket Breakdown → Delivery → Reviews. Skip Constraints, Dependencies, and Technical Design if the work is self-contained and the implementation approach is obvious. Reviews can be selective — record the deferral in the delivery record (`**Reviews Deferred:** quality — pure validation code`) so the ticket can still reach `done`.
- **Standard (3-5 areas, moderate complexity):** The full pipeline through Delivery and all three Reviews. Run each skill in sequence. Use Orchestrate to track progress. Run the three reviews' findings phases in parallel after each delivery.
- **Deep (6+ areas, complex or cross-team):** Run the full pipeline, but consider grouping related capability areas into sub-pipelines — or into several changes that can be delivered independently. Use Orchestrate heavily to manage fan-out. Run Audit at milestones, not just at the end. Delivery creates significant fan-out (each ticket is a delivery + 3 reviews), so track at the ticket level.

Depth should also track **correctness risk, not just capability-area count.** A small, well-understood feature that nonetheless carries a data-integrity, tenant-isolation, or security-critical invariant earns the heavy treatment *on that piece* — full specification, technical design, and all three reviews — even when the rest of the work is Light. Conversely, do not wrap low-risk CRUD-over-existing-schema in ceremony it doesn't need: per-item approval gates and stop-and-report checkpoints are for the parts where getting it wrong is expensive, not for surfacing-existing-data screens.

## Definition of Done

A ticket is **done** when its delivery record says `Delivered`, its Verification Run passed, and each of the three reviews is either `Approved` / `Approved with Notes` or explicitly deferred in the delivery record. A change is **complete** when every ticket under it is done. `pipeline-state.yaml` carries `done: true|false` per ticket and `status: complete` per change, derived from those lines — not from whether files exist. A `Changes Required` verdict from any review holds the ticket at `changes_required` until it is resolved.

A CI gate reads those fields — no dependencies beyond Python 3:

```bash
python3 scripts/gener8v-state.py state --json \
  | python3 -c 'import sys,json; s=json.load(sys.stdin); \
      open=[f"{c}/{t}" for c,ch in s["changes"].items() for t,e in ch["deliveries"].items() if e["delivery"] and not e["done"]]; \
      print("open:",open); sys.exit(1 if open else 0)'
```

`scripts/gener8v-state.py lint` is the other gate worth running in CI: it exits 1 on a requirement prefix used by two specifications, a requirement in no ticket, or a change brief that lists requirement IDs the specification does not contain.

## Workspaces

`.gener8v/` lives at the root you work from — one repository, or a workspace directory that contains several. `context.md` lists the repositories (directory, purpose, language and build, verify commands); every code path in every artifact is root-relative (`api/src/search/query.ts`); Delivery names the repository it changes, runs its verify commands and commits there. Hooks and the state script take the workspace root, and the `@spec` lint walks every repository beneath it.

## Project Structure

```
skills/
  setup/SKILL.md                   # Bootstrap: .gener8v/, CONVENTIONS.md, state, CLAUDE.md directives
  setup/references/conventions.md  # The shared rules, installed into every project as .gener8v/CONVENTIONS.md
  planning/SKILL.md                # Prompt → PRD (amended in place) + change brief
  brownfield/SKILL.md              # Existing code → living baseline + @spec annotations (checkpointed)
  specification/SKILL.md           # Capability area (for a change) → REQ + NFR spec; deltas into the brief
  constraints/SKILL.md             # PRD or spec → constraint analysis
  dependencies/SKILL.md            # PRD + specs → dependency map
  technical-design/SKILL.md        # Specs + constraints → architecture decisions
  ticket-breakdown/SKILL.md        # Spec + change brief → one TICKET-NNN.md per ticket under changes/<slug>/tickets/<area>/
  delivery/SKILL.md                # Ticket → verified code (with @spec) + delivery record
  code-review/SKILL.md             # Delivery → pipeline traceability + @spec verification
  quality-review/SKILL.md          # Delivery → engineering quality review (incl. observability)
  security-review/SKILL.md         # Delivery → OWASP security review
  owasp-top10-review/SKILL.md      # Codebase → OWASP Top 10:2025 coverage assessment
  owasp-llm-top10-review/SKILL.md  # LLM app → OWASP LLM Top 10:2025 assessment
  architecture-review/SKILL.md     # Existing system → adversarial, code-grounded architecture assessment
  flow-mapping/SKILL.md            # Flow evidence → validated Mermaid current-state diagrams
  flow-mapping/scripts/validate-flows.sh
  defect-sweep/SKILL.md            # Subsystem → perimeter defect sweep (forks into defect-sweeper)
  defect-sweep/references/defect-classes.md
  audit/SKILL.md                   # Any artifact(s) → audit report
  audit/references/checks.md       # The check lists, by artifact and across stages
  orchestrate/SKILL.md             # Pipeline status + pipeline-state.yaml + metrics
  */references/example.md          # One canonical worked example, per skill
agents/
  code-reviewer.md                 # Findings phase of Code Review, fresh context
  quality-reviewer.md              # Findings phase of Quality Review
  security-reviewer.md             # Findings phase of Security Review
  defect-sweeper.md                # The fresh pass Defect Sweep forks into
hooks/
  hooks.json                       # SessionStart / PreToolUse / PostToolUse
scripts/
  gener8v-state.py                 # state | summary | lint | metrics | split-tickets  (Python 3, no dependencies)
  session-start.sh                 # SessionStart hook
  pre-write.sh                     # PreToolUse hook
  post-write.sh                    # PostToolUse hook
  check-install.sh                 # Drift check for copied installs
.claude-plugin/
  plugin.json                      # Plugin manifest (name: gener8v)
  marketplace.json                 # Marketplace listing
```

Every `SKILL.md` carries YAML frontmatter — `name`, a trigger `description`, an `argument-hint` for per-target skills (`<capability area> [for <change-slug>]` on Specification and Ticket Breakdown; `<capability area> <TICKET-XXX> [in <change-slug>]` on Delivery and the reviews — the change is optional when exactly one is active), `disable-model-invocation` on the three that change the repository or `CLAUDE.md` (Setup, Brownfield, Delivery), and `context: fork` + `agent: defect-sweeper` on Defect Sweep. Per-target skills read `$ARGUMENTS` and ask for the target if it is missing.

### Pipeline Artifacts (`.gener8v/`)

When skills run, they produce artifacts in a `.gener8v/` directory at the project (or workspace) root:

```
.gener8v/
  CONVENTIONS.md                      # Installed by Setup — paths, vocabularies, ID rules, roles, write authority
  pipeline-state.yaml                 # GENERATED by scripts/gener8v-state.py (hook, Orchestrate, CI)
  runs.jsonl                          # Appended by the hooks — session starts and artifact writes
  prd.md                              # Living: Planning amends (with a Change Log); Brownfield synthesizes
  context.md                          # Living: system context, incl. the ## Repositories table
  brownfield/
    reconnaissance.md                 # Brownfield Phase 1 checkpoint
    capability-areas.md               # Brownfield Phase 3 checkpoint — the durable area → code mapping
  specifications/
    search-and-retrieval.md           # Living, one per area: REQ + NFR, change-tagged; ## @spec Coverage appended by Delivery
    results-presentation.md
  constraints/
    prd.md                            # PRD-level constraints (read by every downstream skill)
    search-and-retrieval.md           # Spec-level constraints
  dependencies/
    dependency-map.md                 # One per PRD
  technical-design/
    search-and-retrieval.md           # One per capability area
    system-design.md                  # Cross-cutting (optional)
  changes/
    support-search/
      change.md                       # The change brief: why, outcome, affected areas + requirement deltas, priority cut
      tickets/
        search-and-retrieval/         # One directory per area touched by this change
          backlog.md                  # Overview, dependency chain, suggested ordering
          TICKET-001.md               # One ticket, one file
          TICKET-002.md
      delivery/
        search-and-retrieval-ticket-001-delivery.md   # Written at reconciliation, plan approval, and delivery
      reviews/
        search-and-retrieval-ticket-001-code-review.md
        search-and-retrieval-ticket-001-quality-review.md
        search-and-retrieval-ticket-001-security-review.md
    search-relevance-v2/              # The next initiative — its own brief, tickets, deliveries, reviews
  reviews/
    acme-owasp-top10-assessment.md    # System-level assessments
    acme-owasp-llm-top10-assessment.md
    acme-architecture-assessment.md
  flows/
    claims.md                         # Flow Mapping — one per domain
  sweeps/
    generation-controls-sweep.md      # Defect Sweep — one per subsystem
  audits/
    pipeline-audit-2026-08-26.md      # Dated; never overwritten
```

A project created before the change-set layout — with `tickets/`, `delivery/` and `reviews/*-review.md` at the top level — is read as the pseudo-change `initial`. Migrate once: `git mv tickets delivery changes/initial/ && mkdir -p changes/initial/reviews && git mv reviews/*-review.md changes/initial/reviews/`. A per-area ticket file (`tickets/<area>.md` with `### TICKET-NNN` sections) is also still read; `gener8v-state.py split-tickets --remove` turns each into the one-file-per-ticket directory.

## Getting Started

Skills are `/<skill>` when copied into `~/.claude/skills/`, and `/gener8v:<skill>` when installed as the plugin.

### Greenfield (new project)

```bash
/gener8v:setup                              # Bootstrap: .gener8v/, CONVENTIONS.md, state, CLAUDE.md directives
/gener8v:planning                           # PRD + the first change brief
/gener8v:specification Search & Retrieval   # Living spec; deltas recorded in the brief (only one change is active)
/gener8v:ticket-breakdown Search & Retrieval
/gener8v:delivery Search & Retrieval TICKET-001
/gener8v:orchestrate                        # See what's next (also injected automatically at session start)
```

### Brownfield (existing code)

```bash
/gener8v:setup
/gener8v:brownfield                         # Living baseline: context, specifications, PRD, @spec annotations
/gener8v:planning                           # Open the first change
```

### A second initiative

```bash
/gener8v:planning                                                    # Amends prd.md; opens changes/search-relevance-v2/
/gener8v:specification Search & Retrieval for search-relevance-v2    # New IDs above the current maximum, tagged with the change
/gener8v:ticket-breakdown Search & Retrieval for search-relevance-v2
/gener8v:delivery Search & Retrieval TICKET-001 in search-relevance-v2
```

## Installation

### Plugin (recommended — skills, hooks, agents and scripts)

```bash
claude plugin marketplace add gener8v/gener8v.claude-skills
claude plugin install gener8v@gener8v-claude-skills
```

Restart Claude Code afterwards — hooks and skills load at session start. Check with `claude plugin list`; the status should read `enabled`. To pick up a new release:

```bash
claude plugin marketplace update gener8v-claude-skills
claude plugin update gener8v@gener8v-claude-skills
```

For development, load the checkout directly (no install, no cache):

```bash
claude --plugin-dir /path/to/gener8v.claude-skills
```

### Upgrading from a copied install

If the skills were previously copied into `~/.claude/skills/`, move those copies out before or after installing the plugin — otherwise every skill exists twice (`/orchestrate` from the copy, `/gener8v:orchestrate` from the plugin) and the copy never updates:

```bash
mkdir -p ~/.claude/skills-backup-gener8v
for s in architecture-review audit brownfield code-review constraints defect-sweep delivery dependencies flow-mapping orchestrate owasp-llm-top10-review owasp-top10-review planning quality-review security-review setup specification technical-design ticket-breakdown; do
  [ -d ~/.claude/skills/$s ] && mv ~/.claude/skills/$s ~/.claude/skills-backup-gener8v/
done
```

Projects already on the pipeline keep working; their `CLAUDE.md` section says `/<skill>`, which reads as `/gener8v:<skill>` under the plugin. Re-run `/gener8v:setup` in each project to refresh `CONVENTIONS.md` and the directives.

### Copy (skills only)

```bash
git clone https://github.com/gener8v/gener8v.claude-skills.git
cp -r gener8v.claude-skills/skills/* ~/.claude/skills/
```

This installs the nineteen skills and nothing else: no hooks, no agents, no `gener8v-state.py`. Orchestrate maintains `pipeline-state.yaml` by hand, the Flow Mapping gate is at `~/.claude/skills/flow-mapping/scripts/validate-flows.sh`, and there is no update mechanism — `scripts/check-install.sh` reports drift.

## Other plugins in this marketplace

### [macos](./plugins/macos/) — `/macos:tile`

Desktop utilities for Claude Code on macOS, independent of the pipeline. `/macos:tile <App>` lays every on-screen window of one app out in an even grid on one monitor; `--dry-run` prints the plan without moving anything and needs no permissions. See [plugins/macos/README.md](./plugins/macos/README.md) for the Accessibility permission it needs to apply.

```bash
claude plugin install macos@gener8v-claude-skills
```

## For maintainers

- **Releasing:** bump `version` in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` for any change to `hooks/`, `agents/` or `scripts/` — the installed plugin is cached by version, and `claude plugin update` only fetches a new one. Skill-only edits are picked up the same way; there is no separate publish step beyond merging to `main`.
- **Hooks:** `hooks/hooks.json` is loaded automatically. Do not list it under `hooks` in `plugin.json` — that registers it twice and the plugin fails to load ("Duplicate hooks file detected"). Hook commands use `${CLAUDE_PLUGIN_ROOT}` and must stay executable (`chmod +x scripts/*.sh`).
- **Before merging:** `claude plugin validate .`; `bash -n scripts/*.sh skills/flow-mapping/scripts/validate-flows.sh`; `python3 -m py_compile scripts/gener8v-state.py`; and run the script's `state`, `lint` and `metrics` against a project with a `.gener8v/` (a fixture with one change, a delivered ticket and a legacy remnant catches most regressions).
- **Conventions first:** a change to a path, a vocabulary word or an ID rule is made in `skills/setup/references/conventions.md`, then in every skill that mentions it, then in `scripts/gener8v-state.py` — with `schema_version` bumped when the state file's shape changes.

## License

[MIT](./LICENSE)

— gener8v
