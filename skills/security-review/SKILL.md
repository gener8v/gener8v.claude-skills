# Security Review Skill

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
- Delivery record: `.gener8v/delivery/[capability-area-slug]-[ticket-id]-delivery.md` (for the file list)
- Actual code files listed in the delivery record's "Files Produced" section
- Constraints: `.gener8v/constraints/[capability-area-slug].md` (if available — for compliance constraints CC-XXX)
- Technical Design: `.gener8v/technical-design/[capability-area-slug].md` or `.gener8v/technical-design/system-design.md` (if available — for auth/authz design decisions)
- System Context: `.gener8v/context.md` (if available — for deployment environment and infrastructure)

**Expects:** Code files to exist. Does NOT require all pipeline artifacts — the skill adapts its coverage based on what is available.

**If input is missing or malformed:**
- If no delivery record exists, the user can point directly to code files to review
- If constraints are missing, compliance verification is skipped — note "Compliance constraints not available" in the report
- If technical design is missing, architecture-level security checks are limited — note in the report
- If code files do not exist, stop and flag the issue

## Output

**Produces:** A security review report with findings and interactive resolutions
**Write to:** `.gener8v/reviews/[capability-area-slug]-[ticket-id]-security-review.md`
**Creates directory:** `.gener8v/reviews/` if it does not exist
**Naming convention:** Matches the delivery record naming with `-security-review` suffix

After interactive resolution, the skill may update delivered code files if the user approves remediations. The review report captures all findings, their resolutions, and any accepted risks.

## Output Format

Produce a markdown document with the following structure:

```markdown
# [Ticket ID]: [Ticket Title] — Security Review

## Summary

[2-3 sentences: what was reviewed, overall security posture, finding count by severity.]

**Files Reviewed:**
- [file path]
- [file path]

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
**OWASP Reference:** [OWASP Top 10 category, e.g., A03:2021 Injection — or "N/A" if not directly mapped]
**Location:** [file:line or function]
**Description:** [What the vulnerability or concern is]
**Attack Scenario:** [How this could be exploited — required for Medium+ severity]
**Impact:** [What happens if exploited — data loss, unauthorized access, etc.]
**Recommendation:** [Specific remediation with code example if helpful]
**Compliance Impact:** [CC-XXX constraint IDs affected, if any, or "None"]
**Status:** [Open / Resolved / Accepted Risk / Deferred]
**Resolution:** [What was done, if resolved — filled in during interactive session]

---

### SEC-002: ...

## Resolution Log

| Finding | Decision | Action Taken | Risk Accepted | File Updated |
|---------|----------|-------------|---------------|--------------|
| SEC-001 | [Decision] | [What was changed] | [Yes/No] | [File path] |
| SEC-002 | Accepted Risk | — | Yes | — |

## Verdict

**Result:** [Approved / Approved with Accepted Risk / Remediation Required]
**Unresolved Critical/High:** [Count — must be 0 for Approved verdict]
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
Not every security finding must be fixed. Some are accepted risks: the likelihood is low, the mitigation cost is high, or compensating controls exist. The review records risk acceptance decisions explicitly with rationale. Critical findings require strong justification for acceptance — document why the risk is tolerable and what compensating controls exist.

### Compliance Constraints Are Non-Negotiable
If the constraints analysis identifies compliance requirements (CC-XXX), violations of those constraints are automatically elevated to Critical severity regardless of exploitability. Compliance is not risk-based — it is requirement-based. A CC-XXX violation means the system does not meet its stated compliance obligations.

### Secrets in Code Are Always Critical
Hardcoded credentials, API keys, tokens, private keys, or connection strings in source code are Critical findings. No exceptions for "dev environments," "temporary values," or "will be changed later." If it is in the code and the code is committed, it is a secret exposure. The remediation is always: remove the secret, rotate it, use environment variables or a secrets manager.

### Dependencies Are Attack Surface
Third-party dependencies with known CVEs are findings. The review should check for outdated dependencies with known vulnerabilities where tooling makes this feasible (e.g., `npm audit`, `pip-audit`, `cargo audit`). The severity matches the CVE severity.

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

12. **Draft Findings**: Create findings with severity, OWASP reference, category, attack scenario (for Medium+), and specific remediation guidance.

13. **Present to User**: Share findings starting with Critical, then High, then Medium, then Low, then Informational. For Critical and High findings, emphasize the attack scenario and impact. Work through interactive resolution — the user may fix, defer, or accept risk.

14. **Apply Approved Remediations**: Update code files for findings the user approves.

15. **Write Report**: Save to `.gener8v/reviews/`.

## Example

### Input

Reviewing the delivery of TICKET-002 from Search & Retrieval: "Configure search index for semantic matching"

Delivered code at `src/search/index.py` and `src/search/index_client.py`.

### Output (abbreviated)

````markdown
# TICKET-002: Configure search index for semantic matching — Security Review

## Summary

Reviewed two files delivered for TICKET-002. The code handles search index configuration and querying. One Medium finding related to the database connection string. One Informational finding regarding query logging. Overall security posture is adequate for the current scope.

**Files Reviewed:**
- `src/search/index.py`
- `src/search/index_client.py`

**Findings:** 2
**Critical:** 0 | **High:** 0 | **Medium:** 1 | **Low:** 0 | **Informational:** 1

## Security Assessment

### Input Validation

**Status:** Adequate
**Notes:** Query text passed to the search function is parameterized in the database query — no SQL injection vector. Vector embedding is generated via API call with the query string; the API client handles encoding.

### Authentication & Authorization

**Status:** Not Applicable
**Notes:** This module does not handle user authentication or authorization. Access control is expected at a higher layer.

### Data Protection

**Status:** Gaps Found
**Notes:** The database connection string is constructed from environment variables, but the fallback default includes a placeholder password (see SEC-001).

### Configuration Security

**Status:** Gaps Found
**Notes:** Fallback connection string in code (see SEC-001).

## Findings

### SEC-001: Database connection string with fallback default

**Severity:** Medium
**Category:** Misconfiguration
**OWASP Reference:** A05:2021 Security Misconfiguration
**Location:** `src/search/index.py:12`
**Description:** The database connection string is read from `DATABASE_URL` environment variable with a fallback default of `postgresql://search:search_dev@localhost:5432/search_db`. While the default points to localhost, committing default credentials normalizes the pattern of credentials in source code.
**Attack Scenario:** A developer or CI system runs the code without setting the environment variable. The code connects with the default credentials. If the default database exists and is accessible, the code operates with unintended credentials. In a deployment misconfiguration, the default could leak into production.
**Impact:** Unauthorized database access in misconfigured environments. Credential exposure in source code.
**Recommendation:** Remove the fallback default. Raise an error if `DATABASE_URL` is not set. Fail explicitly rather than falling back to hardcoded credentials.
**Compliance Impact:** None
**Status:** Open

