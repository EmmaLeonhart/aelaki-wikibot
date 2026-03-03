"""Core morphological operations for Aelaki.

Implements the four fundamental non-concatenative operations that apply
across all major word classes: base form, reduplication, umlaut, and
zero-infix.
"""

from __future__ import annotations

from .phonology import UMLAUT_MAP, apply_umlaut, apply_collective_shift
from .roots import TriRoot, TetraRoot, Root


# ===========================================================================
# Triconsonantal operations (C1-V1-C2-V2-C3)
# ===========================================================================

def tri_base(c1: str, v1: str, c2: str, v2: str, c3: str) -> str:
    """Base form: C1V1C2V2C3 — singular, perfective-incomplete, positive."""
    return f"{c1}{v1}{c2}{v2}{c3}"


def tri_reduplicate(c1: str, v1: str, c2: str, v2: str, c3: str) -> str:
    """Reduplication: C1V1C2V1C2V2C3 — plural, imperfective, comparative.

    Inserts a copy of C2+V1 after the first V1.
    """
    return f"{c1}{v1}{c2}{v1}{c2}{v2}{c3}"


def tri_umlaut(c1: str, v1: str, c2: str, v2: str, c3: str) -> str:
    """Umlaut (fronting): front both vowels — collective, perfective-completed, superlative."""
    fv1 = UMLAUT_MAP.get(v1, v1)
    fv2 = UMLAUT_MAP.get(v2, v2)
    return f"{c1}{fv1}{c2}{fv2}{c3}"


def tri_zero_infix(c1: str, v1: str, c2: str, v2: str, c3: str) -> str:
    """Zero-infix: C1V1fC2V2C3 — negation, zero quantity.

    Inserts /f/ between V1 and C2.
    """
    return f"{c1}{v1}f{c2}{v2}{c3}"


def tri_all_forms(c1: str, v1: str, c2: str, v2: str, c3: str) -> dict[str, str]:
    """Generate all four morphological forms for a triconsonantal root."""
    return {
        "base": tri_base(c1, v1, c2, v2, c3),
        "reduplication": tri_reduplicate(c1, v1, c2, v2, c3),
        "umlaut": tri_umlaut(c1, v1, c2, v2, c3),
        "zero_infix": tri_zero_infix(c1, v1, c2, v2, c3),
    }


# ===========================================================================
# Convenience wrappers using Root objects
# ===========================================================================

def base_form(root: Root, v1: str = "a", v2: str = "a") -> str:
    """Generate the base form of any root with given vowels."""
    if isinstance(root, TriRoot):
        return tri_base(root.c1, v1, root.c2, v2, root.c3)
    elif isinstance(root, TetraRoot):
        # Tetra base: C1-a-C2-u-C3-V-C4-V (default vowels for tetra)
        return f"{root.c1}a{root.c2}u{root.c3}{v1}{root.c4}{v2}"
    raise TypeError(f"Unsupported root type: {type(root)}")


def reduplicate(root: Root, v1: str = "a", v2: str = "a") -> str:
    """Generate the reduplicated form of any root."""
    if isinstance(root, TriRoot):
        return tri_reduplicate(root.c1, v1, root.c2, v2, root.c3)
    elif isinstance(root, TetraRoot):
        # Tetra plural: C1-a-C2-u-C2-u-C3-V-C4-V (duplicate C2-u)
        return f"{root.c1}a{root.c2}u{root.c2}u{root.c3}{v1}{root.c4}{v2}"
    raise TypeError(f"Unsupported root type: {type(root)}")


def umlaut(root: Root, v1: str = "a", v2: str = "a") -> str:
    """Generate the umlaut (fronted) form of any root."""
    if isinstance(root, TriRoot):
        return tri_umlaut(root.c1, v1, root.c2, v2, root.c3)
    elif isinstance(root, TetraRoot):
        base = base_form(root, v1, v2)
        return apply_collective_shift(base)
    raise TypeError(f"Unsupported root type: {type(root)}")


def zero_infix(root: Root, v1: str = "a", v2: str = "a") -> str:
    """Generate the zero-infix (negation) form of any root."""
    if isinstance(root, TriRoot):
        return tri_zero_infix(root.c1, v1, root.c2, v2, root.c3)
    elif isinstance(root, TetraRoot):
        # Tetra zero: add -f after each vowel
        return f"{root.c1}a{root.c2}uf{root.c3}{v1}f{root.c4}{v2}f"
    raise TypeError(f"Unsupported root type: {type(root)}")
