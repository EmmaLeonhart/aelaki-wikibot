"""Known vocabulary roots for Aelaki.

This lexicon catalogs documented roots with their glosses, root type,
and inherent properties (gender for nouns, transitivity for verbs).

Sources: grammar guide, worldbuilding docs, C# implementation, Discord messages.

Data is stored in lexicon.json and loaded at import time.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .roots import TriRoot, TetraRoot
from .gender import Gender


class WordClass(Enum):
    NOUN = "noun"
    VERB_TRANSITIVE = "verb_transitive"
    VERB_ACTIVE = "verb_active"        # Intransitive active
    VERB_STATIVE = "verb_stative"      # Intransitive stative
    ADJECTIVE = "adjective"
    ADVERB = "adverb"


@dataclass(frozen=True)
class LexEntry:
    """A lexicon entry."""
    root: TriRoot | TetraRoot
    word_class: WordClass
    gloss: str
    inherent_gender: Gender | None = None  # For nouns
    citation_form: str = ""                # Known surface form
    old_citation_form: str = ""            # Previous citation form (for page move tracking)


# ===========================================================================
# Load from JSON
# ===========================================================================

_JSON_PATH = Path(__file__).parent / "lexicon.json"

_GENDER_MAP = {
    "male": Gender.MALE,
    "female": Gender.FEMALE,
    "child": Gender.CHILD,
    "inanimate": Gender.INANIMATE,
}


def _make_root(consonants: list[str]) -> TriRoot | TetraRoot:
    if len(consonants) == 4:
        return TetraRoot(*consonants)
    return TriRoot(*consonants)


def _load_entries(section: dict) -> dict[str, LexEntry]:
    entries = {}
    for key, data in section.items():
        entries[key] = LexEntry(
            root=_make_root(data["root"]),
            word_class=WordClass(data["class"]),
            gloss=data["gloss"],
            inherent_gender=_GENDER_MAP.get(data.get("gender", ""), None),
            citation_form=data.get("citation_form", ""),
            old_citation_form=data.get("old_citation_form", ""),
        )
    return entries


def _load_lexicon():
    with open(_JSON_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    verbs = _load_entries(raw["verbs"])
    nouns = _load_entries(raw["nouns"])
    adjectives = _load_entries(raw["adjectives"])
    adverbs = _load_entries(raw["adverbs"])
    colors = dict(raw["colors"])
    pseudopronouns = dict(raw["pseudopronouns"])
    numerals = dict(raw["numerals"])
    particles = dict(raw["particles"])

    return verbs, nouns, adjectives, adverbs, colors, pseudopronouns, numerals, particles


VERBS, NOUNS, ADJECTIVES, ADVERBS, COLORS, PSEUDOPRONOUNS, NUMERALS, PARTICLES = _load_lexicon()


# ===========================================================================
# Lookup
# ===========================================================================

def lookup(key: str) -> LexEntry | None:
    """Look up a lexicon entry by key."""
    for store in (VERBS, NOUNS, ADJECTIVES, ADVERBS):
        if key in store:
            return store[key]
    return None
