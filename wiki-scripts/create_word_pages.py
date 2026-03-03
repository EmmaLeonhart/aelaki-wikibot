#!/usr/bin/env python3
"""
create_word_pages.py
====================
Creates word:LEMMA pages on aelaki.miraheze.org from the Aelaki lexicon.

Each page contains:
- Lead paragraph with word class and gloss
- Root consonant information
- Inflection table (from aelaki_forms.csv)
- See also links and categories
- {{wordpage|v1}} version footer

Usage:
    python create_word_pages.py --dry-run              # preview only
    python create_word_pages.py --apply --limit 10     # create 10 pages
    python create_word_pages.py --apply --run-tag "..." # with CI run tag
"""
import argparse
import csv
import os
import sys

# Add parent directory to path so we can import the aelaki package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import connect, create_page, load_state, append_state, append_log, Progress
from config import THROTTLE

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(__file__)
DEFAULT_STATE_FILE = os.path.join(SCRIPT_DIR, "create_word_pages.state")
DEFAULT_LOG_FILE = os.path.join(SCRIPT_DIR, "create_word_pages.log")
FORMS_CSV = os.path.join(SCRIPT_DIR, "..", "aelaki_forms.csv")

PAGE_VERSION = "v1"

# Map word class labels to wiki info
WORD_CLASS_INFO = {
    "noun": {
        "label": "Noun",
        "link": "[[Nouns|noun]]",
        "category": "Aelaki nouns",
    },
    "verb_transitive": {
        "label": "Transitive verb",
        "link": "[[Verbs|transitive verb]]",
        "category": "Aelaki verbs",
    },
    "verb_active": {
        "label": "Active verb",
        "link": "[[Verbs|active verb]]",
        "category": "Aelaki verbs",
    },
    "verb_stative": {
        "label": "Stative verb",
        "link": "[[Verbs|stative verb]]",
        "category": "Aelaki verbs",
    },
    "adjective": {
        "label": "Adjective",
        "link": "[[Adjectives|adjective]]",
        "category": "Aelaki adjectives",
    },
    "adverb": {
        "label": "Adverb",
        "link": "[[Adverbs|adverb]]",
        "category": "Aelaki adverbs",
    },
}


# ---------------------------------------------------------------------------
# Load forms from CSV
# ---------------------------------------------------------------------------

def load_forms(csv_path: str) -> dict[str, list[dict]]:
    """Load aelaki_forms.csv and group rows by lexicon key."""
    forms_by_key: dict[str, list[dict]] = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row["key"]
            if key not in forms_by_key:
                forms_by_key[key] = []
            forms_by_key[key].append({
                "form_label": row["form_label"],
                "surface_form": row["surface_form"],
            })
    return forms_by_key


# ---------------------------------------------------------------------------
# Load lexicon entries
# ---------------------------------------------------------------------------

def load_lexicon() -> dict[str, dict]:
    """Load all lexicon entries from the aelaki package."""
    from aelaki.lexicon import VERBS, NOUNS, ADJECTIVES, ADVERBS, COLORS

    entries = {}
    for store in (VERBS, NOUNS, ADJECTIVES, ADVERBS):
        for key, entry in store.items():
            root = entry.root
            root_str = "-".join(root.consonants)
            entries[key] = {
                "word_class": entry.word_class.value,
                "gloss": entry.gloss,
                "root": root_str,
                "gender": entry.inherent_gender.value if entry.inherent_gender else None,
                "citation_form": entry.citation_form or key,
            }

    for color_en, color_ae in COLORS.items():
        entries[f"color_{color_en}"] = {
            "word_class": "noun",
            "gloss": f"{color_en} (color)",
            "root": color_ae,
            "gender": None,
            "citation_form": color_ae,
        }

    return entries


# ---------------------------------------------------------------------------
# Generate page wikitext
# ---------------------------------------------------------------------------

def generate_noun_table(forms: list[dict]) -> str:
    """Generate a wikitable for noun declension forms."""
    by_gender_number: dict[str, dict[str, str]] = {}
    for form in forms:
        parts = form["form_label"].split(".")
        if len(parts) == 3:
            gender, number, person = parts
            gn_key = f"{gender}.{number}"
            if gn_key not in by_gender_number:
                by_gender_number[gn_key] = {}
            by_gender_number[gn_key][person] = form["surface_form"]

    if not by_gender_number:
        return ""

    lines = [
        '{| class="wikitable sortable"',
        "! Gender.Number !! 1st !! 2nd !! 3rd !! 4th",
    ]
    for gn_key in sorted(by_gender_number.keys()):
        persons = by_gender_number[gn_key]
        first = persons.get("first", "\u2014")
        second = persons.get("second", "\u2014")
        third = persons.get("third", "\u2014")
        fourth = persons.get("fourth", "\u2014")
        lines.append(f"|-\n| {gn_key} || {first} || {second} || {third} || {fourth}")
    lines.append("|}")
    return "\n".join(lines)


def generate_verb_table(forms: list[dict]) -> str:
    """Generate a wikitable for verb/adj/adv forms."""
    if not forms:
        return ""

    lines = [
        '{| class="wikitable sortable"',
        "! Form !! Surface form",
    ]
    for form in forms:
        lines.append(f"|-\n| {form['form_label']} || {form['surface_form']}")
    lines.append("|}")
    return "\n".join(lines)


