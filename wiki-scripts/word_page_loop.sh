#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Running word page loop from: $ROOT_DIR"
EDIT_LIMIT="${WIKI_EDIT_LIMIT:-10}"
echo "Per-run max pages: $EDIT_LIMIT"

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

RUN_TAG="[[git:${RUN_PATH}|${CAUSE_TEXT}]]"
echo "Run tag: ${RUN_TAG}"

python wiki-scripts/update_bot_status.py --run-tag "${RUN_TAG}"
python wiki-scripts/create_word_pages.py --apply --limit "$EDIT_LIMIT" --run-tag "${RUN_TAG}"
