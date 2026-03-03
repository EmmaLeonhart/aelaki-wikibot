"""Aelaki numeral system.

Mixed base-12 (dozenal) and base-60 (sexagesimal) number system with
six semantic roles: cardinal, ordinal, partitive, fractional, collective,
and adverbial.

Gender agreement: even numbers = female, odd (except 1) = male,
1/10/powers of 10 = child. Fractions always child gender.
"""

from __future__ import annotations

from .gender import Gender
from .phonology import apply_collective_shift

# ---------------------------------------------------------------------------
# Base-12 cardinal names
# ---------------------------------------------------------------------------

UNITS_12: list[str] = [
    "",       # 0 placeholder
    "Pan",    # 1
    "Bal",    # 2
    "Bhan",   # 3
    "Mal",    # 4
    "Tan",    # 5
    "Dal",    # 6
    "Dhan",   # 7
    "Nal",    # 8
    "Kan",    # 9
    "Gal",    # 10
    "Ghan",   # 11
    "Nger",   # 12 (dozen marker)
]

# ---------------------------------------------------------------------------
# Ordinal names (1-12)
# ---------------------------------------------------------------------------

ORDINALS_12: list[str] = [
    "",         # 0
    "Sekon",    # 1st
    "Kezon",    # 2nd
    "Bhalon",   # 3rd
    "Malon",    # 4th
    "Talon",    # 5th
    "Dalon",    # 6th
    "Dhanon",   # 7th
    "Nalon",    # 8th
    "Kanon",    # 9th
    "Galon",    # 10th
    "Ghanon",   # 11th
    "Ngeron",   # 12th
]

# ---------------------------------------------------------------------------
# Partitive names (1-12, hardcoded reduplications)
# ---------------------------------------------------------------------------

PARTITIVES_12: list[str] = [
    "",           # 0
    "Papan",      # 1 (one of)
    "Babal",      # 2
    "Bhabhan",    # 3
    "Mamal",      # 4
    "Tatan",      # 5
    "Dadal",      # 6
    "Dhadhan",    # 7
    "Nanal",      # 8
    "Kakan",      # 9
    "Gagal",      # 10
    "Ghaghan",    # 11
    "Ngenger",    # 12
]

# ---------------------------------------------------------------------------
# Special fractional unit names
# ---------------------------------------------------------------------------

SPECIAL_FRACTIONALS: dict[int, str] = {
    1: "Golo",       # whole
    2: "Kalakel",    # half
    3: "Bhavel",     # third
}

# ---------------------------------------------------------------------------
# Inherent gender of numbers
# ---------------------------------------------------------------------------

def number_gender(n: int) -> Gender:
    """Return the inherent gender of a number.

    Even = female, odd (except 1) = male, 1/10/powers of 10 = child.
    """
    if n <= 0:
        return Gender.FEMALE  # Fol (zero) is feminine
    if n == 1 or n == 10:
        return Gender.CHILD
    if n % 2 == 0:
        return Gender.FEMALE
    return Gender.MALE


# ===========================================================================
# Cardinal numbers
# ===========================================================================

def cardinal(n: int) -> str:
    """Generate cardinal number name.

    Base-12 for 1-59, base-60 with Vibhi for 60+.
    """
    if n <= 0:
        return str(n)
    if n == 60:
        return "Vibhi"
    if n <= 12:
        return UNITS_12[n]
    if n < 60:
        dozens = n // 12
        remainder = n % 12
        if dozens == 1:
            head = UNITS_12[12]  # "Nger"
        else:
            head = UNITS_12[dozens] + UNITS_12[12]
        if remainder == 0:
            return head
        return head + UNITS_12[remainder]
    # n > 60: mixed base-60
    sixty_count = n // 60
    rest = n % 60
    head = ("" if sixty_count == 1 else cardinal(sixty_count)) + "Vibhi"
    if rest == 0:
        return head
    return head + cardinal(rest)


def cardinal_gendered(n: int, gender: Gender) -> str:
    """Generate gender-marked cardinal number.

    Masculine is the baseline. Female replaces a->o, e->o.
    Child replaces a->u, e->ue.
    """
    base = cardinal(n)
    if gender == Gender.MALE:
        return base

    result: list[str] = []
    for ch in base:
        low = ch.lower()
        if gender == Gender.FEMALE:
            if low == "a":
                result.append("o" if ch.islower() else "O")
            elif low == "e":
                result.append("o" if ch.islower() else "O")
            else:
                result.append(ch)
        elif gender == Gender.CHILD:
            if low == "a":
                result.append("u" if ch.islower() else "U")
            elif low == "e":
                result.append("ü" if ch.islower() else "Ü")
            else:
                result.append(ch)
        else:
            result.append(ch)
    return "".join(result)


