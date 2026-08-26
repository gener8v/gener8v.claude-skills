# Defect Sweep — defect classes

These are the sweeps. Each is a question to ask of the subsystem, not a rule to check.

## Inherited defaults

A callee applies a default the caller never chose. Query builders with a default `limit`,
clients with a default timeout, parsers with a default encoding.

*Ask:* for every function this code calls, what does it do when an argument is absent?

*Smell:* the caller reads the callee's **type signature** and stops there. Optional
parameters are where defaults hide, and a type signature does not show you the default.

## Sibling writers

One path into a resource is guarded and another is not. A DELETE handler that refuses
under a condition, next to a POST that overwrites without asking.

*Ask:* what else reads or writes this table, this file, this key?

*Smell:* a guard whose comment explains a hazard. If the hazard is real, it applies to
every writer — find them all.

## Incomplete gates

A control claims coverage it does not have. A kill switch on three of four entry points, a
permission check on the routes somebody remembered.

*Ask:* enumerate every entry point into the guarded capability, then check each one.

*Smell:* a comment stating how many places call something. Count them.

## Fail-open on the error path

An unknown or errored state is treated as permissive. A gate that has not read its
configuration yet, a role lookup that returns null on outage and null when disabled.

*Ask:* for every guard, what happens when its input cannot be read?

*Smell:* `??` or `||` supplying a default to a **security or safety** decision. Failing
open is sometimes right, but it must be a decision with a reason attached, not a fallback.

## Silent truncation

A partial answer is presented as a complete one. Pagination limits, result caps, sampling,
`top-N` — where the consumer is not told what was dropped.

*Ask:* can this return fewer things than exist? Does the caller learn that it did?

*Smell:* a bulk operation that reports successes without reporting a total.

## Stale assertions

A comment, docstring, or document asserts behaviour that is not true — or never was.

*Ask:* for each comment describing what the system does, check it against the system.

*Smell:* specific, confident claims — port numbers, counts, credential types, "X cannot
read Y". Specificity reads as authority and is checked by nothing.

## Identity confusion

Two things keyed differently are assumed to travel together. Records keyed by a natural
key while their subject is keyed by an id, so regenerating the subject rebinds the records.

*Ask:* what is this row keyed by, and does that key survive the operations applied to its
subject?

*Smell:* a delete that leaves rows behind, or a create that finds rows already there.

## Time-based inference

Elapsed time is treated as evidence of intent. "Nobody claimed this in 48 hours, so it was
abandoned" — true only if somebody was able to claim it the whole time.

*Ask:* does this clock keep running during states where the expected actor could not act?

*Smell:* a reaper, sweeper, or timeout that infers neglect from a duration.

## Unasked authorization

Data is returned without asking who is reading. Common where middleware is assumed to
have resolved identity but only resolves *authentication*.

*Ask:* for every route returning person-level data, what permission does it require, and
does the middleware actually supply the thing it is assumed to?

*Smell:* a route with no permission call, in a codebase where most routes have one.

## Over-serving the client

More data crosses the wire than is drawn. Server components passing whole objects to client
components; APIs returning a full record because the type was convenient.

*Ask:* what does the renderer actually read, and what is it handed?

*Smell:* an object built for one audience passed to a narrower one.
