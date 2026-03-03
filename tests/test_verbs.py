"""Tests for verb conjugation.

Validates against C# reference output and grammar guide examples.
"""

import pytest
from aelaki.roots import TetraRoot, TriRoot
from aelaki.gender import Gender, Number, Person
from aelaki.verbs import (
    conjugate_transitive, conjugate_intransitive_active,
    conjugate_intransitive_stative,
    expand_template, StemTemplate, Evidential, DayPrefix,
)


class TestStemTemplates:
    """Test stem template expansion."""

    def setup_method(self):
        self.root = TetraRoot("k", "m", "d", "r")

    def test_telic_perfect(self):
        result = expand_template(self.root, StemTemplate.TELIC_PERFECT, "e")
        assert result == "kamder"

    def test_telic_imperfect(self):
        result = expand_template(self.root, StemTemplate.TELIC_IMPERFECT, "e")
        assert result == "kamdor"

    def test_atelic_perfect(self):
        result = expand_template(self.root, StemTemplate.ATELIC_PERFECT, "e")
        assert result == "kameder"

    def test_atelic_imperfect(self):
        result = expand_template(self.root, StemTemplate.ATELIC_IMPERFECT, "e")
        assert result == "kamedor"  # 1-a-2-v-3-o-4 with v=e -> kamedor

    def test_imperative(self):
        result = expand_template(self.root, StemTemplate.IMPERATIVE, "e")
        assert result.startswith("ala")

    def test_helper_vowel_substitution(self):
        """Test that different evidentials produce different helper vowels."""
        past = expand_template(self.root, StemTemplate.ATELIC_PERFECT, "ə")
        default = expand_template(self.root, StemTemplate.ATELIC_PERFECT, "e")
        assert past != default


class TestTransitiveConjugation:
    """Test full transitive verb conjugation."""

    def setup_method(self):
        self.root = TetraRoot("k", "m", "d", "r")

    def test_basic_conjugation(self):
        """3rd-male-sg subject, 4th-fem-sg object, telic imperfect."""
        result = conjugate_transitive(
            self.root, StemTemplate.TELIC_IMPERFECT,
            subj_person=Person.THIRD, subj_gender=Gender.MALE,
            subj_number=Number.SINGULAR,
            obj_person=Person.FOURTH, obj_gender=Gender.FEMALE,
            obj_number=Number.SINGULAR,
        )
        assert result == "shakamdoroko"

    def test_past_visual(self):
        """With past visual evidential."""
        result = conjugate_transitive(
            self.root, StemTemplate.TELIC_IMPERFECT,
            Evidential.PAST_VISUAL,
            subj_person=Person.THIRD, subj_gender=Gender.MALE,
            subj_number=Number.SINGULAR,
        )
        assert "shë" in result

    def test_subject_prefix_plural_doubled(self):
        """Plural subject should double the prefix."""
        result = conjugate_transitive(
            self.root, StemTemplate.TELIC_IMPERFECT,
            subj_person=Person.FIRST, subj_gender=Gender.CHILD,
            subj_number=Number.PLURAL,
        )
        assert result.startswith("thuthu")

    def test_hodiernal_sandhi(self):
        """Hodiernal day prefix should trigger -nk- insertion."""
        result = conjugate_transitive(
            self.root, StemTemplate.TELIC_IMPERFECT,
            Evidential.HEARSAY, DayPrefix.HODIERNAL,
            subj_person=Person.THIRD, subj_gender=Gender.MALE,
        )
        assert result.startswith("go")
        assert "nk" in result

    def test_stacked_evidential(self):
        """Test stacked evidential suffix."""
        result = conjugate_transitive(
            self.root, StemTemplate.TELIC_IMPERFECT,
            Evidential.PAST_HEARSAY,
            subj_person=Person.THIRD, subj_gender=Gender.MALE,
        )
        assert "shëro" in result


class TestIntransitiveConjugation:
    """Test intransitive verb conjugation."""

    def setup_method(self):
        self.root = TriRoot("zh", "r", "n")

    def test_active_basic(self):
        result = conjugate_intransitive_active(
            self.root,
            subj_person=Person.FIRST, subj_gender=Gender.MALE,
        )
        assert result.startswith("tha")

    def test_stative_basic(self):
        """Stative verbs have suffix agreement, no prefix."""
        result = conjugate_intransitive_stative(
            self.root,
            subj_person=Person.FIRST, subj_gender=Gender.MALE,
            subj_number=Number.SINGULAR,
        )
        # Should end with word-final Ki for 1st-male-singular: "ath"
        assert "ath" in result

    def test_active_no_object_suffix(self):
        """Active intransitive should not have object suffix."""
        result = conjugate_intransitive_active(
            self.root,
            subj_person=Person.THIRD, subj_gender=Gender.MALE,
        )
        # Should be prefix + stem only
        assert result == "shazharan"


class TestEvidentialSuffixes:
    """Verify all evidential suffixes produce expected output."""

    def test_mythical(self):
        root = TetraRoot("k", "m", "d", "r")
        result = conjugate_transitive(
            root, StemTemplate.TELIC_IMPERFECT, Evidential.MYTHICAL,
            subj_person=Person.THIRD, subj_gender=Gender.MALE,
        )
        assert "sher" in result

    def test_intention(self):
        root = TetraRoot("k", "m", "d", "r")
        result = conjugate_transitive(
            root, StemTemplate.TELIC_IMPERFECT, Evidential.INTENTION,
            subj_person=Person.FIRST, subj_gender=Gender.MALE,
        )
        assert "ng" in result

    def test_optative(self):
        root = TetraRoot("k", "m", "d", "r")
        result = conjugate_transitive(
            root, StemTemplate.TELIC_IMPERFECT, Evidential.OPTATIVE,
            subj_person=Person.THIRD, subj_gender=Gender.MALE,
        )
        assert "ya" in result

    def test_deliberative(self):
        root = TetraRoot("k", "m", "d", "r")
        result = conjugate_transitive(
            root, StemTemplate.TELIC_IMPERFECT, Evidential.DELIBERATIVE,
            subj_person=Person.THIRD, subj_gender=Gender.MALE,
        )
        assert "yam" in result
