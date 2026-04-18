"""
create_wanted_pages.py
======================
Fetches all pages from Special:WantedPages and creates them as stubs
containing [[Category:Created from Wanted Pages]].

word: pages get placed into a non-lemma version category so the upgrade
loop in create_word_pages.py picks them up and regenerates them properly.

Any title that is tracked by sync_grammar_pages.py (i.e. lives under
grammar/ in this repo) is skipped — those pages are authored locally and
pushed by the grammar sync step, and must not carry the wanted-pages
category.

Usage:
    python create_wanted_pages.py              # dry-run (list only)
    python create_wanted_pages.py --apply      # actually create pages
"""
import argparse
import glob
import json
import os

from utils import batch_existing_titles, connect, create_page, Progress

SCRIPT_DIR = os.path.dirname(__file__)
VERSION_HISTORY = os.path.join(SCRIPT_DIR, "version_history.txt")
GRAMMAR_DIR = os.path.join(SCRIPT_DIR, "..", "grammar")
GRAMMAR_STATE_FILE = os.path.join(GRAMMAR_DIR, "_sync_state.json")

CATEGORY_TEXT = "[[Category:Created from Wanted Pages]]"
EDIT_SUMMARY_BASE = "Bot: create stub from Special:WantedPages"
STATE_FILE = "wanted_pages_done.txt"

# Namespaces that cannot be directly edited (Wikibase entity namespaces)
SKIP_PREFIXES = {"Property:", "Item:", "Lexeme:"}

# Current version hash from version_history.txt — word: pages tagged with this
# so the upgrade loop treats them as current-version non-lemma forms.
_CURRENT_HASH = None


def _get_current_hash() -> str:
    """Read the latest (last) 'Words HASH' entry from version_history.txt."""
    global _CURRENT_HASH
    if _CURRENT_HASH is not None:
        return _CURRENT_HASH
    last = None
    try:
        with open(VERSION_HISTORY, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("Words "):
                    last = line[len("Words "):]
    except FileNotFoundError:
        pass
    _CURRENT_HASH = last or "unknown"
    return _CURRENT_HASH


def _content_for(title: str) -> str:
    """Return stub content for a wanted page.

    word: pages get a non-lemma version category; everything else gets the
    default wanted-pages category.
    """
    if title.lower().startswith("word:"):
        current = _get_current_hash()
        return (
            f"{CATEGORY_TEXT}\n"
            f"[[Category:Non-lemma forms {current}]]"
        )
    return CATEGORY_TEXT


def load_git_synced_titles() -> set[str]:
    """Return the set of wiki page titles owned by the grammar sync.

    Sourced from grammar/_sync_state.json (authoritative for previously-synced
    pages), plus every grammar/*.wiki filename (covers pages that were added
    locally but haven't been pushed yet). The filename-derived fallback mirrors
    sync_grammar_pages.title_to_filename: "Foo bar" -> "Foo_bar.wiki", and
    "Category:Foo" -> "Category_Foo.wiki". We reverse with a minimal rule
    (underscores -> spaces, restore "Category:" prefix) because that covers
    every shape currently in use and errs on the side of skipping more.
    """
    titles: set[str] = set()
    try:
        with open(GRAMMAR_STATE_FILE, "r", encoding="utf-8") as f:
            titles.update(json.load(f).keys())
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    for path in glob.glob(os.path.join(GRAMMAR_DIR, "*.wiki")):
        stem = os.path.splitext(os.path.basename(path))[0]
        if stem.startswith("Category_"):
            titles.add("Category:" + stem[len("Category_"):].replace("_", " "))
        else:
            titles.add(stem.replace("_", " "))
    return titles


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
    parser.add_argument("--run-tag", default="", help="Wiki-formatted run tag for edit summaries.")
    args = parser.parse_args()

    site = connect()
    print("Fetching wanted pages...", flush=True)
    wanted = fetch_wanted_pages(site)
    print(f"Found {len(wanted)} wanted pages.", flush=True)

    git_synced = load_git_synced_titles()
    if git_synced:
        print(f"Loaded {len(git_synced)} git-synced titles to protect.", flush=True)

    if not wanted:
        print("Nothing to do.")
        return

    # Filter out titles we will never touch: Wikibase-entity namespaces
    # (not directly editable) and pages owned by the grammar sync.
    skipped_ns = 0
    skipped_synced = 0
    candidates: list[str] = []
    for title in wanted:
        if any(title.startswith(p) for p in SKIP_PREFIXES):
            skipped_ns += 1
            continue
        if title in git_synced:
            skipped_synced += 1
            continue
        candidates.append(title)

    # Batch existence check — avoids the ~200ms-per-title page.exists probe
    # that made this step dominate pipeline runtime (≈5000 * 0.2s = 17 min).
    print(f"Batch-checking existence for {len(candidates)} candidate titles...", flush=True)
    existing = batch_existing_titles(site, candidates) if candidates else set()
    to_create = [t for t in candidates if t not in existing]
    print(
        f"  {len(existing)} already exist; {len(to_create)} remain to create.",
        flush=True,
    )

    if not args.apply:
        print("\n--- DRY RUN (pass --apply to create) ---")
        for t in to_create:
            print(f"  would create: {t}")
        print(f"\nTotal: {len(to_create)} pages to create")
        return

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""
    edit_summary = f"{EDIT_SUMMARY_BASE}{run_tag_suffix}"

    stats = Progress()
    stats.skipped = skipped_ns + skipped_synced + len(existing)
    total = len(to_create)
    for i, title in enumerate(to_create, 1):
        stats.processed += 1
        try:
            created = create_page(site, title, _content_for(title), edit_summary)
            if created:
                stats.created += 1
                print(f"  [{i}/{total}] Created: {title}", flush=True)
            else:
                # Race: someone created it between the batch check and now.
                stats.skipped += 1
                print(f"  [{i}/{total}] Skipped (exists): {title}", flush=True)
        except Exception as exc:
            stats.errors += 1
            print(f"  [{i}/{total}] ERROR: {title} — {exc}", flush=True)

    print(f"\nDone. {stats.summary()}")


if __name__ == "__main__":
    main()
