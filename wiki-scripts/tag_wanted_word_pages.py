"""
tag_wanted_word_pages.py
========================
Scans [[Category:Created from Wanted Pages]] for word: pages that are missing
a [[Category:Non-lemma forms …]] tag, and adds the oldest version hash so the
upgrade loop in create_word_pages.py picks them up.

Run early in the pipeline so the upgrade phase can regenerate these stubs.

Usage:
    python tag_wanted_word_pages.py              # dry-run (list only)
    python tag_wanted_word_pages.py --apply      # actually edit pages
"""
import argparse
import os
import re

from utils import connect, safe_save, Progress

SCRIPT_DIR = os.path.dirname(__file__)
VERSION_HISTORY = os.path.join(SCRIPT_DIR, "version_history.txt")

SOURCE_CATEGORY = "Created from Wanted Pages"
NONLEMMA_CAT_RE = re.compile(r"\[\[Category:Non-lemma forms [^\]]+\]\]")

# Batch size for API content fetches (MediaWiki max is 50 for bots)
BATCH_SIZE = 50


def _get_oldest_hash() -> str:
    """Read the oldest 'Words HASH' entry from version_history.txt."""
    try:
        with open(VERSION_HISTORY, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("Words "):
                    return line[len("Words "):]
    except FileNotFoundError:
        pass
    return "unknown"


def _batch_fetch_content(site, titles):
    """Fetch page content for multiple titles in one API call.

    Returns dict of {title: content_str}.
    """
    result = {}
    for i in range(0, len(titles), BATCH_SIZE):
        batch = titles[i:i + BATCH_SIZE]
        resp = site.api("query", prop="revisions", rvprop="content",
                        rvslots="main", titles="|".join(batch))
        pages = resp.get("query", {}).get("pages", {})
        for pid, pdata in pages.items():
            if int(pid) < 0:
                continue  # missing page
            title = pdata.get("title", "")
            revs = pdata.get("revisions", [])
            if revs:
                slots = revs[0].get("slots", {})
                main_slot = slots.get("main", {})
                content = main_slot.get("*", "")
                if content:
                    result[title] = content
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Tag word: pages in Created from Wanted Pages with a non-lemma version category")
    parser.add_argument("--apply", action="store_true",
                        help="Actually edit pages (default is dry-run)")
    parser.add_argument("--run-tag", default="",
                        help="Run-tag to append to edit summaries")
    args = parser.parse_args()

    site = connect()
    oldest_hash = _get_oldest_hash()
    nonlemma_cat_text = f"[[Category:Non-lemma forms {oldest_hash}]]"
    print(f"Target non-lemma category: Non-lemma forms {oldest_hash}", flush=True)

    # Step 1: Collect all word: page titles from the category (metadata only, fast)
    cat = site.categories[SOURCE_CATEGORY]
    word_titles = []

    print(f"Listing [[Category:{SOURCE_CATEGORY}]]...", flush=True)
    for page in cat:
        if page.name.lower().startswith("word:"):
            word_titles.append(page.name)

    print(f"  {len(word_titles)} word: pages in category.", flush=True)

    if not word_titles:
        print("Nothing to do.")
        return

    # Step 2: Batch-fetch content (50 pages per API call instead of 1-by-1)
    print(f"Batch-fetching content ({len(word_titles)} pages, {BATCH_SIZE}/batch)...", flush=True)
    contents = _batch_fetch_content(site, word_titles)
    print(f"  Fetched content for {len(contents)} pages.", flush=True)

    # Step 3: Find pages missing the non-lemma category
    to_tag = []
    for title in word_titles:
        text = contents.get(title)
        if not text:
            continue
        if NONLEMMA_CAT_RE.search(text):
            continue
        to_tag.append((title, text))

    print(f"Found {len(to_tag)} word: pages missing a non-lemma forms category.", flush=True)

    if not to_tag:
        print("Nothing to do.")
        return

    if not args.apply:
        print("\n--- DRY RUN (pass --apply to edit) ---")
        for title, _ in to_tag:
            print(f"  would tag: {title}")
        print(f"\nTotal: {len(to_tag)} pages")
        return

    stats = Progress()
    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""
    for i, (title, text) in enumerate(to_tag, 1):
        stats.processed += 1
        page = site.pages[title]
        new_text = text.rstrip() + "\n" + nonlemma_cat_text
        try:
            saved = safe_save(page, new_text,
                              summary=f"Bot: add non-lemma version category{run_tag_suffix}")
            if saved:
                stats.created += 1
                print(f"  [{i}/{len(to_tag)}] Tagged: {title}", flush=True)
            else:
                stats.skipped += 1
                print(f"  [{i}/{len(to_tag)}] Skipped (no change): {title}", flush=True)
        except Exception as exc:
            stats.errors += 1
            print(f"  [{i}/{len(to_tag)}] ERROR: {title} — {exc}", flush=True)

    print(f"\nDone. {stats.summary()}")


if __name__ == "__main__":
    main()
