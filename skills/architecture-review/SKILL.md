---
name: architecture-review
description: "Adversarial, code-grounded review of an existing system's architecture: is it real (do ADRs match the code), is it right for a system of this nature, what are its inherent limitations and what concretely would have been better — every alternative proven against the code. Use for 'is our architecture sound', technical due diligence, before a major architectural commitment, or at milestone health checks."
argument-hint: "[system slug]"
---
# Architecture Review Skill

## Purpose

Adversarial, code-grounded review of an existing system's architecture. It answers three questions, in order:

1. **Is it real?** Does the running code match the architecture decision records (ADRs), or has the documentation run ahead of the implementation? "Real" is established by reading the source, not by trusting ADRs or docstrings.
2. **Is it good?** Not "is each decision locally defensible" (a low bar almost everything clears) but "is this how a system *of this nature* should be designed?"
3. **What are its inherent limitations, and what would concretely have been a better decision?** Every alternative must be proven against the actual code and shown as a runnable sketch — never a vendor reflex.

This operates at the **system-architecture altitude** and is deliberately adversarial. It is distinct from the other skills: `technical-design` *produces* forward-looking design; `audit` checks `.gener8v/` artifact consistency; `code-review` / `quality-review` / `security-review` operate at the per-delivery code altitude. Architecture Review critiques the architecture of a system that already exists.

## When to Use

- An architect or stakeholder asks "is our architecture sound?" / "what should we change?"
- Technical due diligence — acquisition, investment, or inheriting a codebase
- Before a major architectural commitment (adopting a datastore, a workflow engine, a new boundary)
- When a system has accumulated many ADRs and you want to test design against shipped reality
- Periodic architecture health checks at slice/milestone boundaries

## Input

**Source:** The codebase (the source of truth for "real"), plus whatever architecture intent exists.
**Read from:**
- The implementation — entry points, the core subsystem(s), the data layer, orchestration/control plane, config, IaC, CI
- Architecture decision records / style-of-record docs / fitness functions / risk registers, if present
- Existing per-ticket reviews (optional — to map onto, not duplicate): security reviews from `.gener8v/changes/*/reviews/*-security-review.md` (and the legacy `.gener8v/reviews/*-security-review.md`), quality and code reviews alongside them, and any system-level OWASP assessment in `.gener8v/reviews/`

**Expects:** Code to exist. Architecture intent docs are helpful but optional; with none, derive the implicit architecture from the code and assess that.

## Output

**Produces:** A code-grounded, adversarial architecture assessment.
**Write to:** `.gener8v/reviews/<system-slug>-architecture-assessment.md`
**Creates directory:** `.gener8v/reviews/` if absent.

## Output Format

```markdown
# [System]: Architecture Assessment

## 1. Verdict
[Lead with the sharp theses (T1/T2/T3...), each one sentence. State the headline tension.]

## 2. Is It Real? (from the code, not the ADRs)
[Conformance table: each Accepted decision -> verified in source? Confirm Proposed/RFC items are genuinely unbuilt. Substance-vs-stub evidence (line counts, real calls, test counts). The gaps the doc surface hides.]

## 3. Is the Style Locally Sound? (necessary, not sufficient)
[Brief: yes/no on the narrow "reasonable v0 style" question — then state why that is a low bar.]

## 4. Adversarial: Is This How a System of This Nature Should Be Designed?
[2-4 theses. For each: the critique (code-cited) -> inherent limitation -> what would have been better (concrete sketch + real gotchas) -> steelman.]

## 5. Inherent Limitations
## 6. What the Team Got Right (fairness / steelman)
## 7. Recommendations (prioritized, concrete)
## 8. Open Questions for the Architect
## 9. Bottom Line
```

## Principles

### Real Comes From Code, Not ADRs
An ADR is a claim; a docstring is a claim; only the code is evidence. For every "Accepted" decision, find it in the source. For every "Proposed/RFC" decision, confirm it is genuinely *not* half-built (grep for the would-be imports/tables). Distinguish substance from stubs: line counts, whether functions actually do the work (e.g. a stage that calls the model vs. a `pass` body), real test counts and `skip`/`xfail` counts. The most valuable finding is often the gap between the documentation surface and what runs.

### Local Soundness Is a Low Bar
"Each decision is individually defensible" is almost always true and almost always beside the point. A series of reasonable decisions can compose into a system structurally wrong for its purpose. Always first ask: *what kind of system is this, really?* (a data pipeline? a CRUD app? an event system? an ML product? a ledger?) Then ask whether the architecture matches that nature — and name the mismatch when it doesn't.

### No Vendor or Tool Reflex — Prove It or Drop It
"Adopt Temporal / Dagster / Kafka / a graph DB" is worthless as a reflex. Any "X would be better" claim must be proven *from this codebase*: the specific lines and failure modes it would replace, what it would **and would not** save, and the honest new cost it imposes (operational surface, learning curve). Quantify (e.g. "740 of 1,252 lines are domain persistence no engine would save; the replaceable control plane is ~350"). If you cannot prove it against the code, do not make the claim. When the code contradicts your first instinct, **retract it explicitly** — a visible retraction is what makes the rest of the review credible.

