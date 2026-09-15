---
type: regex
pattern: '^stage: reviewed'
flags: m
match: not_contains
target: { source: file, path: .gener8v/pipeline-state.yaml }
---
