# Orchestrate Skill

## Purpose

Assess the current state of the pipeline and guide the user to the next step. This skill reads all artifacts in `.gener8v/`, determines what has been produced, what's missing, and what may be stale, then recommends which skill(s) to run next — including fan-out guidance for skills that run once per capability area. It is the entry point for anyone resuming work or unsure where the pipeline stands.

## When to Use

Use this skill when:
- Starting a new session and needing to understand pipeline status
- A skill has just completed and the next step is unclear
- Resuming work after a break
- Multiple capability areas exist and it's unclear which have been fully processed
- The user asks "what's next?" or "where are we?"

## Input

**Source:** All artifacts in `.gener8v/`
**Read from:** `.gener8v/` (entire directory tree)
**Expects:** At least `.gener8v/prd.md` to exist. If the directory doesn't exist or is empty, recommend running the Planning skill first.

## Output

**Produces:** A pipeline status assessment presented to the user, with specific next-step recommendations
**Delivery:** Presented directly to the user in conversation. Not written to a file unless the user requests a persistent status snapshot (in which case, write to `.gener8v/status.md`).

## Process

1. **Scan Artifacts**: Read the `.gener8v/` directory tree and inventory all files by type:
   - PRD: `.gener8v/prd.md`
   - System Context: `.gener8v/context.md`
   - Specifications: `.gener8v/specifications/*.md`
   - Constraints: `.gener8v/constraints/*.md`
   - Dependencies: `.gener8v/dependencies/dependency-map.md`
   - Technical Design: `.gener8v/technical-design/*.md`
   - Tickets: `.gener8v/tickets/*.md`
   - Audits: `.gener8v/audits/*.md`

2. **Extract Capability Areas**: Read the PRD and identify all capability areas defined under `## Functional Capabilities`. These are the rows in the coverage matrix.

3. **Build Coverage Matrix**: For each capability area, determine which downstream artifacts exist by matching capability area names to file slugs.

4. **Check Cross-Cutting Artifacts**: Determine whether the dependency map, system context, system-wide technical design, and any audits exist.

5. **Assess Pipeline Stage**: Based on what exists, determine overall progress:
   - **Not started**: No `.gener8v/` directory or no PRD
   - **Planning complete**: PRD exists, no specifications yet
   - **Specifying**: Some specifications exist, not all capability areas covered
   - **Analyzing**: Specifications complete, constraints/dependencies in progress
   - **Designing**: Technical design in progress
   - **Breaking down**: Ticket breakdowns in progress
   - **Complete**: All capability areas have tickets
   - **Audited**: A pipeline audit has been completed

6. **Detect Scale**: Count capability areas and adjust guidance:
   - **1-2 areas**: Run the full pipeline sequentially
   - **3-5 areas**: Recommend parallel specification passes; note where constraints or technical design can be batched
   - **6+ areas**: Recommend grouping related capability areas or splitting into sub-pipelines

7. **Identify Next Steps**: Recommend the next skill(s) to run. For each recommendation:
   - Name the exact skill
   - Name the exact capability area (if the skill runs per-area)
   - Note prerequisites that must complete first
   - Indicate which steps can run in parallel

8. **Present Status**: Show the coverage matrix, pipeline stage, and ordered recommendations.

## Status Format

Present the status to the user in this structure:

```markdown
## Pipeline Status: [PRD Title]

**Stage:** [Current stage name]
**Capability Areas:** [Count]
**System Context:** [Available / Not provided]

### Coverage

| Capability Area | Spec | Constraints | Tech Design | Tickets |
|----------------|------|-------------|-------------|---------|
| [Area name]    | ✓/✗  | ✓/✗         | ✓/✗         | ✓/✗     |

**Dependency Map:** ✓/✗

### Next Steps

1. **[Skill name]** on [target] — [why this is next]
2. **[Skill name]** on [target] — [can run in parallel with step 1]

### Recommendations

- [Guidance about scale, skipped steps, system context, or pipeline health]
```

---

## Principles

### Status, Not Judgment
This skill reports what exists and what's missing. It does not evaluate quality — that's the Audit skill's job. If a specification exists, it's checked off, regardless of whether it's good.

### Specific Over Vague
"Run the Specification skill on the Documentation Ingestion capability area" is useful. "You need more specifications" is not. Every recommendation should name the skill and the target.

### Respect Optional Steps
Not every project needs every skill. Constraints, Technical Design, and Dependencies can be skipped for simple projects. Note skipped steps as recommendations but don't treat them as blockers. Only hard prerequisites (e.g., "specification required before tickets") are flagged as blockers.

### Fan-Out Awareness
Skills that run per-capability-area (Specification, Constraints, Technical Design, Ticket Breakdown) create fan-out. Make the fan-out explicit: "3 of 5 capability areas have specifications. Run Specification on: Area D, Area E."

### Scale-Aware Guidance
A 2-area project and a 12-area project need different approaches. For small projects, the full pipeline is straightforward. For large projects, recommend batching, parallelization, or sub-pipeline splits. Never give the same advice regardless of scale.

## Integration with Other Skills

This skill reads output from all other skills but does not produce artifacts that other skills consume. It is a coordination tool, not a pipeline stage.

## Notes

- This skill does not modify any artifacts — it is read-only
- Run this skill at any time; it adapts to whatever exists in `.gener8v/`
- If `.gener8v/` does not exist, the only recommendation is: run the Planning skill
- This skill can be re-run after each pipeline step to get updated guidance
- For large projects, this skill's coverage matrix is the primary tool for tracking progress across many capability areas
- The Orchestrate skill and Audit skill are complementary: Orchestrate tracks completeness (what exists), Audit tracks quality (is it good)
