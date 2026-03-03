"""Tests for noun morphology.

Validates noun stem building against C# reference implementation output.
"""

import pytest
from aelaki.roots import TetraRoot, TriRoot
from aelaki.gender import Gender, Number, Person
from aelaki.nouns import build_noun, build_tetra_stem, build_tri_stem


class TestTetraconsonantalNouns:
    """Test tetraconsonantal noun paradigm (k-m-d-r)."""

    def setup_method(self):
        self.root = TetraRoot("k", "m", "d", "r")

    def test_male_singular(self):
        assert build_tetra_stem(self.root, Gender.MALE, Number.SINGULAR) == "kamudara"

    def test_male_plural(self):
        assert build_tetra_stem(self.root, Gender.MALE, Number.PLURAL) == "kamumudara"

    def test_male_collective(self):
        result = build_tetra_stem(self.root, Gender.MALE, Number.COLLECTIVE)
        assert result == "kæmidæræ"

    def test_male_zero(self):
        result = build_tetra_stem(self.root, Gender.MALE, Number.ZERO)
        assert "f" in result

    def test_female_singular(self):
        assert build_tetra_stem(self.root, Gender.FEMALE, Number.SINGULAR) == "kamudoro"

    def test_female_plural(self):
        assert build_tetra_stem(self.root, Gender.FEMALE, Number.PLURAL) == "kamumudoro"

    def test_child_singular(self):
        assert build_tetra_stem(self.root, Gender.CHILD, Number.SINGULAR) == "kamuduru"

    def test_child_collective(self):
        result = build_tetra_stem(self.root, Gender.CHILD, Number.COLLECTIVE)
        assert result == "kæmidiri"

    def test_person_suffix_first(self):
        result = build_noun(self.root, Gender.MALE, Number.SINGULAR, Person.FIRST)
        assert result.endswith("th")

    def test_person_suffix_second(self):
        result = build_noun(self.root, Gender.MALE, Number.SINGULAR, Person.SECOND)
        assert result.endswith("j")

    def test_person_suffix_third(self):
        result = build_noun(self.root, Gender.MALE, Number.SINGULAR, Person.THIRD)
        assert result.endswith("sh")

    def test_person_suffix_fourth(self):
        # Fourth person has no suffix
        result = build_noun(self.root, Gender.MALE, Number.SINGULAR, Person.FOURTH)
        assert result == "kamudara"


class TestTriconsonantalNouns:
    """Test triconsonantal noun paradigm (b-s-l)."""

    def setup_method(self):
        self.root = TriRoot("b", "s", "l")

    def test_female_singular(self):
        assert build_tri_stem(self.root, Gender.FEMALE, Number.SINGULAR) == "basolo"

    def test_female_plural(self):
        assert build_tri_stem(self.root, Gender.FEMALE, Number.PLURAL) == "basosolo"

    def test_male_singular(self):
        assert build_tri_stem(self.root, Gender.MALE, Number.SINGULAR) == "basala"

    def test_male_collective(self):
        result = build_tri_stem(self.root, Gender.MALE, Number.COLLECTIVE)
        assert result == "bæsælæ"


class TestBuildNounUnified:
    """Test the unified build_noun interface."""

    def test_tetra_root(self):
        r = TetraRoot("k", "m", "d", "r")
        assert build_noun(r, Gender.MALE, Number.SINGULAR) == "kamudara"

    def test_tri_root(self):
        r = TriRoot("b", "s", "l")
        assert build_noun(r, Gender.FEMALE, Number.SINGULAR) == "basolo"

    def test_unsupported_root_type(self):
        with pytest.raises(TypeError):
            build_noun("not_a_root", Gender.MALE, Number.SINGULAR)
