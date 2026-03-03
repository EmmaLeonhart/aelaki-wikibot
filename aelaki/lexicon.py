"""Known vocabulary roots for Aelaki.

This lexicon catalogs documented roots with their glosses, root type,
and inherent properties (gender for nouns, transitivity for verbs).

Sources: grammar guide, worldbuilding docs, C# implementation, Discord messages.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

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


# ===========================================================================
# Verb roots
# ===========================================================================

VERBS: dict[str, LexEntry] = {
    # Transitive (tetraconsonantal)
    "kmdr": LexEntry(TetraRoot("k", "m", "d", "r"), WordClass.VERB_TRANSITIVE, "worship, ritual"),

    # Active intransitive (triconsonantal)
    "bva": LexEntry(TriRoot("b", "v", "?"), WordClass.VERB_ACTIVE, "drink"),
    "upf": LexEntry(TriRoot("?", "p", "f"), WordClass.VERB_ACTIVE, "eat"),
    "bha": LexEntry(TriRoot("b", "h", "?"), WordClass.VERB_ACTIVE, "see"),
    "xaen": LexEntry(TriRoot("x", "?", "n"), WordClass.VERB_ACTIVE, "hunt"),
    "sae": LexEntry(TriRoot("s", "?", "?"), WordClass.VERB_ACTIVE, "walk"),
    "gho": LexEntry(TriRoot("g", "h", "?"), WordClass.VERB_ACTIVE, "live"),
    "aech": LexEntry(TriRoot("?", "ch", "?"), WordClass.VERB_ACTIVE, "swim"),

    # Stative intransitive
    "zoduk": LexEntry(TriRoot("z", "d", "k"), WordClass.VERB_STATIVE, "know"),
    "aed": LexEntry(TriRoot("?", "?", "d"), WordClass.VERB_STATIVE, "fear"),

    # Well-documented triconsonantal verbs with full root
    "dpz": LexEntry(TriRoot("d", "p", "z"), WordClass.VERB_ACTIVE, "shoot at"),
    "zhrn": LexEntry(TriRoot("zh", "r", "n"), WordClass.VERB_ACTIVE, "live"),

    # From Discord dictionary (2025-05-30 to 2025-06-05)
    "apafath": LexEntry(TriRoot("?", "p", "f"), WordClass.VERB_ACTIVE, "fall", citation_form="apafath"),
    "slodon": LexEntry(TriRoot("sl", "d", "n"), WordClass.VERB_ACTIVE, "shout", citation_form="slodon"),
    "kamamas": LexEntry(TriRoot("k", "m", "s"), WordClass.VERB_ACTIVE, "rise", citation_form="kamas"),

    # Stative verbs from Discord
    "dedik": LexEntry(TriRoot("d", "d", "k"), WordClass.VERB_STATIVE, "learn", citation_form="dedik"),
    "hedek": LexEntry(TriRoot("h", "d", "k"), WordClass.VERB_STATIVE, "become female", citation_form="hedek"),
    "dhum": LexEntry(TriRoot("dh", "?", "m"), WordClass.VERB_STATIVE, "shine, burn", citation_form="dhüm"),
    "bahag": LexEntry(TriRoot("b", "h", "g"), WordClass.VERB_STATIVE, "break", citation_form="bahag"),
}

# ===========================================================================
# Noun roots
# ===========================================================================

NOUNS: dict[str, LexEntry] = {
    # Body parts (inalienable)
    "ae": LexEntry(TriRoot("?", "?", "?"), WordClass.NOUN, "head"),
    "euf": LexEntry(TriRoot("?", "?", "f"), WordClass.NOUN, "eye"),
    "on": LexEntry(TriRoot("?", "?", "n"), WordClass.NOUN, "mouth"),
    "ich": LexEntry(TriRoot("?", "ch", "?"), WordClass.NOUN, "heart"),
    "uch": LexEntry(TriRoot("?", "ch", "?"), WordClass.NOUN, "liver"),

    # Natural world
    "debh": LexEntry(TriRoot("d", "b", "h"), WordClass.NOUN, "tree", Gender.FEMALE),
    "sugh": LexEntry(TriRoot("s", "g", "h"), WordClass.NOUN, "water", Gender.INANIMATE),
    "t'ub'": LexEntry(TriRoot("t'", "b'", "?"), WordClass.NOUN, "sun", Gender.INANIMATE),
    "pu": LexEntry(TriRoot("p", "?", "?"), WordClass.NOUN, "moon"),
    "lu": LexEntry(TriRoot("l", "?", "?"), WordClass.NOUN, "river", Gender.INANIMATE),
    "nek": LexEntry(TriRoot("n", "?", "k"), WordClass.NOUN, "sea", Gender.INANIMATE),

    # Animals
    "maomao": LexEntry(TriRoot("m", "?", "m"), WordClass.NOUN, "maomao (bear-sized companion)"),
    "dzhabho": LexEntry(TriRoot("dzh", "bh", "?"), WordClass.NOUN, "bird"),

    # Tetraconsonantal nouns
    "bsl": LexEntry(TriRoot("b", "s", "l"), WordClass.NOUN, "tree/goddess (feminine)"),

    # From Discord dictionary
    "zahal": LexEntry(TriRoot("z", "h", "l"), WordClass.NOUN, "edible plant", citation_form="zahal"),
    "saromo": LexEntry(TriRoot("s", "r", "m"), WordClass.NOUN, "sky", citation_form="saromo"),
    "gnk": LexEntry(TriRoot("g'", "n", "k"), WordClass.NOUN, "sky fungus", citation_form="g'nk"),
    "gar": LexEntry(TriRoot("g", "?", "r"), WordClass.NOUN, "body", citation_form="gar"),
}


# ===========================================================================
# Adjective roots
# ===========================================================================

ADJECTIVES: dict[str, LexEntry] = {
    "grn": LexEntry(TriRoot("g", "r", "n"), WordClass.ADJECTIVE, "bright"),
    "bsl_adj": LexEntry(TriRoot("b", "s", "l"), WordClass.ADJECTIVE, "stative adjective root"),

    # From Discord dictionary
    "bagadha": LexEntry(TriRoot("b", "g", "dh"), WordClass.ADJECTIVE, "bright", citation_form="bagadha"),
}


# ===========================================================================
# Adverb roots
# ===========================================================================

ADVERBS: dict[str, LexEntry] = {
    "zada": LexEntry(TriRoot("z", "d", "?"), WordClass.ADVERB, "long/lengthy"),
}


# ===========================================================================
# Color terms
# ===========================================================================

COLORS: dict[str, str] = {
    "red": "te",
    "green": "ihm",
    "yellow": "ihf",
    "white": "a",
    "black": "ŋix",
}


# ===========================================================================
# Pronoun/pseudopronoun inventory
# ===========================================================================

PSEUDOPRONOUNS: dict[str, str] = {
    "you_and_me": "Thijith",          # Child gender, exclusive (just us two)
    "us_few": "Thishith",             # Inclusive, paucal
    "us_many": "Thikith",             # Inclusive, plural
}


# ===========================================================================
# Lookup
# ===========================================================================

def lookup(key: str) -> LexEntry | None:
    """Look up a lexicon entry by key."""
    for store in (VERBS, NOUNS, ADJECTIVES, ADVERBS):
        if key in store:
            return store[key]
    return None
