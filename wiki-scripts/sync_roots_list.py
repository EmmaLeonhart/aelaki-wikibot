#!/usr/bin/env python3
"""
sync_roots_list.py
==================
Generates and pushes [[List of Aelaki roots]] — a single wiki page that
links every root in the lexicon, grouped by word class.

Usage:
    python wiki-scripts/sync_roots_list.py              # dry-run
    python wiki-scripts/sync_roots_list.py --apply      # push to wiki
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import connect, safe_save

# ---------------------------------------------------------------------------
# Lexicon loading (same as create_word_pages.py)
# ---------------------------------------------------------------------------

from aelaki.lexicon import VERBS, NOUNS, ADJECTIVES, ADVERBS, COLORS, WordClass
from aelaki.roots import TriRoot, TetraRoot

VERB_CLASSES = {"verb_transitive", "verb_active", "verb_stative"}

PAGE_TITLE = "List of Aelaki roots"

SECTIONS = [
    ("Nouns", NOUNS, "noun"),
    ("Transitive verbs", VERBS, "verb_transitive"),
    ("Active verbs", VERBS, "verb_active"),
    ("Stative verbs", VERBS, "verb_stative"),
    ("Adjectives", ADJECTIVES, "adjective"),
    ("Adverbs", ADVERBS, "adverb"),
]


def _page_title_for(entry, key):
    """Return the word:... page title for a lexicon entry."""
    wc = entry.word_class.value
    if wc in VERB_CLASSES:
        return f"word:√{'-'.join(entry.root.consonants)}"
    return f"word:{entry.citation_form or key}"


def generate_roots_page() -> str:
    """Generate the full wikitext for [[List of Aelaki roots]]."""
    lines = [
        "This page lists all Aelaki roots in the lexicon, grouped by word class.",
        "",
        "__TOC__",
    ]

    for section_name, store, wc_filter in SECTIONS:
        entries = []
        for key, entry in sorted(store.items()):
            if entry.word_class.value != wc_filter:
                continue
            root_str = "-".join(entry.root.consonants)
            title = _page_title_for(entry, key)
            gloss = entry.gloss
            entries.append((root_str, title, gloss))

        if not entries:
            continue

        lines.append(f"\n== {section_name} ({len(entries)}) ==")
        lines.append('{| class="wikitable sortable"')
        lines.append("! Root !! Gloss")
        for root_str, title, gloss in entries:
            lines.append(f"|-\n| [[{title}|{root_str}]] || {gloss}")
        lines.append("|}")

    lines.append("")
    lines.append("[[Category:Aelaki vocabulary]]")
    lines.append("[[Category:git synced pages]]")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate List of Aelaki roots page")
    parser.add_argument("--apply", action="store_true", help="Push to wiki")
    parser.add_argument("--run-tag", default="", help="Run tag for edit summary")
    args = parser.parse_args()

    text = generate_roots_page()

    if not args.apply:
        print(text[:2000])
        print(f"\n... ({len(text)} chars total)")
        return

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""
    site = connect()
    page = site.pages[PAGE_TITLE]
    saved = safe_save(page, text,
                      f"Bot: update list of Aelaki roots{run_tag_suffix}")
    if saved:
        print(f"Updated [[{PAGE_TITLE}]]")
    else:
        print(f"No changes to [[{PAGE_TITLE}]]")


if __name__ == "__main__":
    main()
