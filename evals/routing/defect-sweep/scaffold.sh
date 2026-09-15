#!/usr/bin/env bash
# Seed the empty workspace with the shared fixture (evals/fixture/project): a support-search project on
# the gener8v pipeline with TICKET-001 delivered and unreviewed and TICKET-002 ready, plus a little source.
set -euo pipefail
src="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../fixture/project" && pwd)"
cp -R "$src/." .
git init -q .
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm fixture
