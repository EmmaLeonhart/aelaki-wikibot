"""
create_wanted_files.py
======================
Fetches all titles from Special:WantedFiles and creates each as a File:
description page with content [[Category:Images]]. The file itself is
not uploaded — this only creates the local description page so the
Images category picks them up and the red File: links turn blue.

Runs before create_wanted_pages.py so image descriptions claim their
share of the creation budget first.

Usage:
    python create_wanted_files.py              # dry-run (list only)
    python create_wanted_files.py --apply      # actually create pages
"""
import argparse

from utils import batch_existing_titles, connect, create_page, Progress

CATEGORY_TEXT = "[[Category:Images]]"
EDIT_SUMMARY_BASE = "Bot: create file description from Special:WantedFiles"
DEFAULT_LIMIT = 50


def fetch_wanted_files(site) -> list[str]:
    """Fetch all titles from Special:WantedFiles via the API."""
    titles = []
    qp_continue = None

    while True:
        kwargs = {
            "action": "query",
            "list": "querypage",
            "qppage": "Wantedfiles",
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
    parser = argparse.ArgumentParser(description="Create file description pages from Special:WantedFiles")
    parser.add_argument("--apply", action="store_true", help="Actually create pages (default is dry-run)")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=f"Max pages to create this run (default: {DEFAULT_LIMIT})")
    parser.add_argument("--run-tag", default="", help="Wiki-formatted run tag for edit summaries.")
    args = parser.parse_args()

    site = connect()
    print("Fetching wanted files...", flush=True)
    wanted = fetch_wanted_files(site)
    print(f"Found {len(wanted)} wanted files.", flush=True)

    if not wanted:
        print("Nothing to do.")
        return

    # Special:Wantedfiles is a cached querypage — it can lag behind actual
    # state. Batch-check existence so we don't waste create-budget slots
    # on files whose descriptions have already been written this cycle.
    print(f"Batch-checking existence for {len(wanted)} titles...", flush=True)
    existing = batch_existing_titles(site, wanted)
    to_create = [t for t in wanted if t not in existing]
    print(
        f"  {len(existing)} already exist; {len(to_create)} remain to create.",
        flush=True,
    )

    if args.limit and len(to_create) > args.limit:
        to_create = to_create[:args.limit]
        print(f"  Capped at --limit {args.limit}.", flush=True)

    if not args.apply:
        print("\n--- DRY RUN (pass --apply to create) ---")
        for t in to_create:
            print(f"  would create: {t}")
        print(f"\nTotal: {len(to_create)} pages to create")
        return

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""
    edit_summary = f"{EDIT_SUMMARY_BASE}{run_tag_suffix}"

    stats = Progress()
    stats.skipped = len(existing)
    total = len(to_create)
    for i, title in enumerate(to_create, 1):
        stats.processed += 1
        try:
            created = create_page(site, title, CATEGORY_TEXT, edit_summary)
            if created:
                stats.created += 1
                print(f"  [{i}/{total}] Created: {title}", flush=True)
            else:
                # Race: another process wrote the description between the
                # batch check and now, or the creation budget is exhausted.
                stats.skipped += 1
                print(f"  [{i}/{total}] Skipped (exists or budget): {title}", flush=True)
        except Exception as exc:
            stats.errors += 1
            print(f"  [{i}/{total}] ERROR: {title} — {exc}", flush=True)

    print(f"\nDone. {stats.summary()}")


if __name__ == "__main__":
    main()