def generate_word_page(key: str, entry: dict, forms: list[dict] | None) -> str:
    """Generate full wikitext for a word:LEMMA page."""
    wc = entry["word_class"]
    wc_info = WORD_CLASS_INFO.get(wc, {})
    wc_link = wc_info.get("link", wc)
    category = wc_info.get("category", "Aelaki vocabulary")

    lemma = entry["citation_form"]
    root = entry["root"]
    gloss = entry["gloss"]

    sections = []

    # Lead paragraph
    lead = f"'''{lemma}''' is an [[Aelaki]] {wc_link} meaning \"{gloss}\"."
    if entry.get("gender"):
        lead += f" It has inherent '''{entry['gender']}''' gender."
    sections.append(lead)

    # Overview table
    sections.append("")
    sections.append("== Overview ==")
    overview = ['{| class="wikitable"']
    overview.append("|-\n! Root consonants\n| " + root)
    overview.append("|-\n! Word class\n| " + wc_info.get("label", wc))
    overview.append("|-\n! Gloss\n| " + gloss)
    if entry.get("gender"):
        overview.append("|-\n! Inherent gender\n| " + entry["gender"])
    if lemma != key:
        overview.append("|-\n! Citation form\n| " + lemma)
    overview.append("|}")
    sections.append("\n".join(overview))

    # Inflection table
    if forms:
        sections.append("")
        sections.append("== Inflected forms ==")
        if wc == "noun":
            table = generate_noun_table(forms)
        else:
            table = generate_verb_table(forms)
        if table:
            sections.append(table)

    # See also
    sections.append("")
    sections.append("== See also ==")
    sections.append("* [[Aelaki Lexicon]]")

    # Categories
    sections.append("")
    sections.append(f"[[Category:{category}]]")
    sections.append("[[Category:Aelaki vocabulary]]")
    sections.append("[[Category:Word pages]]")

    # Version footer - MUST be last
    sections.append("{{wordpage|" + PAGE_VERSION + "}}")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Create word:LEMMA pages on aelaki.miraheze.org."
    )
    parser.add_argument("--apply", action="store_true",
                        help="Actually create pages (default is dry-run).")
    parser.add_argument("--limit", type=int, default=10,
                        help="Max pages to create per run (default: 10).")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing pages.")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE)
    parser.add_argument("--log-file", default=DEFAULT_LOG_FILE)
    parser.add_argument("--run-tag", default="",
                        help="Wiki-formatted run tag for edit summaries.")
    parser.add_argument("--keys", default="",
                        help="Comma-separated lexicon keys to process (default: all).")
    args = parser.parse_args()

    # Load data
    print("Loading lexicon...", flush=True)
    lexicon = load_lexicon()
    print(f"  {len(lexicon)} entries loaded.", flush=True)

    print("Loading forms CSV...", flush=True)
    if os.path.exists(FORMS_CSV):
        forms_by_key = load_forms(FORMS_CSV)
        print(f"  {sum(len(v) for v in forms_by_key.values())} forms loaded.", flush=True)
    else:
        print(f"  WARNING: {FORMS_CSV} not found. Pages will have no inflection tables.", flush=True)
        forms_by_key = {}

    # Filter keys
    if args.keys:
        keys = [k.strip() for k in args.keys.split(",")]
    else:
        keys = sorted(lexicon.keys())

    # Load state for resumption
    completed = load_state(args.state_file) if args.apply else set()

    # Connect
    site = None
    if args.apply:
        site = connect()

    progress = Progress()
    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""

    for key in keys:
        if args.limit and progress.created >= args.limit:
            print(f"\nReached limit of {args.limit} pages.", flush=True)
            break

        if key in completed:
            progress.skipped += 1
            continue

        entry = lexicon.get(key)
        if not entry:
            print(f"  SKIP (not in lexicon): {key}", flush=True)
            progress.skipped += 1
            continue

        progress.processed += 1
        lemma = entry["citation_form"]
        title = f"word:{lemma}"
        forms = forms_by_key.get(key)
        wikitext = generate_word_page(key, entry, forms)

        if not args.apply:
            print(f"\n{'=' * 60}")
            print(f"WOULD CREATE: [[{title}]]")
            print(f"{'=' * 60}")
            print(wikitext[:600])
            if len(wikitext) > 600:
                print(f"  ... ({len(wikitext)} chars total)")
            progress.created += 1
        else:
            try:
                created = create_page(
                    site, title, wikitext,
                    summary=f"Bot: create word page for \"{lemma}\"{run_tag_suffix}",
                    overwrite=args.overwrite,
                )
                if created:
                    print(f"  CREATED: [[{title}]]", flush=True)
                    progress.created += 1
                    append_state(args.state_file, key)
                    append_log(args.log_file, {
                        "key": key, "lemma": lemma, "title": title, "status": "created",
                    })
                else:
                    print(f"  EXISTS: [[{title}]] (use --overwrite to replace)", flush=True)
                    progress.skipped += 1
                    append_log(args.log_file, {
                        "key": key, "lemma": lemma, "title": title, "status": "exists",
                    })
            except Exception as e:
                print(f"  ERROR on [[{title}]]: {e}", flush=True)
                progress.errors += 1
                append_log(args.log_file, {
                    "key": key, "lemma": lemma, "title": title,
                    "status": "error", "error": str(e),
                })

    print(f"\n{'=' * 60}")
    print(f"Done. {progress.summary()}")


if __name__ == "__main__":
    main()
