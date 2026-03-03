"""Gender, Number, and Person enumerations for Aelaki."""

from enum import Enum


class Gender(Enum):
    CHILD = "child"
    FEMALE = "female"
    MALE = "male"
    INANIMATE = "inanimate"


class Number(Enum):
    SINGULAR = "singular"
    PLURAL = "plural"
    COLLECTIVE = "collective"
    ZERO = "zero"


class Person(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


# ---------------------------------------------------------------------------
# Gender-Number -> vowel mappings (used in Ki syllables and verb agreement)
# ---------------------------------------------------------------------------

def gender_vowel(gender: Gender, number: Number) -> str:
    """Return the gender-number vowel used in verb agreement and Ki clitics."""
    _map = {
        (Gender.CHILD, Number.SINGULAR):    "u",
        (Gender.CHILD, Number.PLURAL):      "u",
        (Gender.CHILD, Number.COLLECTIVE):  "i",
        (Gender.CHILD, Number.ZERO):        "uf",

        (Gender.FEMALE, Number.SINGULAR):   "o",
        (Gender.FEMALE, Number.PLURAL):     "o",
        (Gender.FEMALE, Number.COLLECTIVE): "e",
        (Gender.FEMALE, Number.ZERO):       "of",

        (Gender.MALE, Number.SINGULAR):     "a",
        (Gender.MALE, Number.PLURAL):       "a",
        (Gender.MALE, Number.COLLECTIVE):   "æ",
        (Gender.MALE, Number.ZERO):         "af",

        (Gender.INANIMATE, Number.SINGULAR): "ïf",
        (Gender.INANIMATE, Number.PLURAL):   "ïf",
        (Gender.INANIMATE, Number.COLLECTIVE): "ïf",
        (Gender.INANIMATE, Number.ZERO):     "ïf",
    }
    return _map[(gender, number)]


def singular_vowel(gender: Gender) -> str:
    """Return the singular gender vowel (the 'base' vowel for a gender)."""
    return {
        Gender.CHILD: "u",
        Gender.FEMALE: "o",
        Gender.MALE: "a",
        Gender.INANIMATE: "ïf",
    }[gender]


def collective_vowel(gender: Gender) -> str:
    """Return the collective gender vowel."""
    return {
        Gender.CHILD: "i",
        Gender.FEMALE: "e",
        Gender.MALE: "æ",
        Gender.INANIMATE: "ïf",
    }[gender]
