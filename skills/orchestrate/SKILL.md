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

**Produces:** Two things:
1. A pipeline status assessment presented to the user, with specific next-step recommendations
2. An updated `.gener8v/pipeline-state.yaml` — a machine-readable pipeline state file that other skills and tools can query

**Write to:** `.gener8v/pipeline-state.yaml` (always updated on every run)
**Delivery:** Status assessment is presented directly to the user in conversation. The YAML state file is written silently.

## Process

1. **Scan Artifacts**: Read the `.gener8v/` directory tree and inventory all files by type:
   - PRD: `.gener8v/prd.md`
   - System Context: `.gener8v/context.md`
   - Specifications: `.gener8v/specifications/*.md`
   - Constraints: `.gener8v/constraints/*.md`
   - Dependencies: `.gener8v/dependencies/dependency-map.md`
   - Technical Design: `.gener8v/technical-design/*.md`
   - Tickets: `.gener8v/tickets/*.md`
   - Delivery Records: `.gener8v/delivery/*.md`
   - Code Reviews: `.gener8v/reviews/*-code-review.md`
   - Quality Reviews: `.gener8v/reviews/*-quality-review.md`
   - Security Reviews: `.gener8v/reviews/*-security-review.md`
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
   - **Ready for delivery**: All capability areas have tickets, no delivery records yet
   - **Delivering**: Some tickets have delivery records, not all
   - **Delivered**: All tickets across all capability areas have delivery records
   - **Reviewing**: Some delivered tickets have review reports (code review, quality review, or security review)
   - **Reviewed**: All delivered tickets have all three review types completed
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

8. **Write Pipeline State**: Write `.gener8v/pipeline-state.yaml` with the machine-readable state (see Pipeline State Format below). This file is the persistent, queryable record of pipeline progress. It is overwritten on every Orchestrate run.

9. **Present Status**: Show the coverage matrix, pipeline stage, and ordered recommendations.

## Status Format

Present the status to the user in this structure:

```markdown
## Pipeline Status: [PRD Title]

**Stage:** [Current stage name]
**Capability Areas:** [Count]
**System Context:** [Available / Not provided]

### Coverage

| Capability Area | Spec | Constraints | Tech Design | Tickets | Delivered | CR | QR | SEC |
|----------------|------|-------------|-------------|---------|-----------|----|----|-----|
| [Area name]    | ✓/✗  | ✓/✗         | ✓/✗         | ✓/✗     | [n/total] | [n/total] | [n/total] | [n/total] |

**Dependency Map:** ✓/✗

*Note: Delivered/CR/QR/SEC columns use `[completed]/[total tickets]` format since delivery and reviews happen per ticket, not per capability area.*

### Next Steps

1. **[Skill name]** on [target] — [why this is next]
2. **[Skill name]** on [target] — [can run in parallel with step 1]

### Recommendations

- [Guidance about scale, skipped steps, system context, or pipeline health]
```

## Pipeline State Format

Write `.gener8v/pipeline-state.yaml` with this structure:

```yaml
# gener8v pipeline state — auto-generated by Orchestrate, do not edit manually
generated: "2026-04-13T10:30:00Z"
stage: delivering
system_context: true

capability_areas:
  search-and-retrieval:
    specification: specifications/search-and-retrieval.md
    constraints: constraints/search-and-retrieval.md
    technical_design: technical-design/search-and-retrieval.md
    tickets: tickets/search-and-retrieval.md
    ticket_count: 4
    deliveries:
      TICKET-001:
        status: reviewed
        delivery: delivery/search-and-retrieval-ticket-001-delivery.md
        code_review: reviews/search-and-retrieval-ticket-001-code-review.md
        quality_review: reviews/search-and-retrieval-ticket-001-quality-review.md
        security_review: reviews/search-and-retrieval-ticket-001-security-review.md
      TICKET-002:
        status: delivered
        delivery: delivery/search-and-retrieval-ticket-002-delivery.md
        code_review: null
        quality_review: null
        security_review: null
      TICKET-003:
        status: ready
        delivery: null
        code_review: null
        quality_review: null
        security_review: null
      TICKET-004:
        status: blocked
        delivery: null
        code_review: null
        quality_review: null
        security_review: null
    progress:
      delivered: 2
      reviewed: 1
      total: 4

  results-presentation:
    specification: specifications/results-presentation.md
    constraints: null
    technical_design: null
    tickets: null
    ticket_count: 0
    deliveries: {}
    progress:
      delivered: 0
      reviewed: 0
      total: 0

cross_cutting:
  dependency_map: dependencies/dependency-map.md
  system_design: technical-design/system-design.md
  audits:
    - audits/pipeline-audit.md

next_steps:
  - skill: code-review
    target: "search-and-retrieval TICKET-002"
    reason: "Delivery complete, needs review"
  - skill: delivery
    target: "search-and-retrieval TICKET-003"
    reason: "Unblocked, ready for implementation"
```

