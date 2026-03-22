#!/usr/bin/env python3
"""
delete_orphaned_pages.py
========================
Deletes pages from Special:OrphanedPages that are non-lemma forms
(word: namespace pages not linked from anywhere).

Only runs if the current year is 2027 or later.

Usage:
    python wiki-scripts/delete_orphaned_pages.py              # dry-run
    python wiki-scripts/delete_orphaned_pages.py --apply      # actually delete
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import THROTTLE
from utils import connect, Progress

import time

MIN_YEAR = 2027


def fetch_orphaned_pages(site) -> list[str]:
    """Fetch all titles from Special:OrphanedPages via the API."""
    titles = []
    qp_continue = None

    while True:
        kwargs = {
            "action": "query",
            "list": "querypage",
            "qppage": "Lonelypages",
            "qplimit": "max",
        }
        if qp_continue:
            kwargs["qpoffset"] = qp_continue

        result = site.api(**kwargs)
        results_list = result.get("query", {}).get("querypage", {}).get("results", [])

        for entry in results_list:
            title = entry.get("title", "")
            if title:
                titles.append(title)

        cont = result.get("continue", {})
        if "qpoffset" in cont:
            qp_continue = cont["qpoffset"]
        else:
            break

    return titles


def main():
    parser = argparse.ArgumentParser(description="Delete orphaned non-lemma word pages")
    parser.add_argument("--apply", action="store_true", help="Actually delete pages")
    parser.add_argument("--max-edits", type=int, default=100, help="Max deletions per run")
    parser.add_argument("--run-tag", default="", help="Run tag for edit summaries")
    args = parser.parse_args()

    now = datetime.datetime.now(datetime.timezone.utc)
    if now.year < MIN_YEAR:
        print(f"Skipping: orphan cleanup only runs in {MIN_YEAR}+, current year is {now.year}.")
        return

    site = connect()
    print("Fetching orphaned pages...", flush=True)
    orphans = fetch_orphaned_pages(site)
    print(f"Found {len(orphans)} orphaned pages.", flush=True)

    # Only delete word: pages (non-lemma forms that were accidentally created)
    word_orphans = [t for t in orphans if t.lower().startswith("word:")]
    print(f"{len(word_orphans)} are word: pages.", flush=True)

    if not word_orphans:
        print("Nothing to do.")
        return

    if not args.apply:
        print("\n--- DRY RUN ---")
        for t in word_orphans[:20]:
            print(f"  would delete: {t}")
        if len(word_orphans) > 20:
            print(f"  ... and {len(word_orphans) - 20} more")
        print(f"\nTotal: {len(word_orphans)} pages")
        return

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""
    stats = Progress()

    for i, title in enumerate(word_orphans, 1):
        if stats.created >= args.max_edits:
            print(f"Reached deletion budget ({args.max_edits}).", flush=True)
            break

        stats.processed += 1
        page = site.pages[title]
        try:
            page.delete(reason=f"Bot: delete orphaned non-lemma form{run_tag_suffix}")
            stats.created += 1
            print(f"  [{i}/{len(word_orphans)}] Deleted: {title}", flush=True)
            time.sleep(THROTTLE)
        except Exception as exc:
            stats.errors += 1
            print(f"  [{i}/{len(word_orphans)}] ERROR: {title} — {exc}", flush=True)

    print(f"\nDone. {stats.summary()}")


if __name__ == "__main__":
    main()
