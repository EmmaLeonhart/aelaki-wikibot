#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Running word page loop from: $ROOT_DIR"
EDIT_LIMIT="${WIKI_EDIT_LIMIT:-100}"
echo "Per-phase max edits: $EDIT_LIMIT"

RUN_ID="${GITHUB_RUN_ID:-}"
REPO="${GITHUB_REPOSITORY:-Emma-Leonhart/aelaki-merged}"
EVENT_NAME="${GITHUB_EVENT_NAME:-local}"

if [ -z "${RUN_ID}" ]; then
  echo "GITHUB_RUN_ID is required to build run-tag; refusing to run."
  exit 1
fi

RUN_PATH="${REPO}/actions/runs/${RUN_ID}"
CAUSE_TEXT="pipeline run"
case "${EVENT_NAME}" in
  push)
    CAUSE_TEXT="commit triggered pipeline"
    ;;
  schedule)
    CAUSE_TEXT="time triggered pipeline"
    ;;
  workflow_dispatch)
    CAUSE_TEXT="manual triggered pipeline"
    ;;
esac

RUN_TAG="[[github:${RUN_PATH}|${CAUSE_TEXT}]]"
echo "Run tag: ${RUN_TAG}"

# Helper: update the stage line on the bot's userpage
stage() {
  python wiki-scripts/update_bot_status.py --run-tag "${RUN_TAG}" --stage "$1"
}

# Helper: commit and push any changed state files immediately
# This ensures state is never lost if a later step fails.
commit_state() {
  local msg="${1:-chore(state): update bot state [skip ci]}"
  git add -A -- "*.state" "aelaki/lexicon.json" "wiki-scripts/version_history.txt" "grammar/"
  if git diff --cached --quiet; then
    echo "  (no state changes to commit)"
    return 0
  fi
  git commit -m "$msg"
  git pull --rebase -X theirs origin "${GITHUB_REF_NAME}"
  git push origin "HEAD:${GITHUB_REF_NAME}"
  echo "  State committed and pushed."
}

# Configure git identity for state commits
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

# 0. Rebuild version_history.txt from git log (canonical, can never lose entries)
stage "Rebuilding version history"
python -c "
import subprocess, os
path = 'wiki-scripts/version_history.txt'
hashes = subprocess.check_output(
    ['git', 'log', '--reverse', '--format=%h'],
    text=True,
).strip().split('\n')
versions = ['legacy categorized words']
for h in hashes:
    h = h.strip()
    if h:
        versions.append(f'Words {h}')
with open(path, 'w', encoding='utf-8') as f:
    for v in versions:
        f.write(v + '\n')
print(f'Rebuilt version_history.txt: {len(versions)} entries')
"
commit_state "chore(state): rebuild version history from git log [skip ci]"

# 0.5 Mark bot as active
python wiki-scripts/update_bot_status.py --run-tag "${RUN_TAG}"

# 1. Early operations
stage "Creating wanted categories"
python wiki-scripts/create_wanted_categories.py --apply --run-tag "${RUN_TAG}"

stage "Deleting unused categories"
python wiki-scripts/delete_unused_categories.py --apply --run-tag "${RUN_TAG}"

# 1.5 Tag word: pages in Created from Wanted Pages with a non-lemma version
#     category so the upgrade loop picks them up.
stage "Tagging wanted word pages"
python wiki-scripts/tag_wanted_word_pages.py --apply --run-tag "${RUN_TAG}"

# 1.6 Normalize lexicon (redistribute inanimate nouns, fix roots)
stage "Normalizing lexicon"
python wiki-scripts/normalize_lexicon.py
commit_state "chore(state): post-normalize lexicon [skip ci]"

# 2. Upgrade outdated lemmas + Create new lemmas
stage "Upgrading and creating lemma pages"
python wiki-scripts/create_word_pages.py --apply --limit "$EDIT_LIMIT" --phase lemma --run-tag "${RUN_TAG}"
commit_state "chore(state): post-lemma state [skip ci]"

# 3. Add to dictionary (new words for next run)
stage "Generating new random words"
python wiki-scripts/generate_random_words.py --count 100
commit_state "chore(state): post-generate lexicon [skip ci]"

# 4. Create 100 new non-lemma forms + Upgrade 100 old non-lemma forms
stage "Creating and upgrading non-lemma form pages"
python wiki-scripts/create_word_pages.py --apply --limit "$EDIT_LIMIT" --phase nonlemma --run-tag "${RUN_TAG}"
commit_state "chore(state): post-nonlemma state [skip ci]"

# 5. Create wanted pages (stubs from Special:WantedPages)
stage "Creating wanted pages"
python wiki-scripts/create_wanted_pages.py --apply --run-tag "${RUN_TAG}"

# 6. Update list of all roots
stage "Updating list of Aelaki roots"
python wiki-scripts/sync_roots_list.py --apply --run-tag "${RUN_TAG}"

# 7. Update git commit log page
stage "Updating git commit log"
python wiki-scripts/sync_commit_log.py --apply --run-tag "${RUN_TAG}"

# 8. Sync grammar pages (bidirectional: pull wiki edits, push local edits)
stage "Syncing grammar pages"
python wiki-scripts/sync_grammar_pages.py --sync --apply --run-tag "${RUN_TAG}"
commit_state "chore(state): post-grammar-sync [skip ci]"

# 9. Delete orphaned pages (only runs in 2027+)
stage "Cleaning orphaned pages"
python wiki-scripts/delete_orphaned_pages.py --apply --max-edits "$EDIT_LIMIT" --run-tag "${RUN_TAG}"

# 10. Mark bot as inactive
python wiki-scripts/update_bot_status.py --run-tag "${RUN_TAG}" --finish
