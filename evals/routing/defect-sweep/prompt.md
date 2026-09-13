---
description: "Siblings of a found defect across a subsystem is a Defect Sweep."
tags: [routing]
max_turns: 4
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
---
We just found a fail-open error path in the search module. There are probably more like it nearby. Hunt for its siblings.
