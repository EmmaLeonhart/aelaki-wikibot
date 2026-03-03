"""Possession constructions for Aelaki.

Two distinct head-marking strategies:
- Inalienable: body parts, kin, inherent properties (infix + -ng suffix)
- Alienable: transferable property, abstract relations (prefix + optional -n)
"""

from __future__ import annotations

from .gender import Gender, Number, Person, singular_vowel
from .phonology import PERSON_CONSONANTS, PERSON_SUFFIXES
from .roots import TriRoot, TetraRoot
from .nouns import build_tetra_stem, build_tri_stem


# ===========================================================================
# Inalienable possession (body parts, kin, part-whole, inherent)
# ===========================================================================

def inalienable_possessed_tetra(
    root: TetraRoot,
    noun_gender: Gender,
    noun_number: Number,
    possessor_person: Person,
    possessor_gender: Gender,
) -> str:
    """Build inalienable possessed form for tetraconsonantal noun.

    Template: C1 + GV(possessor) + PC(possessor) + rest-of-stem + ng

    The possessor's gender vowel and person consonant are infixed after C1,
    then -ng replaces the usual Ki clitic.
    """
    stem = build_tetra_stem(root, noun_gender, noun_number)
    # Split: first consonant cluster vs rest
    c1_len = len(root.c1)
    c1 = stem[:c1_len]
    rest = stem[c1_len:]

    gv = singular_vowel(possessor_gender)
    pc = PERSON_CONSONANTS[possessor_person.value]

    return f"{c1}{gv}{pc}{rest}ng"


def inalienable_possessed_tri(
    root: TriRoot,
    noun_gender: Gender,
    noun_number: Number,
    possessor_person: Person,
    possessor_gender: Gender,
) -> str:
    """Build inalienable possessed form for triconsonantal noun.

    Same pattern: C1 + GV(possessor) + PC(possessor) + rest + ng
    """
    stem = build_tri_stem(root, noun_gender, noun_number)
    c1_len = len(root.c1)
    c1 = stem[:c1_len]
    rest = stem[c1_len:]

    gv = singular_vowel(possessor_gender)
    pc = PERSON_CONSONANTS[possessor_person.value]

    return f"{c1}{gv}{pc}{rest}ng"


# ===========================================================================
# Alienable possession (property, abstract, spatial/temporal)
# ===========================================================================

def alienable_possessed_tetra(
    root: TetraRoot,
    noun_gender: Gender,
    noun_number: Number,
    possessor_person: Person,
    possessor_gender: Gender,
) -> str:
    """Build alienable possessed form for tetraconsonantal noun.

    Template: GV(possessor) + PC(possessor) + stem + n

    The possessor's gender vowel and person consonant are prefixed,
    with an optional -n suffix.
    """
    stem = build_tetra_stem(root, noun_gender, noun_number)
    gv = singular_vowel(possessor_gender)
    pc = PERSON_CONSONANTS[possessor_person.value]

    return f"{gv}{pc}{stem}n"


def alienable_possessed_tri(
    root: TriRoot,
    noun_gender: Gender,
    noun_number: Number,
    possessor_person: Person,
    possessor_gender: Gender,
) -> str:
    """Build alienable possessed form for triconsonantal noun.

    Template: GV(possessor) + PC(possessor) + stem + n
    """
    stem = build_tri_stem(root, noun_gender, noun_number)
    gv = singular_vowel(possessor_gender)
    pc = PERSON_CONSONANTS[possessor_person.value]

    return f"{gv}{pc}{stem}n"


# ===========================================================================
# Possessor NP form (dependent in genitive construction)
# ===========================================================================

def build_possessor_np(
    root: TetraRoot,
    possessor_gender: Gender,
    possessor_number: Number,
    possessed_gender: Gender,
    inalienable: bool,
) -> str:
    """Build the possessor NP form (the dependent/genitive noun).

    The possessor noun takes a special suffix based on whether the
    relationship is inalienable or alienable:
    - Inalienable: base noun + ng
    - Alienable: base noun + n
    """
    stem = build_tetra_stem(root, possessor_gender, possessor_number)
    suffix = "ng" if inalienable else "n"
    return f"{stem}{suffix}"


# ===========================================================================
# Unified interface
# ===========================================================================

def build_possessed(
    root: TriRoot | TetraRoot,
    noun_gender: Gender,
    noun_number: Number,
    possessor_person: Person,
    possessor_gender: Gender,
    inalienable: bool = True,
) -> str:
    """Build a possessed noun form.

    Args:
        root: The noun root (possessed item)
        noun_gender: Gender of the possessed noun
        noun_number: Number of the possessed noun
        possessor_person: Person of the possessor
        possessor_gender: Gender of the possessor
        inalienable: True for body parts/kin, False for property
    """
    if inalienable:
        if isinstance(root, TetraRoot):
            return inalienable_possessed_tetra(
                root, noun_gender, noun_number, possessor_person, possessor_gender)
        return inalienable_possessed_tri(
            root, noun_gender, noun_number, possessor_person, possessor_gender)
    else:
        if isinstance(root, TetraRoot):
            return alienable_possessed_tetra(
                root, noun_gender, noun_number, possessor_person, possessor_gender)
        return alienable_possessed_tri(
            root, noun_gender, noun_number, possessor_person, possessor_gender)
