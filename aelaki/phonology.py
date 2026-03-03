"""Phonological inventory and sound rules for Aelaki.

Contains vowel/consonant inventories, umlaut mappings, collective vowel
shifts, zero-infix rules, and sandhi processes.
"""

# ---------------------------------------------------------------------------
# Vowel inventory
# ---------------------------------------------------------------------------

VOWELS = {"a", "e", "i", "o", "u", "ae", "oe", "ue",
          "ə", "æ", "ü", "ï", "ïf"}

# Phonological umlaut (fronting) — used on verbs, adjectives, adverbs
UMLAUT_MAP: dict[str, str] = {
    "a": "æ",
    "o": "œ",
    "u": "ü",
    "e": "e",   # already front
    "i": "i",   # already front
    "æ": "æ",
    "œ": "œ",
    "ü": "ü",
}

# Grammatical collective shift — used on nouns and numbers
COLLECTIVE_MAP: dict[str, str] = {
    "u": "i",
    "o": "e",
    "a": "æ",
    "ə": "æ",
    "ü": "ï",
}

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
    # Implosives
    "b'", "d'", "g'",
    # Affricates
    "pf", "bv", "ch", "dzh", "ggx",
    # Fricatives
    "f", "v", "s", "z", "sh", "zh", "x", "gx", "gh", "h",
    # Nasals
    "m", "n", "ng", "m'", "n'", "ngl'",
    # Clicks
    "p!", "t!", "k!",
    # Liquids & glides
    "l", "r", "w", "y",
    # Digraph consonants used in grammar
    "th", "dh", "nl'", "mb'", "nd'",
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
    """Apply phonological umlaut (fronting) to all vowels in text."""
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
    """Add -f after a vowel for zero-number marking on nouns."""
    return vowel + "f"
