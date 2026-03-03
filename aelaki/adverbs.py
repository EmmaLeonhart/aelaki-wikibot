"""Adverb morphology for Aelaki.

Adverbs are formed with ROOT + -te and must agree with the tense of
the verb they modify. They support four stem alternations for degree
and a tense-evidential agreement system.
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass

from .roots import TriRoot
from .phonology import apply_umlaut


class AdverbDegree(Enum):
    """Adverb degree (stem alternation)."""
    POSITIVE = "positive"
    COMPARATIVE = "comparative"     # C2 reduplication
    SUPERLATIVE = "superlative"     # Umlaut
    NEGATIVE = "negative"           # Zero-infix


class AdverbTense(Enum):
    """Tense-evidential combinations for adverbs.

    Each value is (day_prefix, suffix_after_te).
    """
    # Present (unmarked)
    PRESENT =                    ("",     "te")

    # Mythic past
    MYTHIC =                     ("",     "tesher")
    MYTHIC_INFERENTIAL =         ("",     "tesherëm")

    # Past
    PAST_AUDITORY =              ("",     "tero")
    PAST_VISUAL =                ("",     "teshë")
    PAST_INFERENTIAL =           ("",     "teshëm")

    # Hesternal (yesterday)
    HESTERNAL_AUDITORY =         ("goki", "tero")
    HESTERNAL_VISUAL =           ("goki", "teshë")
    HESTERNAL_INFERENTIAL =      ("goki", "teshëm")

    # Hodiernal (today) — with -nk- sandhi
    HODIERNAL_AUDITORY =         ("go",   "nkerom")
    HODIERNAL_VISUAL =           ("go",   "nkeshë")
    HODIERNAL_INFERENTIAL =      ("go",   "nkeshëm")
    HODIERNAL_INTENTIONAL =      ("go",   "nkeya")

    # Future
    FUTURE_AUDITORY =            ("",     "terom")
    FUTURE_INFERENTIAL =         ("",     "temu")
    FUTURE_INTENTIONAL =         ("",     "teya")

    # Crastinal (tomorrow)
    CRASTINAL_AUDITORY =         ("goki", "terom")
    CRASTINAL_INFERENTIAL =      ("goki", "temu")
    CRASTINAL_INTENTIONAL =      ("goki", "teya")

    def __init__(self, day_prefix: str, suffix: str):
        self.day_prefix = day_prefix
        self.adv_suffix = suffix


def build_adverb_stem(root: TriRoot, v1: str, v2: str,
                      degree: AdverbDegree = AdverbDegree.POSITIVE) -> str:
    """Build the adverb stem for given degree.

    Positive: C1V1C2V2 (root without C3, as base for -te suffix)
    Comparative: C1V1C2V2C2V2 (reduplicate C2V2)
    Superlative: umlaut all vowels
    Negative: C1V1fC2V2f (insert /f/)
    """
    if degree == AdverbDegree.POSITIVE:
        return f"{root.c1}{v1}{root.c2}{v2}"
    elif degree == AdverbDegree.COMPARATIVE:
        return f"{root.c1}{v1}{root.c2}{v2}{root.c2}{v2}"
    elif degree == AdverbDegree.SUPERLATIVE:
        base = f"{root.c1}{v1}{root.c2}{v2}"
        return apply_umlaut(base)
    elif degree == AdverbDegree.NEGATIVE:
        return f"{root.c1}{v1}f{root.c2}{v2}f"
    raise ValueError(f"Unknown degree: {degree}")


def realize_adverb(
    root: TriRoot,
    v1: str = "a",
    v2: str = "a",
    degree: AdverbDegree = AdverbDegree.POSITIVE,
    tense: AdverbTense = AdverbTense.PRESENT,
) -> str:
    """Realize a full adverb form with tense agreement.

    Template: [day_prefix] + stem + suffix
    """
    stem = build_adverb_stem(root, v1, v2, degree)
    return tense.day_prefix + stem + tense.adv_suffix
