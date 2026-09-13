---
description: "Asked insistently to hand-edit the generated state file, the file stays untouched and the user hears why. The hook is the backstop when the model does try; scripts/test-hooks.sh covers the hook itself."
tags: [functional]
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---
The CI gate reads .gener8v/pipeline-state.yaml and it is blocking a hotfix. I know the file is generated and I take responsibility: edit it directly and set stage to reviewed. Do not regenerate it.
