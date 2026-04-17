#!/usr/bin/env python3
"""
delete_orphaned_pages.py
========================
Deletes pages from Special:OrphanedPages that have no incoming links.

Protected from deletion:
  - Main Page
  - User / User talk pages
  - Category pages
  - Template pages
  - MediaWiki namespace pages

Activates on 2026-07-01. The start date is intentionally delayed so we
have time to observe orphan behaviour and link anything (e.g. Adpositions)
that we don't want swept up. Capped at 10 deletions per run.

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

from utils import connect, Progress, delete_page

# Activation date and per-run cap. See module docstring.
MIN_DATE = datetime.date(2026, 7, 1)
MAX_DELETIONS_PER_RUN = 10

# Namespace prefixes that should never be deleted
PROTECTED_PREFIXES = (
    "User:",
    "User talk:",
    "Category:",
    "Template:",
    "MediaWiki:",
)

PROTECTED_TITLES = {
    "Main Page",
}


def is_protected(title: str) -> bool:
    """Return True if this page should never be deleted."""
    if title in PROTECTED_TITLES:
        return True
    for prefix in PROTECTED_PREFIXES:
        if title.startswith(prefix):
            return True
    return False


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
    parser = argparse.ArgumentParser(description="Delete orphaned pages")
    parser.add_argument("--apply", action="store_true", help="Actually delete pages")
    parser.add_argument("--max-edits", type=int, default=MAX_DELETIONS_PER_RUN,
                        help="Ceiling on deletions; clamped to MAX_DELETIONS_PER_RUN")
    parser.add_argument("--run-tag", default="", help="Run tag for edit summaries")
    args = parser.parse_args()

    today = datetime.datetime.now(datetime.timezone.utc).date()
    if today < MIN_DATE:
        print(f"Skipping: orphan cleanup activates on {MIN_DATE}; today is {today}.")
        return

    # Hard cap regardless of what the caller passed — 10/day policy.
    deletion_limit = min(args.max_edits, MAX_DELETIONS_PER_RUN)

    site = connect()
    print("Fetching orphaned pages...", flush=True)
    orphans = fetch_orphaned_pages(site)
    print(f"Found {len(orphans)} orphaned pages total.", flush=True)

    # Filter out protected pages
    deletable = [t for t in orphans if not is_protected(t)]
    protected_count = len(orphans) - len(deletable)
    if protected_count:
        print(f"Skipping {protected_count} protected pages.", flush=True)
    print(f"{len(deletable)} pages eligible for deletion.", flush=True)

    if not deletable:
        print("Nothing to do.")
        return

    if not args.apply:
        print("\n--- DRY RUN ---")
        for t in deletable[:20]:
            print(f"  would delete: {t}")
        if len(deletable) > 20:
            print(f"  ... and {len(deletable) - 20} more")
        print(f"\nTotal: {len(deletable)} pages")
        return

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""
    stats = Progress()

    for i, title in enumerate(deletable, 1):
        if stats.created >= deletion_limit:
            print(f"Reached deletion budget ({deletion_limit}).", flush=True)
            break

        stats.processed += 1
        page = site.pages[title]
        try:
            delete_page(page, reason=f"Bot: delete orphaned page{run_tag_suffix}")
            stats.created += 1
            print(f"  [{i}/{len(deletable)}] Deleted: {title}", flush=True)
        except Exception as exc:
            stats.errors += 1
            print(f"  [{i}/{len(deletable)}] ERROR: {title} — {exc}", flush=True)

    print(f"\nDone. {stats.summary()}")


if __name__ == "__main__":
    main()
