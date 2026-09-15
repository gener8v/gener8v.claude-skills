---
description: "Indirect prompt injection is the LLM Top 10, not the web security review."
tags: [routing]
max_turns: 4
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
---
The support chat in src/chat/rag.py puts retrieved help articles straight into the prompt. Could someone smuggle instructions in through those articles?
