---
name: owasp-llm-top10-review
description: "OWASP Top 10 for LLM Applications 2025 assessment of anything that calls a model: direct and indirect prompt injection, sensitive disclosure, output handling, excessive agency, system-prompt leakage, vector and embedding weaknesses, unbounded consumption. Use for chat, RAG, agentic or LLM-orchestration code, alongside the web OWASP review."
argument-hint: "[system slug]"
---
# OWASP LLM Top 10 Review Skill

## Purpose

Perform a systematic, category-by-category assessment of an AI/LLM application against the **OWASP Top 10 for LLM Applications 2025**. Generic web security reviews (and even the OWASP web Top 10) do not capture risks that are specific to systems that build prompts from untrusted input, retrieve external content into model context, persist model output as product, grant models agency, or spend money per inference. This skill covers that model-specific surface.

Use it for anything LLM-shaped: chat/assistant apps, RAG pipelines, agentic systems, multi-stage model orchestration, LLM-as-judge, content generation, and tool-using agents.

## When to Use

Use this skill when the system:
- Calls an LLM (hosted API or self-hosted) anywhere in a request or job path
- Substitutes user/tenant input or retrieved content into prompts
- Implements RAG, embeddings, vector search, or any retrieval-augmented context
- Grants a model agency (tool calls, external writes, sends, deploys) based on its output
- Persists or surfaces model output to users as product
- Has a per-inference cost (token/$ spend) that a caller can influence

Run it **alongside** the OWASP Top 10 (web) Review — the web list covers the HTTP/infra surface; this covers the model surface. Both are needed for an LLM app.

## Input

**Source:** The LLM orchestration code plus its surrounding app
**Read from:**
- Prompt assembly code and prompt templates (how variables/retrieved content enter prompts)
- The LLM client(s) — request body construction, output handling, retries, structured-output usage
- Retrieval/ingestion stages (search, scraping, fetch, RAG) and any vector store
- Telemetry/observation surfaces — what model I/O is exposed via API/UI
- Cost/usage tracking and any budget/quota enforcement
- Any agency surface — tool definitions, external writes, sends, exports
- Every existing security review report (`.gener8v/changes/*/reviews/*-security-review.md`, and legacy `.gener8v/reviews/*-security-review.md`) and the web OWASP assessment, referenced as `<change-slug>/<report-slug>/SEC-XXX` (e.g. `support-search/search-and-retrieval-ticket-002-security-review/SEC-002`) or `<system-slug>-owasp-top10-assessment/SEC-XXX`, to map onto rather than duplicate

**Expects:** LLM-touching code to exist. If there is none, say so and stop — this skill does not apply.

## Output

**Produces:** An OWASP LLM Top 10:2025 assessment
**Write to:** `.gener8v/reviews/[slug]-owasp-llm-top10-assessment.md`
**Creates directory:** `.gener8v/reviews/` if absent
**Naming:** `-owasp-llm-top10-assessment` suffix

New findings are numbered `SEC-001…` within this assessment and referenced from elsewhere as `<system-slug>-owasp-llm-top10-assessment/SEC-XXX`. Per-ticket security reviews are never edited by this skill.

## The Framework — OWASP Top 10 for LLM Applications 2025

Assess every category:

- **LLM01:2025 — Prompt Injection** (direct: user input into prompts; **indirect**: attacker-controlled retrieved content into prompts — often the higher-severity vector)
- **LLM02:2025 — Sensitive Information Disclosure** (model leaks PII/secrets/other-tenant data; raw prompt/response exposed via API/UI)
- **LLM03:2025 — Supply Chain** (model provenance/attestation, model gateway trust, client-lib CVEs, plugin/extension trust)
- **LLM04:2025 — Data and Model Poisoning** (poisoned training/fine-tune data; poisoned *retrieved* content; SEO-gamed sources feeding context)
- **LLM05:2025 — Improper Output Handling** (model output used unsafely downstream: eval, SQL/command building, unsanitized HTML/markdown render → XSS)
- **LLM06:2025 — Excessive Agency** (model output triggers external actions — tool calls, writes, sends — without validation or human-in-the-loop)
- **LLM07:2025 — System Prompt Leakage** (system prompts exposed via API/UI/error; secrets embedded in system prompts)
- **LLM08:2025 — Vector and Embedding Weaknesses** (RAG/vector-store risks: embedding inversion, cross-tenant retrieval, index poisoning)
- **LLM09:2025 — Misinformation** (hallucination/overreliance, especially for customer-facing analytical output; provenance/confidence)
- **LLM10:2025 — Unbounded Consumption** (denial-of-wallet / DoS: no spend or token ceiling, no per-tenant quota, unbounded automation)

## Output Format

```markdown
# [System]: OWASP Top 10 for LLM Applications (2025) Assessment

## 1. Coverage Summary
[Table: # | Category | Status | Findings]
[Net: which 1-2 LLM risks are material and why.]

## 2. Category-by-Category Assessment
### LLM01 — Prompt Injection · [status]
**How prompts are built:** [evidence — file:line of substitution]
**Findings:** [direct + indirect; SEC-XXX]
**Mitigations present:** ...
[... repeat LLM02–LLM10 ...]

## 3. New Findings
[Each new SEC-XXX: severity, category (OWASP LLMxx), location, attack scenario, impact, recommendation.]

## 4. Positive Controls (LLM-specific)
## 5. Conclusion
```

