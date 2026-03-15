"""Converb morphology for Aelaki.

Two classes of converbs with distinct TAM properties:
- Class I (prefix converbs): Retain full tense-evidential morphology
- Class II (suffix converbs): Consume TAM; use dedicated suffix morphology
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass

from .gender import Gender, Number, Person
from .phonology import PERSON_CONSONANTS
from .verbs import Evidential, EVIDENTIAL_TABLE, DayPrefix, expand_template, StemTemplate
from .roots import TetraRoot, TriRoot


# ===========================================================================
# Class I: Prefix converbs (keep full TAM)
# ===========================================================================

class ConverbPrefixType(Enum):
    """Class I converb prefixes that retain full TAM."""
    PURPOSIVE = "ki"       # "in order to"
    CAUSAL = "ha"          # "because"
    CONDITIONAL = "sa"     # "if/when"
    CONCESSIVE = "ra"      # "even though"
    INSTRUMENTAL = "mu"    # "by means of"
    ADVERSATIVE = "ne"     # "instead of"


def build_prefix_converb_transitive(
    prefix_type: ConverbPrefixType,
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
    """Build a Class I prefix converb from a transitive verb.

    Template: PREFIX-[DAY-](SUBJ-Ki)ROOT.ASPECT-(OBJ-Ki)-TAM

    Class I converbs retain full TAM from the finite verb system.
    """
    from .verbs import conjugate_transitive
    finite_form = conjugate_transitive(
        root, template, evidential, day,
        subj_person, subj_gender, subj_number,
        obj_person, obj_gender, obj_number,
    )
    return prefix_type.value + finite_form


def build_prefix_converb_intransitive(
    prefix_type: ConverbPrefixType,
    root: TriRoot,
    v1: str = "a",
    v2: str = "a",
    evidential: Evidential = Evidential.NONE,
    day: DayPrefix = DayPrefix.NONE,
    subj_person: Person = Person.THIRD,
    subj_gender: Gender = Gender.MALE,
    subj_number: Number = Number.SINGULAR,
    active: bool = True,
) -> str:
    """Build a Class I prefix converb from an intransitive verb."""
    from .verbs import conjugate_intransitive_active, conjugate_intransitive_stative
    if active:
        finite_form = conjugate_intransitive_active(
            root, v1, v2, evidential, day, subj_person, subj_gender, subj_number)
    else:
        finite_form = conjugate_intransitive_stative(
            root, v1, v2, evidential, day, subj_person, subj_gender, subj_number)
    return prefix_type.value + finite_form


# ===========================================================================
# Class II: Suffix converbs (consume TAM)
# ===========================================================================

class ConverbSuffixType(Enum):
    """Class II converb suffixes that consume TAM.

    Value is (suffix, gloss).
    """
    POSTERIOR =    ("shëlon",  "before")
    ANTERIOR =     ("mulon",   "after / once")
    SEQUENTIAL =   ("lon",     "right after")
    TERMINATIVE =  ("ndor",    "until")
    LOCATIVE =     ("lok",     "where")
    SIMULATIVE =   ("mutu",    "as though")
    BENEFICIARY =  ("rum",     "for the sake of")
    COMITATIVE =   ("wom",     "together with")
    EXCEPTIVE =    ("səf",     "except for")
    RESTRICTIVE =  ("vai",     "only if/when")

    def __init__(self, suffix: str, gloss: str):
        self.suffix = suffix
        self.gloss = gloss


def build_suffix_converb_transitive(
    suffix_type: ConverbSuffixType,
    root: TetraRoot,
    template: StemTemplate,
    day: DayPrefix = DayPrefix.NONE,
    subj_person: Person = Person.THIRD,
    subj_gender: Gender = Gender.MALE,
    subj_number: Number = Number.SINGULAR,
    obj_person: Person = Person.FOURTH,
    obj_gender: Gender = Gender.FEMALE,
    obj_number: Number = Number.SINGULAR,
) -> str:
    """Build a Class II suffix converb from a transitive verb.

    Template: [DAY-](SUBJ-Ki)ROOT-ASPECT-(OBJ-Ki)-SUFFIX

    Class II converbs do NOT carry TAM; they use the suffix instead.
    """
    helper_vowel = "e"  # Default (no evidential)
    stem = expand_template(root, template, helper_vowel)

    # Subject prefix
    cons = PERSON_CONSONANTS[subj_person.value]
    from .gender import gender_vowel
    gv = gender_vowel(subj_gender, subj_number)
    base_v = gv.rstrip("f") if gv.endswith("f") else gv
    subj_prefix = cons + base_v
    if subj_number == Number.PLURAL:
        subj_prefix = subj_prefix + subj_prefix

    # Object suffix
    obj_cons = PERSON_CONSONANTS[obj_person.value]
    obj_gv = gender_vowel(obj_gender, obj_number)
    obj_base_v = obj_gv.rstrip("f") if obj_gv.endswith("f") else obj_gv
    if obj_gender == Gender.INANIMATE:
        obj_suf = obj_gv
    else:
        obj_suf = obj_base_v + obj_cons + obj_gv

    day_str = day.value
    return day_str + subj_prefix + stem + obj_suf + suffix_type.suffix


def build_suffix_converb_intransitive(
    suffix_type: ConverbSuffixType,
    root: TriRoot,
    v1: str = "a",
    v2: str = "a",
    day: DayPrefix = DayPrefix.NONE,
    subj_person: Person = Person.THIRD,
    subj_gender: Gender = Gender.MALE,
    subj_number: Number = Number.SINGULAR,
    active: bool = True,
) -> str:
    """Build a Class II suffix converb from an intransitive verb."""
    stem = f"{root.c1}{v1}{root.c2}{v2}{root.c3}"

    if active:
        # Active: subject prefix + stem + suffix
        cons = PERSON_CONSONANTS[subj_person.value]
        from .gender import gender_vowel
        gv = gender_vowel(subj_gender, subj_number)
        base_v = gv.rstrip("f") if gv.endswith("f") else gv
        prefix = cons + base_v
        if subj_number == Number.PLURAL:
            prefix = prefix + prefix
        day_str = day.value
        return day_str + prefix + stem + suffix_type.suffix
    else:
        # Stative: stem + subject Ki (word-final) + suffix
        from .person import ki_word_final
        ki = ki_word_final(subj_person, subj_gender, subj_number, stem=stem)
        day_str = day.value
        return day_str + stem + ki + suffix_type.suffix
