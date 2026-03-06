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
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import connect, safe_save, move_page, load_state, append_state, append_log, Progress
from config import THROTTLE

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(__file__)
DEFAULT_STATE_FILE = os.path.join(SCRIPT_DIR, "create_word_pages.state")
DEFAULT_LOG_FILE = os.path.join(SCRIPT_DIR, "create_word_pages.log")
DEFAULT_VERSION_HISTORY = os.path.join(SCRIPT_DIR, "version_history.txt")

def _git_commit_id() -> str:
    """Return the short commit hash of HEAD in this repo."""
    return subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=os.path.dirname(__file__) or ".",
        text=True,
    ).strip()


PAGE_VERSION = _git_commit_id()

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
    # Inanimate number label mapping: singular→paucal, plural→plentiful
    INANIMATE_NUMBER_LABEL = {
        Number.SINGULAR: "paucal",
        Number.PLURAL: "plentiful",
    }
    for g in genders:
        if g == Gender.INANIMATE:
            numbers = [Number.SINGULAR, Number.PLURAL]
        else:
            numbers = list(Number)
        for n in numbers:
            for p in Person:
                num_label = INANIMATE_NUMBER_LABEL.get(n, n.value) if g == Gender.INANIMATE else n.value
                label = f"{g.value}.{num_label}.{p.name.lower()}"
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


VERB_CLASSES = {"verb_transitive", "verb_active", "verb_stative"}


# ---------------------------------------------------------------------------
# Collect all forms for non-lemma page creation
# ---------------------------------------------------------------------------

PERSON_NAMES = {"first", "second", "third", "fourth"}


def collect_all_forms(entry: dict) -> list[tuple[str, str]]:
    """Gather ALL generated forms for an entry (inflections + agreement + cases).

    Returns a list of (label, surface_form) tuples.
    """
    wc = entry["word_class"]
    if not entry.get("entry"):
        return []

    forms = []
    if wc == "noun":
        forms.extend(generate_noun_forms(entry))
        forms.extend(generate_noun_case_forms(entry))
    elif wc == "verb_transitive":
        forms.extend(generate_transitive_forms(entry))
        forms.extend(generate_transitive_subject_agreement(entry))
        forms.extend(generate_transitive_object_agreement(entry))
    elif wc == "verb_active":
        forms.extend(generate_active_forms(entry))
        forms.extend(generate_active_agreement(entry))
    elif wc == "verb_stative":
        forms.extend(generate_stative_forms(entry))
        forms.extend(generate_stative_agreement(entry))
    elif wc == "adjective":
        forms.extend(generate_adjective_forms(entry))
        forms.extend(generate_adjective_agreement(entry))
    elif wc == "adverb":
        forms.extend(generate_adverb_forms(entry))
    return forms


def readable_label(label: str) -> str:
    """Convert dot-separated labels into readable text.

    e.g. 'child.collective.first' -> 'Child collective first person'
    Appends 'person' when the last segment is a person name.
    """
    parts = label.replace("_", " ").split(".")
    text = " ".join(parts)
    if parts and parts[-1] in PERSON_NAMES:
        text += " person"
    return text.capitalize()


def create_form_pages(site, entry: dict, run_tag_suffix: str, log_file: str) -> int:
    """Create non-lemma wiki pages for each unique surface form of an entry.

    Returns the count of pages created/updated.
    """
    all_forms = collect_all_forms(entry)
    if not all_forms:
        return 0

    lemma_title = page_title_for(entry)
    # Extract display name from the title (after "word:")
    lemma_display = lemma_title.split(":", 1)[1] if ":" in lemma_title else lemma_title
    citation = entry["citation_form"]

    # Deduplicate: keep first label seen for each surface form
    seen: dict[str, str] = {}  # surface_form -> label
    for label, surface in all_forms:
        if surface.startswith("ERROR"):
            continue
        if surface == citation:
            continue
        if surface not in seen:
            seen[surface] = label

    count = 0
    for surface, label in seen.items():
        form_title = f"word:{surface}"
        readable = readable_label(label)
        content = f"{readable} form of [[{lemma_title}|{lemma_display}]]\n\n[[Category:Non-lemmas]]"

        try:
            page = site.pages[form_title]
            saved = safe_save(page, content,
                              summary=f"Bot: non-lemma form page for \"{lemma_display}\"{run_tag_suffix}")
            if saved:
                count += 1
        except Exception as e:
            print(f"    FORM ERROR [[{form_title}]]: {e}", flush=True)
            append_log(log_file, {
                "key": surface, "lemma": citation, "title": form_title,
                "status": "form_error", "error": str(e),
            })

    return count


