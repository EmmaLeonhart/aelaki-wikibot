"""
sync_lexicon_page.py
====================
Synchronizes the Aelaki Lexicon wiki page with data from the Python lexicon.

Adds a machine-readable summary table to the Aelaki Lexicon page (or a
subpage) listing all known roots with their glosses and word classes,
linked to their individual articles.

Usage:
    python sync_lexicon_page.py --dry-run          # preview changes
    python sync_lexicon_page.py --apply            # apply changes
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import connect, safe_save
from config import THROTTLE


TARGET_PAGE = "Aelaki Lexicon/Roots"
BOT_MARKER_START = "<!-- BOT:ROOTS-TABLE-START -->"
BOT_MARKER_END = "<!-- BOT:ROOTS-TABLE-END -->"


def load_lexicon() -> dict[str, dict]:
    """Load all lexicon entries from the aelaki package."""
    from aelaki.lexicon import VERBS, NOUNS, ADJECTIVES, ADVERBS

    entries = {}
    for store in (VERBS, NOUNS, ADJECTIVES, ADVERBS):
        for key, entry in store.items():
            entries[key] = {
                "word_class": entry.word_class.value,
                "gloss": entry.gloss,
                "root": "-".join(entry.root.consonants),
                "gender": entry.inherent_gender.value if entry.inherent_gender else "",
            }
    return entries


def generate_roots_table(entries: dict[str, dict]) -> str:
    """Generate a wikitable of all known roots."""
    lines = [
        BOT_MARKER_START,
        "This table is automatically generated from the Aelaki lexicon data.",
        "",
        '{| class="wikitable sortable"',
        '! data-sort-type="text" | Root key',
        '! data-sort-type="text" | Root consonants',
        '! data-sort-type="text" | Word class',
        '! data-sort-type="text" | Gloss',
        '! data-sort-type="text" | Gender',
    ]
    for key in sorted(entries.keys()):
        e = entries[key]
        lines.append("|-")
        lines.append(
            f"| [[{key}]] || {e['root']} || {e['word_class']} "
            f"|| {e['gloss']} || {e['gender']}"
        )
    lines.append("|}")
    lines.append(BOT_MARKER_END)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Sync Aelaki Lexicon/Roots page with lexicon data."
    )
    parser.add_argument("--apply", action="store_true",
                        help="Save edits (default is dry-run).")
    parser.add_argument("--page", default=TARGET_PAGE,
                        help=f"Target page title (default: {TARGET_PAGE}).")
    args = parser.parse_args()

    print("Loading lexicon...", flush=True)
    entries = load_lexicon()
    print(f"  {len(entries)} entries.", flush=True)

    table_text = generate_roots_table(entries)

    if not args.apply:
        print(f"\nWould write to [[{args.page}]]:\n")
        print(table_text)
        return

    site = connect()
    page = site.pages[args.page]

    if page.exists:
        current = page.text()
        # Replace between bot markers if they exist
        if BOT_MARKER_START in current and BOT_MARKER_END in current:
            start = current.index(BOT_MARKER_START)
            end = current.index(BOT_MARKER_END) + len(BOT_MARKER_END)
            new_text = current[:start] + table_text + current[end:]
        else:
            new_text = current + "\n\n" + table_text
    else:
        new_text = (
            f"= Aelaki Root Index =\n\n"
            f"Automatically maintained list of all documented Aelaki roots.\n\n"
            f"{table_text}\n\n"
            f"[[Category:Aelaki vocabulary]]"
        )

    saved = safe_save(page, new_text, summary="Bot: sync roots table from lexicon data")
    if saved:
        print(f"Updated [[{args.page}]].", flush=True)
    else:
        print(f"No changes needed for [[{args.page}]].", flush=True)


if __name__ == "__main__":
    main()
