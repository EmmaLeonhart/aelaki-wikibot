"""Verb morphology for Aelaki.

Handles transitive verb conjugation with:
- 11 stem templates (telic/atelic x perfect/imperfect, habitual, gnomic, imperative)
- 17+ evidential categories (5 basic + 12 stacked)
- Polypersonal agreement (subject prefix + object suffix)
- Day prefixes (hodiernal go-, hesternal/crastinal goki-)
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass

from .gender import Gender, Number, Person, gender_vowel
from .phonology import PERSON_CONSONANTS
from .roots import TetraRoot, TriRoot


# ===========================================================================
# Evidentiality
# ===========================================================================

class Evidential(Enum):
    """Evidential/mood markers for verbs."""
    NONE = "none"                   # Present visual (unmarked)
    PRESENT = "present"             # Explicit present (-nü)
    PAST_VISUAL = "past_visual"     # Witnessed past (-shë)
    HEARSAY = "hearsay"             # Reported/auditory (-ro)
    INFERENTIAL = "inferential"     # Inferred (-mu)
    MYTHICAL = "mythical"           # Legendary past (-sher)
    INTENTION = "intention"         # 1p intention / 2p imperative / 3p jussive (-ng)
    OPTATIVE = "optative"           # Wish/hope (-ya)
    DELIBERATIVE = "deliberative"   # Should I? (-yam)

    # Stacked evidentials (primary + secondary)
    PRESENT_PAST = "present_past"
    PRESENT_HEARSAY = "present_hearsay"
    PRESENT_INFERENTIAL = "present_inferential"
    PAST_PRESENT = "past_present"
    PAST_HEARSAY = "past_hearsay"
    PAST_INFERENTIAL = "past_inferential"
    HEARSAY_PRESENT = "hearsay_present"
    HEARSAY_PAST = "hearsay_past"
    HEARSAY_INFERENTIAL = "hearsay_inferential"
    INFERENTIAL_PRESENT = "inferential_present"
    INFERENTIAL_PAST = "inferential_past"
    INFERENTIAL_HEARSAY = "inferential_hearsay"


# Evidential -> (helper_vowel, suffix)
EVIDENTIAL_TABLE: dict[Evidential, tuple[str, str]] = {
    Evidential.NONE:                    ("e",  ""),
    Evidential.PRESENT:                 ("ü",  "nü"),
    Evidential.PAST_VISUAL:             ("ə",  "shë"),
    Evidential.HEARSAY:                 ("o",  "ro"),
    Evidential.INFERENTIAL:             ("u",  "mu"),
    Evidential.MYTHICAL:                ("o",  "sher"),
    Evidential.INTENTION:               ("e",  "ng"),
    Evidential.OPTATIVE:                ("e",  "ya"),
    Evidential.DELIBERATIVE:            ("e",  "yam"),

    # Stacked
    Evidential.PRESENT_PAST:            ("ü",  "nüshë"),
    Evidential.PRESENT_HEARSAY:         ("ü",  "nüro"),
    Evidential.PRESENT_INFERENTIAL:     ("ü",  "nümu"),
    Evidential.PAST_PRESENT:            ("ə",  "shënü"),
    Evidential.PAST_HEARSAY:            ("ə",  "shëro"),
    Evidential.PAST_INFERENTIAL:        ("ə",  "shëmu"),
    Evidential.HEARSAY_PRESENT:         ("o",  "ronü"),
    Evidential.HEARSAY_PAST:            ("o",  "roshë"),
    Evidential.HEARSAY_INFERENTIAL:     ("o",  "romu"),
    Evidential.INFERENTIAL_PRESENT:     ("u",  "munü"),
    Evidential.INFERENTIAL_PAST:        ("u",  "mushë"),
    Evidential.INFERENTIAL_HEARSAY:     ("u",  "muro"),
}


# ===========================================================================
# Day prefixes
# ===========================================================================

class DayPrefix(Enum):
    NONE = ""              # Unmarked
    HODIERNAL = "go"       # Today
    HESTERNAL = "goki"     # Yesterday / tomorrow (context-dependent)


# ===========================================================================
# Verb stem templates (transitive, tetraconsonantal)
# ===========================================================================

class StemTemplate(Enum):
    """The 11 transitive verb stem patterns.

    Pattern notation: digits = root consonant index, letters = literal.
    'v' = helper vowel (replaced by evidential's helper vowel).
    """
    TELIC_PERFECT =       "1-a-2-3-e-4"
    TELIC_IMPERFECT =     "1-a-2-3-o-4"
    ATELIC_PERFECT =      "1-a-2-v-3-e-4"
    ATELIC_IMPERFECT =    "1-a-2-v-3-o-4"
    TELIC_PERFECT_N =     "1-a-2-3-v-3-e-4"
    HABITUAL_IMPERFECT =  "1-a-2-3-v-3-o-4"
    TELIC_PERFECT_2 =     "1-a-2-3-v-2-3-e-4"
    GNOMIC_IMPERFECT =    "1-a-2-3-v-2-3-o-4"
    ATELIC_PERFECT_2 =    "1-a-2-v-3-v-2-v-3-e-4"
    ATELIC_IMPERFECT_2 =  "1-a-2-v-3-v-2-v-3-o-4"
    IMPERATIVE =          "ala-1-a-2-a-3-4-o"


def expand_template(root: TetraRoot, template: StemTemplate,
                    helper_vowel: str = "e") -> str:
    """Expand a stem template with root consonants and helper vowel.

    Template tokens separated by '-':
    - Digit (1-4): replaced by root consonant at that index
    - 'v': replaced by helper vowel
    - Anything else: kept as literal
    """
    pattern = template.value.replace("v", helper_vowel)
    tokens = pattern.split("-")
    parts: list[str] = []
    for token in tokens:
        if token.isdigit() and 1 <= int(token) <= 4:
            parts.append(root[int(token) - 1])
        else:
            parts.append(token)
    return "".join(parts)


# ===========================================================================
# Subject/object agreement markers
# ===========================================================================

def _subject_prefix(person: Person, gender: Gender, number: Number) -> str:
    """Build subject agreement prefix."""
    if gender == Gender.INANIMATE:
        return ""

    cons = PERSON_CONSONANTS[person.value]
    gv = gender_vowel(gender, number)
    base_v = gv.rstrip("f") if gv.endswith("f") else gv

    prefix = cons + base_v
    if number == Number.PLURAL:
        return prefix + prefix
    return prefix


def _object_suffix(person: Person, gender: Gender, number: Number) -> str:
    """Build object agreement suffix."""
    cons = PERSON_CONSONANTS[person.value]
    gv = gender_vowel(gender, number)
    base_v = gv.rstrip("f") if gv.endswith("f") else gv

    if gender == Gender.INANIMATE:
        return gv

    return base_v + cons + gv


# ===========================================================================
# Full conjugation
# ===========================================================================

def conjugate_transitive(
    root: TetraRoot,
    template: StemTemplate,
    evidential: Evidential = Evidential.NONE,
    day: DayPrefix = DayPrefix.NONE,
    subj_person: Person = Person.THIRD,
    subj_gender: Gender = Gender.MALE,
    subj_number: Number = Number.SINGULAR,
    obj_person: Person = Person.FOURTH,
    obj_gender: Gender = Gender.FEMALE,
    obj_number: Number = Number.SINGULAR,
) -> str:
    """Conjugate a transitive verb with full agreement.

    Returns: [day_prefix] + subject_prefix + stem + evidential_suffix + object_suffix
    """
    helper_vowel, evid_suffix = EVIDENTIAL_TABLE[evidential]

    # Build stem
    stem = expand_template(root, template, helper_vowel)

    # Apply hodiernal sandhi if needed
    if day == DayPrefix.HODIERNAL and evid_suffix:
        stem = stem + "nk"

    # Add evidential suffix
    if evid_suffix:
        stem = stem + evid_suffix

    # Agreement markers
    prefix = _subject_prefix(subj_person, subj_gender, subj_number)
    suffix = _object_suffix(obj_person, obj_gender, obj_number)

    # Day prefix
    day_str = day.value

    return day_str + prefix + stem + suffix


# ===========================================================================
# Triconsonantal intransitive verbs (simplified)
# ===========================================================================

def conjugate_intransitive_active(
    root: TriRoot,
    v1: str = "a",
    v2: str = "a",
    evidential: Evidential = Evidential.NONE,
    day: DayPrefix = DayPrefix.NONE,
    subj_person: Person = Person.THIRD,
    subj_gender: Gender = Gender.MALE,
    subj_number: Number = Number.SINGULAR,
) -> str:
    """Conjugate an intransitive active verb.

    Active intransitive: subject prefix + stem + evidential
    (No object suffix)
    """
    _, evid_suffix = EVIDENTIAL_TABLE[evidential]

    # Base stem
    stem = f"{root.c1}{v1}{root.c2}{v2}{root.c3}"

    if day == DayPrefix.HODIERNAL and evid_suffix:
        stem = stem + "nk"

    if evid_suffix:
        stem = stem + evid_suffix

    prefix = _subject_prefix(subj_person, subj_gender, subj_number)
    day_str = day.value

    return day_str + prefix + stem


def conjugate_intransitive_stative(
    root: TriRoot,
    v1: str = "a",
    v2: str = "a",
    evidential: Evidential = Evidential.NONE,
    day: DayPrefix = DayPrefix.NONE,
    subj_person: Person = Person.THIRD,
    subj_gender: Gender = Gender.MALE,
    subj_number: Number = Number.SINGULAR,
) -> str:
    """Conjugate an intransitive stative verb.

    Stative intransitive: stem + evidential + subject suffix (word-final Ki)
    (No subject prefix; subject marked as suffix)
    """
    _, evid_suffix = EVIDENTIAL_TABLE[evidential]

    stem = f"{root.c1}{v1}{root.c2}{v2}{root.c3}"

    if day == DayPrefix.HODIERNAL and evid_suffix:
        stem = stem + "nk"

    if evid_suffix:
        stem = stem + evid_suffix

    # Stative uses word-final Ki for subject (no prefix)
    from .person import ki_word_final
    suffix = ki_word_final(subj_person, subj_gender, subj_number)
    day_str = day.value

    return day_str + stem + suffix
