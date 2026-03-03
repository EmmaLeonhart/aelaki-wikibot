"""Noun morphology for Aelaki.

Handles noun stem building for both triconsonantal and tetraconsonantal
roots with full gender, number, and person agreement.
"""

from __future__ import annotations

from .gender import Gender, Number, Person, gender_vowel, singular_vowel
from .phonology import (
    PERSON_SUFFIXES, PERSON_CONSONANTS,
    apply_collective_shift, apply_zero_suffix,
)
from .roots import TriRoot, TetraRoot


# ===========================================================================
# Tetraconsonantal noun stems (C1-a-C2-u-C3-Vm-C4-Ve)
# ===========================================================================

def _tetra_singular(root: TetraRoot, gender: Gender) -> str:
    """Build singular stem: C1-a-C2-u-C3-Vm-C4-Ve."""
    vm = singular_vowel(gender)
    ve = singular_vowel(gender)
    return f"{root.c1}a{root.c2}u{root.c3}{vm}{root.c4}{ve}"


def _tetra_plural(root: TetraRoot, gender: Gender) -> str:
    """Build plural stem: C1-a-C2-u-C2-u-C3-Vm-C4-Ve (reduplicate C2-u)."""
    vm = singular_vowel(gender)
    ve = singular_vowel(gender)
    return f"{root.c1}a{root.c2}u{root.c2}u{root.c3}{vm}{root.c4}{ve}"


def _tetra_collective(root: TetraRoot, gender: Gender) -> str:
    """Build collective stem: apply collective vowel shift to singular."""
    singular = _tetra_singular(root, gender)
    return apply_collective_shift(singular)


def _tetra_zero(root: TetraRoot, gender: Gender) -> str:
    """Build zero stem: add -f after each gender vowel in singular."""
    vm = singular_vowel(gender)
    ve = singular_vowel(gender)
    vmf = apply_zero_suffix(vm)
    vef = apply_zero_suffix(ve)
    return f"{root.c1}a{root.c2}u{root.c3}{vmf}{root.c4}{vef}"


def build_tetra_stem(root: TetraRoot, gender: Gender, number: Number) -> str:
    """Build a tetraconsonantal noun stem with gender and number."""
    builders = {
        Number.SINGULAR: _tetra_singular,
        Number.PLURAL: _tetra_plural,
        Number.COLLECTIVE: _tetra_collective,
        Number.ZERO: _tetra_zero,
    }
    return builders[number](root, gender)


def build_tetra_form(root: TetraRoot, gender: Gender, number: Number,
                     person: Person) -> str:
    """Build a complete tetraconsonantal noun form with person suffix."""
    stem = build_tetra_stem(root, gender, number)
    suffix = PERSON_SUFFIXES[person.value]
    return (stem + suffix).lower()


# ===========================================================================
# Triconsonantal noun stems (C1-a-C2-Vm-C3-Ve)
# ===========================================================================

def _tri_singular(root: TriRoot, gender: Gender) -> str:
    """Build singular stem: C1-a-C2-Vm-C3-Ve."""
    v = singular_vowel(gender)
    return f"{root.c1}a{root.c2}{v}{root.c3}{v}"


def _tri_plural(root: TriRoot, gender: Gender) -> str:
    """Build plural stem: C1-a-C2-V-C2-V-C3-Ve (reduplicate C2-V)."""
    v = singular_vowel(gender)
    return f"{root.c1}a{root.c2}{v}{root.c2}{v}{root.c3}{v}"


def _tri_collective(root: TriRoot, gender: Gender) -> str:
    """Build collective stem: apply collective shift to singular."""
    singular = _tri_singular(root, gender)
    return apply_collective_shift(singular)


def _tri_zero(root: TriRoot, gender: Gender) -> str:
    """Build zero stem: add -f after each gender vowel."""
    v = singular_vowel(gender)
    vf = apply_zero_suffix(v)
    return f"{root.c1}a{root.c2}{vf}{root.c3}{vf}"


def build_tri_stem(root: TriRoot, gender: Gender, number: Number) -> str:
    """Build a triconsonantal noun stem with gender and number."""
    builders = {
        Number.SINGULAR: _tri_singular,
        Number.PLURAL: _tri_plural,
        Number.COLLECTIVE: _tri_collective,
        Number.ZERO: _tri_zero,
    }
    return builders[number](root, gender)


def build_tri_form(root: TriRoot, gender: Gender, number: Number,
                   person: Person) -> str:
    """Build a complete triconsonantal noun form with person suffix."""
    stem = build_tri_stem(root, gender, number)
    suffix = PERSON_SUFFIXES[person.value]
    return (stem + suffix).lower()


# ===========================================================================
# Unified interface
# ===========================================================================

def build_noun(root: TriRoot | TetraRoot, gender: Gender, number: Number,
               person: Person = Person.FOURTH) -> str:
    """Build a noun form from any root type."""
    if isinstance(root, TetraRoot):
        return build_tetra_form(root, gender, number, person)
    elif isinstance(root, TriRoot):
        return build_tri_form(root, gender, number, person)
    raise TypeError(f"Unsupported root type: {type(root)}")
