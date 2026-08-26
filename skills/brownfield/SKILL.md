---
name: brownfield
description: "Map an existing codebase into the gener8v pipeline bottom-up: system context, one specification per capability area with requirement IDs, a PRD synthesized from the code, and @spec annotations in source. Use when onboarding existing code that has no .gener8v/ artifacts."
argument-hint: "[subsystem or directory to onboard]"
disable-model-invocation: true
---
# Brownfield Skill

## Purpose

Map an existing codebase into the gener8v pipeline. This skill takes a project with existing code and produces `.gener8v/` artifacts — system context, specifications, and a PRD — by reading and analyzing what already exists. It works bottom-up: understand the code first, then derive the specifications and requirements that describe it. The result is a codebase that is fully onboarded to the pipeline, with `@spec` annotations in the source code and a complete artifact set that downstream skills (Constraints, Dependencies, Technical Design, Ticket Breakdown, Delivery, Reviews) can build on.

## When to Use

Use this skill when:
- Starting the pipeline on an existing codebase (not a greenfield project)
- Onboarding a legacy system into the structured pipeline
- A codebase has grown without formal requirements or design documents
- The team wants to retrofit traceability onto code that was written without it
- Before using any other pipeline skill on a codebase that already has working code

Do **not** use this skill when:
- Starting from scratch — use the Planning skill instead
- `.gener8v/prd.md` already exists — use the Orchestrate skill to resume. (A `.gener8v/` holding only `sweeps/`, `flows/` or Setup's scaffold is not an onboarded project — run Brownfield.)

## Input

**Source:** An existing codebase with working code — a single repository, or a workspace directory containing several (`CONVENTIONS.md` §8)
**Read from:**
- The project's source files, configuration files, and any existing documentation
- `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, or similar docs if they exist
- Package manifests (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.)
- CI/CD configuration files
- Database schemas, API definitions, or other structural artifacts
- `.gener8v/context.md` if it already exists (skip the system context phase if so — but add the `## Repositories` table if it is missing)
- `.gener8v/brownfield/reconnaissance.md` and `.gener8v/brownfield/capability-areas.md` if they exist — the checkpoints from an earlier run (see **Resuming**)
- `.gener8v/flows/*.md` if Flow Mapping has run — current-state flows are evidence for capability boundaries
- `.gener8v/CONVENTIONS.md`

**Expects:** A codebase with at least some working code. The codebase does not need documentation, tests, or any particular structure — but having them accelerates the process.

**If input is missing or malformed:**
- If the project directory is empty, stop and recommend using the Planning skill for greenfield development
- If the codebase is very small (a single file or script), recommend Planning + Specification over brownfield onboarding
- If `.gener8v/prd.md` already exists, warn the user — the project is already onboarded and Orchestrate resumes it; a deliberate re-run resumes from the checkpoints (see **Revisions**) and never regenerates the baseline

## Output

**Produces:** A complete artifact set that represents the current state of the codebase:
0. `.gener8v/brownfield/reconnaissance.md` and `.gener8v/brownfield/capability-areas.md` — the approved outputs of Phases 1 and 3, written before the next phase starts so an interrupted run resumes instead of restarting
1. `.gener8v/context.md` — System context (tech stack, architecture, conventions), including the `## Repositories` table
2. `.gener8v/specifications/*.md` — One specification per capability area, with requirement IDs, `**Status:** Draft` / `**Approved by:** pending` in Source Context, and a populated `## @spec Coverage` section
3. `.gener8v/prd.md` — A PRD synthesized bottom-up from the specifications, with `**Status:**` and `**Approved by:**` at the top
4. `@spec` annotations in existing source code, linking code to requirement IDs

Everything this skill writes is a **living** artifact — the as-is baseline (`CONVENTIONS.md` §2). It writes no change: there is no `changes/<change-slug>/` for onboarding, and baseline requirements carry no priority or change tag. The first feature afterwards is opened with `/planning` and is a change like any other.

**Creates directory:** `.gener8v/`, `.gener8v/brownfield/`, `.gener8v/specifications/` if they do not exist

After this skill completes, the project is ready for any pipeline skill: Constraints can analyze the specifications, Dependencies can map the capability areas, Technical Design can document the architecture, and new feature work starts with `/planning`, which amends `prd.md` in place and opens `changes/<change-slug>/change.md`.

## Process

### Resuming

On every start, check for the checkpoints and skip to the first phase whose output is missing: `brownfield/reconnaissance.md` (Phase 1 done), `context.md` (Phase 2), `brownfield/capability-areas.md` (Phase 3), one `specifications/<slug>.md` per listed area (Phase 4 — treat areas that already have a spec as done), `prd.md` (Phase 5), populated `## @spec Coverage` sections (Phase 6). Present what was found before continuing. Phases 1–3 are the expensive part of this skill on a large codebase; they are never repeated because a session ended.

### Phase 1: Reconnaissance

1. **Scan Project Structure**: Read the directory tree, identify source directories, configuration files, documentation, tests, and build artifacts. Note the language(s), framework(s), and project layout conventions. Determine whether the root is a single repository or a **workspace** holding several, and record the **Repositories table** — `| Directory | Purpose | Language / build | Verify commands |`, one row for a single repository, one per repository for a workspace, verify commands taken from each repository's manifest and CI configuration. A workspace can be onboarded as one system (one PRD, capability areas cutting across repositories) or one repository at a time (the argument names it); the table is recorded either way, and every code path in every artifact from here on is **root-relative** (`api/src/search/query.ts`).

2. **Inventory Key Files**: For each significant source file, note:
   - Purpose (what it does)
   - Key exports (functions, classes, types, routes)
   - Dependencies (what it imports from within the project)
   - External dependencies (third-party libraries)
   - Side effects (database access, network calls, file I/O)
   - Role (entry point, library, utility, configuration, test)

3. **Read Existing Documentation**: If README, architecture docs, API docs, or inline documentation exist, read them. These accelerate understanding but should be verified against the actual code — docs often drift.

4. **Identify Boundaries**: Look for natural boundaries in the codebase: modules, packages, services, layers, feature directories, route groups, or domain concepts. These will inform capability area groupings.

**Present to user:** A brief summary of what was found — languages, frameworks, approximate size, notable patterns, and any existing documentation discovered. Ask the user to confirm the summary is accurate and flag anything missing. **Then write it** to `.gener8v/brownfield/reconnaissance.md` (Repositories table, file inventory, boundaries, documentation found) before starting Phase 2.

### Phase 2: System Context

5. **Produce System Context**: Write `.gener8v/context.md` capturing:
   - `## Repositories` — the table recorded in Phase 1, verbatim (Delivery reads its verify commands; the hooks and the `@spec` lint walk every directory it lists). If `context.md` already existed without this table, add the table and leave the rest of the document alone
   - Technology stack (languages, frameworks, runtime, database, infrastructure)
   - Architecture patterns (monolith, microservices, layered, event-driven, etc.)
   - Code conventions (naming, file organization, module patterns)
   - External integrations (APIs, services, databases, message queues)
   - Build and deployment (CI/CD, environments, deployment targets)
   - Testing approach (frameworks, coverage patterns, test organization)

**Present to user:** The system context document for review. The user may correct, expand, or approve.

### Phase 3: Capability Discovery

6. **Propose Capability Groupings**: Based on the reconnaissance, propose 3-5 different ways to decompose the codebase into capability areas. Each grouping should represent a fundamentally different mental model:
   - By **user capability** (what end users can do)
   - By **data domain** (what entities the system manages)
   - By **behavioral boundary** (what changes together)
   - By **data flow** (how information moves through the system)
   - By **integration surface** (what talks to external systems)

   For each proposed grouping, list the specific capability areas and which code maps to each.

   Do **not** group by:
   - File location or directory structure (that's an implementation detail)
   - Team ownership (that's organizational, not architectural)
   - Deployment boundary (that's infrastructure, not capability)

7. **User Selects Grouping**: Present the options and let the user choose which mental model best represents their system. The user may also provide their own grouping or modify a proposed one.

8. **Refine Areas**: Once the grouping is selected, define each capability area with:
   - Name (clear, descriptive, 2-4 words)
   - Slug (kebab-case, used for file naming)
   - Summary (1-2 sentences describing what this area covers)
   - Key code locations (directories, files, or modules that belong to this area — root-relative, so a workspace area can span repositories)
   - Cross-area touchpoints (where this area interacts with others)

**Present to user:** The refined capability areas for approval. The user may adjust boundaries, rename areas, or split/merge areas. **Then write the approved list** — name, slug, requirement prefix, summary, key code locations, touchpoints — to `.gener8v/brownfield/capability-areas.md`. This file is the durable area→code mapping that Delivery, the reviews, Defect Sweep and Orchestrate rely on.

### Phase 4: Specification Extraction

9. **Derive Specifications**: For each capability area in `capability-areas.md` that has no specification yet, read the associated code and extract a specification following the standard Specification skill format. On a large codebase run one area at a time (or one area per subagent, each given only `capability-areas.md` and that area's code paths) so a single extraction cannot exhaust the context:
   - **Overview**: What this capability area does, based on the code
   - **Source Context**: Reference to the PRD (note: PRD will be synthesized in Phase 5 — write `**Parent PRD:** (synthesized in Phase 5)` now and back-fill the title in step 12), `**Requirement prefix:**` from `capability-areas.md`, and the approval lines `**Status:** Draft` / `**Approved by:** pending` (`CONVENTIONS.md` §7)
   - **Functional Requirements**: Each observable behavior in the code becomes a requirement with a namespaced ID ([PREFIX]-REQ-XXX). Requirements describe what the code does today, not what it should do. Derive the prefix from the capability area name, unique within the project. Baseline requirements carry no priority or change tag — a tag names the change that introduced a requirement, and the baseline was introduced by no change
   - **Non-Functional Requirements**: Only the measurable targets the repository already enforces or measures (a load-test threshold, a timeout, a retention job, a structured-log contract) become `[PREFIX]-NFR-XXX`, each with the artifact that verifies it. Do not invent targets; a target the team believes in but nothing measures is an Open Question
   - **Behaviors & Rules**: Business logic, validation rules, and behavioral patterns found in the code
   - **Edge Cases & Error Handling**: How the code handles errors, edge cases, and unexpected input
   - **States & Transitions**: State machines, status flows, or lifecycle patterns in the code
   - **Data Requirements**: Data models, schemas, and data flow patterns
   - **User Interactions**: How users (or callers) interact with this capability

   **Critical rule:** Specifications describe what the code **does**, not what it **should** do. If the code has a bug, the specification describes the bugged behavior and adds an Open Question noting the potential issue. Specifications are a map of the territory, not a wish list.

10. **Write Specifications**: Save each specification to `.gener8v/specifications/[capability-area-slug].md`.

**Present to user:** Each specification for review. The user may:
- **Approve**: The specification accurately reflects the code — set `**Status:** Approved` and `**Approved by:** Product Owner — <name>, YYYY-MM-DD` in its Source Context
- **Correct**: The specification misunderstands something — adjust it
- **Flag**: A behavior described is actually a bug — add an Open Question
- **Extend**: The specification misses functionality — add the missing requirements

### Phase 5: PRD Synthesis

11. **Synthesize PRD**: Working bottom-up from the specifications, produce a PRD that describes the system as it exists today. The PRD follows the standard Planning skill format, with `**Status:** Draft` and `**Approved by:** pending` directly under the title:
    - **Problem Context**: What problem this system solves (derived from documentation and code behavior)
    - **Goals**: What the system achieves (derived from its capabilities)
    - **Functional Capabilities**: The capability areas from Phase 3, each with a summary and key requirements (referencing the specifications)
    - **User Scenarios**: Representative usage patterns observed in the code (routes, workflows, entry points)
    - **Out of Scope**: Explicitly state what the system does not do
    - **Open Questions**: Anything unclear from the code, potential bugs flagged by the user, or areas where documentation contradicts behavior

12. **Write PRD**: Save to `.gener8v/prd.md`. Then back-fill `**Parent PRD:**` in every specification written in Phase 4 with the PRD's title.

**Present to user:** The PRD for review and approval. When the user approves, set `**Status:** Approved` and `**Approved by:** Product Owner — <name>, YYYY-MM-DD`. Planning later amends this PRD in place with a `## Change Log`; it never overwrites the baseline.

### Phase 6: Spec Annotation

13. **Add `@spec` Annotations**: For each requirement in the specifications, locate the code that implements it and add an `@spec` annotation comment:

    ```
    # @spec SR-REQ-001, SR-REQ-002
    def process_query(text):
    ```

    Use the language's native comment syntax. Place annotations on the line immediately above the function, class, method, route handler, or block that implements the requirement.

    Annotation rules:
    - One annotation per code location, listing all requirement IDs implemented there
    - A requirement may appear in multiple annotations if it is implemented across multiple locations
    - Annotations go on functions, classes, methods, route handlers, or configuration blocks — not on individual lines within a function
    - If a requirement cannot be tied to a specific code location (e.g., a cross-cutting concern enforced by middleware), annotate the middleware or configuration that enforces it

14. **Write Annotation Summary**: Add an `## @spec Coverage` section at the end of each specification, in the Specification skill's table format (`| Requirement | Code Location(s) |`), listing:
    - Each requirement ID
    - The code location(s) annotated with it (`file:function`, root-relative — `api/src/search/query.ts:parseQuery`)
    - Any requirements that could not be annotated (a row with the explanation in the location column)

**Present to user:** A summary of annotations added, including any requirements that could not be tied to specific code. The user may adjust annotations or flag requirements that should map to different code locations.

## Principles

### Bottom-Up, Not Top-Down
Greenfield projects go top-down: intent becomes requirements becomes code. Brownfield goes bottom-up: code becomes specifications becomes a PRD. The code is the source of truth. Resist the urge to describe what the system should be — describe what it is.

### Code Over Documentation
When code and documentation disagree, the code is right. Documentation is useful for understanding intent, but the specification must reflect actual behavior. Flag contradictions as Open Questions.

### The User Knows the Domain
The reconnaissance and analysis provide structure, but the user understands the business domain, the history, and the intent behind the code. Every phase requires user review because automated analysis will miss context that only a human has.

### Existing Bugs Are Requirements (Until They're Not)
If the code does something, the specification describes it as a requirement. If the user identifies a behavior as a bug, it becomes an Open Question on the specification — not an omission. This ensures the specification is an accurate map of reality, and bug fixes flow through the standard pipeline as new tickets.

### Annotate Everything Reachable
Every requirement should map to at least one code location via `@spec` annotations. If a requirement cannot be annotated, it may be an emergent behavior (the result of multiple components interacting) — document this in the specification's `@spec Coverage` section. The goal is maximal traceability from day one.

### Minimal Disruption
This skill adds `.gener8v/` artifacts and `@spec` annotation comments. It does not modify code behavior, refactor, rename, or restructure anything — the annotation comment is the only source change it is allowed to make (`CONVENTIONS.md` §2). The codebase should work identically before and after brownfield onboarding.

### Checkpoint Every Approval
Each phase ends with user approval, and each approval is written to disk before the next phase begins. The conversation is not the record.

## Example

The worked example onboards an existing Support Documentation Search System — a two-repository workspace (`api/`, `web/`) — end to end: the Phase 1 reconnaissance with its Repositories table, the Phase 3 groupings that yield Search & Retrieval (`SR`), Results Presentation (`RP`) and Documentation Ingestion (`DI`), the as-is Search & Retrieval specification (SR-REQ-001..010, two NFRs the repository already measures, a user-flagged bug kept as an Open Question, approval lines, root-relative `@spec Coverage`), the synthesized PRD, the `@spec` annotations, and the first change opened afterwards with `/planning`.
It lives at `skills/brownfield/references/example.md`.
Read it before producing your first artifact of this kind.

---

## Integration with Other Skills

**Upstream:**
- None — this is an entry point for existing codebases (the equivalent of Planning for brownfield projects)

**Downstream:**
- **Constraints Skill**: Can analyze the specifications produced here
- **Dependencies Skill**: Can map dependencies between the capability areas identified here
- **Technical Design Skill**: Can document the architecture that already exists (or use the system context as a starting point)
- **Planning Skill**: Opens the first change on the onboarded system — amends `prd.md` in place and writes `changes/<change-slug>/change.md`
- **Ticket Breakdown Skill**: Can decompose specifications for new feature work, inside the change Planning opened (`changes/<change-slug>/tickets/<area-slug>/TICKET-NNN.md` — one ticket, one file — plus `tickets/<area-slug>/backlog.md`)
- **Delivery Skill**: New tickets referencing brownfield specifications flow through standard delivery, using the verify commands from `context.md`'s Repositories table
- **Code Review Skill**: Can verify `@spec` annotations against specifications
- **Orchestrate Skill**: Reads the artifacts produced here to determine pipeline status

**Replaces:**
- **Planning Skill** — for the baseline only. This skill produces the as-is PRD instead of Planning, synthesized bottom-up from code rather than top-down from intent, and writes no change. Every initiative after onboarding — including the first — goes through `/planning`.
- **Specification Skill** — for the baseline only. This skill produces the initial specifications. Changes to them, and new capability areas added later, use the standard Specification skill, which amends the living specification and tags what it adds with the change.

## Revisions

- If the codebase changes significantly after brownfield onboarding, re-run this skill (it resumes from the checkpoints; delete `brownfield/capability-areas.md` to redo the grouping) — existing requirement IDs are preserved and new ones allocated above the maximum
- The first *change* to an onboarded codebase is `/planning`, which amends the PRD in place (it never overwrites the as-is baseline) and opens `changes/<change-slug>/change.md` → Specification (amending the area's living spec, tagging what the change adds) → Ticket Breakdown (one `changes/<change-slug>/tickets/<area-slug>/TICKET-NNN.md` per ticket, plus `backlog.md`) → Delivery
- New features added through the standard pipeline (Planning → Specification → ... → Delivery) do not require re-running this skill — they produce their own specifications
- `@spec` annotations should be maintained as code evolves — when code moves, annotations move with it
- If a specification becomes inaccurate due to code changes, update the specification and its `@spec Coverage` section

## Notes

- This skill is token-intensive — it reads significant portions of the codebase. For very large codebases (100+ files), consider running it on subsystems or modules rather than the entire project
- Phase 3 (Capability Discovery) is the most important phase — getting the capability area boundaries right determines the quality of everything downstream
- Specifications produced by this skill describe current behavior, not desired behavior. Future improvements go through the standard pipeline as new tickets
- The system context produced here is the same format consumed by Technical Design, Delivery, and Review skills — it's immediately useful across the pipeline
- If the project already has `.gener8v/context.md`, Phase 2 is skipped and the existing context is used — except that a missing `## Repositories` table is added from the Phase 1 reconnaissance
- On a workspace, onboard as one system when the repositories ship together and capability areas cut across them; onboard one repository at a time when they are independent products that happen to share a root. Either way the Repositories table lists them all and code paths are root-relative
- `@spec` annotations are greppable: `grep -rn "@spec" .` from the root shows every annotated code location in every repository
