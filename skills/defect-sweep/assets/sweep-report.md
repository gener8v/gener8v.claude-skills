# [Subsystem]: Defect Sweep

## Scope

What was swept, and what was deliberately not. A sweep that does not say where it stopped
reads as a clean bill of health for code nobody opened.

## Findings

### DS-001: [Consequence, as a sentence — not a category]

**What breaks.** One or two sentences, consequence first.

**Mechanism.** The code path, with file:line. Why it happens, not merely that it does.

**Circumstance.** What has to be true for this to fire. A defect that needs an impossible
state is a note; one that needs a Friday afternoon is a finding.

**Proof.** How to see it: a failing test, a query, a reproduction. If a fix is proposed,
state what breaks when the fix is removed.

**Class.** One of the classes in `references/defect-classes.md`.

### DS-002: ...

## Swept and clean

The classes checked that turned up nothing, named explicitly. Silence is ambiguous —
a reader cannot tell "checked and fine" from "never looked".

## Verdict

What should be fixed now, what can wait, and what needs a decision rather than a fix.
Findings to fix now become tickets (see Integration); name them here as `DS-XXX → ticket`,
and name the change they go into.

## Since the last sweep (if any)

[Earlier findings fixed / still open / new this time.]
