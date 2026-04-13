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
- The codebase already has `.gener8v/` artifacts — use the Orchestrate skill to resume

## Input

**Source:** An existing codebase with working code
**Read from:**
- The project's source files, configuration files, and any existing documentation
- `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, or similar docs if they exist
- Package manifests (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.)
- CI/CD configuration files
- Database schemas, API definitions, or other structural artifacts
- `.gener8v/context.md` if it already exists (skip system context phase if so)

**Expects:** A codebase with at least some working code. The codebase does not need documentation, tests, or any particular structure — but having them accelerates the process.

**If input is missing or malformed:**
- If the project directory is empty, stop and recommend using the Planning skill for greenfield development
- If the codebase is very small (a single file or script), recommend Planning + Specification over brownfield onboarding
- If `.gener8v/prd.md` already exists, warn the user — running Brownfield will overwrite existing pipeline artifacts

## Output

**Produces:** A complete artifact set that represents the current state of the codebase:
1. `.gener8v/context.md` — System context (tech stack, architecture, conventions)
2. `.gener8v/specifications/*.md` — One specification per capability area, with requirement IDs
3. `.gener8v/prd.md` — A PRD synthesized bottom-up from the specifications
4. `@spec` annotations in existing source code, linking code to requirement IDs

**Creates directory:** `.gener8v/`, `.gener8v/specifications/` if they do not exist

After this skill completes, the project is ready for any pipeline skill: Constraints can analyze the specifications, Dependencies can map the capability areas, Technical Design can document the architecture, and new feature work can go through the standard pipeline flow.

## Process

### Phase 1: Reconnaissance

1. **Scan Project Structure**: Read the directory tree, identify source directories, configuration files, documentation, tests, and build artifacts. Note the language(s), framework(s), and project layout conventions.

2. **Inventory Key Files**: For each significant source file, note:
   - Purpose (what it does)
   - Key exports (functions, classes, types, routes)
   - Dependencies (what it imports from within the project)
   - External dependencies (third-party libraries)
   - Side effects (database access, network calls, file I/O)
   - Role (entry point, library, utility, configuration, test)

3. **Read Existing Documentation**: If README, architecture docs, API docs, or inline documentation exist, read them. These accelerate understanding but should be verified against the actual code — docs often drift.

4. **Identify Boundaries**: Look for natural boundaries in the codebase: modules, packages, services, layers, feature directories, route groups, or domain concepts. These will inform capability area groupings.

**Present to user:** A brief summary of what was found — languages, frameworks, approximate size, notable patterns, and any existing documentation discovered. Ask the user to confirm the summary is accurate and flag anything missing.

### Phase 2: System Context

5. **Produce System Context**: Write `.gener8v/context.md` capturing:
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
   - Key code locations (directories, files, or modules that belong to this area)
   - Cross-area touchpoints (where this area interacts with others)

**Present to user:** The refined capability areas for approval. The user may adjust boundaries, rename areas, or split/merge areas.

### Phase 4: Specification Extraction

9. **Derive Specifications**: For each capability area, read the associated code and extract a specification following the standard Specification skill format:
   - **Overview**: What this capability area does, based on the code
   - **Source Context**: Reference to the PRD (note: PRD will be synthesized in Phase 5 — use a forward reference)
   - **Functional Requirements**: Each observable behavior in the code becomes a requirement with a namespaced ID ([PREFIX]-REQ-XXX). Requirements describe what the code does today, not what it should do. Derive the prefix from the capability area name, unique within the project
   - **Behaviors & Rules**: Business logic, validation rules, and behavioral patterns found in the code
   - **Edge Cases & Error Handling**: How the code handles errors, edge cases, and unexpected input
   - **States & Transitions**: State machines, status flows, or lifecycle patterns in the code
   - **Data Requirements**: Data models, schemas, and data flow patterns
   - **User Interactions**: How users (or callers) interact with this capability

   **Critical rule:** Specifications describe what the code **does**, not what it **should** do. If the code has a bug, the specification describes the bugged behavior and adds an Open Question noting the potential issue. Specifications are a map of the territory, not a wish list.

10. **Write Specifications**: Save each specification to `.gener8v/specifications/[capability-area-slug].md`.

**Present to user:** Each specification for review. The user may:
- **Approve**: The specification accurately reflects the code
- **Correct**: The specification misunderstands something — adjust it
- **Flag**: A behavior described is actually a bug — add an Open Question
- **Extend**: The specification misses functionality — add the missing requirements

### Phase 5: PRD Synthesis

11. **Synthesize PRD**: Working bottom-up from the specifications, produce a PRD that describes the system as it exists today. The PRD follows the standard Planning skill format:
    - **Problem Context**: What problem this system solves (derived from documentation and code behavior)
    - **Goals**: What the system achieves (derived from its capabilities)
    - **Functional Capabilities**: The capability areas from Phase 3, each with a summary and key requirements (referencing the specifications)
    - **User Scenarios**: Representative usage patterns observed in the code (routes, workflows, entry points)
    - **Out of Scope**: Explicitly state what the system does not do
    - **Open Questions**: Anything unclear from the code, potential bugs flagged by the user, or areas where documentation contradicts behavior

12. **Write PRD**: Save to `.gener8v/prd.md`.

**Present to user:** The PRD for review and approval.

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

14. **Write Annotation Summary**: Add an `## @spec Coverage` section at the end of each specification listing:
    - Each requirement ID
    - The code location(s) annotated with it
    - Any requirements that could not be annotated (with explanation)

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
This skill adds `.gener8v/` artifacts and `@spec` annotations. It does not modify code behavior, refactor, rename, or restructure anything. The codebase should work identically before and after brownfield onboarding.

## Example

### Input

An existing Python web application with:
- FastAPI backend in `src/api/`
- SQLAlchemy models in `src/models/`
- Background job processing in `src/jobs/`
- React frontend in `frontend/`
- PostgreSQL database
- No formal requirements or design documents
- A README with setup instructions

### Output (abbreviated)

#### Phase 1 — Reconnaissance Summary

> **Project:** Python/TypeScript web application
> **Backend:** FastAPI (Python 3.11), SQLAlchemy ORM, PostgreSQL
> **Frontend:** React 18, TypeScript, Vite
> **Jobs:** Celery with Redis broker
> **Tests:** pytest (backend), Vitest (frontend) — ~40% coverage
> **Structure:** Monorepo with `src/` (backend) and `frontend/` directories
> **Documentation:** README with setup instructions, no architecture docs
> **Notable:** 3 API route groups (auth, projects, exports), 8 database models, 5 background jobs

#### Phase 3 — Capability Groupings (one of several proposed)

> **Option A: By User Capability**
> 1. **Authentication & Access** — Login, registration, password reset, role management (`src/api/auth/`, `src/models/user.py`)
> 2. **Project Management** — CRUD operations on projects, collaboration, settings (`src/api/projects/`, `src/models/project.py`, `src/models/membership.py`)
> 3. **Data Export** — PDF/CSV export generation, background processing, delivery (`src/api/exports/`, `src/jobs/export_*.py`, `src/models/export.py`)
> 4. **Notifications** — Email and in-app notifications for project events (`src/jobs/notify_*.py`, `src/models/notification.py`)

#### Phase 4 — Specification (abbreviated, one area)

````markdown
# Data Export — Specification

## Overview

The Data Export capability allows users to generate PDF and CSV exports of project data. Exports are processed asynchronously via background jobs and delivered through download links. ...

## Functional Requirements

### DE-REQ-001: Initiate export request
The system accepts an export request specifying project ID, format (PDF or CSV), and optional date range filter.

### DE-REQ-002: Queue export for background processing
The system enqueues the export request as a Celery task and returns a pending export record with a tracking ID.

### DE-REQ-003: Generate PDF export
The system generates a PDF document containing project data formatted with headers, tables, and summary statistics. ...
````

#### Phase 6 — Spec Annotations

```python
# src/api/exports/routes.py

# @spec DE-REQ-001, DE-REQ-002
@router.post("/exports")
async def create_export(request: ExportRequest, db: Session = Depends(get_db)):
    ...
```

```python
# src/jobs/export_pdf.py

# @spec DE-REQ-003
@celery_app.task
def generate_pdf_export(export_id: int):
    ...
```

---

## Integration with Other Skills

**Upstream:**
- None — this is an entry point for existing codebases (the equivalent of Planning for brownfield projects)

**Downstream:**
- **Constraints Skill**: Can analyze the specifications produced here
- **Dependencies Skill**: Can map dependencies between the capability areas identified here
- **Technical Design Skill**: Can document the architecture that already exists (or use the system context as a starting point)
- **Ticket Breakdown Skill**: Can decompose specifications for new feature work
- **Delivery Skill**: New tickets referencing brownfield specifications flow through standard delivery
- **Code Review Skill**: Can verify `@spec` annotations against specifications
- **Orchestrate Skill**: Reads the artifacts produced here to determine pipeline status

**Replaces:**
- **Planning Skill**: For brownfield projects, this skill produces the PRD instead of Planning. The PRD is synthesized bottom-up from code rather than top-down from intent.
- **Specification Skill**: For brownfield projects, this skill produces the initial specifications. New capability areas added later use the standard Specification skill.

## Revisions

- If the codebase changes significantly after brownfield onboarding, re-run this skill or update specifications manually
- New features added through the standard pipeline (Planning → Specification → ... → Delivery) do not require re-running this skill — they produce their own specifications
- `@spec` annotations should be maintained as code evolves — when code moves, annotations move with it
- If a specification becomes inaccurate due to code changes, update the specification and its `@spec Coverage` section

## Notes

- This skill is token-intensive — it reads significant portions of the codebase. For very large codebases (100+ files), consider running it on subsystems or modules rather than the entire project
- Phase 3 (Capability Discovery) is the most important phase — getting the capability area boundaries right determines the quality of everything downstream
- Specifications produced by this skill describe current behavior, not desired behavior. Future improvements go through the standard pipeline as new tickets
- The system context produced here is the same format consumed by Technical Design, Delivery, and Review skills — it's immediately useful across the pipeline
- If the project already has `.gener8v/context.md`, Phase 2 is skipped and the existing context is used
- `@spec` annotations are greppable: `grep -r "@spec" src/` shows all annotated code locations
