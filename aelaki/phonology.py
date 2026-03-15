"""Phonological inventory and sound rules for Aelaki.

Contains vowel/consonant inventories, vowel shift mappings, collective vowel
shifts, zero-infix rules, and sandhi processes.
"""

# ---------------------------------------------------------------------------
# Vowel inventory
# ---------------------------------------------------------------------------
#
# Aelaki vowels are organized in a back/front grid. The collective form
# shifts back (left column) vowels to their front (right column) counterparts.
#
#   Back  Front
#    u      i      high:      /u/  /i/
#    ü      ï      near-high: /ʊ/  /ɪ/
#    o      e      mid:       /o/  /e/
#    a      æ      low:       /ɑ/  /æ/
#
# ə (schwa) appears in grammatical affixes (verb TAM prefixes, converbs)
# but does not participate in the vowel grid.

VOWELS = {"a", "e", "i", "o", "u", "æ", "ü", "ï", "ə", "ë", "ïf"}

# Back-to-front vowel shift — used on verbs, adjectives, adverbs (umlaut),
# and on nouns and numbers (collective). Same phonological process applied
# in different grammatical contexts.
VOWEL_SHIFT_MAP: dict[str, str] = {
    "u": "i",
    "ü": "ï",
    "o": "e",
    "a": "æ",
    "ə": "æ",
    # Front vowels are unchanged
    "i": "i",
    "ï": "ï",
    "e": "e",
    "æ": "æ",
}

# Legacy aliases — both use the same back-to-front shift
UMLAUT_MAP = VOWEL_SHIFT_MAP
COLLECTIVE_MAP = VOWEL_SHIFT_MAP

# ---------------------------------------------------------------------------
# Gender vowel slots
# ---------------------------------------------------------------------------

# (singular_vowel, collective_vowel)
GENDER_VOWELS: dict[str, tuple[str, str]] = {
    "child":     ("u", "i"),
    "female":    ("o", "e"),
    "male":      ("a", "æ"),
    "inanimate": ("ïf", "ïf"),
}

# ---------------------------------------------------------------------------
# Person consonants
# ---------------------------------------------------------------------------

PERSON_CONSONANTS: dict[int, str] = {
    1: "th",
    2: "j",
    3: "sh",
    4: "k",
}

# Person suffixes (non-genitive; 4th person is unmarked)
PERSON_SUFFIXES: dict[int, str] = {
    1: "th",
    2: "j",
    3: "sh",
    4: "",
}

# ---------------------------------------------------------------------------
# Consonant inventory (for validation)
# ---------------------------------------------------------------------------

CONSONANTS = {
    # Stops
    "p", "b", "t", "d", "k", "g",
    # Affricates
    "ch", "j",
    # Fricatives
    "f", "v", "s", "z", "sh", "zh", "th", "dh", "h",
    # Nasals
    "m", "n", "ng",
    # Liquids & glides
    "l", "r", "w", "y",
}

# ---------------------------------------------------------------------------
# Sandhi rules
# ---------------------------------------------------------------------------

def hodiernal_sandhi(stem: str) -> str:
    """Insert -nk- before hodiernal TAM suffixes.

    Applied when hodiernal prefix go- is used and suffix follows.
    Example: zada -> zadank
    """
    return stem + "nk"


def apply_umlaut(text: str) -> str:
    """Apply back-to-front vowel shift to all vowels in text."""
    result: list[str] = []
    i = 0
    while i < len(text):
        # Check for two-char vowels first
        if i + 1 < len(text):
            digraph = text[i:i + 2]
            if digraph in UMLAUT_MAP:
                result.append(UMLAUT_MAP[digraph])
                i += 2
                continue
        ch = text[i]
        if ch in UMLAUT_MAP:
            result.append(UMLAUT_MAP[ch])
        else:
            result.append(ch)
        i += 1
    return "".join(result)


def apply_collective_shift(text: str) -> str:
    """Apply collective vowel shift to all vowels in text."""
    result: list[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in COLLECTIVE_MAP:
            result.append(COLLECTIVE_MAP[ch])
        else:
            result.append(ch)
        i += 1
    return "".join(result)


def apply_zero_suffix(vowel: str) -> str:
    """Add -f after a vowel for zero-number marking on nouns.

    If the vowel already ends in 'f' (e.g. inanimate 'ïf'), do not double it.
    """
    if vowel.endswith("f"):
        return vowel
    return vowel + "f"
