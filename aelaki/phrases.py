"""Phrase and clause composition for Aelaki.

Provides NounPhrase, VerbPhrase, and Clause classes for building
complete Aelaki sentences with proper agreement and word order.

Default word order: V(S)(O) — verb-initial with pro-drop.
Imperative: frozen S-O-V morphology.
"""

from __future__ import annotations
from dataclasses import dataclass, field

from .gender import Gender, Number, Person
from .roots import TriRoot, TetraRoot
from .nouns import build_noun
from .possession import build_possessed
from .adjectives import realize_adjective, AdjDegree, AdjEvidential
from .numerals import cardinal
from .verbs import (
    conjugate_transitive, conjugate_intransitive_active,
    conjugate_intransitive_stative,
    StemTemplate, Evidential, DayPrefix,
)
from .adverbs import realize_adverb, AdverbDegree, AdverbTense
from .converbs import (
    ConverbPrefixType, ConverbSuffixType,
    build_prefix_converb_transitive, build_suffix_converb_transitive,
)


# ===========================================================================
# NounPhrase
# ===========================================================================

@dataclass
class NounPhrase:
    """A noun phrase with optional adjectives, numerals, and possession."""
    root: TriRoot | TetraRoot
    gender: Gender
    number: Number
    person: Person = Person.FOURTH
    dropped: bool = False  # Pro-drop: noun omitted but features retained

    # Modifiers
    adjectives: list[tuple[TriRoot, AdjDegree]] = field(default_factory=list)
    numeral: int | None = None

    # Possession
    possessor_root: TriRoot | TetraRoot | None = None
    possessor_person: Person = Person.FOURTH
    possessor_gender: Gender = Gender.MALE
    inalienable: bool = True

    def add_adjective(self, root: TriRoot, degree: AdjDegree = AdjDegree.POSITIVE) -> NounPhrase:
        """Add an adjective that agrees with this noun."""
        self.adjectives.append((root, degree))
        return self

    def add_numeral(self, n: int) -> NounPhrase:
        """Add a numeral; automatically sets plural if > 1."""
        self.numeral = n
        if n > 1 and self.number == Number.SINGULAR:
            self.number = Number.PLURAL
        return self

    def set_possessor(self, root: TriRoot | TetraRoot, person: Person,
                      gender: Gender, inalienable: bool = True) -> NounPhrase:
        """Set the possessor of this noun."""
        self.possessor_root = root
        self.possessor_person = person
        self.possessor_gender = gender
        self.inalienable = inalienable
        return self

    def realize(self) -> str:
        """Generate the surface form of this noun phrase."""
        parts: list[str] = []

        # Front adjectives (including numeral as adjective)
        if self.numeral is not None:
            parts.append(cardinal(self.numeral))

        for adj_root, adj_degree in self.adjectives:
            parts.append(realize_adjective(
                adj_root, self.person, self.gender, self.number, adj_degree))

        # Head noun
        if not self.dropped:
            if self.possessor_root is not None:
                parts.append(build_possessed(
                    self.root, self.gender, self.number,
                    self.possessor_person, self.possessor_gender,
                    self.inalienable))
            else:
                parts.append(build_noun(self.root, self.gender, self.number, self.person))

        return " ".join(parts)


# ===========================================================================
# VerbPhrase
# ===========================================================================

@dataclass
class VerbPhrase:
    """A verb phrase with template, evidential, and optional adverbs/converbs."""
    root: TetraRoot | TriRoot
    template: StemTemplate = StemTemplate.TELIC_IMPERFECT
    evidential: Evidential = Evidential.NONE
    day: DayPrefix = DayPrefix.NONE
    verb_type: str = "transitive"  # "transitive", "active", "stative"

    adverbs: list[tuple[TriRoot, str, str, AdverbDegree, AdverbTense]] = field(default_factory=list)

    def add_adverb(self, root: TriRoot, v1: str = "a", v2: str = "a",
                   degree: AdverbDegree = AdverbDegree.POSITIVE,
                   tense: AdverbTense = AdverbTense.PRESENT) -> VerbPhrase:
        """Add an adverb to this verb phrase."""
        self.adverbs.append((root, v1, v2, degree, tense))
        return self

    def realize(self, subject: NounPhrase, obj: NounPhrase | None = None) -> str:
        """Generate the surface form of this verb phrase."""
        parts: list[str] = []

        # Adverbs
        for adv_root, v1, v2, degree, tense in self.adverbs:
            parts.append(realize_adverb(adv_root, v1, v2, degree, tense))

        # Verb
        if self.verb_type == "transitive" and isinstance(self.root, TetraRoot):
            assert obj is not None, "Transitive verb requires object NP"
            verb_form = conjugate_transitive(
                self.root, self.template, self.evidential, self.day,
                subject.person, subject.gender, subject.number,
                obj.person, obj.gender, obj.number,
            )
        elif self.verb_type == "active" and isinstance(self.root, TriRoot):
            verb_form = conjugate_intransitive_active(
                self.root, "a", "a", self.evidential, self.day,
                subject.person, subject.gender, subject.number,
            )
        elif self.verb_type == "stative" and isinstance(self.root, TriRoot):
            verb_form = conjugate_intransitive_stative(
                self.root, "a", "a", self.evidential, self.day,
                subject.person, subject.gender, subject.number,
            )
        else:
            raise ValueError(f"Invalid verb_type/root combination: {self.verb_type}/{type(self.root)}")

        parts.append(verb_form)
        return " ".join(parts)


# ===========================================================================
# Clause
# ===========================================================================

@dataclass
class Clause:
    """A complete clause with subject, verb, and optional object.

    Default word order: V(S)(O) — verb-initial.
    Subject and object may be dropped (pro-drop language).
    """
    subject: NounPhrase
    verb: VerbPhrase
    obj: NounPhrase | None = None

    def realize(self) -> str:
        """Generate the surface form of this clause.

        Word order: Verb Subject Object (VSO)
        Dropped NPs are omitted but their features are still used for agreement.
        """
        parts: list[str] = []

        # Verb (always present, carries agreement)
        parts.append(self.verb.realize(self.subject, self.obj))

        # Subject (if not dropped)
        subj_form = self.subject.realize()
        if subj_form:
            parts.append(subj_form)

        # Object (if not dropped)
        if self.obj is not None:
            obj_form = self.obj.realize()
            if obj_form:
                parts.append(obj_form)

        return " ".join(parts)
