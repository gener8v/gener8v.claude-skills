# TICKET-001: [Concise action-oriented title]

**Change:** [change-slug]
**Capability Area:** [Area name] ([area-slug])
**Specification:** specifications/[area-slug].md

**Summary:** [1-2 sentences describing what this ticket accomplishes]
**Priority:** [Must / Should / Could — from the change brief's Priority Cut]
**Value:** [One sentence — what the user or operator gets when this lands]

**Requirements Covered:**
- [XX]-REQ-001: [Brief description]
- [XX]-REQ-002: [Brief description]
- [XX]-NFR-001: [target — verified by … — NFR IDs are listed exactly like REQ IDs]

**Prior Art:** [What to read/understand before starting. For tickets with
no dependencies, point to relevant pipeline documents. For tickets that
depend on other tickets, specify the files and directories produced by
those tickets that this work builds on.]
- Read: [root-relative file path — source file, config, module, or pipeline artifact] — [what to look for in that file and why it matters]

**Acceptance Criteria:**
- [ ] [Observable, verifiable condition that must be true when complete]
- [ ] [Another condition]
- [ ] [For each NFR carried: the measurable target and its verification method —
      e.g., "p95 latency ≤ 800 ms at 50 concurrent users, verified by the k6 load test"]

**Output:**
- [File or directory this ticket produces or modifies, root-relative to the
  workspace (e.g., `api/src/search/query.ts`), with enough detail that
  downstream tickets can locate the work]
- [The test file(s) that prove the acceptance criteria — every ticket with
  testable criteria lists at least one; name which criterion each test covers]

**Constraints:** [Qualified constraint IDs and brief description, or "None identified"]

**Known Hazards:** [Front-loaded traps the implementer must know *before* starting — or "None identified". This is where decision supersessions, cross-document conflicts, and schema/pattern gotchas live, so they are seen first, not discovered mid-build. Each hazard names what to do about it.]
- [e.g., "AD-004 supersedes the spec's wording of SR-REQ-006 — rank on the stored score, NOT on recomputed similarity; the spec text is stale"]
- [e.g., "Spec conflict: SR-REQ-009 and TC-002 disagree on whether a source reference may be a URL — implement per TC-002, flag the conflict in the delivery record's Decisions, do NOT silently reconcile"]
- [e.g., "`status` has no DB CHECK — enforce the enum at the application layer at every write path"]

**Depends On:** [Other ticket IDs this is blocked by, or "None"]
**Blocks:** [Other ticket IDs this unblocks, or "None"]

**Size:** [Small / Medium / Large]

**Notes:** [Implementation hints, context, or warnings — optional]
