---
name: security-review
description: "OWASP-informed, code-level security review of delivered code: injection, authentication and authorization, data exposure, configuration, dependencies, cryptography and logging, with attack scenarios for Medium+ findings and compliance constraints (CC-XXX) treated as Critical. Use after a delivery, especially for input handling, auth, sensitive data or external integrations."
argument-hint: "<capability area> <TICKET-XXX> [in <change-slug>] | <files>"
---
# Security Review Skill

**Invoked with:** `$ARGUMENTS`

If that is empty, ask the user which delivered ticket (or which files) to review before doing anything else. Never guess the target.

A ticket belongs to a change. When exactly one change is active (`ready` or `in_delivery` in `.gener8v/pipeline-state.yaml`), default to it; when several are active and the argument does not name one (`… in <change-slug>`), ask which change before reading anything.

## Purpose

Perform an OWASP-informed, code-level security review of implemented code. This skill looks for vulnerabilities, misconfigurations, and security anti-patterns in delivered code. It operates at the code level — examining actual implementation for injection vectors, authentication gaps, data exposure, and insecure defaults. When constraints or technical design are available, it cross-references compliance requirements and security architecture decisions.

## When to Use

Use this skill when:
- A ticket has been delivered, especially tickets involving user input, authentication, data handling, external integrations, or configuration
- The system handles sensitive data (PII, credentials, financial data, health records)
- Before deployment or release
- After or in parallel with Code Review and Quality Review
- When compliance constraints (CC-XXX) exist that require security verification
- When the technical design includes authentication, authorization, or data protection decisions

## Input

**Source:** Delivered code files, plus security-relevant pipeline artifacts
**Read from:**
- Delivery record: `.gener8v/changes/<change-slug>/delivery/<area-slug>-ticket-NNN-delivery.md` (for the file list)
- Actual code files listed in the delivery record's "Files Produced" section
- Constraints: `.gener8v/constraints/prd.md` and `.gener8v/constraints/<area-slug>.md` (whichever exist — compliance constraints CC-XXX at either level apply)
- Conventions: `.gener8v/CONVENTIONS.md`
- Technical Design: `.gener8v/technical-design/<area-slug>.md` or `.gener8v/technical-design/system-design.md` (if available — for auth/authz design decisions)
- System Context: `.gener8v/context.md` (if available — for deployment environment and infrastructure; its `## Repositories` table says which repository each root-relative path lives in when the root is a workspace)

**Expects:** Code files to exist. Does NOT require all pipeline artifacts — the skill adapts its coverage based on what is available.

**If input is missing or malformed:**
- If no delivery record exists, the user can point directly to code files to review
- If constraints are missing, compliance verification is skipped — note "Compliance constraints not available" in the report
- If technical design is missing, architecture-level security checks are limited — note in the report
- If code files do not exist, stop and flag the issue

## Output

**Produces:** A security review report with findings and interactive resolutions
**Write to:** `.gener8v/changes/<change-slug>/reviews/<area-slug>-ticket-NNN-security-review.md`
**Creates directory:** `.gener8v/changes/<change-slug>/reviews/` if it does not exist
**Naming convention:** Matches the delivery record naming with `-security-review` suffix, inside the same change's directory. The top-level `.gener8v/reviews/` holds system-level assessments only — never write a ticket review there.

The report is written as soon as findings are drafted (all `Open`) and updated finding by finding during resolution. Approved remediations are applied in the resolution phase, re-verified, and recorded in the delivery record's `## Post-Review Amendments`. Findings are referenced from other documents as `<change-slug>/<report-slug>/SEC-XXX` — e.g. `support-search/search-and-retrieval-ticket-002-security-review/SEC-001` (numbering restarts per report; see `CONVENTIONS.md` §4).

## Output Format

Produce a markdown document with the following structure:

