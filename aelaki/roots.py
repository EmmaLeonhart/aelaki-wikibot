"""Root representation for Aelaki words.

Aelaki uses non-concatenative morphology with triconsonantal and
tetraconsonantal roots. Roots are stored as lists of strings to
support multi-character consonants (sh, th, ng, kx, etc.).
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Root:
    """Base class for a consonantal root."""
    consonants: tuple[str, ...]

    @property
    def size(self) -> int:
        return len(self.consonants)

    def __getitem__(self, idx: int) -> str:
        return self.consonants[idx]

    def __repr__(self) -> str:
        return f"Root({'-'.join(self.consonants)})"


class TriRoot(Root):
    """A triconsonantal root (C1, C2, C3).

    Primary root type for intransitive verbs and basic nouns.
    Example: d-p-z (shoot), g-r-n (bright), zh-r-n (live)
    """

    def __init__(self, c1: str, c2: str, c3: str):
        super().__init__(consonants=(c1, c2, c3))

    @property
    def c1(self) -> str:
        return self.consonants[0]

    @property
    def c2(self) -> str:
        return self.consonants[1]

    @property
    def c3(self) -> str:
        return self.consonants[2]


class TetraRoot(Root):
    """A tetraconsonantal root (C1, C2, C3, C4).

    Used for transitive verbs and some nouns.
    Example: k-m-d-r (worship/ritual)
    """

    def __init__(self, c1: str, c2: str, c3: str, c4: str):
        super().__init__(consonants=(c1, c2, c3, c4))

    @property
    def c1(self) -> str:
        return self.consonants[0]

    @property
    def c2(self) -> str:
        return self.consonants[1]

    @property
    def c3(self) -> str:
        return self.consonants[2]

    @property
    def c4(self) -> str:
        return self.consonants[3]


def parse_triconsonantal(word: str) -> tuple[str, str, str, str, str] | None:
    """Parse a 5-character triconsonantal word into (C1, V1, C2, V2, C3).

    Simple parser for basic C-V-C-V-C words where each segment is one
    character. For multi-character consonants, use TriRoot directly.

    Returns None if the word doesn't match the expected pattern.
    """
    if len(word) != 5:
        return None
    c1, v1, c2, v2, c3 = word[0], word[1], word[2], word[3], word[4]
    return (c1, v1, c2, v2, c3)
