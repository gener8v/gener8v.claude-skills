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