```markdown
# [Ticket ID]: [Ticket Title] — Security Review

## Summary

[2-3 sentences: what was reviewed, overall security posture, finding count by severity.]

**Files Reviewed:**
- [root-relative file path]
- [root-relative file path]

**Findings:** [Total count]
**Critical:** [Count] | **High:** [Count] | **Medium:** [Count] | **Low:** [Count] | **Informational:** [Count]

## Security Assessment

### Input Validation

**Status:** [Adequate / Gaps Found / Not Applicable]
**Notes:** [Assessment of input validation coverage at all entry points.
What inputs are validated, what is missing, what vectors exist.]

### Authentication & Authorization

**Status:** [Adequate / Gaps Found / Not Applicable]
**Notes:** [Assessment of auth patterns. Are auth checks present where needed?
Are authorization boundaries enforced? Are sessions handled securely?]

### Data Protection

**Status:** [Adequate / Gaps Found / Not Applicable]
**Notes:** [Assessment of sensitive data handling. Is PII protected?
Are credentials stored securely? Is data encrypted in transit/at rest where required?]

### Configuration Security

**Status:** [Adequate / Gaps Found / Not Applicable]
**Notes:** [Assessment of hardcoded secrets, environment configuration,
security-relevant defaults, CORS settings, security headers.]

## Findings

### SEC-001: [Finding title]

**Severity:** [Critical / High / Medium / Low / Informational]
**Category:** [Injection / Authentication / Authorization / Data Exposure / Misconfiguration / Dependency / Input Validation / Cryptography / Logging / Session Management]
**OWASP Reference:** [OWASP Top 10:2025 category, e.g. A05:2025 Injection — or "N/A" if not directly mapped]
**Location:** [root-relative path:line or function — `api/src/search/query.ts:42`, never relative to a repository inside a workspace]
**Description:** [What the vulnerability or concern is]
**Attack Scenario:** [How this could be exploited — required for Medium+ severity]
**Impact:** [What happens if exploited — data loss, unauthorized access, etc.]
**Recommendation:** [Specific remediation with code example if helpful]
**Compliance Impact:** [CC-XXX constraint IDs affected, if any, or "None"]
**Status:** [Open / Resolved / Accepted Risk / Deferred → TICKET-NNN or reason / Dismissed]
**Risk accepted by:** [Security — <name>, YYYY-MM-DD — required when Status is Accepted Risk; omit otherwise]
**Resolution:** [What was done, if resolved — filled in during resolution; for an accepted risk, the rationale and compensating controls]

---

### SEC-002: ...

## Resolution Log

| Finding | Decision | Action Taken | Risk Accepted | File Updated |
|---------|----------|-------------|---------------|--------------|
| SEC-001 | [Decision] | [What was changed] | [Yes/No] | [File path] |
| SEC-002 | Accepted Risk | — | Yes | — |

## Verdict

**Result:** [Approved / Approved with Notes / Changes Required]
**Unresolved Critical/High:** [Count — must be 0 for an Approved variant]
**Accepted Risks:** [Count, with brief summary of what was accepted]
**Notes:** [Any conditions on the approval or follow-up actions]
```

---

## Principles

### Severity Drives Priority
Use OWASP-aligned severity levels:
- **Critical**: Actively exploitable with high impact. Remote code execution, authentication bypass, SQL injection with data access. Must be remediated before deployment.
- **High**: Exploitable with moderate effort or significant impact. Privilege escalation, stored XSS, insecure direct object references. Should be remediated before deployment.
- **Medium**: Exploitable under specific conditions or with moderate impact. Reflected XSS, missing rate limiting, verbose error messages exposing internals. Should be addressed.
- **Low**: Minor concern or defense-in-depth gap. Missing security headers, overly permissive CORS in non-sensitive contexts. Address when practical.
- **Informational**: Best practice recommendation. Security improvement opportunity with no immediate risk.

Critical and High findings block approval unless the user explicitly accepts the risk with documented rationale.

### Attack Scenarios Are Required
Every Medium-severity-or-higher finding must include a plausible attack scenario: who is the attacker, what access do they have, what steps do they take, what do they achieve? This distinguishes real vulnerabilities from theoretical concerns. A finding without an attack scenario is an assertion, not evidence.

### Defense in Depth, Not Perfection
Security is layered. A missing validation at one layer is less severe if another layer catches it. Assess findings in the context of the full stack, not in isolation. A SQL injection vector behind an authentication wall and input sanitization middleware is lower severity than one in an unauthenticated public endpoint.

### Accepted Risk Is a Valid Outcome
Not every security finding must be fixed. Some are accepted risks: the likelihood is low, the mitigation cost is high, or compensating controls exist. The review records risk acceptance decisions explicitly with rationale. Critical findings require strong justification for acceptance — document why the risk is tolerable and what compensating controls exist. Acceptance is the Security role's decision (`CONVENTIONS.md` §7): every accepted-risk finding carries `**Risk accepted by:** Security — <name>, YYYY-MM-DD` next to its rationale, even when one person holds every role.

