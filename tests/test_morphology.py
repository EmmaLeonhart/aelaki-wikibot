"""Tests for core morphological operations.

Validates the 4 fundamental operations against documented examples
from the grammar guide and existing Python script.
"""

import pytest
from aelaki.morphology import (
    tri_base, tri_reduplicate, tri_umlaut, tri_zero_infix, tri_all_forms,
    base_form, reduplicate, umlaut, zero_infix,
)
from aelaki.roots import TriRoot, TetraRoot


class TestTriconsonantalOperations:
    """Test the 4 core operations on triconsonantal roots."""

    def test_dapaz_base(self):
        assert tri_base("d", "a", "p", "a", "z") == "dapaz"

    def test_dapaz_reduplication(self):
        assert tri_reduplicate("d", "a", "p", "a", "z") == "dapapaz"

    def test_dapaz_umlaut(self):
        assert tri_umlaut("d", "a", "p", "a", "z") == "dæpæz"

    def test_dapaz_zero_infix(self):
        assert tri_zero_infix("d", "a", "p", "a", "z") == "dafpaz"

    def test_goran_base(self):
        assert tri_base("g", "o", "r", "a", "n") == "goran"

    def test_goran_reduplication(self):
        assert tri_reduplicate("g", "o", "r", "o", "r") == "gororor"

    def test_goran_umlaut(self):
        assert tri_umlaut("g", "o", "r", "a", "n") == "gœræn"

    def test_goran_zero_infix(self):
        assert tri_zero_infix("g", "o", "r", "a", "n") == "gofran"

    def test_all_forms_returns_dict(self):
        forms = tri_all_forms("d", "a", "p", "a", "z")
        assert set(forms.keys()) == {"base", "reduplication", "umlaut", "zero_infix"}
        assert forms["base"] == "dapaz"


class TestRootObjectOperations:
    """Test operations via Root objects."""

    def test_tri_root_base(self):
        r = TriRoot("d", "p", "z")
        assert base_form(r, "a", "a") == "dapaz"

    def test_tri_root_reduplicate(self):
        r = TriRoot("d", "p", "z")
        assert reduplicate(r, "a", "a") == "dapapaz"

    def test_tetra_root_base(self):
        r = TetraRoot("k", "m", "d", "r")
        assert base_form(r, "a", "a") == "kamudara"

    def test_tetra_root_reduplicate(self):
        r = TetraRoot("k", "m", "d", "r")
        assert reduplicate(r, "a", "a") == "kamumudara"

    def test_tetra_root_umlaut(self):
        r = TetraRoot("k", "m", "d", "r")
        result = umlaut(r, "a", "a")
        # Collective shift: u->i, a->æ
        assert "i" in result  # u shifted to i
        assert "æ" in result  # a shifted to æ

    def test_tetra_root_zero(self):
        r = TetraRoot("k", "m", "d", "r")
        result = zero_infix(r, "a", "a")
        assert "f" in result  # Should contain f markers


class TestMultiCharConsonants:
    """Test that multi-character consonants work correctly."""

    def test_sh_root(self):
        r = TriRoot("sh", "k", "r")
        assert base_form(r, "a", "a") == "shakar"

    def test_th_root(self):
        r = TriRoot("th", "n", "g")
        assert base_form(r, "a", "a") == "thanag"

    def test_ng_root(self):
        r = TriRoot("ng", "r", "s")
        result = reduplicate(r, "a", "a")
        assert result == "ngararas"  # C1V1-C2V1-C2V2C3 = ng-a-r-a-r-a-s

    def test_zh_root(self):
        """Test zh-r-n (live) from grammar guide."""
        r = TriRoot("zh", "r", "n")
        assert base_form(r, "a", "a") == "zharan"
