# [Capability Area Name] — Backlog ([change-slug])

## Overview

[2-3 sentences summarizing the breakdown. State total ticket count,
how they cluster, and any notable sequencing from the dependency analysis.]

## Source Context

**Specification:** [Title] · **Constraints Analysis:** [Title, or "Not yet performed"] · **Dependency Map:** [Title, or "Not yet performed"] · **Technical Design:** [Title, or "Not yet performed"]
**Change brief:** changes/[change-slug]/change.md (Priority Cut applied)

## Ticket Dependency Chain

[Visual representation of ticket ordering]

```
TICKET-001 ──→ TICKET-003 ──→ TICKET-005
TICKET-002 ──→ TICKET-004 ──┘
```

## Suggested Ordering

[Recommended implementation sequence with rationale — weigh priority with
dependency and risk; a Could ticket never precedes a Must ticket unless a
dependency forces it]

1. **TICKET-001** — [Why first: foundational, unblocks others, etc.]
2. **TICKET-002** — [Can parallel with TICKET-001 because...]
3. ...

## Backlog Summary

| Ticket | Title | Priority | Size | Depends On | Status |
|--------|-------|----------|------|------------|--------|
| TICKET-001 | [Title] | Must | Small | None | Ready |
| TICKET-002 | [Title] | Must | Medium | None | Ready |
| TICKET-003 | [Title] | Should | Large | TICKET-001 | Blocked |
| ... | ... | ... | ... | ... | ... |

**Total Tickets:** [Count]
**Ready to Start:** [Count of tickets with no unresolved dependencies]

*Status here is as of this breakdown. Live status (delivered, reviewed, done) is derived from delivery records and reviews into `.gener8v/pipeline-state.yaml`; this table is not updated as tickets progress.*
