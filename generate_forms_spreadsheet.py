"""Generate all Aelaki word forms into a CSV spreadsheet.

Iterates over every root in the lexicon and generates morphological forms
using the existing generation modules. Incomplete roots (containing '?')
are still included — the '?' will appear literally in the output.

Output: aelaki_forms.csv
"""

import csv
import sys

from aelaki.lexicon import VERBS, NOUNS, ADJECTIVES, ADVERBS, WordClass
from aelaki.gender import Gender, Number, Person
from aelaki.roots import TriRoot, TetraRoot
from aelaki.nouns import build_noun
from aelaki.verbs import (
    conjugate_transitive, conjugate_intransitive_active,
    conjugate_intransitive_stative,
    StemTemplate, Evidential, DayPrefix,
)
from aelaki.stative_verbs import stative_paradigm
from aelaki.adjectives import realize_adjective, AdjDegree, AdjEvidential
from aelaki.adverbs import realize_adverb, AdverbDegree, AdverbTense
from aelaki.numerals import all_roles, negative_cardinal

# ── Representative subsets for verbs ──────────────────────────────────────

REPR_TEMPLATES = [
    StemTemplate.TELIC_PERFECT,
    StemTemplate.ATELIC_IMPERFECT,
    StemTemplate.IMPERATIVE,
]

REPR_EVIDENTIALS = [
    Evidential.NONE,
    Evidential.PAST_VISUAL,
    Evidential.HEARSAY,
    Evidential.INFERENTIAL,
    Evidential.INTENTION,
]

# Canonical citation form: 3rd male singular subject, 4th female singular object
SUBJ = (Person.THIRD, Gender.MALE, Number.SINGULAR)
OBJ = (Person.FOURTH, Gender.FEMALE, Number.SINGULAR)

# ── Key numbers for numeral paradigm ──────────────────────────────────────

KEY_NUMBERS = list(range(1, 13)) + [13, 20, 24, 36, 48, 59, 60, 120]

# ── CSV output ────────────────────────────────────────────────────────────

OUTPUT = "aelaki_forms.csv"
COLUMNS = ["key", "gloss", "word_class", "root", "form_label", "surface_form"]


def root_str(root):
    """Human-readable root consonants."""
    return "-".join(root.consonants)


def generate_noun_rows(key, entry):
    """Generate noun forms: all genders × numbers × persons, or inherent gender only."""
    rows = []
    genders = [entry.inherent_gender] if entry.inherent_gender else list(Gender)
    for g in genders:
        for n in Number:
            for p in Person:
                label = f"{g.value}.{n.value}.{p.name.lower()}"
                try:
                    form = build_noun(entry.root, g, n, p)
                except Exception as e:
                    form = f"ERROR: {e}"
                rows.append((key, entry.gloss, "noun", root_str(entry.root),
                             label, form))
    return rows


def generate_transitive_rows(key, entry):
    """Generate representative transitive verb forms."""
    rows = []
    root = entry.root
    for tmpl in REPR_TEMPLATES:
        for evid in REPR_EVIDENTIALS:
            label = f"{tmpl.name.lower()}.{evid.name.lower()}"
            try:
                form = conjugate_transitive(
                    root, tmpl, evid, DayPrefix.NONE,
                    *SUBJ, *OBJ,
                )
            except Exception as e:
                form = f"ERROR: {e}"
            rows.append((key, entry.gloss, "verb_transitive",
                         root_str(root), label, form))
    return rows


def generate_active_rows(key, entry):
    """Generate representative active intransitive verb forms."""
    rows = []
    root = entry.root
    for evid in REPR_EVIDENTIALS:
        label = f"active.{evid.name.lower()}"
        try:
            form = conjugate_intransitive_active(
                root, "a", "a", evid, DayPrefix.NONE, *SUBJ,
            )
        except Exception as e:
            form = f"ERROR: {e}"
        rows.append((key, entry.gloss, "verb_active",
                     root_str(root), label, form))
    return rows


