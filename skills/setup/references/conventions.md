# gener8v Conventions

Setup copies this file to `.gener8v/CONVENTIONS.md`. It is the single source for the rules every skill
depends on and none of them owns. Read it once per session; when a skill's own text disagrees with it, this
file wins and the skill has a bug.

## 1. Where the pipeline is

A project is "on the pipeline" when `.gener8v/prd.md` exists. The mere presence of `.gener8v/` proves
nothing — Defect Sweep and Flow Mapping create it on repositories that have never been onboarded. Setup,
Brownfield and Orchestrate all key their "already set up?" decision on `prd.md`.

`.gener8v/` lives at the root the user works from: a single repository, or a **workspace** directory that
contains several (§8). Skills are invoked as `/<skill>` when the skills were copied into
`~/.claude/skills/`, and as `/gener8v:<skill>` when the plugin is installed. Documents use the short form.

## 2. Living artifacts and change artifacts

Two kinds of artifact. **Living** artifacts describe the product — as it is (Brownfield) and as it should
be — and are amended in place; their IDs are append-only. **Change** artifacts belong to one initiative
and live under `changes/<change-slug>/`. A change is opened by Planning, specified by Specification (which
amends the living specifications and records the deltas in the brief), broken into tickets, delivered and
reviewed — all inside its own directory.

| Artifact | Path (under `.gener8v/`) | Kind | Written by | Read by |
|---|---|---|---|---|
| Conventions | `CONVENTIONS.md` | living | Setup | every skill |
| Pipeline state | `pipeline-state.yaml` | derived | `scripts/gener8v-state.py` — never by hand, never by the model when the script is available | Orchestrate, hooks, CI |
| Run log | `runs.jsonl` | derived | the hooks (session start, artifact writes) — never by the model | `gener8v-state.py metrics`, Orchestrate |
| PRD | `prd.md` | living | Planning (amends, with a Change Log), Brownfield (synthesizes) | everything |
| System context | `context.md` | living | Planning (optional), Brownfield (Phase 2); holds the `## Repositories` table | Constraints, Technical Design, Delivery, reviews, hooks |
| Brownfield checkpoints | `brownfield/reconnaissance.md`, `brownfield/capability-areas.md` | checkpoint | Brownfield (Phases 1, 3) | Brownfield (resume), Orchestrate |
| Specification | `specifications/<area-slug>.md` | living | Specification, Brownfield (Phase 4); `## @spec Coverage` rows appended by Delivery | Constraints, Dependencies, Technical Design, Ticket Breakdown, Delivery, Code Review, Audit |
| Constraints | `constraints/prd.md`, `constraints/<area-slug>.md` | living | Constraints | Dependencies, Technical Design, Ticket Breakdown, Delivery, Code Review, Security Review, Audit |
| Dependency map | `dependencies/dependency-map.md` | living | Dependencies | Technical Design, Ticket Breakdown, Audit |
| Technical design | `technical-design/<area-slug>.md`, `technical-design/system-design.md` | living | Technical Design | Ticket Breakdown, Delivery, Code Review, Security Review, Architecture Review, Audit |
| Change brief | `changes/<change-slug>/change.md` | change | Planning (opens); Specification (fills requirement deltas); the approving user (status) | Specification, Ticket Breakdown, Delivery, Orchestrate, Audit |
| Tickets | `changes/<change-slug>/tickets/<area-slug>/TICKET-NNN.md` — **one ticket, one file** — plus `tickets/<area-slug>/backlog.md` (overview, dependency chain, suggested ordering) | change | Ticket Breakdown; reviews may append a **Known Hazard** to a ticket's file when they defer a finding to it | Delivery, Orchestrate, Audit |
| Delivery record | `changes/<change-slug>/delivery/<area-slug>-ticket-NNN-delivery.md` | change | Delivery (from reconciliation onward); reviews append `## Post-Review Amendments` | reviews, Orchestrate, Audit, later Deliveries |
| Reviews | `changes/<change-slug>/reviews/<area-slug>-ticket-NNN-{code,quality,security}-review.md` | change | the review skill (or its agent) | Orchestrate, Audit, assessments, later Deliveries |
| Assessments | `reviews/<system-slug>-owasp-top10-assessment.md`, `…-owasp-llm-top10-assessment.md`, `…-architecture-assessment.md` | system-level | the assessment skill | Orchestrate, Audit |
| Flow maps | `flows/<domain-slug>.md` | standalone | Flow Mapping | Technical Design, Brownfield, Orchestrate |
| Sweeps | `sweeps/<subsystem-slug>-sweep.md` | standalone | Defect Sweep (or its agent) | Ticket Breakdown, Orchestrate, Audit |
| Audits | `audits/<scope>-audit-YYYY-MM-DD.md` | dated | Audit | Audit (carries deferrals forward), Orchestrate |