Field definitions:
- **generated**: ISO 8601 timestamp of when this state was written
- **stage**: Overall pipeline stage (same values as the Status Format: `not_started`, `planning_complete`, `specifying`, `analyzing`, `designing`, `breaking_down`, `ready_for_delivery`, `delivering`, `delivered`, `reviewing`, `reviewed`, `audited`)
- **system_context**: Whether `.gener8v/context.md` exists
- **capability_areas**: Map of capability area slugs to their artifact state. All file paths are relative to `.gener8v/`. `null` means the artifact does not exist.
- **ticket status values**: `blocked` (depends on undelivered tickets), `ready` (all dependencies delivered, not yet started), `delivered` (delivery record exists, not yet reviewed), `reviewed` (all three reviews complete)
- **progress**: Per-area delivery and review counts
- **cross_cutting**: Artifacts that span multiple capability areas
- **next_steps**: Ordered list of recommended next actions with skill name, target, and reason

---

## Principles

### Status, Not Judgment
This skill reports what exists and what's missing. It does not evaluate quality — that's the Audit skill's job. If a specification exists, it's checked off, regardless of whether it's good.

### Specific Over Vague
"Run the Specification skill on the Documentation Ingestion capability area" is useful. "You need more specifications" is not. Every recommendation should name the skill and the target.

### Respect Optional Steps
Not every project needs every skill. Constraints, Technical Design, and Dependencies can be skipped for simple projects. Note skipped steps as recommendations but don't treat them as blockers. Only hard prerequisites (e.g., "specification required before tickets") are flagged as blockers.

### Fan-Out Awareness
Skills that run per-capability-area (Specification, Constraints, Technical Design, Ticket Breakdown) create fan-out. Delivery and reviews create even more fan-out — each ticket is a separate delivery, and each delivery spawns up to three reviews. Make the fan-out explicit: "3 of 5 capability areas have specifications. Run Specification on: Area D, Area E." For delivery stages: "Search & Retrieval: 2/4 tickets delivered. Next: Deliver TICKET-003 (unblocked by TICKET-001, TICKET-002)."

### Delivery-Stage Guidance
When the pipeline reaches the delivery stage, shift from capability-area-level tracking to ticket-level tracking. For each capability area with tickets:
- Identify which tickets are Ready (all Depends On tickets delivered)
- Recommend delivering the next ready ticket
- After delivery, recommend running Code Review, Quality Review, and Security Review in parallel
- After all three reviews resolve with approved verdicts, identify the next ready ticket

### Scale-Aware Guidance
A 2-area project and a 12-area project need different approaches. For small projects, the full pipeline is straightforward. For large projects, recommend batching, parallelization, or sub-pipeline splits. Never give the same advice regardless of scale.

## Integration with Other Skills

This skill reads output from all other skills but does not produce artifacts that other skills consume. It is a coordination tool, not a pipeline stage.

## Notes

- This skill reads all artifacts but only writes `.gener8v/pipeline-state.yaml` — it does not modify any other artifacts
- Run this skill at any time; it adapts to whatever exists in `.gener8v/`
- If `.gener8v/` does not exist, the only recommendation is: run the Setup skill followed by Planning (greenfield) or Brownfield (existing code)
- This skill can be re-run after each pipeline step to get updated guidance
- For large projects, this skill's coverage matrix is the primary tool for tracking progress across many capability areas
- The Orchestrate skill and Audit skill are complementary: Orchestrate tracks completeness (what exists), Audit tracks quality (is it good)
- `.gener8v/pipeline-state.yaml` is machine-readable and greppable — other tools, scripts, or CI/CD pipelines can parse it to gate deployments or track progress
- The state file is always overwritten, never appended — it reflects a point-in-time snapshot of the pipeline