### Better-Decisions Must Be Concrete
"Use row-level security" is a slogan. A migration (`ENABLE ROW LEVEL SECURITY` + `CREATE POLICY ...`), the wiring change, and the three gotchas that actually bite (non-owner role, the resolution chicken-and-egg, per-checkout transaction scoping) is a defensible alternative. Show runnable sketches — SQL, schema, code — with their real caveats. The caveats are not optional; they are what separate engineering judgment from name-dropping.

### Find the Design-to-Validation Ratio
Count what is *decided* versus what is *validated by running code*. Thirty ADRs and one end-to-end path is an inversion. Watch for the twin smell: **over-building in one dimension while under-building another** (a DAG engine executing a strictly linear pipeline; an elaborate recovery detector that is written, tested, and never wired in). Both are failures of *where* effort went, and both are code-provable.

### Critique Risk Sequencing, Not Just Risk Presence
Right-thing-wrong-time is a finding. Ask which risks were deferred and which were hardened. If the existential risks for a system of this nature (tenant isolation of sensitive data, correctness/groundedness of outputs sold to customers, data-loss/consistency) were postponed while cheap invariants were polished, that inversion is the headline — even when every individual deferral was "reasonable for the slice."

### Adversarial, But Fair
Steelman every critique and include an honest "what the team got right." Note where a deferral is genuinely correct for the stage. Adversarial without credibility is just contrarian; the goal is feedback on the quality of reality, delivered so it survives the architect's pushback.

### Quantify and Cite
`file:line`, line counts, grep results, test counts. "It's over-engineered" is an opinion; "Kahn's-algorithm topological sort + cycle detection in `stages/__init__.py`, but `next_stage()` is `order.index(current)+1` — a DAG engine running a linked list" is a finding.

## Process

1. **Name the system's nature.** Before judging the architecture, state what kind of system this actually is. Everything downstream tests fit-to-nature.
2. **Inventory the intent.** Read the style-of-record, ADRs (split Accepted vs Proposed/RFC), fitness functions, and risk register. Note what is claimed.
3. **Reality audit (code is truth).** For each Accepted decision, verify in source. Confirm Proposed items are genuinely unbuilt (grep for absence). Substance-vs-stub: line counts, real work vs placeholders, test counts and skips. Record the gaps the doc surface hides.
4. **Local soundness (brief).** Answer the narrow "reasonable style?" question, then explicitly mark it as necessary-not-sufficient.
5. **Adversarial pass.** Develop 2-4 theses about whether a system of this nature should be built this way. Ground each in cited code. Read the actual control plane / core subsystem deeply enough to be specific.
6. **For each thesis:** critique -> inherent limitation -> concrete better-decision (sketch + gotchas) -> steelman. Kill any claim you cannot prove from the code; retract overstatements visibly.
7. **Design-to-validation ratio + risk sequencing.** Make these explicit findings.
8. **Recommendations.** Prioritized, concrete, cheap-first. Distinguish "wire what you already built" from "adopt a new substrate" and give the *trigger* for the latter rather than recommending it by default.
9. **Open questions for the architect.** The load-bearing decisions still unmade.
10. **Write the report.**

## Example (abbreviated — from a real review)

> **T1 — Silent ownership of execution correctness, mis-invested.** The product is an LLM data-pipeline, but it runs on a task queue (`arq`), so the team owns durability by hand. Reading the runtime: ~740 of `orchestrator.py`'s 1,252 lines are irreducible domain persistence **no workflow engine would save** (retract the reflexive "adopt Dagster"). The genuine findings are opposite-signed: they *over-built* a DAG substrate (Kahn's sort, cycle detection) to run a **strictly linear** pipeline (`next_stage()` = `index+1`), and *under-built* recovery — `find_stale_running_stages()` is written, tested, and **never wired** (grep: referenced only by tests + `__all__`), so a dead worker strands an audit until a human notices. Better-decision is therefore **not** "adopt a vendor" but "wire the recovery you already built (~1 hr), add backoff, and write the ADR naming the *trigger* for a durable executor (pipeline goes non-linear / resume-from-step becomes an SLA need)." Steelman: for a tiny team migrating off a prototype, hand-rolled-but-wired is right.

## Integration with Other Skills

**Upstream:** Technical Design (the forward design this reviews against); Security Review / OWASP reviews (map their SEC-NNN onto architecture concerns, e.g. tenant isolation, denial-of-wallet — cite them qualified with the change segment, `<change-slug>/<area-slug>-ticket-NNN-security-review/SEC-NNN`, since finding numbers restart per report).
**Parallel:** Quality Review (code altitude) — different altitude, complementary.
**Downstream:** Audit (can fold architecture findings into a cross-stage assessment); Ticket Breakdown (recommendations that need code changes become tickets); Orchestrate (lists the assessment under `cross_cutting.assessments` and recommends one at milestone boundaries).

## Revisions

- Re-run when the architecture changes materially (new datastore, new boundary, a deferred risk coming due) and at milestone boundaries; the report is point-in-time.
- Re-running replaces `<system-slug>-architecture-assessment.md`; carry forward the previous theses with their current status (addressed / still open / retracted).

## Notes

- Adversarial by design. The point is to pressure-test reality, not validate it — but every critique must be fair (steelman) and provable (code-cited).
- Re-run when the architecture changes materially (new datastore, new boundary, a deferred risk coming due).
- This skill reads code deeply — budget for reading the actual control plane / core subsystem, not just the ADRs. The whole method depends on it.
- Define software acronyms (DAG, RLS, CRUD, ...) at first use; these reports are read by mixed audiences.
