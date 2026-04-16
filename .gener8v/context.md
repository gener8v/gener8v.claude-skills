# System Context

This document captures known and inferred context for the `gener8v.claude-skills.containerized` project. Items marked **Assumed** should be confirmed; items marked **Open** are unresolved and tracked in the PRD.

## Organizational Context

- **Publisher:** gener8v
- **License:** MIT (consistent with the existing `gener8v.claude-skills` plugin)
- **Repository host:** GitHub, public repo
- **Target repo name:** `gener8v.claude-skills.containerized`
- **Relationship to existing work:** Sibling project to `gener8v.claude-skills`. Reuses the pipeline philosophy and skill definitions but reorganizes them into a layered architecture and adds containerized runtime, agent personas, credential management, and observability.

## Reference Implementations

The project draws from two existing systems:

- **archie** (`simon-downes/archie`, v0.6.0) — source of the layered skill taxonomy concept, Docker sandbox pattern, credential/config separation, agent persona with tiered access, and project-level provider dispatch. Written in Python, packaged with Hatchling, CLI built with Click, YAML for config.
- **claude-session-tracker** (`ej31/claude-session-tracker`, v2.9.6) — source of the hook-based session lifecycle tracking, hash-chained audit trail, idle detection, and resume handling patterns. Python hooks, uses `gh` CLI for GitHub operations.

This project is not a fork of either; it adopts patterns while rebuilding around gener8v's pipeline philosophy and traceability model.

## Target Agent Runtime

- **Primary target:** Claude Code (CLI tool from Anthropic)
- **Skill format:** Markdown `SKILL.md` files with YAML frontmatter, following Claude Code's skill conventions
- **Hook events to integrate with:** `SessionStart`, `UserPromptSubmit`, `PostToolUse`, `Stop`, `SessionEnd`
- **Open:** Whether to also support Kiro CLI (as archie does), or remain Claude Code-specific

## Development Environment

- **Host OS:** macOS (Darwin) — primary development platform
- **Shell:** zsh
- **Assumed support targets:** macOS + Linux (standard for Docker-based toolkits). Windows support is not assumed.
- **Container runtime:** Docker Desktop / OrbStack on macOS
- **Open:** Whether to target Podman and other OCI-compatible runtimes as first-class

## Technology Preferences

These are **assumed** based on archie's precedent and ecosystem fit; confirm before committing:

- **CLI language:** Python (assumed) — matches archie, aligns with hooks being Python, `uv` available for dependency management
- **CLI framework:** Click (assumed) — archie's choice, mature, familiar
- **Packaging:** Hatchling + `pyproject.toml` (assumed) — modern Python packaging
- **Config format:** YAML (assumed) — matches archie, human-editable, widely supported
- **Output formatting:** Rich (assumed) — for banners, tables, colored output in CLI

**Open:** Whether the CLI should be Node.js instead, given Claude Code itself is Node-based and users may already have that ecosystem.

## Existing Pipeline Skills (to be migrated)

Currently in `gener8v.claude-skills/skills/`:

- setup, planning, brownfield, specification, constraints, dependencies, technical-design, ticket-breakdown, delivery, code-review, quality-review, security-review, audit, orchestrate (14 skills)

All are single-file SKILL.md markdown documents with no YAML frontmatter currently. The containerized version will add frontmatter and reorganize by layer.

## Artifact Conventions (inherited)

- Pipeline artifacts live in `.gener8v/` at the project root
- Pipeline state is machine-readable YAML (`.gener8v/pipeline-state.yaml`)
- Requirement IDs use prefixed format (e.g., `SR-REQ-001` for Search & Retrieval)
- @spec annotations embedded in code comments link back to requirement IDs
- Capability area slugs use hyphenated lowercase (`search-and-retrieval`)

## External Integrations (anticipated)

- **Git hosting:** GitHub (primary); open whether to support GitLab/Bitbucket like archie does
- **Issue tracking:** GitHub Issues + optionally Linear (following archie's provider dispatch pattern)
- **Notifications:** Slack webhooks (optional, per archie)
- **Session storage:** GitHub Issues in a private notes repo (following session-tracker pattern), with local pipeline-state.yaml integration
- **Auth providers:** Static tokens (GitHub, Linear, Slack), OAuth2 + PKCE for providers that support it (Notion as archie does)

## Known Constraints

- The toolkit must be installable as a self-contained package; no external service dependencies required for core pipeline operation
- Credentials must never be committed to the repository or included in the Docker image
- The sandbox container user must match the host user's UID to avoid file permission issues on mounted volumes
- All destructive operations must require explicit user approval, even for the most privileged agent

## Team and Scale

- **Team size:** Single developer (gener8v), solo project
- **Users:** Individual developers using the toolkit on their own machines
- **Not targeted:** Multi-tenant, multi-user collaboration, team-shared credential vaults (listed as future considerations in PRD)

## Out-of-Band Information Needed

Before or during specification, the following should be confirmed:

- CLI language choice (Python vs Node.js)
- Container runtime support scope (Docker-only vs OCI-compatible)
- Agent runtime support scope (Claude Code only vs multi-agent like archie)
- Credential scoping model (per-agent in agent definition vs separate access policy file)
- Session record destination (local files vs GitHub Issues vs both)
- Minimum viable sandbox toolset (what goes in the Dockerfile at v0.1.0)
