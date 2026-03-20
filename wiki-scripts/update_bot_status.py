#!/usr/bin/env python3
"""
update_bot_status.py
====================
Updates User:EmmaBot on aelaki.miraheze.org with the current pipeline run status.

Two modes:
  --stage "..." : Update only the current stage line (fast, called before each step)
  (no --stage)  : Full status block rebuild (called once at pipeline start/end)

Adapted from shintowiki-scripts update_bot_userpage_status.py.
See: https://github.com/Emma-Leonhart/shintowiki-scripts/
"""
import datetime as dt
import json
import os
import argparse
import sys
from pathlib import Path

import mwclient

sys.path.insert(0, os.path.dirname(__file__))
from config import WIKI_URL, WIKI_PATH, USERNAME, PASSWORD, BOT_UA

STATUS_PAGE = os.getenv("WIKI_STATUS_PAGE", "User:EmmaBot")
BASE_PAGE_PATH = os.getenv("WIKI_STATUS_TEMPLATE_PATH",
                           os.path.join(os.path.dirname(__file__), "EmmaBot.wiki"))
START_MARKER = "<!-- BOT-RUN-STATUS:START -->"
END_MARKER = "<!-- BOT-RUN-STATUS:END -->"
STAGE_MARKER = "<!-- BOT-STAGE -->"


def load_event_data():
    event_path = os.getenv("GITHUB_EVENT_PATH", "").strip()
    if not event_path:
        return {}
    try:
        with open(event_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def summarize_trigger(event_name, event):
    if event_name == "push":
        commit = (event.get("head_commit") or {})
        msg = (commit.get("message") or "").strip().splitlines()
        first_line = msg[0] if msg else "(no commit message)"
        short_sha = (os.getenv("GITHUB_SHA", "") or "")[:7]
        return f'push: "{first_line}" ({short_sha})'
    if event_name == "schedule":
        return "scheduled daily run"
    if event_name == "workflow_dispatch":
        actor = os.getenv("GITHUB_ACTOR", "unknown")
        return f"manual run by {actor}"
    return event_name or "unknown"


def build_status_block(active=True):
    event_name = os.getenv("GITHUB_EVENT_NAME", "local")
    event = load_event_data()
    now_utc = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    trigger_summary = summarize_trigger(event_name, event)
    run_id = os.getenv("GITHUB_RUN_ID", "")
    repository = os.getenv("GITHUB_REPOSITORY", "")
    run_url = ""
    if repository and run_id:
        run_url = f"https://github.com/{repository}/actions/runs/{run_id}"

    status_label = "'''Active'''" if active else "Inactive"

    lines = [
        START_MARKER,
        "== Bot run status ==",
        f"* Status: {status_label}",
        f"* Last pipeline start (UTC): {now_utc}",
        f"* Trigger: {trigger_summary}",
    ]
    if run_url:
        lines.append(f"* Workflow run: {run_url}")
    # Stage line placeholder — updated in-place by --stage calls
    if active:
        lines.append(f"* Current stage: Starting... {STAGE_MARKER}")
    lines.append(END_MARKER)
    return "\n".join(lines)


def merge_base_and_status(base_text, status_block):
    text = base_text.strip()
    if START_MARKER in text and END_MARKER in text:
        before = text.split(START_MARKER, 1)[0].rstrip()
        after = text.split(END_MARKER, 1)[1].lstrip()
        merged = f"{before}\n\n{status_block}\n\n{after}".strip()
        return merged + "\n"
    return f"{text}\n\n{status_block}\n"


def update_stage(site, page, stage_text, run_tag):
    """Replace just the stage line in the live page text."""
    now_utc = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    current = page.text()
    if STAGE_MARKER not in current:
        # No stage marker yet — can't update in-place
        print(f"  Warning: no stage marker found on {STATUS_PAGE}", flush=True)
        return

    lines = current.split("\n")
    new_lines = []
    for line in lines:
        if STAGE_MARKER in line:
            new_lines.append(f"* Current stage: {stage_text} (since {now_utc}) {STAGE_MARKER}")
        else:
            new_lines.append(line)
    new_text = "\n".join(new_lines)
    if new_text.rstrip() != current.rstrip():
        page.save(new_text, summary=f"Bot: stage → {stage_text} {run_tag}")
        print(f"  Stage updated: {stage_text}", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-tag", required=True,
                        help="Wiki-formatted run tag link for edit summaries.")
    parser.add_argument("--stage",
                        help="Update only the current stage line (e.g. 'Creating wanted categories').")
    parser.add_argument("--finish", action="store_true",
                        help="Mark the bot as inactive (end of pipeline).")
    args = parser.parse_args()

    if not PASSWORD:
        raise RuntimeError("WIKI_PASSWORD must be set.")

    site = mwclient.Site(WIKI_URL, path=WIKI_PATH, clients_useragent=BOT_UA)
    site.login(USERNAME, PASSWORD)
    page = site.pages[STATUS_PAGE]

    if args.stage:
        # Quick update: just swap the stage line
        update_stage(site, page, args.stage, args.run_tag)
        return

    if args.finish:
        # End of pipeline: rebuild with inactive status
        base_path = Path(BASE_PAGE_PATH)
        if not base_path.exists():
            raise FileNotFoundError(f"Template page file not found: {base_path}")
        base_text = base_path.read_text(encoding="utf-8")
        status_block = build_status_block(active=False)
        new_text = merge_base_and_status(base_text, status_block)
        page.save(new_text, summary=f"Bot: pipeline finished {args.run_tag}")
        print(f"Updated {STATUS_PAGE} → inactive")
        return

    # Default: full status block rebuild (pipeline start)
    base_path = Path(BASE_PAGE_PATH)
    if not base_path.exists():
        raise FileNotFoundError(f"Template page file not found: {base_path}")
    base_text = base_path.read_text(encoding="utf-8")

    status_block = build_status_block(active=True)
    new_text = merge_base_and_status(base_text, status_block)
    page.save(new_text, summary=f"Bot: pipeline started {args.run_tag}")
    print(f"Updated {STATUS_PAGE} → active")


if __name__ == "__main__":
    main()
