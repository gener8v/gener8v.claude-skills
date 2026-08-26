---
name: planning
description: "Turn a description of a feature, product or system into a PRD at .gener8v/prd.md (3-7 capability areas, user scenarios, scope boundaries, open questions) and open a change brief at .gener8v/changes/<change-slug>/change.md with its priority cut. Use when the user describes what they want built: a greenfield product, a second initiative on an existing PRD, or the first feature after brownfield onboarding. To onboard an existing codebase that has no PRD, use brownfield instead."
argument-hint: "[what you want built]"
---
# Planning Skill

## Purpose

Transform a user prompt into a structured Product Requirements Document (PRD) that describes the functional capabilities needed to satisfy the request, and open the **change** that will deliver it: a change brief naming the initiative, the capability areas it touches, and the priority cut. The PRD is a living artifact, amended in place across initiatives; the brief belongs to one initiative. Both are designed for downstream decomposition by LLM agents into detailed specifications and tickets.

## When to Use

Use this skill when:
- A user describes a new feature, product, or system they want built
- A user has a problem statement that needs translation into requirements
- Work needs to be scoped before technical planning begins
- A new initiative starts on a project already on the pipeline: a second change, or the first feature after Brownfield onboarding (Planning amends the PRD and opens a new change)

## Input

**Source:** User prompt (natural language description of what they want built), including any must / should / could the user states. Ask for that cut if it is missing; the change brief's Priority Cut is filled from it.
**Location:** Provided directly by the user in conversation. No file input is required for a first initiative.

**Also read when present:**
- `.gener8v/CONVENTIONS.md`: the slug rule, vocabularies and roles
- `.gener8v/prd.md`: the living PRD to amend (never overwrite)
- `.gener8v/changes/*/change.md`: existing changes, so the new slug does not collide and the new brief does not duplicate an open initiative

## Output

**Produces:** Two markdown documents: the living PRD and a change brief
**Write to:**
- `.gener8v/prd.md`: the Product Requirements Document (living; amended in place, with a `## Change Log`)
- `.gener8v/changes/<change-slug>/change.md`: the change brief for this initiative (format below)
**Creates directories:** `.gener8v/` and `.gener8v/changes/<change-slug>/` if they do not exist

**Change slug:** kebab-case, derived from the initiative's title with the slug rule in `CONVENTIONS.md` §3 ("Search relevance v2" → `search-relevance-v2`). Choose it before writing anything: it names the directory every downstream change artifact lives in (`changes/<change-slug>/tickets/`, `changes/<change-slug>/delivery/`, `changes/<change-slug>/reviews/`) and never changes afterwards.

There is always a change. A greenfield first initiative writes `prd.md` *and* `changes/<change-slug>/change.md`; the first change is not special. Both documents are written with `**Status:** Draft` and `**Approved by:** pending`. When the Product Owner approves in conversation, update both lines on the approved document (`**Status:** Approved`, `**Approved by:** Product Owner — <name>, YYYY-MM-DD`).

**If `.gener8v/prd.md` already exists** (a second initiative, or the first change after Brownfield onboarding), Planning does not overwrite it. It reads the existing PRD, adds new capability areas or amends existing ones in place, keeps every existing area name (downstream slugs and requirement prefixes depend on them), marks anything dropped `*(Withdrawn YYYY-MM-DD)*`, and appends an entry to the `## Change Log` section at the end of the document saying what changed and why, naming the change slug. Existing change briefs are never edited by Planning. Downstream skills then run only for the areas this change touches, under `changes/<change-slug>/`.

The PRD is the single entry point for all downstream skills; they reference this path to locate it. The change brief is what Specification and Ticket Breakdown read to learn which areas and requirements this initiative touches and what not to build.

### System Context (Optional)

After producing the PRD, ask the user whether they want to provide system context — information about their existing technology stack, infrastructure, team capabilities, and organizational constraints. If provided, write to `.gener8v/context.md` as freeform markdown, including a `## Repositories` table (`| Directory | Purpose | Language / build | Verify commands |`) with one row for a single repository and several for a workspace.

This file is not required for the pipeline to proceed, but significantly improves the quality of Constraints analysis and Technical Design. Without it, those skills infer constraints from functional documents alone.

## Output Format

Produce two markdown documents with the following structures.

### PRD: `.gener8v/prd.md`

```markdown
# [Descriptive Title]

**Status:** [Draft / Approved]
**Approved by:** [Product Owner — name, YYYY-MM-DD — or "pending"]

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

## Change Log

- YYYY-MM-DD — opened; capability areas [list] (Planning, change: [change-slug])
- YYYY-MM-DD — [area] added / [area] amended / [area] withdrawn: [why] (Planning, change: [change-slug])
```

### Change brief: `.gener8v/changes/<change-slug>/change.md`

```markdown
# [Change title]

**Status:** [Draft / Approved / In Delivery / Complete / Abandoned]
**Approved by:** [Product Owner — name, YYYY-MM-DD — or "pending"]
**Opened:** YYYY-MM-DD
**Slug:** [change-slug]

## Why
[2–4 sentences: the problem or opportunity, and why now.]

## Outcome
[2–5 bullets: what is true when this change is complete.]

## Affected Capability Areas

| Area | Kind | Requirements |
|------|------|--------------|
| Search & Retrieval | modifies | Adds SR-REQ-011, SR-REQ-012, SR-NFR-002; Modifies SR-REQ-005; Withdraws — |
| Results Presentation | adds area | (pending specification) |

## Priority Cut
- **Must:** [the requirements/tickets without which the change is not worth shipping]
- **Should:** [...]
- **Could / later:** [...]

## Out of Scope
- ...

## Open Questions
- [ ] **OQ-001**: ...

## Change Log
- YYYY-MM-DD — opened (Planning)
- YYYY-MM-DD — SR specification amended: adds SR-REQ-011..012 (Specification)
```

