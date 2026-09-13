---
name: planning
description: "Turn a description of a feature, product or system into a PRD at .gener8v/prd.md (3-7 capability areas, user scenarios, scope boundaries, open questions) and open a change brief under .gener8v/changes/ with its priority cut. Use when the user describes something new they want built, such as 'I want to build a support portal' or 'add a feature that lets agents export results': a greenfield product, new scope on a project already on the pipeline (Planning opens a new change for it rather than folding it into a change in delivery), or the first feature after brownfield onboarding. Not for onboarding an existing codebase with no PRD (brownfield) or detailing an area the current change already covers (specification)."
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
- `.gener8v/changes/<change-slug>/change.md`: the change brief for this initiative (shape in `assets/change-brief.md`)
**Creates directories:** `.gener8v/` and `.gener8v/changes/<change-slug>/` if they do not exist

**Change slug:** kebab-case, derived from the initiative's title with the slug rule in `CONVENTIONS.md` §3 ("Search relevance v2" → `search-relevance-v2`). Choose it before writing anything: it names the directory every downstream change artifact lives in (`changes/<change-slug>/tickets/`, `changes/<change-slug>/delivery/`, `changes/<change-slug>/reviews/`) and never changes afterwards.

There is always a change. A greenfield first initiative writes `prd.md` *and* `changes/<change-slug>/change.md`; the first change is not special. Both documents are written with `**Status:** Draft` and `**Approved by:** pending`. When the Product Owner approves in conversation, update both lines on the approved document (`**Status:** Approved`, `**Approved by:** Product Owner — <name>, YYYY-MM-DD`).

**If `.gener8v/prd.md` already exists** (a second initiative, or the first change after Brownfield onboarding), Planning does not overwrite it. It reads the existing PRD, adds new capability areas or amends existing ones in place, keeps every existing area name (downstream slugs and requirement prefixes depend on them), marks anything dropped `*(Withdrawn YYYY-MM-DD)*`, and appends an entry to the `## Change Log` section at the end of the document saying what changed and why, naming the change slug. Existing change briefs are never edited by Planning. Downstream skills then run only for the areas this change touches, under `changes/<change-slug>/`.

The PRD is the single entry point for all downstream skills; they reference this path to locate it. The change brief is what Specification and Ticket Breakdown read to learn which areas and requirements this initiative touches and what not to build.

### System Context (Optional)

After producing the PRD, ask the user whether they want to provide system context — information about their existing technology stack, infrastructure, team capabilities, and organizational constraints. If provided, write to `.gener8v/context.md` as freeform markdown, including a `## Repositories` table (`| Directory | Purpose | Language / build | Verify commands |`) with one row for a single repository and several for a workspace.

This file is not required for the pipeline to proceed, but significantly improves the quality of Constraints analysis and Technical Design. Without it, those skills infer constraints from functional documents alone.

## Output Format

Produce two markdown documents, each from its template in `assets/`. Read the template before writing and follow it exactly, headings, field lines and table columns included: `scripts/gener8v-state.py` parses them.

### PRD: `.gener8v/prd.md`

Write it in the shape of `assets/prd.md`. The state script takes the first `# ` heading as the PRD title, the `**Status:**` line as its approval state, and each `### ` heading under `## Functional Capabilities` as a capability area — the slug of that heading names the area's specification, constraints, technical design and ticket directories. A trailing `*(Withdrawn YYYY-MM-DD)*` is stripped from the name.

### Change brief: `.gener8v/changes/<change-slug>/change.md`

Write it in the shape of `assets/change-brief.md`. The state script reads its `**Status:**` line and parses the `## Affected Capability Areas` table row by row — area name, kind, requirements cell — to derive the change's areas and which of them are still pending specification; lint checks every requirement ID in a cell against that area's specification.

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

10. **Write the Change Brief**: Write `.gener8v/changes/<change-slug>/change.md` in the shape of `assets/change-brief.md`: `**Status:** Draft`, `**Approved by:** pending`, every Affected Capability Areas row at `(pending specification)`, the Priority Cut filled from the user's stated must / should / could (ask when it is missing), and a Change Log line `opened (Planning)`.

11. **Record Approval**: **Ask, do not wait.** Present the artifact and request approval before the session moves on to another area, another skill, or another run — an artifact left `Draft` because nobody was asked is indistinguishable in the record from one the user declined to approve. When the user approves the PRD or the brief in conversation, set `**Status:** Approved` and `**Approved by:** Product Owner — <name>, YYYY-MM-DD` on that document. Until then the record says `Draft`, and Audit warns if downstream stages are produced from it.

## Example

The worked example shows both files Planning writes for the Support Documentation Search System: the living `prd.md` (three capability areas, Status and Change Log lines) and the change brief `changes/support-search/change.md` with its Affected Capability Areas at `(pending specification)` and its Priority Cut. It lives at `skills/planning/references/example.md`. Read it before producing your first artifact of this kind.

---

## Troubleshooting

- **The chosen change slug already names a directory under `.gener8v/changes/`.** Choose another: the slug names every artifact directory of the change and never changes afterwards. If the existing change is the same initiative, this is not a new change — resume it (Orchestrate says where it stands) instead of opening a second brief for the same work.
- **The user states no must / should / could.** Ask before writing the brief. The Priority Cut is the only place priority enters the pipeline — Specification tags requirements from it and every ticket's `**Priority:**` comes from it — so a cut Planning invents reappears on every ticket as if the Product Owner had set it.
- **An existing capability area's name no longer fits.** Keep the name and clarify the area in its bullets. The slug of the `### ` heading names the area's specification, constraints, technical design and ticket directories; renaming the heading orphans them, and the state script warns `specifications/<old-slug>.md has no matching capability area in the PRD`. A rename that cannot be avoided is recorded in the Change Log and renames every dependent file with it.
- **Orchestrate warns `change '<change-slug>' names area '<area-slug>' which is not in the PRD`.** A row in the brief's Affected Capability Areas table does not match a `### ` heading in the PRD — the script slugifies both and compares the slugs. Correct the row's area name, or add the area to the PRD when this change introduces it.
- **Orchestrate warns `PRD has no '### ' capability areas under '## Functional Capabilities'`.** The section heading was renamed or the areas were written at another heading level. Restore the structure of `assets/prd.md`; until then no area has a slug, and nothing downstream can be located.

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
