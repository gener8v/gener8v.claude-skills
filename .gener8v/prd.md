# Containerized AI Agent Development Toolkit

## Problem Context

AI coding agents (Claude Code, Kiro, etc.) run with full host access by default — no isolation, no credential scoping, no observability into what they're doing or why. Existing approaches like archie solve container sandboxing but treat the development process as a simple plan→implement→review chain. Meanwhile, session tracking tools like claude-session-tracker add observability but operate in isolation from the development workflow. There is no system that combines sandboxed execution, structured development pipeline skills, and operational observability into a coherent, traceable whole.

## Goals

- The system should provide isolated, reproducible execution environments for AI coding agents with scoped access controls
- The system should organize development skills into layers that reflect the distinct natures of work (defining standards, orchestrating flow, producing artifacts, verifying quality)
- The system should manage credentials securely with per-agent scoping — agents only see the secrets their role requires
- The system should maintain an auditable trail across the full stack: from requirements through conversations through code
- The system should be installable as a self-contained toolkit that bootstraps its own configuration, sandbox, and skill system

## Functional Capabilities

### Skill Layer System

- The system should organize skills into distinct layers based on their nature: defining standards, orchestrating pipeline flow, producing development artifacts, and verifying quality
- The system should enforce naming conventions that make a skill's layer immediately apparent from its directory name
- The system should support skill discovery so that agents can locate and invoke skills by layer or by name
- The system should allow skills within one layer to reference skills in other layers (e.g., review skills consuming standard definitions)
- The system should ship with the gener8v development pipeline skills reorganized into the layer taxonomy
- The system should define a skill authoring format (frontmatter + markdown body) with layer-specific guidance for each layer type

### Containerized Sandbox

- The system should define a Docker image containing the tools needed for AI-assisted development (language runtimes, CLI tools, linters, formatters)
- The system should mount project files into the container so agents work on the real codebase
- The system should align container user identity with the host user to avoid file permission mismatches
- The system should support mounting configuration, credentials, and skill definitions into the container at expected paths
- The system should prevent running duplicate container sessions for the same project and tool combination
- The system should support both interactive (TTY) and non-interactive execution modes

### Agent Persona Management

- The system should define agent personas as configuration files specifying model, system prompt, available tools, and trusted subagents
- The system should support tiered access controls — an orchestrating agent has broader access than a reviewing agent, which has broader access than a research agent
- The system should map agent roles to pipeline concerns: orchestration, artifact production, verification, and read-only investigation
- The system should allow the orchestrating agent to delegate work to scoped subagents
- The system should restrict destructive operations (file deletion, force push, package removal) to explicit human approval even for the most privileged agent

### Credential and Configuration Management

- The system should store credentials separately from configuration, with restricted file permissions on the credentials file
- The system should map credentials to environment variables and inject them into containers at launch
- The system should scope credential injection per agent role — a read-only research agent should not receive write-capable tokens
- The system should support static credential entry (manual set/import) and OAuth flows (browser-based PKCE) for providers that support it
- The system should auto-refresh expired OAuth tokens before container launch
- The system should resolve per-project configuration (source provider, issue tracker, notification channels) from the git remote of the current workspace
- The system should silently skip missing optional credentials rather than failing

### Session Observability

- The system should track session lifecycle through defined states (registered, responding, waiting, closed) using Claude Code hook events
- The system should persist conversation prompts and responses as an auditable record
- The system should chain session records with cryptographic hashes to enable tamper detection
- The system should detect idle sessions and auto-close them after a configurable timeout
- The system should handle session resume without creating duplicate tracking records
- The system should feed session state back into the pipeline state so that the orchestration layer knows what work is in progress

### CLI Interface

- The system should provide a single command-line entry point for all operations (install, build, auth, run, status)
- The system should bootstrap configuration files with sensible defaults on first install
- The system should deploy skill and agent definitions from the package to the user's configuration directory
- The system should build the sandbox Docker image from the included Dockerfile
- The system should support dynamic tool registration — new agent tools defined in configuration become CLI subcommands without code changes
- The system should guard all commands behind an install check to prevent running in an unconfigured state

### Pipeline State and Traceability

- The system should maintain a machine-readable pipeline state file tracking which skills have run, what they produced, and what is stale
- The system should propagate staleness — when an upstream artifact changes, downstream artifacts are marked stale
- The system should support @spec annotations linking code back to requirement IDs defined in specifications
- The system should connect session audit trails to pipeline state so that conversations are traceable to the pipeline phase they occurred in
- The system should make the full traceability chain queryable: requirement → specification → ticket → code (@spec) → review → conversation history

## User Scenarios

**Scenario: First-Time Setup**
A developer installs the toolkit, runs the install command, and is guided through initial configuration: which git provider they use, whether they have a Linear account for issue tracking, and their preferred notification channel. The system creates configuration files, builds the sandbox image, and deploys skills and agent definitions. The developer launches their first session and the observability hooks begin tracking automatically.

**Scenario: Running the Full Pipeline in a Sandbox**
A developer describes a feature they want built. The orchestrating agent, running inside an isolated container, invokes the planning skill to produce a PRD, then works through specification, design, and ticket breakdown — each skill reading the artifacts produced by the previous one. When delivery begins, the agent writes code with @spec annotations. The review skills verify the code against the standards layer. Throughout, every conversation turn is logged with hash-chain integrity, and the pipeline state file reflects exactly what has been completed and what is stale.

**Scenario: Scoped Agent Delegation**
During the review phase, the orchestrating agent delegates code review to a reviewer subagent that has read-only file access and no credentials for pushing code. The reviewer evaluates the code against standard-layer definitions and produces a review artifact. The orchestrating agent collects review results and updates pipeline state. At no point did the reviewer have access to write tokens or destructive shell commands.

**Scenario: Credential Rotation**
A developer's GitHub token expires. They run the auth command to set a new token. On the next container launch, the system injects the fresh token as an environment variable. The developer's OAuth-based Notion token is refreshed automatically without manual intervention. The read-only research agent receives only the GitHub token (read scope); the delivery agent receives the full write-capable token.

## Out of Scope

- This work does not include building a custom AI model or fine-tuning — it orchestrates existing models (Claude, etc.)
- This work does not include a web UI or dashboard — the interface is CLI and file-based
- This work does not include multi-user collaboration features — this is a single-developer toolkit
- This work does not include hosting or cloud deployment of the sandbox — containers run locally
- This work does not include porting all of archie's language-specific tooling (PHP, Terraform) — the sandbox is tailored to gener8v's pipeline needs
- Future consideration: remote/cloud sandbox execution
- Future consideration: team-shared configuration and credential vaults
- Future consideration: plugin marketplace for community-contributed skills

## Open Questions

- [ ] Which container runtime to target — Docker only, or also Podman/OrbStack?
- [ ] Should the CLI be Python (like archie) or Node.js (closer to Claude Code's ecosystem)?
- [ ] What agent runtime to target inside the container — Claude Code, Kiro, both, or agent-agnostic?
- [ ] Should session observability records go to GitHub Issues (like session-tracker), local files, or both?
- [ ] How should credential scoping be defined — per-agent in the agent definition file, or in a separate access policy?
- [ ] Should the system support multiple concurrent sandboxed sessions for the same project (e.g., delivery and review in parallel containers)?
- [ ] What is the minimum viable set of tools in the sandbox Docker image?
- [ ] Should pipeline-state.yaml live inside the container (mounted) or be managed by the host CLI?
- [ ] How should the system handle skill updates — re-run install, or hot-reload from a mounted directory?
