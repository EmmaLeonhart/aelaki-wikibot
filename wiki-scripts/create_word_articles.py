"""
create_word_articles.py
=======================
Creates wiki articles for Aelaki vocabulary words.

Reads the lexicon from the aelaki Python package and generated forms CSV,
then creates one article per root word with:
- Root consonants and word class
- English gloss
- Inflection table (from aelaki_forms.csv)
- Links to related grammar pages
- Appropriate categories

Usage:
    python create_word_articles.py --dry-run          # preview only
    python create_word_articles.py --apply            # create pages
    python create_word_articles.py --apply --limit 5  # create first 5
"""
import argparse
import csv
import os
import sys
import time

# Add parent directory to path so we can import the aelaki package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import connect, create_page, load_state, append_state, append_log, Progress
from config import THROTTLE

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_STATE_FILE = os.path.join(os.path.dirname(__file__), "create_word_articles.state")
DEFAULT_LOG_FILE = os.path.join(os.path.dirname(__file__), "create_word_articles.log")
FORMS_CSV = os.path.join(os.path.dirname(__file__), "..", "aelaki_forms.csv")

# Map word class labels to wiki page links and categories
WORD_CLASS_INFO = {
    "noun": {
        "label": "Noun",
        "link": "[[Aelaki declensions]]",
        "category": "Aelaki nouns",
        "grammar_page": "Aelaki declensions",
    },
    "verb_transitive": {
        "label": "Transitive verb",
        "link": "[[Transitive verbs]]",
        "category": "Aelaki verbs",
        "grammar_page": "Verbs",
    },
    "verb_active": {
        "label": "Active verb",
        "link": "[[Active verbs]]",
        "category": "Aelaki verbs",
        "grammar_page": "Active verbs",
    },
    "verb_stative": {
        "label": "Stative verb",
        "link": "[[Stative verbs]]",
        "category": "Aelaki verbs",
        "grammar_page": "Stative verbs",
    },
    "adjective": {
        "label": "Adjective",
        "link": "[[Adjectives]]",
        "category": "Aelaki adjectives",
        "grammar_page": "Adjectives",
    },
    "adverb": {
        "label": "Adverb",
        "link": "[[Adjectives|Adverbs]]",
        "category": "Aelaki adverbs",
        "grammar_page": "Adjectives",
    },
}


# ---------------------------------------------------------------------------
# Load forms from CSV
# ---------------------------------------------------------------------------

def load_forms(csv_path: str) -> dict[str, list[dict]]:
    """Load aelaki_forms.csv and group rows by lexicon key.

    Returns dict: key -> [{"form_label": ..., "surface_form": ...}, ...]
    """
    forms_by_key: dict[str, list[dict]] = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row["key"]
            if key not in forms_by_key:
                forms_by_key[key] = []
            forms_by_key[key].append({
                "gloss": row["gloss"],
                "word_class": row["word_class"],
                "root": row["root"],
                "form_label": row["form_label"],
                "surface_form": row["surface_form"],
            })
    return forms_by_key


# ---------------------------------------------------------------------------
# Load lexicon entries
# ---------------------------------------------------------------------------

def load_lexicon() -> dict[str, dict]:
    """Load all lexicon entries from the aelaki package.

    Returns dict: key -> {"word_class": str, "gloss": str, "root": str, ...}
    """
    from aelaki.lexicon import VERBS, NOUNS, ADJECTIVES, ADVERBS, COLORS

    entries = {}
    for store in (VERBS, NOUNS, ADJECTIVES, ADVERBS):
        for key, entry in store.items():
            root = entry.root
            root_str = "-".join(root.consonants)
            wc = entry.word_class.value
            # Verbs use √C1-C2-C3 root citation form
            if wc in ("verb_transitive", "verb_active", "verb_stative"):
                citation = f"√{root_str}"
            else:
                citation = entry.citation_form or ""
            entries[key] = {
                "word_class": wc,
                "gloss": entry.gloss,
                "root": root_str,
                "gender": entry.inherent_gender.value if entry.inherent_gender else None,
                "citation_form": citation,
            }

    # Also add color terms as special entries
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
# Generate article wikitext
# ---------------------------------------------------------------------------

def generate_noun_table(forms: list[dict]) -> str:
    """Generate a wikitable for noun declension forms."""
    # Group by gender.number
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
        '{| class="wikitable"',
        "! Gender.Number !! 1st !! 2nd !! 3rd !! 4th",
    ]
    for gn_key in sorted(by_gender_number.keys()):
        persons = by_gender_number[gn_key]
        first = persons.get("first", "—")
        second = persons.get("second", "—")
        third = persons.get("third", "—")
        fourth = persons.get("fourth", "—")
        lines.append(f"|-\n| {gn_key} || {first} || {second} || {third} || {fourth}")
    lines.append("|}")
    return "\n".join(lines)


def generate_verb_table(forms: list[dict]) -> str:
    """Generate a wikitable for verb forms."""
    if not forms:
        return ""

    lines = [
        '{| class="wikitable"',
        "! Form !! Surface form",
    ]
    for form in forms:
        lines.append(f"|-\n| {form['form_label']} || {form['surface_form']}")
    lines.append("|}")
    return "\n".join(lines)


