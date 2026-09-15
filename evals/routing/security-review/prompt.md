---
description: "A security check of what one delivery shipped is a Security Review, not a whole-codebase OWASP assessment."
tags: [routing]
max_turns: 4
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
---
TICKET-001 in search-and-retrieval was just delivered. Before we merge, check what it shipped for security problems: injection, input handling, data exposure.
