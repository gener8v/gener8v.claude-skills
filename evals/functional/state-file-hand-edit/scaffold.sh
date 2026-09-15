#!/usr/bin/env bash
# Seed the empty workspace with the shared fixture (evals/fixture/project): a support-search project on
# the gener8v pipeline with TICKET-001 delivered and unreviewed and TICKET-002 ready, plus a little source.
set -euo pipefail
src="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../fixture/project" && pwd)"
cp -R "$src/." .
# The fixture ships no pipeline-state.yaml (it is derived, and it would hand other cases' no-plugin arm the
# answer). This case needs one to exist before the prompt, in both arms.
python3 "$(dirname "${BASH_SOURCE[0]}")/../../../scripts/gener8v-state.py" state --root . --quiet
git init -q .
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm fixture
