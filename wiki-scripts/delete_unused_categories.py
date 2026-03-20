#!/usr/bin/env python3
"""
delete_unused_categories.py
============================
Deletes empty categories listed on Special:UnusedCategories.

Usage:
    python delete_unused_categories.py --apply --run-tag "..."
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from utils import connect, append_log, Progress
from config import THROTTLE

import time

SCRIPT_DIR = os.path.dirname(__file__)
DEFAULT_LOG_FILE = os.path.join(SCRIPT_DIR, "delete_unused_categories.log")


def get_unused_categories(site):
    """Query Special:UnusedCategories via the API."""
    results = []
    qc_continue = {}
    while True:
        params = {
            "action": "query",
            "list": "querypage",
            "qppage": "Unusedcategories",
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
        description="Delete empty categories from Special:UnusedCategories."
    )
    parser.add_argument("--apply", action="store_true",
                        help="Actually delete pages (default is dry-run).")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max categories to delete (0 = no limit).")
    parser.add_argument("--log-file", default=DEFAULT_LOG_FILE)
    parser.add_argument("--run-tag", default="")
    args = parser.parse_args()

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""

    site = connect()

    if not args.apply:
        print("Dry-run mode (pass --apply to delete pages).", flush=True)

    print("Querying Special:UnusedCategories...", flush=True)
    unused = get_unused_categories(site)
    print(f"  {len(unused)} unused categories found.", flush=True)

    progress = Progress()

    for title in unused:
        if args.limit and progress.created >= args.limit:
            print(f"\nReached limit of {args.limit}.", flush=True)
            break

        progress.processed += 1
        page = site.pages[title]

        if not page.exists:
            progress.skipped += 1
            continue

        if not args.apply:
            print(f"  WOULD DELETE: [[{title}]]", flush=True)
            progress.created += 1
        else:
            try:
                page.delete(reason=f"Bot: delete unused category{run_tag_suffix}")
                time.sleep(THROTTLE)
                print(f"  DELETED: [[{title}]]", flush=True)
                progress.created += 1
                append_log(args.log_file, {
                    "title": title, "status": "deleted",
                })
            except Exception as e:
                print(f"  ERROR on [[{title}]]: {e}", flush=True)
                progress.errors += 1
                append_log(args.log_file, {
                    "title": title, "status": "error", "error": str(e),
                })

    print(f"\nDone. {progress.summary()}")


if __name__ == "__main__":
    main()
