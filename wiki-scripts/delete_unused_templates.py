#!/usr/bin/env python3
"""
delete_unused_templates.py
===========================
Deletes templates listed on Special:UnusedTemplates (i.e. pages in the
Template namespace not transcluded anywhere).

Tries page.delete() first; if the bot lacks delete rights, falls back to
blanking the page so it can be cleaned up by an admin.

Usage:
    python delete_unused_templates.py --apply --run-tag "..."
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from utils import connect, safe_save, append_log, Progress, delete_page

SCRIPT_DIR = os.path.dirname(__file__)
DEFAULT_LOG_FILE = os.path.join(SCRIPT_DIR, "delete_unused_templates.log")

# Templates that should never be removed even if currently unused.
# Add names here (without the "Template:" prefix) to protect them.
PROTECTED: set[str] = set()


def get_unused_templates(site):
    """Query Special:UnusedTemplates via the API."""
    results = []
    qc_continue = {}
    while True:
        params = {
            "action": "query",
            "list": "querypage",
            "qppage": "Unusedtemplates",
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


def template_name(title):
    """Strip 'Template:' prefix if present."""
    if title.startswith("Template:"):
        return title[len("Template:"):]
    return title


def main():
    parser = argparse.ArgumentParser(
        description="Delete templates from Special:UnusedTemplates."
    )
    parser.add_argument("--apply", action="store_true",
                        help="Actually delete pages (default is dry-run).")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max templates to delete (0 = no limit).")
    parser.add_argument("--log-file", default=DEFAULT_LOG_FILE)
    parser.add_argument("--run-tag", default="")
    args = parser.parse_args()

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""

    site = connect()

    if not args.apply:
        print("Dry-run mode (pass --apply to delete pages).", flush=True)

    print("Querying Special:UnusedTemplates...", flush=True)
    unused = get_unused_templates(site)
    print(f"  {len(unused)} unused templates found.", flush=True)

    progress = Progress()
    deleted_count = 0

    for title in unused:
        if args.limit and deleted_count >= args.limit:
            print(f"\nReached limit of {args.limit}.", flush=True)
            break

        name = template_name(title)
        if name in PROTECTED:
            print(f"  PROTECTED: [[{title}]]", flush=True)
            progress.skipped += 1
            continue

        progress.processed += 1
        page = site.pages[title]

        if not page.exists:
            print(f"  SKIP (page gone): [[{title}]]", flush=True)
            progress.skipped += 1
            continue

        if not args.apply:
            print(f"  WOULD DELETE: [[{title}]]", flush=True)
            deleted_count += 1
            continue

        # Try actual deletion first, fall back to blanking
        try:
            delete_page(page, reason=f"Bot: delete unused template{run_tag_suffix}")
            print(f"  DELETED: [[{title}]]", flush=True)
            deleted_count += 1
            append_log(args.log_file, {"title": title, "status": "deleted"})
        except Exception as del_err:
            # If delete fails (e.g. no permission), blank the page instead
            print(f"  Delete failed ({del_err}), blanking instead...", flush=True)
            try:
                saved = safe_save(page, "",
                                  summary=f"Bot: blank unused template (no delete permission){run_tag_suffix}")
                if saved:
                    print(f"  BLANKED: [[{title}]]", flush=True)
                    deleted_count += 1
                    append_log(args.log_file, {"title": title, "status": "blanked"})
                else:
                    progress.skipped += 1
            except Exception as blank_err:
                print(f"  ERROR on [[{title}]]: {blank_err}", flush=True)
                progress.errors += 1
                append_log(args.log_file, {
                    "title": title, "status": "error", "error": str(blank_err),
                })

    progress.created = deleted_count
    print(f"\nDone. {progress.summary()}")


if __name__ == "__main__":
    main()