# ===========================================================================
# Ordinal numbers
# ===========================================================================

def ordinal(n: int) -> str:
    """Generate ordinal number name (1st, 2nd, ...)."""
    if n <= 0:
        return str(n)
    if n == 60:
        return "Vibhisekon"
    if n <= 12:
        return ORDINALS_12[n]
    if n < 60:
        dozens = n // 12
        remainder = n % 12
        if dozens == 1:
            head = UNITS_12[12]
        else:
            head = UNITS_12[dozens] + UNITS_12[12]
        if remainder == 0:
            return head + "on"  # Add ordinal ending
        return head + ORDINALS_12[remainder]
    # n > 60
    sixty_count = n // 60
    rest = n % 60
    head = ("" if sixty_count == 1 else ordinal(sixty_count)) + "Vibhi"
    if rest == 0:
        return head
    return head + ordinal(rest)


# ===========================================================================
# Partitive numbers (subset: "two of them", "three of them")
# ===========================================================================

def partitive(n: int) -> str:
    """Generate partitive number name."""
    if n <= 0:
        return str(n)
    if n == 60:
        return "Vibhibhi"
    if n <= 12:
        return PARTITIVES_12[n]
    if n < 60:
        dozens = n // 12
        remainder = n % 12
        if remainder == 0:
            return UNITS_12[dozens] + "Ngenger"
        if dozens == 1:
            prefix = "Nger"
        else:
            prefix = UNITS_12[dozens] + "Nger"
        return prefix + PARTITIVES_12[remainder]
    # n > 60
    sixty_count = n // 60
    rest = n % 60
    head = ("" if sixty_count == 1 else partitive(sixty_count)) + "Vibhi"
    if rest == 0:
        return head
    return head + partitive(rest)


# ===========================================================================
# Fractional unit names (denominator of fraction: "half", "third", etc.)
# ===========================================================================

def fractional_unit(n: int) -> str:
    """Generate fractional unit name (the denominator label)."""
    if n in SPECIAL_FRACTIONALS:
        return SPECIAL_FRACTIONALS[n]
    return cardinal(n) + "fel"


def fraction(numerator: int, denominator: int) -> str:
    """Generate a fraction: partitive(num) + fractional_unit(denom).

    Example: 3/4 -> "Bhabhan Malfel" (three-of fourths)
    """
    return f"{partitive(numerator)} {fractional_unit(denominator)}"


# ===========================================================================
# Collective numbers ("both", "all three", etc.)
# ===========================================================================

def collective(n: int) -> str:
    """Generate collective number name (umlaut/collective shift of cardinal)."""
    base = cardinal(n)
    return apply_collective_shift(base)


# ===========================================================================
# Adverbial numbers ("once", "twice", "30 times")
# ===========================================================================

def adverbial(n: int) -> str:
    """Generate adverbial number name: cardinal + 'te'."""
    return cardinal(n) + "te"


# ===========================================================================
# Negative numerals (insert /f/ before C2)
# ===========================================================================

def negative_cardinal(n: int) -> str:
    """Generate negative cardinal: insert /f/ in cardinal form.

    Semantics: absent, owed, removed.
    """
    base = cardinal(abs(n))
    # Find first vowel-consonant boundary after initial consonant
    # Simple approach: insert 'f' after second character for basic forms
    if len(base) >= 3:
        # Insert f before the second consonant cluster
        # For simple forms like "Mal" -> "Mafal", "Bal" -> "Bafal"
        return base[0:2] + "f" + base[2:]
    return base + "f"


# ===========================================================================
# All six roles for a number
# ===========================================================================

def all_roles(n: int) -> dict[str, str]:
    """Generate all six semantic roles for a number."""
    return {
        "cardinal": cardinal(n),
        "ordinal": ordinal(n),
        "partitive": partitive(n),
        "fractional": fractional_unit(n),
        "collective": collective(n),
        "adverbial": adverbial(n),
    }
