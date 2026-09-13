# gener8v evals

The `claude plugin eval` suite for the gener8v plugin. It answers two questions a skill file cannot answer about itself: does a natural request reach the right skill, and does the skill then do the right thing.

## Layout

- **`routing/<skill>/`** — one natural request per skill, phrased the way a user would say it rather than naming the skill. Each case has two graders: the skill fired, and its nearest sibling did not (`code-review` for a quality question, `security-review` for an OWASP posture question, `quality-review` for a trend). Nine skills are review-shaped, so the second grader is the one that catches a description drifting into its neighbour's territory. `routing/unrelated-question/` checks that a general programming question loads no pipeline skill at all.
- **`functional/<case>/`** — outcome checks:
  - `orchestrate-next-step` — Orchestrate reads the injected state and puts TICKET-001's missing reviews first. Its `context-injected` grader checks the state script's output reached the skill; it can only pass with `--allow-tools Bash`, because an eval grants tools from the command line and a skill's `allowed-tools` cannot widen that.
  - `rot-watch-first-run` — the first watch writes `rot/baseline.md` with its `**Deliveries:**` line and reports nothing.
  - `state-file-hand-edit` — asked insistently to hand-edit `pipeline-state.yaml`, the file stays untouched and the user hears why. Current models usually decline on their own, so this checks the outcome; the hook that refuses the edit when a model does try is covered deterministically by `scripts/test-hooks.sh`.
- **`fixture/project/`** — the project every scaffolded case starts from, assembled from the skills' own worked examples: the Support Documentation Search PRD and the `support-search` change, an approved Search & Retrieval specification, four tickets, TICKET-001 delivered and unreviewed, TICKET-002 ready. The source is small and deliberately flawed so the review and assessment prompts have something real to point at: SQL built from user input and MD5 password hashes in `src/auth/login.py`, retrieved articles concatenated into a prompt in `src/chat/rag.py`, a fail-open `except` in `src/search/query_input.py`. Each case's `scaffold.sh` copies it into the empty workspace and commits it.

## Running

Every run is a real model call on your account. Cases run three times per arm by default, with the plugin and without it.

```bash
# the whole suite, as CI would run it
claude plugin eval . --scaffold --allow-tools Bash Write Edit \
  --model claude-sonnet-5 --judge-model claude-haiku-4-5 --no-publish --max-cost-usd 25

# routing only, one run each, no baseline arm — the quick check after editing a description
claude plugin eval . --scaffold --tag routing --runs 1 --ablation none

# one case while iterating on it
claude plugin eval . --scaffold --case rot-watch-first-run --runs 1 --ablation none --allow-tools Bash Write Edit
```

- `--scaffold` is required: without it the fixture is not copied and every scaffolded case runs in an empty directory.
- Claude Code refuses to grant Bash to an eval on a machine it cannot sandbox reliably — for example when the Docker credential store (`~/.docker`) contains a symbolic link. There, run the functional cases with `--allow-tools Write Edit`, and expect `context-injected` to fail.
- The functional cases need `--allow-tools`. Orchestrate's injected context runs through Bash, Rot Watch writes its baseline, and the hand-edit case offers Claude the tools it would use to make the edit. Granted Bash runs under Claude Code's OS sandbox.
- A routing case's `fires` grader is a plugin-fired indicator in a two-arm run: it cannot pass without the plugin, so Claude Code reports it without scoring it. The `not-…` grader is scored in both arms.
- The runs cap turns deliberately low for routing (the choice is made on the first turn), so a routing run ending at its turn limit is expected, not a failure.

## When to run it

- After changing any skill's `description` — run `--tag routing`, and read the `not-…` graders as closely as the `fires` ones.
- After changing a hook, `pipeline-context.sh`, or a template in `assets/` — run `--tag functional`.
- Before a release — the whole suite with pinned models, so a model rollout is not mistaken for a plugin regression.

Results land in `evals/results/<timestamp>/` (ignored by git): `aggregate-result.json` for scripts, `report.html` for people.
