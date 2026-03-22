#!/usr/bin/env python3
"""
reconcile_state.py
==================
Rebuilds create_word_pages.state from the wiki by checking page.exists
for every lexicon key. Clears stale entries and adds missing ones.

Runs annually: first run 2026-03-22, then Jan 1 each year after.

Usage:
    python wiki-scripts/reconcile_state.py              # dry-run
    python wiki-scripts/reconcile_state.py --apply      # rebuild state file
"""
import argparse
import datetime
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import THROTTLE
from utils import connect

SCRIPT_DIR = os.path.dirname(__file__)
STATE_FILE = os.path.join(SCRIPT_DIR, "create_word_pages.state")
LAST_RUN_FILE = os.path.join(SCRIPT_DIR, "reconcile_state.last")

# Reuse lexicon loading from create_word_pages
from aelaki.lexicon import VERBS, NOUNS, ADJECTIVES, ADVERBS, COLORS, WordClass
from aelaki.roots import TriRoot, TetraRoot

VERB_CLASSES = {"verb_transitive", "verb_active", "verb_stative"}


def load_lexicon() -> dict[str, dict]:
    entries = {}
    for store in (VERBS, NOUNS, ADJECTIVES, ADVERBS):
        for key, entry in store.items():
            wc = entry.word_class.value
            if wc in VERB_CLASSES:
                title = f"word:√{'-'.join(entry.root.consonants)}"
            else:
                title = f"word:{entry.citation_form or key}"
            entries[key] = title
    return entries


def should_run() -> bool:
    """Check if it's time for the annual reconciliation."""
    now = datetime.datetime.now(datetime.timezone.utc)

    if not os.path.exists(LAST_RUN_FILE):
        return True

    with open(LAST_RUN_FILE, "r") as f:
        last = f.read().strip()

    try:
        last_date = datetime.datetime.fromisoformat(last)
    except ValueError:
        return True

    # Next run is Jan 1 of the year after last run
    next_run = datetime.datetime(last_date.year + 1, 1, 1,
                                  tzinfo=datetime.timezone.utc)
    return now >= next_run


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild create_word_pages.state from wiki page.exists checks")
    parser.add_argument("--apply", action="store_true",
                        help="Actually rebuild the state file")
    parser.add_argument("--force", action="store_true",
                        help="Run even if not due yet")
    args = parser.parse_args()

    if not args.force and not should_run():
        print("Reconciliation not due yet (annual). Use --force to override.")
        return

    print("Loading lexicon...", flush=True)
    lexicon = load_lexicon()
    print(f"  {len(lexicon)} entries.", flush=True)

    if not args.apply:
        print(f"\nDry run: would check {len(lexicon)} pages on wiki.")
        return

    site = connect()
    exists_keys = []
    missing_keys = []

    for i, (key, title) in enumerate(sorted(lexicon.items()), 1):
        page = site.pages[title]
        if page.exists:
            exists_keys.append(key)
        else:
            missing_keys.append(key)

        if i % 100 == 0:
            print(f"  Checked {i}/{len(lexicon)}...", flush=True)

        time.sleep(0.1)  # light throttle for API

    # Write fresh state file
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        for key in sorted(exists_keys):
            f.write(key + "\n")

    # Record last run date
    now = datetime.datetime.now(datetime.timezone.utc)
    with open(LAST_RUN_FILE, "w") as f:
        f.write(now.isoformat())

    print(f"\nReconciliation complete:")
    print(f"  {len(exists_keys)} keys with existing pages (written to state)")
    print(f"  {len(missing_keys)} keys without pages (will be created next run)")
    if missing_keys[:10]:
        print(f"  Sample missing: {missing_keys[:10]}")


if __name__ == "__main__":
    main()
