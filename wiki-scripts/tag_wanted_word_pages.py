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

    cat = site.categories[SOURCE_CATEGORY]
    stats = Progress()
    to_tag = []

    print(f"Scanning [[Category:{SOURCE_CATEGORY}]]...", flush=True)
    for page in cat:
        if not page.name.lower().startswith("word:"):
            continue
        try:
            text = page.text()
        except Exception:
            continue

        if NONLEMMA_CAT_RE.search(text):
            continue  # already has a non-lemma forms category

        to_tag.append((page, text))

    print(f"Found {len(to_tag)} word: pages missing a non-lemma forms category.", flush=True)

    if not to_tag:
        print("Nothing to do.")
        return

    if not args.apply:
        print("\n--- DRY RUN (pass --apply to edit) ---")
        for page, _ in to_tag:
            print(f"  would tag: {page.name}")
        print(f"\nTotal: {len(to_tag)} pages")
        return

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""
    for i, (page, text) in enumerate(to_tag, 1):
        stats.processed += 1
        new_text = text.rstrip() + "\n" + nonlemma_cat_text
        try:
            saved = safe_save(page, new_text,
                              summary=f"Bot: add non-lemma version category{run_tag_suffix}")
            if saved:
                stats.created += 1
                print(f"  [{i}/{len(to_tag)}] Tagged: {page.name}", flush=True)
            else:
                stats.skipped += 1
                print(f"  [{i}/{len(to_tag)}] Skipped (no change): {page.name}", flush=True)
        except Exception as exc:
            stats.errors += 1
            print(f"  [{i}/{len(to_tag)}] ERROR: {page.name} — {exc}", flush=True)

    print(f"\nDone. {stats.summary()}")


if __name__ == "__main__":
    main()