### Compliance Constraints Are Non-Negotiable
If the constraints analysis identifies compliance requirements (CC-XXX), violations of those constraints are automatically elevated to Critical severity regardless of exploitability. Compliance is not risk-based — it is requirement-based. A CC-XXX violation means the system does not meet its stated compliance obligations.

### Secrets in Code Are Always Critical
Hardcoded credentials, API keys, tokens, private keys, or connection strings in source code are Critical findings. No exceptions for "dev environments," "temporary values," or "will be changed later." If it is in the code and the code is committed, it is a secret exposure. The remediation is always: remove the secret, rotate it, use environment variables or a secrets manager.

### Dependencies Are Attack Surface
Third-party dependencies with known CVEs are findings. The review should check for outdated dependencies with known vulnerabilities where tooling makes this feasible (e.g., `npm audit`, `pip-audit`, `cargo audit`). The severity matches the CVE severity.

### Two Phases, Two Runtimes
**Findings** (steps 1–12) can run in a fresh context — the shipped `security-reviewer` agent, in parallel with the other two reviewers — because a reviewer who did not build the code has no reason to trust the builder's account of it. The findings phase writes the report with every finding `Status: Open` and a provisional verdict, and changes nothing else. **Resolution** (steps 13–15) runs in the main session with the user, one review at a time so three reviewers never edit the same file concurrently. Every approved change is re-verified and appended to the delivery record's `## Post-Review Amendments`; the report is updated per finding as it is resolved, and the final verdict is written last.

### Log Sensitive Data Never
Logging that includes PII, credentials, session tokens, full request/response bodies with sensitive fields, or stack traces with internal paths in production is a finding. Good logging is essential for security monitoring — but logging sensitive data creates a new exposure vector.

## Process

1. **Locate Code**: Read the delivery record to get the list of files produced. If no delivery record exists, use file paths provided directly by the user.

2. **Read All Code**: Read every delivered code file thoroughly.

3. **Read Security Context**: Read constraints (for CC-XXX compliance requirements), technical design (for auth/authz patterns and security-related architecture decisions), and system context (for deployment environment).

4. **Check Input Validation**: Examine all entry points — function parameters from external input, API endpoints, form handlers, file uploads, URL parameters, headers. Check for:
   - Missing validation on user-controlled input
   - SQL injection vectors (string concatenation in queries)
   - NoSQL injection vectors
   - Command injection (shell commands with user input)
   - Template injection
   - XSS vectors (unescaped output of user input)
   - Path traversal (user input in file paths)

5. **Check Authentication & Authorization**: Verify auth patterns:
   - Are authentication checks present on protected endpoints?
   - Are authorization checks granular (not just "is logged in" but "has permission")?
   - Are sessions handled securely (expiration, invalidation, secure flags)?
   - Are passwords hashed with appropriate algorithms (bcrypt, argon2, scrypt)?
   - Are tokens validated properly (signature, expiration, audience)?

6. **Check Data Protection**: Look for sensitive data exposure:
   - PII in logs, error messages, or API responses
   - Credentials or secrets in source code, configuration files, or comments
   - Sensitive data in URLs (query parameters are logged by servers and proxies)
   - Missing encryption for sensitive data at rest or in transit
   - Overly broad data exposure in API responses (returning full objects when subsets suffice)

7. **Check Configuration Security**:
   - Hardcoded secrets, API keys, connection strings
   - Insecure defaults (debug mode enabled, verbose errors, open CORS)
   - Missing security headers (CSP, X-Frame-Options, HSTS)
   - Overly permissive file/directory permissions
   - Default credentials or accounts

8. **Check Dependencies**: Where tooling is available, check for known vulnerable dependencies. Note the tool used and findings.

9. **Check Cryptography**: If the code uses cryptographic operations:
   - Are algorithms current and appropriate (not MD5, SHA1 for security purposes)?
   - Is key management handled properly (not hardcoded)?
   - Are random numbers generated with cryptographically secure functions?

10. **Check Logging & Monitoring**: Verify that security-relevant events are logged (authentication attempts, authorization failures, input validation rejections) and that sensitive data is excluded from logs.

