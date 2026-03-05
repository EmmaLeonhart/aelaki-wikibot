#!/usr/bin/env python3
"""
create_word_pages.py
====================
Creates word:LEMMA pages on aelaki.miraheze.org from the Aelaki lexicon.
Generates ALL forms directly from the morphology engine.

Usage:
    python create_word_pages.py                        # preview only
    python create_word_pages.py --apply --limit 10     # create 10 pages
    python create_word_pages.py --apply --run-tag "..."
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import connect, safe_save, load_state, append_state, append_log, Progress
from config import THROTTLE

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(__file__)
DEFAULT_STATE_FILE = os.path.join(SCRIPT_DIR, "create_word_pages.state")
DEFAULT_LOG_FILE = os.path.join(SCRIPT_DIR, "create_word_pages.log")

PAGE_VERSION = "v5"

WORD_CLASS_INFO = {
    "noun": {"label": "Noun", "link": "[[Nouns|noun]]", "category": "Aelaki nouns"},
    "verb_transitive": {"label": "Transitive verb", "link": "[[Verbs|transitive verb]]", "category": "Aelaki verbs"},
    "verb_active": {"label": "Active verb", "link": "[[Verbs|active verb]]", "category": "Aelaki verbs"},
    "verb_stative": {"label": "Stative verb", "link": "[[Verbs|stative verb]]", "category": "Aelaki verbs"},
    "adjective": {"label": "Adjective", "link": "[[Adjectives|adjective]]", "category": "Aelaki adjectives"},
    "adverb": {"label": "Adverb", "link": "[[Adverbs|adverb]]", "category": "Aelaki adverbs"},
}


# ---------------------------------------------------------------------------
# Morphology imports
# ---------------------------------------------------------------------------

from aelaki.lexicon import VERBS, NOUNS, ADJECTIVES, ADVERBS, COLORS, WordClass
from aelaki.gender import Gender, Number, Person
from aelaki.roots import TriRoot, TetraRoot
from aelaki.nouns import build_noun, build_tri_stem, build_tetra_stem
from aelaki.person import (
    agent_case, patient_case, possessive_case,
    instrumental_case, dative_case, speaker_case,
)
from aelaki.verbs import (
    conjugate_transitive, conjugate_intransitive_active,
    conjugate_intransitive_stative,
    StemTemplate, Evidential, DayPrefix,
)
from aelaki.stative_verbs import stative_paradigm
from aelaki.adjectives import realize_adjective, AdjDegree, AdjEvidential
from aelaki.adverbs import realize_adverb, AdverbDegree, AdverbTense

# Canonical agreement for verb/adj tables (3rd male singular subject, 4th female singular object)
SUBJ = (Person.THIRD, Gender.MALE, Number.SINGULAR)
OBJ = (Person.FOURTH, Gender.FEMALE, Number.SINGULAR)


# ---------------------------------------------------------------------------
# Load lexicon
# ---------------------------------------------------------------------------

def load_lexicon() -> dict[str, dict]:
    entries = {}
    for store in (VERBS, NOUNS, ADJECTIVES, ADVERBS):
        for key, entry in store.items():
            entries[key] = {
                "word_class": entry.word_class.value,
                "gloss": entry.gloss,
                "root": entry.root,
                "root_str": "-".join(entry.root.consonants),
                "gender": entry.inherent_gender,
                "citation_form": entry.citation_form or key,
                "entry": entry,
            }

    for color_en, color_ae in COLORS.items():
        entries[f"color_{color_en}"] = {
            "word_class": "noun",
            "gloss": f"{color_en} (color)",
            "root": TriRoot("?", "?", "?"),
            "root_str": color_ae,
            "gender": None,
            "citation_form": color_ae,
            "entry": None,
        }

    return entries


# ---------------------------------------------------------------------------
# Form generation — directly from morphology engine
# ---------------------------------------------------------------------------

def generate_noun_forms(entry) -> list[tuple[str, str]]:
    """All gender x number x person forms for a noun."""
    root = entry["root"]
    genders = [entry["gender"]] if entry["gender"] else list(Gender)
    forms = []
    for g in genders:
        for n in Number:
            for p in Person:
                label = f"{g.value}.{n.value}.{p.name.lower()}"
                try:
                    form = build_noun(root, g, n, p)
                except Exception as e:
                    form = f"ERROR: {e}"
                forms.append((label, form))
    return forms


def generate_transitive_forms(entry) -> list[tuple[str, str]]:
    """All template x evidential x day prefix forms (canonical agreement)."""
    root = entry["root"]
    forms = []
    for tmpl in StemTemplate:
        for evid in Evidential:
            for day in DayPrefix:
                day_lbl = f"{day.name.lower()}." if day != DayPrefix.NONE else ""
                label = f"{tmpl.name.lower()}.{day_lbl}{evid.name.lower()}"
                try:
                    form = conjugate_transitive(root, tmpl, evid, day, *SUBJ, *OBJ)
                except Exception as e:
                    form = f"ERROR: {e}"
                forms.append((label, form))
    return forms


def generate_active_forms(entry) -> list[tuple[str, str]]:
    """All evidential x day prefix forms (canonical agreement)."""
    root = entry["root"]
    forms = []
    for evid in Evidential:
        for day in DayPrefix:
            day_lbl = f"{day.name.lower()}." if day != DayPrefix.NONE else ""
            label = f"active.{day_lbl}{evid.name.lower()}"
            try:
                form = conjugate_intransitive_active(root, "a", "a", evid, day, *SUBJ)
            except Exception as e:
                form = f"ERROR: {e}"
            forms.append((label, form))
    return forms


def generate_stative_forms(entry) -> list[tuple[str, str]]:
    """All evidential x day prefix forms + full stative prefix paradigm."""
    root = entry["root"]
    forms = []
    # Conjugated forms
    for evid in Evidential:
        for day in DayPrefix:
            day_lbl = f"{day.name.lower()}." if day != DayPrefix.NONE else ""
            label = f"stative.{day_lbl}{evid.name.lower()}"
            try:
                form = conjugate_intransitive_stative(root, "a", "a", evid, day, *SUBJ)
            except Exception as e:
                form = f"ERROR: {e}"
            forms.append((label, form))
    # Prefix paradigm (32 forms)
    base_stem = f"{root.c1}a{root.c2}a{root.c3}"
    try:
        paradigm = stative_paradigm(base_stem)
        for form_name, form in paradigm.items():
            forms.append((f"stative_prefix.{form_name}", form))
    except Exception as e:
        forms.append(("stative_prefix.ERROR", f"ERROR: {e}"))
    return forms


def generate_adjective_forms(entry) -> list[tuple[str, str]]:
    """All degree x evidential forms (canonical agreement)."""
    root = entry["root"]
    forms = []
    for deg in AdjDegree:
        for evid in AdjEvidential:
            label = f"{deg.name.lower()}.{evid.name.lower()}"
            try:
                form = realize_adjective(root, *SUBJ, deg, evid)
            except Exception as e:
                form = f"ERROR: {e}"
            forms.append((label, form))
    return forms


def generate_adverb_forms(entry) -> list[tuple[str, str]]:
    """All degree x tense forms."""
    root = entry["root"]
    forms = []
    for deg in AdverbDegree:
        for tense in AdverbTense:
            label = f"{deg.name.lower()}.{tense.name.lower()}"
            try:
                form = realize_adverb(root, "a", "a", deg, tense)
            except Exception as e:
                form = f"ERROR: {e}"
            forms.append((label, form))
    return forms


CASE_FUNCTIONS = [
    ("agent", agent_case),
    ("patient", None),  # patient uses build_noun (unmarked form)
    ("possessive", possessive_case),
    ("instrumental", instrumental_case),
    ("dative", dative_case),
    ("speaker", speaker_case),
]


def generate_noun_case_forms(entry) -> list[tuple[str, str]]:
    """6 cases x 4 persons for a noun (inherent gender, singular)."""
    root = entry["root"]
    gender = entry["gender"] or Gender.MALE
    number = Number.SINGULAR

    # Build bare stem for case functions
    if isinstance(root, TetraRoot):
        stem = build_tetra_stem(root, gender, number)
    else:
        stem = build_tri_stem(root, gender, number)

    forms = []
    for case_name, case_func in CASE_FUNCTIONS:
        for p in Person:
            label = f"{case_name}.{p.name.lower()}"
            try:
                if case_func is None:
                    # Patient = unmarked form from build_noun
                    form = build_noun(root, gender, number, p)
                else:
                    form = case_func(stem, p, gender, number)
            except Exception as e:
                form = f"ERROR: {e}"
            forms.append((label, form))
    return forms


def generate_case_table(forms: list[tuple[str, str]]) -> str:
    """Wikitable with rows = 6 cases, cols = 4 persons."""
    by_case: dict[str, dict[str, str]] = {}
    for label, surface in forms:
        case_name, person = label.split(".")
        if case_name not in by_case:
            by_case[case_name] = {}
        by_case[case_name][person] = surface

    if not by_case:
        return ""

    row_order = ["agent", "patient", "possessive", "instrumental", "dative", "speaker"]
    display = {
        "agent": "[[Agent]]", "patient": "[[Patient]]", "possessive": "[[Possessive]]",
        "instrumental": "[[Instrumental]]", "dative": "[[Dative]]", "speaker": "[[Speaker]]",
    }
    dash = "\u2014"
    lines = [
        '{| class="wikitable"',
        "! Case !! 1st !! 2nd !! 3rd !! 4th",
    ]
    for case_name in row_order:
        p = by_case.get(case_name, {})
        lines.append(
            f"|-\n| {display[case_name]} "
            f"|| {p.get('first', dash)} || {p.get('second', dash)} "
            f"|| {p.get('third', dash)} || {p.get('fourth', dash)}"
        )
    lines.append("|}")
    return "\n".join(lines)


FORM_GENERATORS = {
    "noun": generate_noun_forms,
    "verb_transitive": generate_transitive_forms,
    "verb_active": generate_active_forms,
    "verb_stative": generate_stative_forms,
    "adjective": generate_adjective_forms,
    "adverb": generate_adverb_forms,
}


# ---------------------------------------------------------------------------
# Agreement paradigm generators (person x gender x number)
# ---------------------------------------------------------------------------

def generate_active_agreement(entry) -> list[tuple[str, str]]:
    """All person x gender x number forms for active verb (base present)."""
    root = entry["root"]
    forms = []
    for g in Gender:
        for n in Number:
            for p in Person:
                label = f"{g.value}.{n.value}.{p.name.lower()}"
                try:
                    form = conjugate_intransitive_active(
                        root, "a", "a",
                        subj_person=p, subj_gender=g, subj_number=n,
                    )
                except Exception as e:
                    form = f"ERROR: {e}"
                forms.append((label, form))
    return forms


def generate_stative_agreement(entry) -> list[tuple[str, str]]:
    """All person x gender x number forms for stative verb (base present)."""
    root = entry["root"]
    forms = []
    for g in Gender:
        for n in Number:
            for p in Person:
                label = f"{g.value}.{n.value}.{p.name.lower()}"
                try:
                    form = conjugate_intransitive_stative(
                        root, "a", "a",
                        subj_person=p, subj_gender=g, subj_number=n,
                    )
                except Exception as e:
                    form = f"ERROR: {e}"
                forms.append((label, form))
    return forms


def generate_transitive_subject_agreement(entry) -> list[tuple[str, str]]:
    """Vary subject p x g x n with fixed canonical object, telic perfect."""
    root = entry["root"]
    forms = []
    for g in Gender:
        for n in Number:
            for p in Person:
                label = f"{g.value}.{n.value}.{p.name.lower()}"
                try:
                    form = conjugate_transitive(
                        root, StemTemplate.TELIC_PERFECT,
                        subj_person=p, subj_gender=g, subj_number=n,
                        obj_person=OBJ[0], obj_gender=OBJ[1], obj_number=OBJ[2],
                    )
                except Exception as e:
                    form = f"ERROR: {e}"
                forms.append((label, form))
    return forms


def generate_transitive_object_agreement(entry) -> list[tuple[str, str]]:
    """Vary object p x g x n with fixed canonical subject, telic perfect."""
    root = entry["root"]
    forms = []
    for g in Gender:
        for n in Number:
            for p in Person:
                label = f"{g.value}.{n.value}.{p.name.lower()}"
                try:
                    form = conjugate_transitive(
                        root, StemTemplate.TELIC_PERFECT,
                        subj_person=SUBJ[0], subj_gender=SUBJ[1], subj_number=SUBJ[2],
                        obj_person=p, obj_gender=g, obj_number=n,
                    )
                except Exception as e:
                    form = f"ERROR: {e}"
                forms.append((label, form))
    return forms


def generate_adjective_agreement(entry) -> list[tuple[str, str]]:
    """All person x gender x number forms for adjective (positive, no evidential)."""
    root = entry["root"]
    forms = []
    for g in Gender:
        for n in Number:
            for p in Person:
                label = f"{g.value}.{n.value}.{p.name.lower()}"
                try:
                    form = realize_adjective(root, p, g, n)
                except Exception as e:
                    form = f"ERROR: {e}"
                forms.append((label, form))
    return forms


# ---------------------------------------------------------------------------
# Generate page wikitext
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Wikitext linking helpers (v5)
# ---------------------------------------------------------------------------

LINKABLE_TERMS = {
    # Degrees
    "positive", "comparative", "superlative", "negative",
    # Evidentials
    "visual", "hearsay", "inferential", "optative", "hodiernal",
    # Aspects/templates
    "telic", "atelic", "perfect", "imperfect",
    # Voice/type
    "active", "stative",
    # Gender
    "child", "female", "male", "inanimate",
    # Number
    "singular", "plural", "collective", "zero",
}


def wikt_gloss(gloss: str) -> str:
    """Wrap the core word of a gloss in a [[Wikt:...]] interwiki link."""
    match = re.match(r'^(.+?)\s*(\([^)]+\))$', gloss)
    if match:
        core = match.group(1).strip()
        suffix = " " + match.group(2)
    else:
        core = gloss
        suffix = ""
    wikt_title = core[0].upper() + core[1:] if core else core
    return f"[[Wikt:{wikt_title}|{core}]]{suffix}"


def link_form_label(label: str) -> str:
    """Link known grammatical terms in dot/underscore-separated form labels."""
    parts = label.split(".")
    linked = []
    for part in parts:
        subparts = part.split("_")
        linked_sub = []
        for sp in subparts:
            if sp in LINKABLE_TERMS:
                linked_sub.append(f"[[{sp}]]")
            else:
                linked_sub.append(sp)
        linked.append("_".join(linked_sub))
    return ".".join(linked)


def generate_noun_table(forms: list[tuple[str, str]]) -> str:
    """Grouped noun table: rows = gender.number, cols = person."""
    by_gn: dict[str, dict[str, str]] = {}
    for label, surface in forms:
        parts = label.split(".")
        if len(parts) == 3:
            gender, number, person = parts
            gn = f"{gender}.{number}"
            if gn not in by_gn:
                by_gn[gn] = {}
            by_gn[gn][person] = surface
    if not by_gn:
        return ""
    lines = [
        '{| class="wikitable sortable"',
        "! Gender.Number !! 1st !! 2nd !! 3rd !! 4th",
    ]
    dash = "\u2014"
    for gn in sorted(by_gn.keys()):
        p = by_gn[gn]
        first = p.get("first", dash)
        second = p.get("second", dash)
        third = p.get("third", dash)
        fourth = p.get("fourth", dash)
        lines.append(f"|-\n| {link_form_label(gn)} || {first} || {second} || {third} || {fourth}")
    lines.append("|}")
    return "\n".join(lines)


def generate_forms_table(forms: list[tuple[str, str]]) -> str:
    """Simple two-column form table."""
    if not forms:
        return ""
    lines = ['{| class="wikitable sortable"', "! Form !! Surface form"]
    for label, surface in forms:
        lines.append(f"|-\n| {link_form_label(label)} || {surface}")
    lines.append("|}")
    return "\n".join(lines)


def generate_word_page(key: str, entry: dict) -> str:
    """Generate full wikitext for a word:LEMMA page (v5)."""
    wc = entry["word_class"]
    wc_info = WORD_CLASS_INFO.get(wc, {})
    wc_link = wc_info.get("link", wc)
    category = wc_info.get("category", "Aelaki vocabulary")

    lemma = entry["citation_form"]
    root_str = entry["root_str"]
    gloss = entry["gloss"]

    sections = []

    # Lead
    lead = f"'''{lemma}''' is an [[Aelaki]] {wc_link} meaning \"{wikt_gloss(gloss)}\"."
    if entry.get("gender"):
        lead += f" It has inherent '''{entry['gender'].value}''' gender."
    sections.append(lead)

    # Overview table
    sections.append("\n== Overview ==")
    overview = ['{| class="wikitable"']
    overview.append(f"|-\n! Root consonants\n| {root_str}")
    overview.append(f"|-\n! Word class\n| [[{wc_info.get('label', wc)}]]")
    overview.append(f"|-\n! Gloss\n| {wikt_gloss(gloss)}")
    if entry.get("gender"):
        overview.append(f"|-\n! Inherent gender\n| {entry['gender'].value}")
    if lemma != key:
        overview.append(f"|-\n! Citation form\n| {lemma}")
    overview.append("|}")
    sections.append("\n".join(overview))

    # Generate forms from morphology engine
    generator = FORM_GENERATORS.get(wc)
    if generator and entry.get("entry"):
        forms = generator(entry)

        # Agreement paradigm section (verbs and adjectives)
        if wc == "verb_transitive":
            subj_forms = generate_transitive_subject_agreement(entry)
            obj_forms = generate_transitive_object_agreement(entry)
            sections.append("\n== Agreement paradigm ==")
            sections.append("=== Subject agreement ===")
            sections.append(f"''Object fixed at {OBJ[0].name.lower()} {OBJ[1].value} {OBJ[2].value}, telic perfect template.''")
            sections.append(generate_noun_table(subj_forms))
            sections.append("=== Object agreement ===")
            sections.append(f"''Subject fixed at {SUBJ[0].name.lower()} {SUBJ[1].value} {SUBJ[2].value}, telic perfect template.''")
            sections.append(generate_noun_table(obj_forms))
        elif wc == "verb_active":
            agreement_forms = generate_active_agreement(entry)
            sections.append("\n== Agreement paradigm ==")
            sections.append("''Base present, no evidential.''")
            sections.append(generate_noun_table(agreement_forms))
        elif wc == "verb_stative":
            agreement_forms = generate_stative_agreement(entry)
            sections.append("\n== Agreement paradigm ==")
            sections.append("''Base present, no evidential.''")
            sections.append(generate_noun_table(agreement_forms))
        elif wc == "adjective":
            agreement_forms = generate_adjective_agreement(entry)
            sections.append("\n== Agreement paradigm ==")
            sections.append("''Positive degree, no evidential.''")
            sections.append(generate_noun_table(agreement_forms))

        # Main forms table
        if forms:
            if wc == "noun":
                sections.append("\n== Inflected forms ==")
                sections.append(generate_noun_table(forms))
            elif wc in ("verb_transitive", "verb_active", "verb_stative", "adjective"):
                sections.append("\n== Evidential and TAM forms ==")
                sections.append(generate_forms_table(forms))
            else:
                sections.append("\n== Inflected forms ==")
                sections.append(generate_forms_table(forms))
            sections.append(f"\n''{len(forms)} forms generated.''")

        # Case paradigm for nouns
        if wc == "noun":
            case_forms = generate_noun_case_forms(entry)
            if case_forms:
                gender = entry["gender"] or Gender.MALE
                sections.append("\n== Case paradigm ==")
                sections.append(f"''Shown for {gender.value} singular.''")
                sections.append(generate_case_table(case_forms))

    # See also
    sections.append("\n== See also ==")
    sections.append("* [[Aelaki Lexicon]]")

    # Categories
    sections.append("")
    sections.append(f"[[Category:{category}]]")
    sections.append("[[Category:Aelaki vocabulary]]")
    sections.append("[[Category:Word pages]]")

    # Version footer
    sections.append("{{wordpage|" + PAGE_VERSION + "}}")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Upgrade old versions
# ---------------------------------------------------------------------------

def upgrade_old_versions(site, lexicon, limit_per_version, run_tag_suffix, log_file):
    """Upgrade pages from older versions to current PAGE_VERSION.

    Iterates through Category:Words v1, v2, etc. sequentially.
    Upgrades up to `limit_per_version` pages from EACH old version category.
    """
    current_num = int(PAGE_VERSION[1:])  # "v2" -> 2
    total_upgraded = 0

    for v in range(1, current_num):
        cat_name = f"Words v{v}"
        print(f"\nChecking [[Category:{cat_name}]]...", flush=True)
        cat = site.categories[cat_name]
        upgraded_this_version = 0

        for page in cat:
            if upgraded_this_version >= limit_per_version:
                print(f"  Reached limit of {limit_per_version} for v{v}.", flush=True)
                break
            if not page.name.startswith("word:"):
                continue

            # Find the lexicon key for this page
            lemma = page.name[5:]  # strip "word:"
            entry = None
            for k, e in lexicon.items():
                if e["citation_form"] == lemma:
                    entry = e
                    key = k
                    break
            if not entry:
                print(f"  SKIP upgrade (no lexicon match): [[{page.name}]]", flush=True)
                continue

            new_text = generate_word_page(key, entry)
            try:
                saved = safe_save(page, new_text,
                                  summary=f"Bot: upgrade word page to {PAGE_VERSION}{run_tag_suffix}")
                if saved:
                    print(f"  UPGRADED: [[{page.name}]] v{v} -> {PAGE_VERSION}", flush=True)
                    upgraded_this_version += 1
                    total_upgraded += 1
                    append_log(log_file, {
                        "key": key, "lemma": lemma, "title": page.name,
                        "status": "upgraded", "from": f"v{v}", "to": PAGE_VERSION,
                    })
                else:
                    print(f"  SKIP (no change): [[{page.name}]]", flush=True)
            except Exception as e:
                print(f"  ERROR upgrading [[{page.name}]]: {e}", flush=True)
                append_log(log_file, {
                    "key": key, "lemma": lemma, "title": page.name,
                    "status": "upgrade_error", "error": str(e),
                })

        print(f"  v{v}: upgraded {upgraded_this_version} pages.", flush=True)

    return total_upgraded


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Create word:LEMMA pages on aelaki.miraheze.org."
    )
    parser.add_argument("--apply", action="store_true",
                        help="Actually create/update pages (default is dry-run).")
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

    print("Loading lexicon...", flush=True)
    lexicon = load_lexicon()
    print(f"  {len(lexicon)} entries loaded.", flush=True)

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""

    # Connect
    site = None
    if args.apply:
        site = connect()

    # --- Phase 1: Upgrade old version pages (10 per old version) ---
    if args.apply:
        print(f"\n--- Phase 1: Upgrade old pages to {PAGE_VERSION} (up to {args.limit} per version) ---", flush=True)
        upgraded = upgrade_old_versions(site, lexicon, args.limit, run_tag_suffix, args.log_file)
        print(f"\n  Total upgraded: {upgraded} pages.", flush=True)
    else:
        print(f"\n--- Phase 1: Would upgrade old pages to {PAGE_VERSION} (dry-run) ---", flush=True)

    # --- Phase 2: Create new pages (independent limit) ---
    print(f"\n--- Phase 2: Create up to {args.limit} new pages ---", flush=True)

    if args.keys:
        keys = [k.strip() for k in args.keys.split(",")]
    else:
        keys = sorted(lexicon.keys())

    completed = load_state(args.state_file) if args.apply else set()
    progress = Progress()

    for key in keys:
        if args.limit and progress.created >= args.limit:
            print(f"\nReached limit of {args.limit} new pages.", flush=True)
            break

        if key in completed:
            progress.skipped += 1
            continue

        entry = lexicon.get(key)
        if not entry:
            progress.skipped += 1
            continue

        progress.processed += 1
        lemma = entry["citation_form"]
        title = f"word:{lemma}"
        wikitext = generate_word_page(key, entry)

        if not args.apply:
            print(f"\n{'=' * 60}")
            print(f"WOULD CREATE: [[{title}]]")
            print(f"{'=' * 60}")
            print(wikitext[:800])
            if len(wikitext) > 800:
                print(f"  ... ({len(wikitext)} chars total)")
            progress.created += 1
        else:
            try:
                page = site.pages[title]
                if page.exists and not args.overwrite:
                    print(f"  EXISTS: [[{title}]]", flush=True)
                    progress.skipped += 1
                    append_state(args.state_file, key)
                    continue
                saved = safe_save(page, wikitext,
                                  summary=f"Bot: create word page for \"{lemma}\"{run_tag_suffix}")
                if saved:
                    print(f"  CREATED: [[{title}]]", flush=True)
                    progress.created += 1
                    append_state(args.state_file, key)
                    append_log(args.log_file, {
                        "key": key, "lemma": lemma, "title": title, "status": "created",
                    })
                else:
                    progress.skipped += 1
                    append_state(args.state_file, key)
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