def verb_root_title(root_str: str) -> str:
    """Return the √C1-C2-C3 citation form for a verb root string."""
    return f"√{root_str}"


def page_title_for(entry: dict) -> str:
    """Return the word:... page title for a lexicon entry.

    Verbs use √C1-C2-C3 form; all other word classes use the citation form.
    """
    if entry["word_class"] in VERB_CLASSES:
        return f"word:{verb_root_title(entry['root_str'])}"
    return f"word:{entry['citation_form']}"


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
# Wikitext linking helpers (v6)
# ---------------------------------------------------------------------------

LINKABLE_TERMS = {
    # Degrees
    "positive", "comparative", "superlative", "negative",
    # Evidentials & moods
    "visual", "hearsay", "inferential", "optative", "hodiernal",
    "mythical", "mythic", "auditory", "deliberative",
    "intention", "intentional",
    # Tense / day prefixes
    "present", "past", "future", "hesternal", "crastinal",
    # Aspects / templates
    "telic", "atelic", "perfect", "imperfect",
    "habitual", "gnomic", "imperative",
    # Voice / type
    "active", "stative",
    # Stative prefixes
    "probable", "inchoative", "cessative", "resumptive",
    "repetitive", "cess", "almost", "continuous",
    # Gender
    "child", "female", "male", "inanimate",
    # Number
    "singular", "plural", "collective", "zero", "paucal", "plentiful",
    # Person
    "first", "second", "third", "fourth",
    # Cases
    "agent", "patient", "possessive", "instrumental", "dative", "speaker",
    # Form types
    "non-lemmas",
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
    return f"[[Wikt:{core}|{core}]]{suffix}"


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
    """Generate full wikitext for a word:LEMMA page."""
    wc = entry["word_class"]
    wc_info = WORD_CLASS_INFO.get(wc, {})
    wc_link = wc_info.get("link", wc)
    category = wc_info.get("category", "Aelaki vocabulary")

    lemma = entry["citation_form"]
    root_str = entry["root_str"]
    gloss = entry["gloss"]

    # Verbs use √C1-C2-C3 as their page heading
    is_verb = wc in VERB_CLASSES
    display_name = verb_root_title(root_str) if is_verb else lemma

    sections = []

    # Lead
    if is_verb:
        lead = f"'''{display_name}''' ('''{lemma}''') is an [[Aelaki]] {wc_link} meaning \"{wikt_gloss(gloss)}\"."
    else:
        lead = f"'''{display_name}''' is an [[Aelaki]] {wc_link} meaning \"{wikt_gloss(gloss)}\"."
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
    if is_verb:
        overview.append(f"|-\n! Citation form\n| {display_name}")
        overview.append(f"|-\n! Lemma\n| {lemma}")
    elif lemma != key:
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
    if wc == "noun" and entry.get("gender"):
        sections.append(f"[[Category:Aelaki {entry['gender'].value} nouns]]")
    if wc.startswith("verb_"):
        verb_type = wc.split("_", 1)[1]
        sections.append(f"[[Category:Aelaki {verb_type} verbs]]")
    sections.append("[[Category:Aelaki vocabulary]]")
    sections.append("[[Category:Aelaki lemmas]]")
    sections.append("[[Category:Word pages]]")

    # Version footer
    sections.append("{{wordpage|" + PAGE_VERSION + "}}")

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Upgrade old versions
# ---------------------------------------------------------------------------

def load_version_history(path: str) -> list[str]:
    """Load the ordered list of version category names."""
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


def ensure_current_version(path: str) -> list[str]:
    """Append PAGE_VERSION to version_history.txt if not already present.

    Returns the full ordered list of category names.
    """
    versions = load_version_history(path)
    cat_name = f"Words {PAGE_VERSION}"
    if cat_name not in versions:
        versions.append(cat_name)
        with open(path, "a") as f:
            f.write(cat_name + "\n")
        print(f"  Registered new version category: [[Category:{cat_name}]]", flush=True)
    return versions


def upgrade_old_versions(site, lexicon, limit, run_tag_suffix, log_file,
                         version_history_file):
    """Upgrade word pages from older version categories in order.

    Reads version_history.txt for the ordered list of categories, then
    walks each one (oldest first) except the current commit's category,
    upgrading pages until the limit is reached.
    """
    versions = ensure_current_version(version_history_file)
    current_cat_name = f"Words {PAGE_VERSION}"
    total_upgraded = 0

    for cat_name in versions:
        if cat_name == current_cat_name:
            continue
        if total_upgraded >= limit:
            break

        print(f"\nChecking [[Category:{cat_name}]]...", flush=True)
        cat = site.categories[cat_name]
        upgraded_this_cat = 0

        for page in cat:
            if total_upgraded >= limit:
                print(f"  Reached upgrade limit of {limit}.", flush=True)
                break
            if not page.name.lower().startswith("word:"):
                continue

            lemma = page.name.split(":", 1)[1]  # strip namespace prefix
            entry = None
            for k, e in lexicon.items():
                if e["citation_form"] == lemma:
                    entry = e
                    key = k
                    break
                # Also match by √root form (already-migrated verb pages)
                if e["word_class"] in VERB_CLASSES and verb_root_title(e["root_str"]) == lemma:
                    entry = e
                    key = k
                    break
            if not entry:
                print(f"  SKIP upgrade (no lexicon match): [[{page.name}]]", flush=True)
                continue

            new_title = page_title_for(entry)
            new_text = generate_word_page(key, entry)

            # If this is a verb page at the old citation-form title, move it
            if entry["word_class"] in VERB_CLASSES and page.name != new_title:
                try:
                    moved = move_page(site, page.name, new_title,
                                      reason=f"Bot: rename verb to root citation form {PAGE_VERSION}{run_tag_suffix}")
                    if moved:
                        print(f"  MOVED: [[{page.name}]] -> [[{new_title}]]", flush=True)
                    else:
                        print(f"  SKIP move (target exists or source missing): [[{page.name}]] -> [[{new_title}]]", flush=True)
                except Exception as e:
                    print(f"  ERROR moving [[{page.name}]]: {e}", flush=True)
                    append_log(log_file, {
                        "key": key, "lemma": lemma, "title": page.name,
                        "status": "move_error", "error": str(e),
                    })
                    continue
                # Update the moved page with new content
                page = site.pages[new_title]

            try:
                saved = safe_save(page, new_text,
                                  summary=f"Bot: upgrade word page to {PAGE_VERSION}{run_tag_suffix}")
                if saved:
                    print(f"  UPGRADED: [[{page.name}]] {cat_name} -> {current_cat_name}", flush=True)
                    upgraded_this_cat += 1
                    total_upgraded += 1
                    append_log(log_file, {
                        "key": key, "lemma": lemma, "title": page.name,
                        "status": "upgraded", "from": cat_name, "to": PAGE_VERSION,
                    })
                    # Create non-lemma form pages
                    form_count = create_form_pages(site, entry, run_tag_suffix, log_file)
                    if form_count:
                        print(f"    +{form_count} form pages", flush=True)
                else:
                    print(f"  SKIP (no change): [[{page.name}]]", flush=True)
            except Exception as e:
                print(f"  ERROR upgrading [[{page.name}]]: {e}", flush=True)
                append_log(log_file, {
                    "key": key, "lemma": lemma, "title": page.name,
                    "status": "upgrade_error", "error": str(e),
                })

        print(f"  {cat_name}: upgraded {upgraded_this_cat} pages.", flush=True)

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
    parser.add_argument("--version-history", default=DEFAULT_VERSION_HISTORY,
                        help="Ordered list of version category names.")
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

    # Register current commit in version history (even in dry-run)
    ensure_current_version(args.version_history)

    # --- Phase 1: Upgrade old pages to current commit ---
    if args.apply:
        print(f"\n--- Phase 1: Upgrade old pages to {PAGE_VERSION} (up to {args.limit}) ---", flush=True)
        upgraded = upgrade_old_versions(site, lexicon, args.limit, run_tag_suffix,
                                       args.log_file, args.version_history)
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
        title = page_title_for(entry)
        wikitext = generate_word_page(key, entry)

        if not args.apply:
            print(f"\n{'=' * 60}")
            print(f"WOULD CREATE: [[{title}]]")
            print(f"{'=' * 60}")
            print(wikitext[:800])
            if len(wikitext) > 800:
                print(f"  ... ({len(wikitext)} chars total)")
            # Preview form page count
            all_forms = collect_all_forms(entry)
            citation = entry["citation_form"]
            unique = {s for _, s in all_forms if not s.startswith("ERROR") and s != citation}
            print(f"  Would create {len(unique)} non-lemma form pages")
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
                    # Create non-lemma form pages
                    form_count = create_form_pages(site, entry, run_tag_suffix, args.log_file)
                    if form_count:
                        print(f"    +{form_count} form pages", flush=True)
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
