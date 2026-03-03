"""Ki-syllable system and person agreement tables for Aelaki.

The Ki system provides ~50 clitics encoding person, gender, and number.
They attach to the right edge of predicates or focused constituents.
"""

from .gender import Gender, Number, Person, gender_vowel
from .phonology import PERSON_CONSONANTS, PERSON_SUFFIXES


# ---------------------------------------------------------------------------
# Ki-syllable generation
# ---------------------------------------------------------------------------

def ki_predicate_final(person: Person, gender: Gender, number: Number) -> str:
    """Generate predicate-final Ki syllable (free clitic position).

    Pattern: PersonConsonant + GenderVowel
    Plural: doubled (e.g., thu -> thuthu)
    Zero: uses base vowel form (strip trailing f for consonant part)
    """
    if gender == Gender.INANIMATE:
        if number == Number.PLURAL:
            return "ïfïf"
        return "ïf"

    cons = PERSON_CONSONANTS[person.value]
    gv = gender_vowel(gender, number)

    # For zero, the vowel already has 'f' suffix (e.g., "uf", "of", "af")
    # The Ki form uses the base vowel for the consonant part
    base_v = gv.rstrip("f") if gv.endswith("f") else gv

    syllable = cons + base_v

    if number == Number.PLURAL:
        return syllable + syllable
    return syllable


def ki_word_final(person: Person, gender: Gender, number: Number) -> str:
    """Generate word-final Ki suffix (bound morpheme position).

    Pattern: GenderVowel + PersonConsonant + GenderVowel
    Exceptions: 4th person singular/collective have no trailing consonant
    """
    if gender == Gender.INANIMATE:
        if number == Number.PLURAL:
            return "ïfïf"
        return "ïf"

    cons = PERSON_CONSONANTS[person.value]
    gv = gender_vowel(gender, number)
    base_v = gv.rstrip("f") if gv.endswith("f") else gv

    if person == Person.FOURTH:
        if number == Number.SINGULAR:
            return base_v
        elif number == Number.COLLECTIVE:
            return base_v
        elif number == Number.PLURAL:
            return ""  # 4th person plural word-final is empty
        elif number == Number.ZERO:
            return gv  # includes the f

    if number == Number.PLURAL:
        return base_v + cons + base_v + cons
    if number == Number.ZERO:
        return gv + base_v + cons  # e.g., "uf" + "u" + "th" = "ufuth"

    return base_v + cons + gv


# ---------------------------------------------------------------------------
# Subject prefix (for verb agreement)
# ---------------------------------------------------------------------------

def subject_prefix(person: Person, gender: Gender, number: Number) -> str:
    """Generate subject agreement prefix for verbs.

    Pattern: PersonConsonant + GenderVowel (base, no trailing f)
    Plural: doubled prefix
    """
    if gender == Gender.INANIMATE:
        return ""  # Inanimate cannot be agent of dynamic verbs

    cons = PERSON_CONSONANTS[person.value]
    gv = gender_vowel(gender, number)
    base_v = gv.rstrip("f") if gv.endswith("f") else gv

    prefix = cons + base_v
    if number == Number.PLURAL:
        return prefix + prefix
    return prefix


def object_suffix(person: Person, gender: Gender, number: Number) -> str:
    """Generate object agreement suffix for verbs.

    Pattern: GenderVowel(base) + PersonConsonant + GenderVowel(full)
    """
    cons = PERSON_CONSONANTS[person.value]
    gv = gender_vowel(gender, number)
    base_v = gv.rstrip("f") if gv.endswith("f") else gv

    if gender == Gender.INANIMATE:
        return gv  # Just the inanimate vowel marker

    return base_v + cons + gv


# ---------------------------------------------------------------------------
# Case marking
# ---------------------------------------------------------------------------

def agent_case(noun_form: str, person: Person, gender: Gender, number: Number) -> str:
    """Mark noun with agent case (predicate-final Ki)."""
    return noun_form + ki_predicate_final(person, gender, number)


def patient_case(noun_form: str, person: Person, gender: Gender, number: Number) -> str:
    """Mark noun with patient case (word-final Ki — least marked)."""
    return noun_form + ki_word_final(person, gender, number)


def possessive_case(noun_form: str, person: Person, gender: Gender, number: Number) -> str:
    """Mark noun with possessive case (Ki + -l suffix)."""
    ki = ki_predicate_final(person, gender, number)
    return noun_form + ki + "l"


def instrumental_case(noun_form: str, person: Person, gender: Gender, number: Number) -> str:
    """Mark noun with instrumental case (complex Ki form)."""
    wf = ki_word_final(person, gender, number)
    pf = ki_predicate_final(person, gender, number)
    return noun_form + wf + pf


def dative_case(noun_form: str, person: Person, gender: Gender, number: Number) -> str:
    """Mark noun with dative case (Ki + -n suffix)."""
    ki = ki_predicate_final(person, gender, number)
    return noun_form + ki + "n"


def speaker_case(noun_form: str, person: Person, gender: Gender, number: Number) -> str:
    """Mark noun with speaker case (Ki + -oro suffix)."""
    ki = ki_predicate_final(person, gender, number)
    return noun_form + ki + "oro"