def generate_stative_rows(key, entry):
    """Generate stative verb forms: basic conjugation + full prefix paradigm."""
    rows = []
    root = entry.root

    # Basic conjugation with representative evidentials
    for evid in REPR_EVIDENTIALS:
        label = f"stative.{evid.name.lower()}"
        try:
            form = conjugate_intransitive_stative(
                root, "a", "a", evid, DayPrefix.NONE, *SUBJ,
            )
        except Exception as e:
            form = f"ERROR: {e}"
        rows.append((key, entry.gloss, "verb_stative",
                     root_str(root), label, form))

    # Full stative prefix paradigm (32 forms)
    base_stem = f"{root.c1}a{root.c2}a{root.c3}"
    try:
        paradigm = stative_paradigm(base_stem)
        for form_name, form in paradigm.items():
            label = f"stative_prefix.{form_name}"
            rows.append((key, entry.gloss, "verb_stative",
                         root_str(root), label, form))
    except Exception as e:
        rows.append((key, entry.gloss, "verb_stative",
                     root_str(root), "stative_prefix.ERROR", f"ERROR: {e}"))

    return rows


def generate_adjective_rows(key, entry):
    """Generate adjective forms: 4 degrees × 1 evidential × 1 agreement."""
    rows = []
    root = entry.root
    for deg in AdjDegree:
        label = f"{deg.name.lower()}"
        try:
            form = realize_adjective(
                root, Person.THIRD, Gender.MALE, Number.SINGULAR,
                deg, AdjEvidential.NONE,
            )
        except Exception as e:
            form = f"ERROR: {e}"
        rows.append((key, entry.gloss, "adjective",
                     root_str(root), label, form))
    return rows


def generate_adverb_rows(key, entry):
    """Generate adverb forms: 4 degrees × all 20 tenses = 80 forms."""
    rows = []
    root = entry.root
    for deg in AdverbDegree:
        for tense in AdverbTense:
            label = f"{deg.name.lower()}.{tense.name.lower()}"
            try:
                form = realize_adverb(root, "a", "a", deg, tense)
            except Exception as e:
                form = f"ERROR: {e}"
            rows.append((key, entry.gloss, "adverb",
                         root_str(root), label, form))
    return rows


def generate_numeral_rows():
    """Generate numeral forms: key numbers × 7 roles."""
    rows = []
    for n in KEY_NUMBERS:
        # 6 standard roles
        try:
            roles = all_roles(n)
            for role_name, form in roles.items():
                rows.append((str(n), f"number {n}", "numeral", str(n),
                             role_name, form))
        except Exception as e:
            rows.append((str(n), f"number {n}", "numeral", str(n),
                         "ERROR", f"ERROR: {e}"))
        # 7th role: negative cardinal
        try:
            form = negative_cardinal(n)
            rows.append((str(n), f"number {n}", "numeral", str(n),
                         "negative_cardinal", form))
        except Exception as e:
            rows.append((str(n), f"number {n}", "numeral", str(n),
                         "negative_cardinal", f"ERROR: {e}"))
    return rows


def main():
    all_rows = []

    # ── Nouns ──
    for key, entry in NOUNS.items():
        all_rows.extend(generate_noun_rows(key, entry))

    # ── Verbs ──
    for key, entry in VERBS.items():
        if entry.word_class == WordClass.VERB_TRANSITIVE:
            all_rows.extend(generate_transitive_rows(key, entry))
        elif entry.word_class == WordClass.VERB_ACTIVE:
            all_rows.extend(generate_active_rows(key, entry))
        elif entry.word_class == WordClass.VERB_STATIVE:
            all_rows.extend(generate_stative_rows(key, entry))

    # ── Adjectives ──
    for key, entry in ADJECTIVES.items():
        all_rows.extend(generate_adjective_rows(key, entry))

    # ── Adverbs ──
    for key, entry in ADVERBS.items():
        all_rows.extend(generate_adverb_rows(key, entry))

    # ── Numerals ──
    all_rows.extend(generate_numeral_rows())

    # ── Write CSV ──
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        writer.writerows(all_rows)

    print(f"Wrote {len(all_rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
