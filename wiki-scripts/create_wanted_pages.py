"""
create_wanted_pages.py
======================
Fetches all pages from Special:WantedPages and creates them as stubs
containing [[Category:Created from Wanted Pages]].

Usage:
    python create_wanted_pages.py              # dry-run (list only)
    python create_wanted_pages.py --apply      # actually create pages
"""
import argparse

from utils import connect, create_page, Progress

CATEGORY_TEXT = "[[Category:Created from Wanted Pages]]"
EDIT_SUMMARY = "Bot: create stub from Special:WantedPages"
STATE_FILE = "wanted_pages_done.txt"


def fetch_wanted_pages(site) -> list[str]:
    """Fetch all titles from Special:WantedPages via the API."""
    titles = []
    qp_continue = None

    while True:
        kwargs = {
            "action": "query",
            "list": "querypage",
            "qppage": "Wantedpages",
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

        # Handle continuation
        cont = result.get("continue", {})
        if "qpoffset" in cont:
            qp_continue = cont["qpoffset"]
        else:
            break

    return titles


def main():
    parser = argparse.ArgumentParser(description="Create pages from Special:WantedPages")
    parser.add_argument("--apply", action="store_true", help="Actually create pages (default is dry-run)")
    args = parser.parse_args()

    site = connect()
    print("Fetching wanted pages...", flush=True)
    wanted = fetch_wanted_pages(site)
    print(f"Found {len(wanted)} wanted pages.", flush=True)

    if not wanted:
        print("Nothing to do.")
        return

    if not args.apply:
        print("\n--- DRY RUN (pass --apply to create) ---")
        for t in wanted:
            print(f"  would create: {t}")
        print(f"\nTotal: {len(wanted)} pages")
        return

    stats = Progress()
    for i, title in enumerate(wanted, 1):
        stats.processed += 1
        try:
            created = create_page(site, title, CATEGORY_TEXT, EDIT_SUMMARY)
            if created:
                stats.created += 1
                print(f"  [{i}/{len(wanted)}] Created: {title}", flush=True)
            else:
                stats.skipped += 1
                print(f"  [{i}/{len(wanted)}] Skipped (exists): {title}", flush=True)
        except Exception as exc:
            stats.errors += 1
            print(f"  [{i}/{len(wanted)}] ERROR: {title} — {exc}", flush=True)

    print(f"\nDone. {stats.summary()}")


if __name__ == "__main__":
    main()
