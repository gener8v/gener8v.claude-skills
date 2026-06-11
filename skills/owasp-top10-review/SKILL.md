# OWASP Top 10 Review Skill

## Purpose

Perform a systematic, category-by-category assessment of a codebase against the **OWASP Top 10:2025** web application security risks. Where the Security Review skill hunts for individual vulnerabilities bottom-up, this skill works top-down: it walks all ten OWASP categories, assesses the system's posture in each, maps existing findings (SEC-XXX) onto the framework, verifies the categories a finding-by-finding pass tends to under-probe, and produces a coverage matrix that makes gaps and strengths legible against an industry-standard taxonomy.

It is the framework-coverage complement to Security Review: Security Review finds the bugs; this skill proves coverage and surfaces whole categories that were missed.

## When to Use

Use this skill when:
- A stakeholder asks "are we OWASP-compliant?" or "how do we score against the Top 10?"
- After a Security Review, to organize findings against a recognized taxonomy and check for blind spots
- Before an audit, certification, or customer security questionnaire
- When a finding register exists and needs re-ranking against the current OWASP edition (the 2025 list reshuffled and renamed several categories)
- For periodic posture reviews where category completeness matters more than finding novelty

## Input

**Source:** Delivered code, configuration, infrastructure-as-code, CI/CD, and any existing security finding register
**Read from:**
- The codebase (application routes, auth, data layer, config, containers, compose/IaC, CI workflows)
- An existing security review report (e.g. `.gener8v/reviews/[slug]-security-review.md`) if one exists — to map SEC-XXX findings onto categories rather than re-deriving them
- Constraints: `.gener8v/constraints/[slug].md` (if available — for compliance requirements)
- Technical Design / System Context (if available — for deployment topology)

**Expects:** Code to exist. Degrades gracefully — with no prior security review it derives findings directly; with one, it maps and supplements.

## Output

**Produces:** An OWASP Top 10:2025 coverage assessment
**Write to:** `.gener8v/reviews/[slug]-owasp-top10-assessment.md`
**Creates directory:** `.gener8v/reviews/` if absent
**Naming:** `-owasp-top10-assessment` suffix

New findings discovered during the pass are assigned the next SEC-XXX IDs and added back to the canonical security review register (so there is one source of truth), with full descriptions in this document.

## The Framework — OWASP Top 10:2025

Assess every category. The 2025 edition (finalized January 2026) reshuffled and added categories — use these, not the 2021 list:

- **A01:2025 — Broken Access Control** (authn, authz, IDOR, tenant isolation, function/object-level checks)
- **A02:2025 — Security Misconfiguration** (↑ from #5: env gating, exposed surfaces, CORS, headers, container hardening, IaC, default secrets)
- **A03:2025 — Software Supply Chain Failures** (NEW, broadens "Vulnerable & Outdated Components": dependencies + build systems + distribution + CI/CD integrity)
- **A04:2025 — Cryptographic Failures** (hashing, token signing, data-at-rest/in-transit, key management)
- **A05:2025 — Injection** (SQL/NoSQL/command/template/LDAP, XSS, insecure deserialization)
- **A06:2025 — Insecure Design** (design-level flaws, missing controls by design, abuse cases, mass assignment, resource limits)
- **A07:2025 — Authentication Failures** (credential strength, brute-force protection, session/token lifecycle, enumeration)
- **A08:2025 — Data Integrity Failures** (deserialization integrity, update integrity, CI/CD pipeline integrity not covered by A03)
- **A09:2025 — Security Logging & Alerting Failures** (logging of auth/authz events, monitoring coverage, alerting)
- **A10:2025 — Mishandling of Exceptional Conditions** (NEW, 24 CWEs: fail-open behavior, improper error handling, failing into insecure state)

Note: SSRF is no longer a standalone top-level category in 2025 (folded in) — still assess it as a sub-check under A10/A05.

## Output Format

```markdown
# [System]: OWASP Top 10:2025 Assessment

## 1. Coverage Summary
[Table: # | Category | Status (Adequate / Gaps / Primary gap / Not applicable) | Driving findings]
[2-3 sentence net: where risk concentrates, which categories pass.]

## 2. Category-by-Category Assessment
### A01 — Broken Access Control · [status]
**What was checked:** ...
**Evidence (controls present):** ...
**Gaps / findings:** [mapped SEC-XXX + any new]
[... repeat for A02–A10 ...]

## 3. New-Category / New-Finding Pass
[Focused analysis of A03 supply chain and A10 exceptional-conditions, plus any new SEC-XXX raised, fully described: severity, category, location, attack scenario (Med+), impact, recommendation.]

## 4. Updated Register Totals
[Counts by severity; table of findings by 2025 category slot.]

## 5. Conclusion
[Priority guidance re-ranked by 2025 weighting.]
```

## Principles

### Assess Every Category — Including "Not Applicable"
A category with no findings is a result, not a skip. State what was checked and why it does not apply (e.g. "no vector DB → A10-LLM N/A"). A blank category reads as "not assessed," which is the opposite of coverage.

### Verify the Under-Probed Categories
Bottom-up bug hunts reliably miss A08 (insecure deserialization), A09 (logging gaps), A10 (fail-open error handling), and the SSRF sub-check. Actively grep for them: `pickle`/`yaml.load`/`marshal` (deserialization); logging calls around auth failures and authz denials (A09); broad/`except Exception` and silent fallbacks (A10); backend fetches of user-controlled URLs (SSRF). Absence of evidence is only evidence of absence after you look.

### Map, Don't Duplicate
If a security review register exists, map its SEC-XXX onto categories rather than re-describing each finding. Add value through coverage and re-ranking, not restatement. Only fully describe findings this pass newly discovers.

### Honor the 2025 Re-Ranking
The 2025 edition moved Security Misconfiguration to #2 and introduced Software Supply Chain Failures at #3. When advising priority, reflect the current weighting — a misconfiguration cluster is now a #2-class concern, not a #5-class one.

### Attack Scenarios for Medium+
Every Medium-or-higher finding states who the attacker is, what access they have, and what they achieve. A finding without a scenario is an assertion.

### Compliance Constraints Are Non-Negotiable
A documented compliance constraint (CC-XXX) violation is automatically Critical regardless of exploitability.

## Process

1. **Locate inputs** — read the codebase and any existing security review register.
2. **Inventory the attack surface** — routes/entry points, auth model, data layer, config, containers, IaC, CI/CD.
3. **Walk A01→A10** — for each, record what was checked, evidence of controls present, and gaps; map existing SEC-XXX.
4. **Run the under-probed verifications** — deserialization, security-event logging, fail-open `except` patterns, SSRF, mass assignment. Use targeted greps; cite file:line.
5. **Deep-pass the 2025 additions** — A03 (deps + base-image pinning + CI integrity + a continuous-scan gate) and A10 (enumerate every degrading/broad `except`; classify fail-open vs fail-closed vs intentional-degradation; the security-relevant fail-opens become findings).
6. **Raise & number new findings** — next SEC-XXX IDs; full descriptions; push back to the canonical register.
7. **Build the coverage matrix + re-ranked priority** — counts by severity, findings by 2025 category.
8. **Write the report** to `.gener8v/reviews/`.

## Example (abbreviated)

> **A02 — Security Misconfiguration · Primary Gap.** Confirmed-live `local`-mode stack on the public internet (SEC-010), public API docs (SEC-011), CORS wildcard methods/headers (SEC-006), root containers (SEC-012), unpinned base images (SEC-013), missing security headers (SEC-014). Elevated to #2 under the 2025 weighting.
>
> **A10 — Mishandling of Exceptional Conditions · Minor.** Reviewed every degrading `except`: credential *decryption* fails closed (correct); credential *factory* falls back to global creds on decrypt error (fail-open → new finding SEC-021); arq-pool and enqueue degradations are intentional but should alert (ties A09/SEC-018).

## Integration with Other Skills

**Upstream:** Security Review (provides the SEC-XXX register to map); Constraints (compliance); Technical Design (topology).
**Parallel:** OWASP LLM Top 10 Review (for AI/LLM systems — run both; this covers the web surface, that covers the model surface).
**Downstream:** Audit (consumes coverage results); the report is a reference artifact.

## Notes

- Point-in-time. OWASP revises the Top 10 periodically (2021 → 2025); confirm you are assessing against the current edition and re-rank prior registers when a new edition lands.
- This skill assesses against a taxonomy — it does not replace deep bug-hunting (Security Review) or threat modeling.
- For API-heavy systems, add a short **OWASP API Security Top 10 (2023)** cross-map — it resolves object/function-level authz and resource-consumption risks the web list blurs.
- Can run standalone (derives findings) or as a coverage layer over an existing Security Review (maps + supplements).
