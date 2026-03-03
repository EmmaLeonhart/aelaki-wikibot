"""Aelaki constructed language grammar generator.

Generates morphologically correct Aelaki words and phrases from roots,
implementing the full non-concatenative templatic morphology system.

Modules:
    phonology    - Vowel/consonant inventories, umlaut, sandhi
    roots        - TriRoot and TetraRoot classes
    morphology   - 4 core operations (base, reduplication, umlaut, zero-infix)
    gender       - Gender, Number, Person enums
    person       - Ki-syllable system, case marking
    nouns        - Noun stem building
    possession   - Alienable/inalienable possession
    numerals     - Base-12/60 numeral system
    verbs        - Transitive/intransitive verb conjugation
    stative_verbs - Stative verb prefix system
    adjectives   - Adjective agreement and degrees
    adverbs      - Adverb formation with tense agreement
    converbs     - Class I (prefix) and Class II (suffix) converbs
    particles    - Small words, connectives, adpositions
    phrases      - NounPhrase, VerbPhrase, Clause composition
    lexicon      - Known vocabulary roots
"""

from .gender import Gender, Number, Person
from .roots import Root, TriRoot, TetraRoot
from .morphology import base_form, reduplicate, umlaut, zero_infix

__all__ = [
    "Gender", "Number", "Person",
    "Root", "TriRoot", "TetraRoot",
    "base_form", "reduplicate", "umlaut", "zero_infix",
]