Planning fills every Affected Capability Areas row's Requirements cell with `(pending specification)`; the `Kind` column is `adds area` or `modifies`. Specification replaces the cell with the real IDs (Adds / Modifies / Withdraws) when it runs for the change and appends its own Change Log line. The state script recommends `specification <area> for <change>` while a cell still says pending.

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

### Living PRD, Scoped Change
The PRD describes the whole product as it should be after every change so far; it is amended, never rewritten, and its capability area names are stable. The change brief describes only this initiative: which areas it adds or modifies, and the Priority Cut, which is where "what not to build" is decided. Put product truth in the PRD and initiative scope in the brief; do not repeat the PRD's capability bullets in the brief.

## Process

1. **Parse Intent**: Read the user prompt and identify the core problem or outcome they're seeking.

2. **Identify Capability Areas**: What major functional areas does this work span? Group related capabilities together.

3. **Draft Capabilities**: For each area, enumerate what the system should do using clear, testable statements.

4. **Ground in Scenarios**: Write 2-4 user scenarios that demonstrate the capabilities working together.

5. **Define Boundaries**: Explicitly list what's out of scope to prevent future confusion.

6. **Surface Unknowns**: Capture any ambiguity, missing information, or decisions needed as open questions.

7. **Review for Technical Leakage**: Scan the document and remove any implementation-specific language.

8. **Choose the Change Slug**: Derive it from the initiative's title with the slug rule in `CONVENTIONS.md` §3, and check `.gener8v/changes/` so it does not collide with an existing change.

9. **Write the PRD, Amending Rather Than Overwriting**: Write `.gener8v/prd.md` with `**Status:** Draft` and `**Approved by:** pending`. If a PRD already existed, confirm every pre-existing capability area is still present (or explicitly withdrawn), and record the change in `## Change Log` with the change slug.

10. **Write the Change Brief**: Write `.gener8v/changes/<change-slug>/change.md` in the format above: `**Status:** Draft`, `**Approved by:** pending`, every Affected Capability Areas row at `(pending specification)`, the Priority Cut filled from the user's stated must / should / could (ask when it is missing), and a Change Log line `opened (Planning)`.

11. **Record Approval**: When the user approves the PRD or the brief in conversation, set `**Status:** Approved` and `**Approved by:** Product Owner — <name>, YYYY-MM-DD` on that document. Until then the record says `Draft`, and Audit warns if downstream stages are produced from it.

## Example

The worked example shows both files Planning writes for the Support Documentation Search System: the living `prd.md` (three capability areas, Status and Change Log lines) and the change brief `changes/support-search/change.md` with its Affected Capability Areas at `(pending specification)` and its Priority Cut. It lives at `skills/planning/references/example.md`. Read it before producing your first artifact of this kind.

---

## Integration with Other Skills

This skill produces output that feeds into:
- **Specification Skill**: Reads the change brief, takes each affected Capability Area and amends its living specification, then replaces the brief's `(pending specification)` cell with the requirement IDs it added, modified or withdrew
- **Constraints Skill**: Analyzes the PRD for technical, compliance, or integration constraints
- **Dependencies Skill**: Maps dependencies between capability areas and external systems
- **Technical Design Skill**: Translates specifications and constraints into architecture decisions
- **Ticket Breakdown Skill**: Reads the brief's Priority Cut and Affected Capability Areas and decomposes the change's requirements into `changes/<change-slug>/tickets/<area-slug>/` (one `TICKET-NNN.md` per ticket, plus `backlog.md`)
- **Orchestrate Skill**: Reads the PRD and lists changes (`active_changes`, per-change status and pending specification / breakdown in `pipeline-state.yaml`) to determine pipeline status and next steps

**Alternative entry point:**
- **Brownfield Skill**: For existing codebases, the Brownfield skill produces the living baseline (the PRD and specifications) bottom-up from code instead of top-down from user intent, and opens no change. The first feature afterwards is a Planning change like any other.

## Revisions

- A second initiative is a new change: re-running this skill opens `.gener8v/changes/<new-change-slug>/change.md` and amends `.gener8v/prd.md` in place, recording the change in `## Change Log`. The PRD is never overwritten, and existing change briefs are never edited by Planning
- Only the downstream artifacts of the areas the new change touches become stale; the state script recommends `specification <area> for <change>` while a brief cell still says `(pending specification)`
- If the change is limited to one capability area, re-run only the affected downstream skills for that change (Orchestrate's `warnings` will flag a specification whose area was renamed or withdrawn)
- If capability areas are added or removed, the Orchestrate skill can identify which downstream artifacts need to be created or are now orphaned
- A change that will not ship is not deleted: set its brief to `**Status:** Abandoned` with a Change Log line saying why
- System context (`.gener8v/context.md`) does not need to be regenerated when the PRD changes unless the project scope shifts significantly

## Notes

- Do not include time estimates; these are determined during ticket breakdown
- Do not include acceptance criteria; these are defined during specification
- Keep the document readable by non-technical stakeholders
- The PRD should be understandable without access to the original prompt
- Do not record priorities on PRD capability bullets; the Priority Cut lives in the change brief, and per-requirement priority tags are allocated by Specification
- **For existing codebases not yet on the pipeline**: If the project already has working code and no `.gener8v/prd.md`, use the Brownfield skill first. Brownfield works bottom-up (code → specifications → PRD) and writes the living baseline; Planning works top-down (intent → PRD → change brief → specifications) and opens every change, including the first feature after onboarding
