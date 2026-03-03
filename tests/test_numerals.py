"""Tests for the numeral system.

Validates cardinal, ordinal, partitive, fractional, collective,
and adverbial forms against the C# reference implementation and
grammar guide documentation.
"""

import pytest
from aelaki.numerals import (
    cardinal, ordinal, partitive, fractional_unit, collective,
    adverbial, fraction, all_roles, number_gender, cardinal_gendered,
)
from aelaki.gender import Gender


class TestCardinals:
    """Test cardinal number generation."""

    def test_units(self):
        assert cardinal(1) == "Pan"
        assert cardinal(2) == "Bal"
        assert cardinal(3) == "Bhan"
        assert cardinal(4) == "Mal"
        assert cardinal(5) == "Tan"
        assert cardinal(6) == "Dal"
        assert cardinal(7) == "Dhan"
        assert cardinal(8) == "Nal"
        assert cardinal(9) == "Kan"
        assert cardinal(10) == "Gal"
        assert cardinal(11) == "Ghan"
        assert cardinal(12) == "Nger"

    def test_teens(self):
        assert cardinal(13) == "NgerPan"
        assert cardinal(14) == "NgerBal"
        assert cardinal(15) == "NgerBhan"

    def test_dozens(self):
        assert cardinal(24) == "BalNger"
        assert cardinal(36) == "BhanNger"

    def test_dozens_with_units(self):
        assert cardinal(25) == "BalNgerPan"
        assert cardinal(37) == "BhanNgerPan"

    def test_sixty(self):
        assert cardinal(60) == "Vibhi"

    def test_above_sixty(self):
        assert cardinal(61) == "VibhiPan"
        assert cardinal(72) == "VibhiNger"

    def test_one_twenty(self):
        assert cardinal(120) == "BalVibhi"

    def test_large_number(self):
        assert cardinal(180) == "BhanVibhi"


class TestOrdinals:
    """Test ordinal number generation."""

    def test_first_through_twelfth(self):
        assert ordinal(1) == "Sekon"
        assert ordinal(2) == "Kezon"
        assert ordinal(3) == "Bhalon"
        assert ordinal(12) == "Ngeron"

    def test_sixtieth(self):
        assert ordinal(60) == "Vibhisekon"


class TestPartitives:
    """Test partitive forms (reduplicated)."""

    def test_basic_partitives(self):
        assert partitive(1) == "Papan"
        assert partitive(2) == "Babal"
        assert partitive(3) == "Bhabhan"
        assert partitive(12) == "Ngenger"

    def test_composite_partitives(self):
        assert partitive(13) == "NgerPapan"

    def test_sixty(self):
        assert partitive(60) == "Vibhibhi"


class TestFractionals:
    """Test fractional unit names."""

    def test_special_fractions(self):
        assert fractional_unit(1) == "Golo"
        assert fractional_unit(2) == "Kalakel"
        assert fractional_unit(3) == "Bhavel"

    def test_regular_fractions(self):
        assert fractional_unit(4) == "Malfel"
        assert fractional_unit(12) == "Ngerfel"


class TestCollective:
    """Test collective forms (vowel shift)."""

    def test_collective_two(self):
        # Bal -> Bæl
        result = collective(2)
        assert result == "Bæl"

    def test_collective_one(self):
        # Pan -> Pæn
        result = collective(1)
        assert result == "Pæn"


class TestAdverbial:
    """Test adverbial forms (cardinal + -te)."""

    def test_adverbial(self):
        assert adverbial(1) == "Pante"
        assert adverbial(2) == "Balte"
        assert adverbial(12) == "Ngerte"
        assert adverbial(30) == "BalNgerDalte"


class TestFractions:
    """Test fraction generation."""

    def test_one_half(self):
        assert fraction(1, 2) == "Papan Kalakel"

    def test_three_fourths(self):
        assert fraction(3, 4) == "Bhabhan Malfel"

    def test_five_twelfths(self):
        assert fraction(5, 12) == "Tatan Ngerfel"


class TestNumberGender:
    """Test inherent gender of numbers."""

    def test_one_is_child(self):
        assert number_gender(1) == Gender.CHILD

    def test_ten_is_child(self):
        assert number_gender(10) == Gender.CHILD

    def test_even_is_female(self):
        assert number_gender(2) == Gender.FEMALE
        assert number_gender(4) == Gender.FEMALE
        assert number_gender(8) == Gender.FEMALE

    def test_odd_is_male(self):
        assert number_gender(3) == Gender.MALE
        assert number_gender(5) == Gender.MALE
        assert number_gender(9) == Gender.MALE


class TestAllRoles:
    """Test the all_roles convenience function."""

    def test_returns_all_six(self):
        roles = all_roles(5)
        assert set(roles.keys()) == {
            "cardinal", "ordinal", "partitive",
            "fractional", "collective", "adverbial",
        }
        assert roles["cardinal"] == "Tan"
        assert roles["ordinal"] == "Talon"
        assert roles["partitive"] == "Tatan"
        assert roles["adverbial"] == "Tante"
