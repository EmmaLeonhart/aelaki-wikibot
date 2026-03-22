#!/usr/bin/env bash
# ============================================================================
# word_page_loop.sh — Main pipeline for the Aelaki word page bot (EmmaBot)
# ============================================================================
#
# Runs via GitHub Actions (.github/workflows/word-pages.yml).
# Triggered by: push to master, daily schedule, or manual dispatch.
#
# PIPELINE OVERVIEW
# =================
# Each step is annotated with:
#   [wiki]  = edits wiki pages (idempotent — safe to re-run)
#   [local] = writes local files (needs commit_state to persist)
#   [safe]  = no local state; if run crashes here, nothing is lost
#
# Step 0:   Rebuild version_history.txt from git log        [local] → commit
# Step 0.5: Mark bot active on wiki                         [wiki]
# Step 1:   Create wanted categories on wiki                [safe]
# Step 1.1: Delete unused categories on wiki                [safe]
# Step 1.5: Tag wanted word pages on wiki                   [safe]
# Step 1.6: Normalize lexicon (gender redistribution)       [local] → commit
# Step 2:   Upgrade old lemmas + create new lemma pages     [local+wiki] → commit
# Step 3:   Generate new random words into lexicon          [local] → commit
# Step 4:   Create + upgrade non-lemma form pages           [local+wiki] → commit
# Step 5:   Create wanted page stubs                        [safe]
# Step 6:   Update [[List of Aelaki roots]]                 [safe]
# Step 7:   Update [[Git commit log]]                       [safe]
# Step 8:   Sync grammar pages (bidirectional)              [local+wiki] → commit
# Step 9:   Delete orphaned pages (2027+ only)              [safe]
# Step 10:  Mark bot inactive on wiki                       [wiki]
#
# LOCAL STATE FILES
# =================
# These files are mutated by the pipeline and must be committed:
#   wiki-scripts/version_history.txt  — ordered list of all commit hashes
#   aelaki/lexicon.json               — word entries (normalize, generate)
#   wiki-scripts/create_word_pages.state — tracks which keys have pages
#   grammar/*.wiki                    — pulled grammar page content
#   grammar/_sync_state.json          — grammar sync metadata
#
# The commit_state() helper commits and pushes these after every step
# that mutates them. If the run crashes between a wiki edit and its
# commit_state, the only risk is that:
#   - A .state entry is missing → the page won't be re-created (it already
#     exists on the wiki), it just won't be skipped as fast next run.
#   - lexicon.json changes are lost → normalize/generate reruns next time,
#     producing the same result (idempotent).
#   - grammar/ files are stale → next pull will re-fetch them.
#
# WHAT IS NOT AT RISK
# ===================
# Steps marked [safe] only edit wiki pages and write no local state.
# If the run crashes during or after any [safe] step, nothing is lost —
# the wiki edits are already persisted and the step is idempotent.
# ============================================================================

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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Update the stage line on the bot's wiki userpage
stage() {
  python wiki-scripts/update_bot_status.py --run-tag "${RUN_TAG}" --stage "$1"
}

