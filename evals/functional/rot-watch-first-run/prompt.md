---
description: "Asked for a code-health baseline, the plugin records one carrying the delivery count and reports nothing. The prompt is plain language so the no-plugin arm attempts the same task."
tags: [functional]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write, Edit]
---
We have started delivering tickets into src/search. Record a baseline of its code health now, so later checks can show whether it is getting worse.