def generate_article(key: str, entry: dict, forms: list[dict] | None) -> str:
    """Generate full wikitext for a word article."""
    wc = entry["word_class"]
    wc_info = WORD_CLASS_INFO.get(wc, {})
    wc_label = wc_info.get("label", wc)
    wc_link = wc_info.get("link", wc_label)
    category = wc_info.get("category", "Aelaki vocabulary")
    grammar_page = wc_info.get("grammar_page", "")

    sections = []

    # Lead paragraph
    gloss = entry["gloss"]
    root = entry["root"]
    is_verb = wc in ("verb_transitive", "verb_active", "verb_stative")
    display_name = f"√{root}" if is_verb else key
    lead = f"'''{display_name}''' (root: {root}) is an Aelaki {wc_link.lower()} meaning \"{gloss}\"."
    if entry.get("gender"):
        lead += f" It has inherent {entry['gender']} gender."
    sections.append(lead)

    # Etymology / root info
    sections.append("\n== Root ==")
    sections.append(f"The root consonants are '''{root}'''.")
    if entry.get("citation_form"):
        sections.append(f"\nCitation form: '''{entry['citation_form']}'''")

    # Inflection table
    if forms:
        sections.append("\n== Inflected forms ==")
        if wc == "noun":
            table = generate_noun_table(forms)
        else:
            table = generate_verb_table(forms)
        if table:
            sections.append(table)

    # See also
    sections.append("\n== See also ==")
    see_also_links = ["[[Aelaki Lexicon]]", "[[Aelaki roots]]"]
    if grammar_page:
        see_also_links.insert(0, f"[[{grammar_page}]]")
    sections.append("\n".join(f"* {link}" for link in see_also_links))

    # Categories
    sections.append("")
    sections.append(f"[[Category:{category}]]")
    sections.append("[[Category:Aelaki vocabulary]]")
    sections.append("[[Category:Aelaki lemmas]]")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Create wiki articles for Aelaki vocabulary words."
    )
    parser.add_argument("--apply", action="store_true",
                        help="Actually create pages (default is dry-run).")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max pages to create (0 = no limit).")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing pages.")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE,
                        help="Path to resume-state file.")
    parser.add_argument("--log-file", default=DEFAULT_LOG_FILE,
                        help="Path to JSONL run log.")
    parser.add_argument("--keys", default="",
                        help="Comma-separated lexicon keys to process (default: all).")
    args = parser.parse_args()

    # Load data
    print("Loading lexicon...", flush=True)
    lexicon = load_lexicon()
    print(f"  {len(lexicon)} entries loaded.", flush=True)

    print("Loading forms CSV...", flush=True)
    forms_csv = FORMS_CSV
    if os.path.exists(forms_csv):
        forms_by_key = load_forms(forms_csv)
        print(f"  {sum(len(v) for v in forms_by_key.values())} forms loaded.", flush=True)
    else:
        print(f"  WARNING: {forms_csv} not found. Articles will have no inflection tables.")
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

    for key in keys:
        if args.limit and progress.created >= args.limit:
            print(f"\nReached limit of {args.limit} pages.", flush=True)
            break

        if key in completed:
            print(f"  SKIP (already done): {key}")
            progress.skipped += 1
            continue

        entry = lexicon.get(key)
        if not entry:
            print(f"  SKIP (not in lexicon): {key}")
            progress.skipped += 1
            continue

        progress.processed += 1
        wc = entry["word_class"]
        # Verbs use √C1-C2-C3 root form as page title
        if wc in ("verb_transitive", "verb_active", "verb_stative"):
            title = entry["citation_form"]  # already √root form
        else:
            title = key
        forms = forms_by_key.get(key)
        wikitext = generate_article(key, entry, forms)

        if not args.apply:
            # Dry-run: just print what would happen
            print(f"\n{'='*60}")
            print(f"WOULD CREATE: [[{title}]]")
            print(f"{'='*60}")
            print(wikitext[:500])
            if len(wikitext) > 500:
                print(f"  ... ({len(wikitext)} chars total)")
            progress.created += 1
        else:
            try:
                created = create_page(
                    site, title, wikitext,
                    summary=f"Bot: create article for Aelaki word \"{key}\"",
                    overwrite=args.overwrite,
                )
                if created:
                    print(f"  CREATED: [[{title}]]", flush=True)
                    progress.created += 1
                    append_state(args.state_file, key)
                    append_log(args.log_file, {
                        "key": key, "title": title, "status": "created",
                    })
                else:
                    print(f"  EXISTS: [[{title}]] (use --overwrite to replace)", flush=True)
                    progress.skipped += 1
                    append_log(args.log_file, {
                        "key": key, "title": title, "status": "exists",
                    })
            except Exception as e:
                print(f"  ERROR on [[{title}]]: {e}", flush=True)
                progress.errors += 1
                append_log(args.log_file, {
                    "key": key, "title": title, "status": "error", "error": str(e),
                })

    print(f"\n{'='*60}")
    print(f"Done. {progress.summary()}")


if __name__ == "__main__":
    main()
