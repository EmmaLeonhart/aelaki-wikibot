#!/usr/bin/env bash
# ============================================================================
# commit_state.sh — commit and push mutated state files
# ============================================================================
#
# Called from .github/workflows/word-pages.yml after every pipeline step that
# writes local files. Stages the known state patterns, commits with the
# provided message, rebases against the remote, and pushes.
#
# Usage:
#   wiki-scripts/commit_state.sh "chore(state): post-<step> [skip ci]"
#
# Idempotent: exits 0 with no action when there are no staged changes.
# ============================================================================

set -euo pipefail

MSG="${1:-chore(state): update bot state [skip ci]}"
BRANCH="${GITHUB_REF_NAME:-master}"

# Add each pattern separately — some globs (e.g. *.last) may not exist yet.
git add -A -- "*.state" 2>/dev/null || true
git add -A -- "*.last" 2>/dev/null || true
git add -A -- "aelaki/lexicon.json" "wiki-scripts/version_history.txt" "grammar/"
git add -A -- "images/imagewikitext/" 2>/dev/null || true

if git diff --cached --quiet; then
  echo "  (no state changes to commit)"
  exit 0
fi

git commit -m "$MSG"

# Stash any unstaged changes so git pull --rebase doesn't fail.
stashed=false
if ! git diff --quiet; then
  git stash push -q
  stashed=true
fi

git pull --rebase -X theirs origin "$BRANCH"
git push origin "HEAD:${BRANCH}"

if $stashed; then
  git stash pop -q
fi

echo "  State committed and pushed."
