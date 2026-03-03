"""Adjective morphology for Aelaki.

Adjectives derive from stative verb stems and support:
- Agreement with head noun in gender, number, person
- 4 degrees: base, comparative (reduplication), superlative (umlaut), negative (zero-infix)
- Limited TAM: 8-way system (4 evidentials x 2 tenses: general + hodiernal)
- No goki- prefix allowed on adjectives
"""

from __future__ import annotations
from enum import Enum

from .gender import Gender, Number, Person, gender_vowel
from .phonology import PERSON_CONSONANTS, apply_umlaut
from .roots import TriRoot


class AdjDegree(Enum):
    """Adjective degree (comparative morphology)."""
    POSITIVE = "positive"
    COMPARATIVE = "comparative"   # Reduplication
    SUPERLATIVE = "superlative"   # Umlaut
    NEGATIVE = "negative"         # Zero-infix


class AdjEvidential(Enum):
    """Limited evidential system for adjectives (8-way)."""
    NONE = ("", "")                    # Neutral
    VISUAL = ("", "shë")              # Visually confirmed
    HEARSAY = ("", "ro")              # By testimony
    INFERENTIAL = ("", "mu")          # Inferred
    OPTATIVE = ("", "ya")             # Hopefully
    HODIERNAL_VISUAL = ("go", "shë")  # Currently (seen)
    HODIERNAL_HEARSAY = ("go", "ro")  # Currently (heard)
    HODIERNAL_INFERENTIAL = ("go", "mu")  # Currently (inferred)
    HODIERNAL_OPTATIVE = ("go", "ya")     # Currently (hoped)

    def __init__(self, prefix: str, suffix: str):
        self.day_prefix = prefix
        self.evid_suffix = suffix


def build_adjective_stem(root: TriRoot, degree: AdjDegree = AdjDegree.POSITIVE) -> str:
    """Build the adjective stem from a triconsonantal root.

    Base template: C1-o-C2-a-C3
    Comparative: C1-o-C2-a-C2-a-C3 (reduplication of C2-a)
    Superlative: front all vowels (umlaut)
    Negative: C1-o-C2-f-a-C3 (insert /f/)
    """
    if degree == AdjDegree.POSITIVE:
        return f"{root.c1}o{root.c2}a{root.c3}"
    elif degree == AdjDegree.COMPARATIVE:
        return f"{root.c1}o{root.c2}a{root.c2}a{root.c3}"
    elif degree == AdjDegree.SUPERLATIVE:
        base = f"{root.c1}o{root.c2}a{root.c3}"
        return apply_umlaut(base)
    elif degree == AdjDegree.NEGATIVE:
        return f"{root.c1}o{root.c2}fa{root.c3}"
    raise ValueError(f"Unknown degree: {degree}")


def realize_adjective(
    root: TriRoot,
    noun_person: Person,
    noun_gender: Gender,
    noun_number: Number,
    degree: AdjDegree = AdjDegree.POSITIVE,
    evidential: AdjEvidential = AdjEvidential.NONE,
) -> str:
    """Realize a full adjective form agreeing with its head noun.

    Template: [day-prefix] + stem + [evid-suffix] + GV + PC + GV

    Where GV = gender vowel and PC = person consonant.
    """
    stem = build_adjective_stem(root, degree)

    gv = gender_vowel(noun_gender, noun_number)
    pc = PERSON_CONSONANTS[noun_person.value]

    # Apply evidential
    day_prefix = evidential.day_prefix
    evid_suffix = evidential.evid_suffix

    # Apply hodiernal sandhi if needed
    if day_prefix == "go" and evid_suffix:
        stem = stem + "nk"

    if evid_suffix:
        stem = stem + evid_suffix

    # Agreement: GV + PersonConsonant + GV
    agreement = gv + pc + gv

    return day_prefix + stem + agreement
