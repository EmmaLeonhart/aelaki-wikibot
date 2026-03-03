"""Aelaki constructed language grammar generator.

Generates morphologically correct Aelaki words and phrases from roots,
implementing the full non-concatenative templatic morphology system.
"""

from .gender import Gender, Number, Person
from .roots import Root, TriRoot, TetraRoot
from .morphology import base_form, reduplicate, umlaut, zero_infix

__all__ = [
    "Gender", "Number", "Person",
    "Root", "TriRoot", "TetraRoot",
    "base_form", "reduplicate", "umlaut", "zero_infix",
]
