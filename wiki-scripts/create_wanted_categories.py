#!/usr/bin/env python3
"""
create_wanted_categories.py
===========================
Creates missing categories listed on Special:WantedCategories.
Each created category page contains only: [[Category:Bot created categories]]

Usage:
    python create_wanted_categories.py --apply --run-tag "..."
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from utils import connect, safe_save, append_log, Progress
from config import THROTTLE

SCRIPT_DIR = os.path.dirname(__file__)
DEFAULT_LOG_FILE = os.path.join(SCRIPT_DIR, "create_wanted_categories.log")


def get_wanted_categories(site):
    """Query Special:WantedCategories via the API."""
    results = []
    qc_continue = {}
    while True:
        params = {
            "action": "query",
            "list": "querypage",
            "qppage": "Wantedcategories",
            "qplimit": "max",
            "format": "json",
        }
        params.update(qc_continue)
        resp = site.api(**params)
        for item in resp.get("query", {}).get("querypage", {}).get("results", []):
            title = item.get("title", "")
            if title:
                results.append(title)
        cont = resp.get("continue")
        if not cont:
            break
        qc_continue = cont
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Create missing categories from Special:WantedCategories."
    )
    parser.add_argument("--apply", action="store_true",
                        help="Actually create pages (default is dry-run).")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max categories to create (0 = no limit).")
    parser.add_argument("--log-file", default=DEFAULT_LOG_FILE)
    parser.add_argument("--run-tag", default="")
    args = parser.parse_args()

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""

    site = None
    if args.apply:
        site = connect()
    else:
        print("Dry-run mode (pass --apply to create pages).", flush=True)
        # Still need to connect to query wanted categories
        site = connect()

    print("Querying Special:WantedCategories...", flush=True)
    wanted = get_wanted_categories(site)
    print(f"  {len(wanted)} wanted categories found.", flush=True)

    progress = Progress()
    content = "[[Category:Bot created categories]]"

    for title in wanted:
        if args.limit and progress.created >= args.limit:
            print(f"\nReached limit of {args.limit}.", flush=True)
            break

        progress.processed += 1
        page = site.pages[title]

        if page.exists:
            progress.skipped += 1
            continue

        if not args.apply:
            print(f"  WOULD CREATE: [[{title}]]", flush=True)
            progress.created += 1
        else:
            try:
                saved = safe_save(page, content,
                                  summary=f"Bot: create wanted category{run_tag_suffix}")
                if saved:
                    print(f"  CREATED: [[{title}]]", flush=True)
                    progress.created += 1
                    append_log(args.log_file, {
                        "title": title, "status": "created",
                    })
                else:
                    progress.skipped += 1
            except Exception as e:
                print(f"  ERROR on [[{title}]]: {e}", flush=True)
                progress.errors += 1
                append_log(args.log_file, {
                    "title": title, "status": "error", "error": str(e),
                })

    print(f"\nDone. {progress.summary()}")


if __name__ == "__main__":
    main()