11. **Cross-Reference Compliance**: For each CC-XXX constraint from the constraints analysis, verify the code meets the requirement. Flag violations at Critical severity.

12. **Draft Findings and Write the Report**: Create findings with severity, OWASP reference, category, attack scenario (for Medium+), and specific remediation guidance. Write the full report to `.gener8v/changes/<change-slug>/reviews/` now, every finding `Open`, verdict provisional. *(End of the findings phase — when run as the `security-reviewer` agent, stop here and return the report path, verdict and counts.)*

13. **Present to User**: Share findings starting with Critical, then High, then Medium, then Low, then Informational. For Critical and High findings, emphasize the attack scenario and impact. Work through interactive resolution — the user may fix, defer, or accept risk — updating each finding in the report as it is decided. A finding deferred to a named ticket (`Deferred → TICKET-NNN`) also gets a Known Hazard appended to that ticket in its breakdown file, so the implementer sees it (`CONVENTIONS.md` §2). When a risk is accepted, write the `**Risk accepted by:** Security — <name>, YYYY-MM-DD` line and the rationale on the finding at that moment, and mark the Resolution Log row `Risk Accepted: Yes`.

14. **Apply Approved Remediations**: Update code files for findings the user approves, re-run the delivery record's Verification Run, and append each change to the delivery record's `## Post-Review Amendments`.

15. **Write the Verdict**: Set the final `**Result:**` and `**Accepted Risks:**` last.

## Example

A worked example — the findings-phase report for Search & Retrieval TICKET-002 (semantic index) in change `support-search`, with one Medium and one Informational finding, followed by the resolution excerpt that records an accepted risk — is in `references/example.md`. Read it before producing your first security review report.

---

## Integration with Other Skills

**Upstream:**
- **Delivery Skill**: Provides the delivery record (`changes/<change-slug>/delivery/…`, with the file list) and the delivered code to review
- **Constraints Skill**: Provides compliance constraints (CC-XXX) for mandatory security requirements
- **Technical Design Skill**: Provides security-related architecture decisions (auth patterns, data protection approach)

**Downstream:**
- **Audit Skill**: Can include security review findings and risk acceptances in cross-stage assessments
- **OWASP Top 10 / OWASP LLM Top 10 / Architecture Review**: read every `changes/*/reviews/*-security-review.md` (and legacy `reviews/*-security-review.md`) and map its findings (qualified as `<change-slug>/<report-slug>/SEC-XXX`) onto their taxonomies
- **Delivery Skill** (later tickets): reads this report from `changes/<change-slug>/reviews/` for deferred findings and accepted risks on files it will touch
- **Orchestrate**: reads the `**Result:**` line; `Changes Required` holds the ticket at `changes_required`

**Parallel:**
- **Code Review Skill**: Reviews the same code for pipeline traceability — different concern, can run in parallel
- **Quality Review Skill**: Reviews the same code for engineering quality — different concern, can run in parallel

## Revisions

- Security review reports capture a point-in-time assessment — they do not auto-update when code changes or new CVEs are published
- After code modifications from other review findings, consider re-running the security review if the changes affect security-relevant code
- If new compliance constraints (CC-XXX) are added, re-run the security review to verify the code meets the updated requirements
- Dependency vulnerability checks become stale quickly — re-run periodically or when dependencies are updated

## Notes

- This skill reviews code, not architecture — for design-level security analysis (threat modeling, trust boundaries), use the Constraints skill with a security focus or create a dedicated threat model
- The findings phase runs after Delivery, in parallel with Code Review and Quality Review (as the reviewer agents); resolution phases run one at a time
- The OWASP Top 10:2025 is the primary reference framework (the same edition the OWASP Top 10 Review skill assesses against), but findings are not limited to it
- Verdict vocabulary is shared by all three reviews: Approved / Approved with Notes / Changes Required; accepted risks are counted separately
- Risk acceptance is a first-class outcome — the report explicitly records what risks were accepted, why, and who accepted them (`**Risk accepted by:** Security — …`)
- For dependency vulnerability checks, note which tool was used and when — results are time-sensitive
- If no security-relevant code is found (pure data transformation, formatting, etc.), the review can be brief with an "Approved" verdict and a note explaining the limited attack surface
- This skill can be used without a delivery record by pointing directly at code files — it degrades gracefully
