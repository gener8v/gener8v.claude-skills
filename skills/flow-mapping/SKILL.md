# Flow Mapping Skill

## Purpose

Turn current-state data-flow findings into Mermaid diagrams that **compile, read clearly, and state
their own maturity** — then iterate on them until they do. A flow map is not decoration: it is the
artifact stakeholders argue with. A diagram that renders but hides its cadence, its reliability, or
its evidence is worse than no diagram, because it looks authoritative while asserting nothing.

The skill pairs a **deterministic validator** (compilation + structural lints) with an **LLM review
pass** (judgement). The split matters: regex settles what is decidable, so the model's attention is
spent only on what needs a reader's judgement.

## When to Use

Use this skill when:
- A data-flow / system-map / integration-map deliverable needs diagrams
- Existing diagrams need to be checked before publication (they may not even compile)
- Current-state flows must be shown per domain (Sales, Policy, Underwriting, Claims, ...)
- Prose describes flows that nobody has drawn, so contradictions stay invisible
- A pipeline emits flows as `{source, target, transformation}` triples and needs them rendered

Do **not** use it for future-state architecture proposals — this skill asserts what *is*, evidenced.

## Input

**Source:** flow findings in any of these shapes
- `data-flow` / `system-map` / `integration-map` deliverables (`.json` or `.md`)
- flow triples: `[{name, source, target, transformation}, ...]`
- interview evidence describing how data moves

**Expects:** at minimum a source, a target, and what moves between them. Cadence, mechanism, and
reliability are what the skill exists to force into the open — their absence is a finding, not a
blocker.

## Output

**Writes to:** `.gener8v/flows/[domain-slug].md` (one file per domain), each containing:
- a short prose statement of the domain's current-state flow
- one or more Mermaid diagrams
- an explicit **Unknowns** list — what could not be evidenced

**Gate:** `workflows/validate-flows.sh` must exit 0 before the artifact is considered done.

## Output Format

````markdown
# [Domain] — Current-State Data Flow

## How data moves today
[Prose: the flow in plain language, naming systems and the humans in the loop.]

```mermaid
graph TD
    classDef reliable fill:#d4edda,stroke:#28a745,color:#000
    classDef fragile  fill:#fff3cd,stroke:#ffc107,color:#000
    classDef broken   fill:#f8d7da,stroke:#dc3545,color:#000
    classDef isolated fill:#e2e3e5,stroke:#6c757d,color:#000,stroke-dasharray: 5 5

    Personify["Personify"]
    FINYS["FINYS"]
    class Personify fragile
    class FINYS fragile

    Personify -. "member number, name, address | batch | nightly" .-> FINYS
```

## Reliability
| Node/Flow | Class | Why |
|---|---|---|
| Personify → FINYS | fragile | Nightly batch; DOB silently dropped |

## Unknowns
- [What the evidence does not establish — named, not smoothed over.]
````

## Principles

1. **Compilation is non-negotiable.** A diagram that does not render is not a deliverable. Gate it
   mechanically (`mmdc` exits 1 on a parse error); never eyeball it.
2. **Every edge states its payload.** `A --> B` asserts nothing. Say *what* moves, *how*, and *how
   often*: `-. "member number | batch | nightly" .->`.
3. **Reliability is part of the model, not a footnote.** Use the four classes — `reliable`,
   `fragile`, `broken`, `isolated`. An unclassed node is an unasked question.
4. **`isolated` means deliberately unconnected.** An isolated store with no edges *is* the finding
   (nothing reads or writes it). Do not "fix" it by inventing an edge, and do not lint it as an
   orphan.
5. **Evidence or unknown — never plausible.** A flow nobody described does not go in the diagram
   because it would be tidy. It goes in **Unknowns**.
6. **One domain per diagram.** Past ~18 nodes a graph stops being read and starts being admired.
   Split by domain and link.
7. **Contradiction is signal.** When IT and field staff describe the same flow differently, draw
   both and mark the conflict. Averaging them destroys the finding.
8. **Regex first, model second.** Do not spend an LLM call on what a lint decides.

## Process

1. **Collect** flows from the source deliverable/evidence. Group by domain.
2. **Draft** one diagram per domain in the Output Format above.
3. **Validate (mechanical):**
   ```bash
   workflows/validate-flows.sh .gener8v/flows/*.md
   ```
   Fix every `ERROR` (compilation, no nodes). Treat each `WARN` as a question to answer, not noise
   to silence — an unlabelled edge usually means the evidence never said what moves.
4. **Review (judgement)** — the LLM pass, on what the lint cannot decide:
   - **Clarity:** would a stakeholder who was *not* in the interviews read this the way we mean?
     Are labels domain language, or our shorthand? Is direction consistent?
   - **Maturity:** is each class assignment defensible from evidence? Is cadence real or assumed?
     Are the humans in the loop drawn, or silently abstracted into a system box?
   - **Fidelity:** does the diagram claim anything the evidence does not support? Anything in the
     prose that is missing from the diagram (or vice versa)?
5. **Iterate** 3–4 until validation is clean and review raises nothing new. Record what changed.
6. **Report** unresolved conflicts and Unknowns — they are output, not failure.

## Example

**Input triple**
```json
{"name": "member sync", "source": "Personify", "target": "FINYS",
 "transformation": "nightly batch; DOB dropped"}
```

**Draft (fails)**
```
graph TD
  Personify --> FINYS
```
`validate-flows.sh` → `WARN 1/1 edge(s) unlabelled`, `WARN no classDef`, `WARN no cadence`.
It compiles, so it looks finished — and asserts nothing.

**After iteration**
```
graph TD
    classDef fragile fill:#fff3cd,stroke:#ffc107,color:#000
    Personify["Personify"]
    FINYS["FINYS"]
    class Personify fragile
    class FINYS fragile
    Personify -. "member number, name, address | batch | nightly" .-> FINYS
```
Now it says: this is a batch flow, it runs nightly, it is fragile, and here is exactly what crosses.
The DOB loss surfaces in **Reliability** and drives a finding.

## Integration with Other Skills

- **Upstream:** consumes `data-flow` / `system-map` / `integration-map` deliverables.
- **Quality Review:** the LLM review pass (step 4) is the same detect→fix loop shape; findings can
  be routed to a rewriter rather than fixed inline.
- **Technical Design:** current-state flows are the baseline any target-state design must move from.
- **Specification:** Unknowns become open questions.

## Notes

- The validator needs `npx` (Node). It fetches `@mermaid-js/mermaid-cli@11` on first run.
- `MAX_NODES` (default 18) tunes the split threshold: `MAX_NODES=24 validate-flows.sh ...`.
- The four `classDef` colors are the house convention carried over from the interview decomposer's
  flow maps; keep them stable so diagrams read the same across engagements.
- Exit codes: `0` all diagrams compile and no ERROR lints; `1` otherwise; `2` bad usage.