**Legacy layouts.** A project whose `tickets/`, `delivery/` and `reviews/*-review.md` sit at the top level
is read as the pseudo-change `initial`. Migrate once with
`git mv tickets delivery changes/initial/ && mkdir -p changes/initial/reviews && git mv reviews/*-review.md changes/initial/reviews/`.
A per-area ticket *file* (`tickets/<area-slug>.md` holding `### TICKET-NNN:` sections) is likewise still read,
and `gener8v-state.py split-tickets` turns it into the one-file-per-ticket directory. No skill writes to either
legacy shape.

**Active change.** A change is *active* while its status is `ready` or `in_delivery`. When exactly one
change is active, per-ticket skills (Ticket Breakdown, Delivery, the reviews) default to it; when several
are, name it — `/delivery Search & Retrieval TICKET-003 in search-relevance-v2` — and the skill asks if you
do not.

**Write authority for source code.** Delivery writes source on a ticket. Brownfield adds `@spec` annotation
comments and changes nothing else. Code, Quality and Security Review change source only in their resolution
phase, with the user's approval, and record every change in the delivery record's `## Post-Review Amendments`.
Defect Sweep may add a failing test as proof and says so in the sweep. Nothing else in the pipeline touches
source. Outside the pipeline, trivial fixes (typo, formatting, config) are fine; anything else is a ticket.

## 3. Slugs and prefixes

- **Slug:** lower-case the name, replace `&` with `and`, replace every run of non-alphanumerics with `-`,
  trim `-`. "Search & Retrieval" → `search-and-retrieval`; a change titled "Search relevance v2" →
  `search-relevance-v2`. `scripts/gener8v-state.py` implements exactly this.
- **Requirement prefix:** 2–4 upper-case letters derived from the capability area name (initials, or the
  first letters), unique across the project. Record the chosen prefix in the specification's Source Context
  (`**Requirement prefix:** SR`). `gener8v-state.py lint` fails on a prefix used by two specifications.
- **Reserved prefixes and segments** (never use as a requirement prefix): `TC CC IC OC RF DEP EXT RES RD AD
  TR TQ OQ DEL CR QR SEC DS FIND NFR REQ`.

## 4. Identifiers

| ID | Meaning | Allocated in |
|---|---|---|
| `<PFX>-REQ-NNN` | functional requirement | specification |
| `<PFX>-NFR-NNN` | non-functional requirement — a measurable target with a named verification method | specification |
| `TC/CC/IC/OC-NNN`, `RF-NNN` | technical / compliance / integration / operational constraint, risk flag | constraints document |
| `DEP/EXT/RES/RD-NNN` | internal dependency, external dependency, shared resource, risk dependency | dependency map |
| `AD-NNN`, `TR-NNN`, `TQ-NNN` | architecture decision, technical risk, technical question | technical design |
| `OQ-NNN` | open question | any document |
| `TICKET-NNN` | ticket — one action item, one file | `changes/<change-slug>/tickets/<area-slug>/TICKET-NNN.md`; numbering restarts per area within a change |
| `DEL-NNN` | delivery decision | delivery record |
| `CR/QR/SEC-NNN` | code / quality / security finding | review report |
| `DS-NNN` | sweep finding | sweep |
| `FIND-NNN` | audit finding | audit report |

**IDs are append-only.** Once issued, an ID is never reused or renumbered. A skill that re-runs loads the
existing document first, keeps every existing ID and heading, allocates new IDs above the current maximum,
and marks anything removed `**Status:** Withdrawn` in place. Code carries `@spec` annotations that point at
requirement IDs; renumbering silently re-binds them to the wrong requirement.

**Requirement tags.** A requirement introduced or amended by a change says so inline:
`- **SR-REQ-011** *(must · change: search-relevance-v2)*: …`; an amended one appends
`*(amended 2026-08-26 by search-relevance-v2)*`. Baseline (Brownfield) requirements carry no tag. The
priority word (`must` / `should` / `could`) is optional on requirements and required on tickets.

**One ticket, one file.** A ticket is read, delivered and reviewed on its own, so it lives on its own: `TICKET-NNN.md`
opens with `# TICKET-NNN: title` and three header lines (`**Change:**`, `**Capability Area:**`, `**Specification:**`)
that make it self-describing, then the ticket fields. A withdrawn ticket keeps its file with `**Status:** Withdrawn`
at the top; a re-run breakdown adds files and never rewrites a delivered ticket's file.

**Qualify IDs outside their home document.** Numbering restarts per document, so a reference from another
document names the source: `prd/TC-001`, `search-and-retrieval/TC-001`,
`search-relevance-v2/search-and-retrieval/TICKET-003`,
`search-relevance-v2/search-and-retrieval-ticket-001-security-review/SEC-002`, `TICKET-003/DEL-001`. No
skill keeps a shared counter; there is no register to race on.

## 5. Vocabularies