## Principles

### Indirect Injection Is the Sharp Edge
Direct prompt injection (a user editing their own prompt) is usually low-impact — the user only harms their own session, and output is typically parsed, not executed. **Indirect** injection — adversarial instructions inside retrieved web pages, documents, or search results that the pipeline feeds to the model as trusted context — is the higher-severity vector because the attacker need not be a user. Always trace where *retrieved/external* content enters a prompt, and treat it as untrusted, clearly-delimited data.

### Follow the Money (LLM10)
LLM apps have a per-inference cost. "Cost is tracked" is not "cost is bounded." Check whether anything *enforces* a per-request, per-tenant, or aggregate ceiling and aborts on breach. Unbounded, caller-influenced inference is denial-of-wallet — a real availability/financial risk, sharper when the endpoint is public or unauthenticated.

### Agency Is the Multiplier
Rate every category higher when the model can *act* (tools, writes, sends). With no agency (read-only stages writing to own DB), LLM05/06 are low; the moment output drives external artifacts or actions, re-rate and demand output validation + human-in-the-loop. Always note planned agency ("Sheets export ships next slice → re-assess LLM06").

### Check What's Exposed, Not Just What's Stored
For LLM02/LLM07, inspect the API/UI response schemas: is raw prompt or response text surfaced? Are system prompts reachable via any endpoint or error? Deliberate suppression of raw model I/O is a positive control worth crediting.

### Structured Output Is a Backstop, Not a Fix
Strict JSON-schema/`response_format` constrains output shape and limits injection blast radius — credit it, but it does not stop injection from skewing the *content* within the schema. Don't let it substitute for input-trust handling.

### Attack Scenarios for Medium+
Same rule as the other review skills: who, what access, what they achieve.

## Process

1. **Confirm applicability** — locate LLM-touching code; if none, stop.
2. **Trace prompt assembly** — how do user input and retrieved content enter prompts? Is there delimiting/escaping? (LLM01)
3. **Trace retrieval/ingestion** — what external content is fetched and fed to the model? Trust-scored? Sanitized? (LLM01 indirect, LLM04, LLM08)
4. **Inspect output handling** — is model output parsed, or eval'd / used to build SQL/commands / rendered as raw HTML? (LLM05)
5. **Map agency** — does output trigger external actions? With what validation/human gate? (LLM06)
6. **Inspect exposure surfaces** — API/UI schemas for raw prompt/response/system-prompt leakage; cross-tenant context. (LLM02, LLM07)
7. **Follow the money** — per-call caps vs aggregate/tenant ceilings; abort-on-breach; quotas. (LLM10)
8. **Model supply chain** — provenance/pinning, gateway trust, client-lib CVEs, plugins. (LLM03)
9. **Misinformation controls** — quality scoring, provenance/confidence surfacing, human-in-the-loop for customer-facing output. (LLM09)
10. **Raise & number findings**, write **positive controls**, and write the report to `.gener8v/reviews/`.

## Example (abbreviated)

> **LLM10 — Unbounded Consumption · Gaps.** Per-call `max_tokens` exists, but nothing caps total tokens/$ per audit, engagement, or tenant, and no run aborts on cost. Cost is tracked post-hoc, never enforced. With public exposure + no rate limit → denial-of-wallet. → **SEC-019 (Medium)**.
>
> **LLM01 — Prompt Injection · Gaps.** Naive `{{var}}` substitution of tenant input (SEC-008, info) *and* of web-search-retrieved page content (SEC-020, Medium — an attacker who ranks a page for the target entity injects instructions into the model's context). Structured-output constrains the blast radius but does not remove it.

## Integration with Other Skills

**Parallel:** OWASP Top 10 (web) Review — run both for an LLM app; this covers the model surface, that the HTTP/infra surface.
**Upstream:** Security Review (per-ticket SEC-XXX findings under `changes/<change-slug>/reviews/`); Technical Design (model/agency architecture).
**Downstream:** Audit; Ticket Breakdown (findings that need code changes become tickets); Orchestrate (lists the assessment under `cross_cutting.assessments`).

## Revisions

- Re-assess on architectural change — adding RAG/vectors re-opens LLM08 and LLM02; adding tools/agents re-rates LLM05/06; going multi-tenant re-opens LLM02 cross-tenant — and when the OWASP GenAI list is revised.
- Re-running replaces `[slug]-owasp-llm-top10-assessment.md`; carry forward open findings with their status.

## Notes

- Framework version: OWASP Top 10 for LLM Applications **2025**. The list evolves quickly (the 2025 edition added Vector & Embedding Weaknesses and System Prompt Leakage and reordered others); confirm the current edition before assessing.
- The OWASP GenAI Security Project also publishes companion guidance (agentic threats, red-teaming); pull from it for agentic systems.
- Pairs naturally with a threat model for the orchestration/agency layer.