---

### SEC-002: Search queries logged at DEBUG level

**Severity:** Informational
**Category:** Logging
**OWASP Reference:** N/A
**Location:** `src/search/index_client.py:28`
**Description:** User search queries are logged at DEBUG level. Search queries may contain sensitive information depending on the domain (e.g., employee names, case numbers, internal project details).
**Attack Scenario:** N/A (Informational)
**Impact:** Potential exposure of sensitive query content in log files if DEBUG logging is enabled in production.
**Recommendation:** Ensure DEBUG logging is disabled in production. Consider whether search queries should be logged at all, or logged with redaction.
**Compliance Impact:** None
**Status:** Open

## Verdict

**Result:** Approved with Accepted Risk
**Unresolved Critical/High:** 0
**Accepted Risks:** 0
**Notes:** SEC-001 should be addressed before production deployment. SEC-002 is informational and depends on logging configuration in production.
````

---

## Integration with Other Skills

**Upstream:**
- **Delivery Skill**: Provides the delivery record (file list) and the delivered code to review
- **Constraints Skill**: Provides compliance constraints (CC-XXX) for mandatory security requirements
- **Technical Design Skill**: Provides security-related architecture decisions (auth patterns, data protection approach)

**Downstream:**
- **Audit Skill**: Can include security review findings and risk acceptances in cross-stage assessments
- Security review reports are reference documents — no other skill consumes them as direct input

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
- Run this skill after Delivery, in parallel with Code Review and Quality Review
- The OWASP Top 10 is the primary reference framework, but findings are not limited to it
- Risk acceptance is a first-class outcome — the report explicitly records what risks were accepted and why
- For dependency vulnerability checks, note which tool was used and when — results are time-sensitive
- If no security-relevant code is found (pure data transformation, formatting, etc.), the review can be brief with an "Approved" verdict and a note explaining the limited attack surface
- This skill can be used without a delivery record by pointing directly at code files — it degrades gracefully
