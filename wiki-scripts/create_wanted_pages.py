"""
create_wanted_pages.py
======================
Fetches all pages from Special:WantedPages and creates them as stubs
containing [[Category:Created from Wanted Pages]].

word: pages get placed into a non-lemma version category so the upgrade
loop in create_word_pages.py picks them up and regenerates them properly.

Usage:
    python create_wanted_pages.py              # dry-run (list only)
    python create_wanted_pages.py --apply      # actually create pages
"""
import argparse
import os

from utils import connect, create_page, Progress

SCRIPT_DIR = os.path.dirname(__file__)
VERSION_HISTORY = os.path.join(SCRIPT_DIR, "version_history.txt")

CATEGORY_TEXT = "[[Category:Created from Wanted Pages]]"
EDIT_SUMMARY = "Bot: create stub from Special:WantedPages"
STATE_FILE = "wanted_pages_done.txt"

# Oldest version hash from version_history.txt — word: pages tagged with this
# get picked up by the upgrade loop on the next run.
_OLDEST_HASH = None


def _get_oldest_hash() -> str:
    """Read the oldest 'Words HASH' entry from version_history.txt."""
    global _OLDEST_HASH
    if _OLDEST_HASH is not None:
        return _OLDEST_HASH
    try:
        with open(VERSION_HISTORY, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("Words "):
                    _OLDEST_HASH = line[len("Words "):]
                    return _OLDEST_HASH
    except FileNotFoundError:
        pass
    _OLDEST_HASH = "unknown"
    return _OLDEST_HASH


def _content_for(title: str) -> str:
    """Return stub content for a wanted page.

    word: pages get a non-lemma version category; everything else gets the
    default wanted-pages category.
    """
    if title.lower().startswith("word:"):
        oldest = _get_oldest_hash()
        return (
            f"{CATEGORY_TEXT}\n"
            f"[[Category:Non-lemma forms {oldest}]]"
        )
    return CATEGORY_TEXT


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
            created = create_page(site, title, _content_for(title), EDIT_SUMMARY)
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
