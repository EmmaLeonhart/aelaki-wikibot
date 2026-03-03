"""Tests for phrase and clause composition."""

import pytest
from aelaki.roots import TetraRoot, TriRoot
from aelaki.gender import Gender, Number, Person
from aelaki.verbs import StemTemplate, Evidential
from aelaki.phrases import NounPhrase, VerbPhrase, Clause
from aelaki.adjectives import AdjDegree
from aelaki.person import ki_predicate_final, ki_word_final, subject_prefix, object_suffix


class TestNounPhrase:
    """Test NounPhrase composition."""

    def test_basic_noun(self):
        np = NounPhrase(TetraRoot("k", "m", "d", "r"), Gender.MALE, Number.SINGULAR)
        result = np.realize()
        assert result == "kamudara"

    def test_with_adjective(self):
        np = NounPhrase(TetraRoot("k", "m", "d", "r"), Gender.MALE, Number.SINGULAR)
        np.add_adjective(TriRoot("b", "s", "l"))
        result = np.realize()
        assert "bosal" in result
        assert "kamudara" in result

    def test_with_numeral(self):
        np = NounPhrase(TetraRoot("k", "m", "d", "r"), Gender.MALE, Number.SINGULAR)
        np.add_numeral(5)
        result = np.realize()
        assert "Tan" in result
        assert np.number == Number.PLURAL  # Auto-upgraded

    def test_dropped_noun(self):
        np = NounPhrase(TetraRoot("k", "m", "d", "r"), Gender.MALE, Number.SINGULAR, dropped=True)
        result = np.realize()
        assert result == ""

    def test_dropped_with_adjective(self):
        np = NounPhrase(TetraRoot("k", "m", "d", "r"), Gender.MALE, Number.SINGULAR, dropped=True)
        np.add_adjective(TriRoot("b", "s", "l"))
        result = np.realize()
        assert "bosal" in result  # Adjective still realized
        assert "kamudara" not in result  # But noun is dropped


class TestVerbPhrase:
    """Test VerbPhrase composition."""

    def test_transitive_verb(self):
        subj = NounPhrase(TetraRoot("k", "m", "d", "r"), Gender.MALE, Number.SINGULAR, Person.THIRD)
        obj = NounPhrase(TriRoot("b", "s", "l"), Gender.FEMALE, Number.SINGULAR, Person.FOURTH)
        vp = VerbPhrase(TetraRoot("k", "m", "d", "r"), StemTemplate.TELIC_IMPERFECT)
        result = vp.realize(subj, obj)
        assert "sha" in result  # 3rd-male-sg subject prefix

    def test_intransitive_active(self):
        subj = NounPhrase(TriRoot("zh", "r", "n"), Gender.MALE, Number.SINGULAR, Person.FIRST)
        vp = VerbPhrase(TriRoot("zh", "r", "n"), verb_type="active")
        result = vp.realize(subj)
        assert result.startswith("tha")


class TestClause:
    """Test full clause composition."""

    def test_basic_clause(self):
        subj = NounPhrase(TetraRoot("k", "m", "d", "r"), Gender.MALE, Number.SINGULAR, Person.THIRD)
        obj = NounPhrase(TriRoot("b", "s", "l"), Gender.FEMALE, Number.SINGULAR, Person.FOURTH)
        vp = VerbPhrase(TetraRoot("k", "m", "d", "r"), StemTemplate.TELIC_IMPERFECT)
        clause = Clause(subj, vp, obj)
        result = clause.realize()
        # VSO order: verb first, then subject, then object
        parts = result.split()
        assert len(parts) >= 3

    def test_pro_drop_subject(self):
        subj = NounPhrase(TetraRoot("k", "m", "d", "r"), Gender.MALE, Number.SINGULAR,
                          Person.THIRD, dropped=True)
        obj = NounPhrase(TriRoot("b", "s", "l"), Gender.FEMALE, Number.SINGULAR, Person.FOURTH)
        vp = VerbPhrase(TetraRoot("k", "m", "d", "r"), StemTemplate.TELIC_IMPERFECT)
        clause = Clause(subj, vp, obj)
        result = clause.realize()
        # Verb still has agreement, but subject NP is absent
        assert "kamudara" not in result  # Subject noun not present
        assert "sha" in result  # But agreement prefix is there


class TestKiSyllables:
    """Test Ki syllable generation."""

    def test_predicate_final_basics(self):
        assert ki_predicate_final(Person.FIRST, Gender.CHILD, Number.SINGULAR) == "thu"
        assert ki_predicate_final(Person.SECOND, Gender.FEMALE, Number.SINGULAR) == "jo"
        assert ki_predicate_final(Person.THIRD, Gender.MALE, Number.SINGULAR) == "sha"
        assert ki_predicate_final(Person.FOURTH, Gender.CHILD, Number.SINGULAR) == "ku"

    def test_predicate_final_plural_doubled(self):
        assert ki_predicate_final(Person.FIRST, Gender.CHILD, Number.PLURAL) == "thuthu"
        assert ki_predicate_final(Person.THIRD, Gender.MALE, Number.PLURAL) == "shasha"

    def test_predicate_final_collective(self):
        assert ki_predicate_final(Person.FOURTH, Gender.CHILD, Number.COLLECTIVE) == "ki"
        assert ki_predicate_final(Person.FIRST, Gender.FEMALE, Number.COLLECTIVE) == "the"

    def test_word_final_basics(self):
        assert ki_word_final(Person.FIRST, Gender.CHILD, Number.SINGULAR) == "uthu"

    def test_subject_prefix(self):
        assert subject_prefix(Person.FIRST, Gender.CHILD, Number.SINGULAR) == "thu"
        assert subject_prefix(Person.THIRD, Gender.MALE, Number.PLURAL) == "shasha"

    def test_object_suffix(self):
        assert object_suffix(Person.THIRD, Gender.FEMALE, Number.SINGULAR) == "osho"