# Commit and push any changed state files immediately.
# Called after every step that writes local files.
# Files tracked: *.state, aelaki/lexicon.json, version_history.txt, grammar/
commit_state() {
  local msg="${1:-chore(state): update bot state [skip ci]}"
  git add -A -- "*.state" "*.last" "aelaki/lexicon.json" "wiki-scripts/version_history.txt" "grammar/"
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

# ===========================================================================
# Step 0 [local → commit]: Rebuild version_history.txt from git log
# Writes: wiki-scripts/version_history.txt
# Risk if crash: none — rebuilt from scratch every run
# ===========================================================================
stage "Rebuilding version history"
python -c "
import subprocess
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

# ===========================================================================
# Step 0.1 [local → commit]: Reconcile state file (annual)
# Writes: create_word_pages.state, reconcile_state.last
# Runs: first time 2026-03-22, then Jan 1 each year
# Risk if crash: state file may be partially written — next run rebuilds it
# ===========================================================================
stage "Reconciling state file (annual)"
python wiki-scripts/reconcile_state.py --apply
commit_state "chore(state): annual state reconciliation [skip ci]"

# ===========================================================================
# Step 0.5 [wiki]: Mark bot as active
# Writes: wiki only (User:EmmaBot)
# ===========================================================================
python wiki-scripts/update_bot_status.py --run-tag "${RUN_TAG}"

# ===========================================================================
# Step 1 [safe]: Create wanted categories + delete unused categories
# Writes: wiki only (category pages)
# ===========================================================================
stage "Creating wanted categories"
python wiki-scripts/create_wanted_categories.py --apply --run-tag "${RUN_TAG}"

stage "Deleting unused categories"
python wiki-scripts/delete_unused_categories.py --apply --run-tag "${RUN_TAG}"

# ===========================================================================
# Step 1.5 [safe]: Tag wanted word pages with non-lemma version category
# Writes: wiki only (adds category to stub pages)
# ===========================================================================
stage "Tagging wanted word pages"
python wiki-scripts/tag_wanted_word_pages.py --apply --run-tag "${RUN_TAG}"

# ===========================================================================
# Step 1.6 [local → commit]: Normalize lexicon
# Writes: aelaki/lexicon.json (gender redistribution, old_citation_form)
# Risk if crash before commit: normalize is idempotent, reruns same result
# ===========================================================================
stage "Normalizing lexicon"
python wiki-scripts/normalize_lexicon.py
commit_state "chore(state): post-normalize lexicon [skip ci]"

# ===========================================================================
# Step 2 [local+wiki → commit]: Upgrade old + create new lemma pages
# Writes: wiki (word pages), create_word_pages.state, version_history.txt
# Risk if crash before commit: state entries missing → pages won't be
#   skipped next run but they already exist on wiki, so safe_save is a no-op
# ===========================================================================
stage "Upgrading and creating lemma pages"
python wiki-scripts/create_word_pages.py --apply --limit "$EDIT_LIMIT" --phase lemma --run-tag "${RUN_TAG}"
commit_state "chore(state): post-lemma state [skip ci]"

# ===========================================================================
# Step 3 [local → commit]: Generate new random words
# Writes: aelaki/lexicon.json (new entries)
# Risk if crash before commit: new words lost → regenerated next run
#   (different random words, but same count — acceptable)
# ===========================================================================
stage "Generating new random words"
python wiki-scripts/generate_random_words.py --count 100
commit_state "chore(state): post-generate lexicon [skip ci]"

# ===========================================================================
# Step 4 [local+wiki → commit]: Create + upgrade non-lemma form pages
# Writes: wiki (form pages), create_word_pages.state
# Risk if crash before commit: same as step 2 — safe_save is idempotent
# ===========================================================================
stage "Creating and upgrading non-lemma form pages"
python wiki-scripts/create_word_pages.py --apply --limit "$EDIT_LIMIT" --phase nonlemma --run-tag "${RUN_TAG}"
commit_state "chore(state): post-nonlemma state [skip ci]"

# ===========================================================================
# Step 5 [safe]: Create wanted page stubs from Special:WantedPages
# Writes: wiki only (stub pages)
# ===========================================================================
stage "Creating wanted pages"
python wiki-scripts/create_wanted_pages.py --apply --run-tag "${RUN_TAG}"

# ===========================================================================
# Step 6 [safe]: Update [[List of Aelaki roots]]
# Writes: wiki only (single page)
# ===========================================================================
stage "Updating list of Aelaki roots"
python wiki-scripts/sync_roots_list.py --apply --run-tag "${RUN_TAG}"

# ===========================================================================
# Step 7 [safe]: Update [[Git commit log]]
# Writes: wiki only (single page)
# ===========================================================================
stage "Updating git commit log"
python wiki-scripts/sync_commit_log.py --apply --run-tag "${RUN_TAG}"

# ===========================================================================
# Step 8 [local+wiki → commit]: Sync grammar pages (bidirectional)
# Writes: grammar/*.wiki (pull), _sync_state.json, wiki (push)
# Risk if crash before commit: grammar files stale → next pull re-fetches
# ===========================================================================
stage "Syncing grammar pages"
python wiki-scripts/sync_grammar_pages.py --sync --apply --run-tag "${RUN_TAG}"
commit_state "chore(state): post-grammar-sync [skip ci]"

# ===========================================================================
# Step 9 [safe]: Delete orphaned pages (year-gated to 2027+)
# Writes: wiki only (page deletions)
# ===========================================================================
stage "Cleaning orphaned pages"
python wiki-scripts/delete_orphaned_pages.py --apply --max-edits "$EDIT_LIMIT" --run-tag "${RUN_TAG}"

# ===========================================================================
# Step 10 [wiki]: Mark bot as inactive
# Writes: wiki only (User:EmmaBot)
# ===========================================================================
python wiki-scripts/update_bot_status.py --run-tag "${RUN_TAG}" --finish
