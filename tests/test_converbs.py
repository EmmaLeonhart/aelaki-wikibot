"""Tests for converb morphology."""

import pytest
from aelaki.roots import TetraRoot, TriRoot
from aelaki.gender import Gender, Number, Person
from aelaki.verbs import StemTemplate, Evidential, DayPrefix
from aelaki.converbs import (
    ConverbPrefixType, ConverbSuffixType,
    build_prefix_converb_transitive,
    build_suffix_converb_transitive,
    build_prefix_converb_intransitive,
    build_suffix_converb_intransitive,
)


class TestClassIPrefixConverbs:
    """Test Class I (prefix) converbs that retain TAM."""

    def setup_method(self):
        self.root = TetraRoot("k", "m", "d", "r")

    def test_purposive_prefix(self):
        result = build_prefix_converb_transitive(
            ConverbPrefixType.PURPOSIVE, self.root, StemTemplate.TELIC_IMPERFECT,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert result.startswith("ki")

    def test_causal_prefix(self):
        result = build_prefix_converb_transitive(
            ConverbPrefixType.CAUSAL, self.root, StemTemplate.TELIC_IMPERFECT,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert result.startswith("ha")

    def test_conditional_prefix(self):
        result = build_prefix_converb_transitive(
            ConverbPrefixType.CONDITIONAL, self.root, StemTemplate.TELIC_IMPERFECT,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert result.startswith("sa")

    def test_retains_evidential(self):
        result = build_prefix_converb_transitive(
            ConverbPrefixType.PURPOSIVE, self.root, StemTemplate.TELIC_IMPERFECT,
            Evidential.INFERENTIAL,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert "mu" in result

    def test_intransitive_prefix(self):
        root = TriRoot("zh", "r", "n")
        result = build_prefix_converb_intransitive(
            ConverbPrefixType.CAUSAL, root,
            subj_person=Person.FIRST, subj_gender=Gender.MALE)
        assert result.startswith("ha")


class TestClassIISuffixConverbs:
    """Test Class II (suffix) converbs that consume TAM."""

    def setup_method(self):
        self.root = TetraRoot("k", "m", "d", "r")

    def test_posterior_suffix(self):
        result = build_suffix_converb_transitive(
            ConverbSuffixType.POSTERIOR, self.root, StemTemplate.TELIC_IMPERFECT,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert result.endswith("shëlon")

    def test_sequential_suffix(self):
        result = build_suffix_converb_transitive(
            ConverbSuffixType.SEQUENTIAL, self.root, StemTemplate.TELIC_IMPERFECT,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert result.endswith("lon")

    def test_terminative_suffix(self):
        result = build_suffix_converb_transitive(
            ConverbSuffixType.TERMINATIVE, self.root, StemTemplate.TELIC_IMPERFECT,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert result.endswith("ndor")

    def test_beneficiary_suffix(self):
        result = build_suffix_converb_transitive(
            ConverbSuffixType.BENEFICIARY, self.root, StemTemplate.TELIC_IMPERFECT,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert result.endswith("rum")

    def test_with_day_prefix(self):
        result = build_suffix_converb_transitive(
            ConverbSuffixType.POSTERIOR, self.root, StemTemplate.TELIC_IMPERFECT,
            DayPrefix.HESTERNAL,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert result.startswith("goki")

    def test_intransitive_suffix(self):
        root = TriRoot("zh", "r", "n")
        result = build_suffix_converb_intransitive(
            ConverbSuffixType.LOCATIVE, root,
            subj_person=Person.THIRD, subj_gender=Gender.MALE)
        assert result.endswith("lok")
