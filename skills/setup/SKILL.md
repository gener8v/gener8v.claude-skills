# Setup Skill

## Purpose

Bootstrap the gener8v pipeline in a project. This skill creates the `.gener8v/` directory structure, patches the project's `CLAUDE.md` with pipeline activation directives, and initializes the pipeline state file. After setup, the pipeline activates automatically — the Orchestrate skill is consulted whenever the user starts a session or asks to make changes, and all code modifications flow through the structured pipeline.

## When to Use

Use this skill when:
- Starting a new project that will use the gener8v pipeline
- Onboarding an existing project to the pipeline for the first time
- The project has no `.gener8v/` directory or `CLAUDE.md` pipeline directives
- The user says "set up gener8v" or "initialize the pipeline"

Do **not** use this skill when:
- The project already has `.gener8v/` artifacts and `CLAUDE.md` directives — use the Orchestrate skill instead
- The user wants to start building immediately — run Planning (greenfield) or Brownfield (existing code) directly, which will create `.gener8v/` as needed

## Input

**Source:** The project root directory
**Read from:**
- `CLAUDE.md` in the project root (if it exists)
- `.gener8v/` directory (to check if already initialized)

**Expects:** A project directory. May or may not have existing code, documentation, or a `CLAUDE.md`.

## Output

**Produces:**
1. `.gener8v/` directory structure
2. `.gener8v/pipeline-state.yaml` initialized with empty state
3. `CLAUDE.md` with pipeline activation directives (created or patched)

## Process

1. **Check Existing State**: Scan for `.gener8v/` directory and `CLAUDE.md`.

2. **Create Directory Structure**: If `.gener8v/` does not exist, create it:
   ```
   .gener8v/
     specifications/
     constraints/
     dependencies/
     technical-design/
     tickets/
     delivery/
     reviews/
     audits/
   ```

3. **Initialize Pipeline State**: Write `.gener8v/pipeline-state.yaml` with the initial empty state:
   ```yaml
   # gener8v pipeline state — auto-generated, do not edit manually
   # Updated by the Orchestrate skill after each pipeline step
   generated: [timestamp]
   stage: not_started
   system_context: false
   capability_areas: {}
   cross_cutting:
     dependency_map: null
     system_design: null
     audits: []
   ```

4. **Patch CLAUDE.md**: If `CLAUDE.md` exists, append the pipeline directives below. If it does not exist, create it with just the directives.

   **Before patching**, read the existing `CLAUDE.md` and check for an existing `## gener8v Pipeline` section. If one exists, ask the user whether to replace it or skip.

5. **Present Summary**: Tell the user what was created/modified and recommend next steps:
   - **Greenfield**: Run the Planning skill (`/planning`)
   - **Brownfield**: Run the Brownfield skill (`/brownfield`)
   - **Resuming**: Run the Orchestrate skill (`/orchestrate`)

## CLAUDE.md Directives

Append the following to the project's `CLAUDE.md`:

````markdown
## gener8v Pipeline

This project uses the [gener8v pipeline](https://github.com/gener8v/gener8v.claude-skills) for structured development. Follow these rules:

### Session Start
- At the start of every session, run `/orchestrate` to assess pipeline status before doing any work.
- Read `.gener8v/pipeline-state.yaml` for a quick view of where things stand.

### Code Changes
- All new features, enhancements, and non-trivial changes must flow through the pipeline: Planning/Brownfield → Specification → Constraints → Technical Design → Ticket Breakdown → Delivery → Reviews.
- Do not write code outside of the Delivery skill unless it is a trivial fix (typo, formatting, config tweak).
- For bug fixes on code with `@spec` annotations, verify the fix against the referenced specification before implementing.

### Traceability
- All delivered code must include `@spec` annotations linking functions, classes, and handlers to their requirement IDs (e.g., `# @spec SR-REQ-001`).
- When modifying annotated code, preserve and update `@spec` annotations.
- Use `grep -r "@spec" src/` (adjust path) to audit annotation coverage.

### Pipeline Artifacts
- All pipeline artifacts live in `.gener8v/`. Do not edit these files manually — use the appropriate skill.
- `.gener8v/pipeline-state.yaml` is the machine-readable pipeline state. It is updated by the Orchestrate skill.
- After completing any pipeline skill, run `/orchestrate` to update the pipeline state and get next steps.

### Scale
- For small changes (1-2 capability areas): Planning → Specification → Ticket Breakdown → Delivery → Reviews.
- For standard work (3-5 areas): Full pipeline including Constraints, Dependencies, and Technical Design.
- For large initiatives (6+ areas): Full pipeline with parallel specification passes and sub-pipeline splits.
````

## Principles

### Non-Destructive
Never overwrite existing `CLAUDE.md` content. Always append. If the file has existing directives, check before duplicating them.

### Opinionated Defaults
The directives encode the pipeline's best practices as rules. Users can later relax them (e.g., allowing code changes outside Delivery for prototyping) by editing their `CLAUDE.md`. Start strict, loosen as needed.

### Immediate Value
After setup, the user should know exactly what to do next. Don't leave them staring at an empty pipeline — recommend the right entry point (Planning, Brownfield, or Orchestrate).

## Example

### Input

A project with an existing `CLAUDE.md` containing coding conventions but no pipeline directives.

### Output

```
Setup complete:

  Created:
  - .gener8v/ directory structure (8 subdirectories)
  - .gener8v/pipeline-state.yaml (initialized)

  Updated:
  - CLAUDE.md (appended ## gener8v Pipeline section)

  Next steps:
  - This project has existing code. Run /brownfield to map it into the pipeline.
  - Or, if starting fresh work, run /planning to create a PRD.
```

---

## Integration with Other Skills

**Upstream:**
- None — this is the first skill to run in any project

**Downstream:**
- **Planning Skill**: For greenfield projects, run after setup
- **Brownfield Skill**: For existing codebases, run after setup
- **Orchestrate Skill**: Reads the pipeline state file created here; the `CLAUDE.md` directives ensure Orchestrate is run at session start

## Notes

- This skill is idempotent — running it again on a project that is already set up will not duplicate directives or overwrite artifacts
- The `CLAUDE.md` directives are suggestions that work with Claude Code's existing CLAUDE.md conventions
- Users can customize the directives after setup — they are guidance, not enforcement
- The `.gener8v/` directory should be committed to version control so pipeline state is shared across the team
- `.gener8v/pipeline-state.yaml` is auto-generated and updated by Orchestrate — manual edits will be overwritten