- **Change brief `**Status:**`:** `Draft` · `Approved` · `In Delivery` · `Complete` · `Abandoned`. The state
  script derives the working status (`planned` / `ready` / `in_delivery` / `complete` / `abandoned`) from the
  artifacts and warns when the declared status disagrees.
- **Artifact `**Status:**`** on PRD, specification, constraints (PRD-level and per-area), dependency map and
  technical design (per-area and system): `Draft` · `Approved`, with `**Approved by:** <Role> — <name>,
  YYYY-MM-DD` (§7). The state script counts every `Draft` one toward `approvals_pending`.
- **Ticket `**Priority:**`:** `Must` · `Should` · `Could`.
- **Delivery record `**Status:**`:** `Reconciled` (pre-flight Go, plan not yet approved) · `In Progress`
  (plan approved, code being written) · `Delivered` · `Partial` · `Blocked`.
- **Delivery record `**Verification:**`:** `passed` · `failed` · `not run` — from the `## Verification Run`
  section's executed commands.
- **Review `**Result:**`** (all three reviews, identical): `Approved` · `Approved with Notes` ·
  `Changes Required`. Security Review additionally reports `**Accepted Risks:** N`.
- **Finding `**Status:**`:** `Open` · `Resolved` · `Deferred → <TICKET-NNN or reason>` · `Dismissed` ·
  `Accepted Risk` (security only).
- **Ticket status in `pipeline-state.yaml`:** `blocked` (a dependency is not delivered) · `ready` ·
  `reconciled` · `in_progress` · `partial` · `blocked_delivery` (pre-flight failed) · `delivered` ·
  `changes_required` · `reviewed` · plus `done: true|false`.
- **Review deferral:** a delivery record may carry `**Reviews Deferred:** quality, security — <reason>`; the
  state script treats a deferred review as satisfied so a Light-scope project can reach `done`.

## 6. Definition of Done

A ticket is **done** when its delivery record says `Delivered`, its `## Verification Run` passed, and each
of the three reviews is either `Approved` / `Approved with Notes` or explicitly deferred in the delivery
record. A change is **complete** when every ticket in every breakdown under it is done. Anything else —
including a `Changes Required` verdict — leaves the ticket open, and `pipeline-state.yaml` says so
(`done: false`, `status: changes_required`). CI gates read that field, not the existence of files.

## 7. Roles and approvals

One person may hold every role; the record still names the role, so that a reader knows which hat approved
what and a team can split them later.

| Role | Approves | Recorded where |
|---|---|---|
| Product Owner | PRD, change brief, specifications (scope, priority cut) | `**Approved by:**` line on the artifact |
| Architect | technical design, constraints, the dependency map | `**Approved by:**` line on the artifact |
| Engineer | the implementation plan, before code is written | `**Plan approved by:**` in the delivery record |
| Security | risk acceptance on a security finding | `**Risk accepted by:**` on the finding |
| Reviewer | the three reviews' findings phases — always a different context from the builder | the reviewer agents; the report names the agent |

The skill that writes an artifact writes `**Status:** Draft` and `**Approved by:** pending`; when the user
approves in conversation the skill updates both lines. Approval is a gate for the *next* stage only in the
sense that Audit raises a Warning when tickets were cut from a Draft specification or a delivery started
from a Draft change brief; it never blocks — the record simply says so.

## 8. Workspaces

`context.md` carries a `## Repositories` table — `| Directory | Purpose | Language / build | Verify
commands |` — with one row for a single repository and several for a workspace. Every code path in every
artifact is **root-relative** (`api/src/search/query.ts`), including ticket Output and Prior Art, delivery
Files Produced, `@spec Coverage` locations and review Location fields. Delivery names the repository it
changes in its plan, runs that repository's verify commands, and commits in that repository; a ticket that
touches two repositories is two tickets unless the change is atomic. Hooks and the state script take the
workspace root (`CLAUDE_PROJECT_DIR`); the `@spec` lint walks every repository beneath it.

## 9. Verify against ground truth

Every skill that consumes another artifact's claims about the repository checks them against the repository
before building on them: Ticket Breakdown confirms Prior Art paths exist, Technical Design confirms the
infrastructure it assumes is present, Delivery reconciles the ticket before planning, Audit's reconciliation
mode does it for externally-authored plans. Resolve from code what code can answer; escalate only what
remains.

## 10. Metrics are derived

`gener8v-state.py metrics` computes review verdict distributions, finding counts, rework rate, verification
pass rate, deferred reviews, approvals pending, sweep findings, lead time (from git) and session counts
(from `runs.jsonl`). Nothing in the pipeline asks a person or a model to record a metric; if a number is
worth knowing it is worth deriving from the artifacts.

## 11. Keep skills engagement-neutral

Skill bodies describe the method. Client systems, product names, decision-log IDs from a particular
engagement and real dataset names belong in an example file, not in the rules an agent will generalise from.
