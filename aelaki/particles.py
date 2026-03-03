"""Small words, particles, and adpositions for Aelaki.

Contains all grammatical particles organized by function:
- Affirmatives/negatives (yes/no)
- Connectives (and, and-not)
- Switch reference and focus
- Question particles
- Spatial adpositions
- Temporal adpositions
- Copula forms
"""

from __future__ import annotations
from dataclasses import dataclass


# ===========================================================================
# Affirmatives & Negatives
# ===========================================================================
# Note: Zero-infix /f/ NEVER appears in yes/no particles.

@dataclass(frozen=True)
class YesNoParticle:
    base: str           # Singular/simple
    reduplicated: str   # Discursive (continuing)
    umlaut: str         # Final / emphatic
    redup_umlaut: str   # Maximally emphatic

YES = YesNoParticle("Su", "Susu", "Si", "Sisi")
NO = YesNoParticle("Fu", "Fufu", "Fi", "Fifi")


# ===========================================================================
# Connectives
# ===========================================================================

CONNECTIVES = {
    "and_continues": "Zuzu",   # And (list continues)
    "and_ends": "Zu",          # And (list ends, non-exhaustive)
    "and_exhaustive": "Zi",    # And (exhaustive list)
    "and_not": "Zuf",          # And NOT / excluding
}


# ===========================================================================
# Switch Reference & Focus
# ===========================================================================

SWITCH_REFERENCE = {
    "known_referent": "No",     # Switch to known referent; partitive
    "new_referent": "Nono",     # Introduce new referent
    "merge_referents": "Ne",    # Merge previous and current referents
    "except_referent": "Nof",   # Negate / except this referent
}


# ===========================================================================
# Question Particles
# ===========================================================================

QUESTION_PARTICLES = {
    "what": "Shu",              # What / yes-no question marker
    "discuss": "Shushu",        # Discuss / explain
    "final_answer": "Shi",      # Give final answer
}


# ===========================================================================
# Spatial Adpositions (Locative)
# ===========================================================================

@dataclass(frozen=True)
class AdpositionSet:
    """A set of related adpositions with base, reduplicated, umlaut, and question forms."""
    base: str
    reduplicated: str
    umlaut: str
    question_base: str
    question_redup: str
    question_umlaut: str

SPATIAL = AdpositionSet(
    base="Snü",              # At
    reduplicated="Snüsnü",   # Through
    umlaut="Snï",            # Final location (goal)
    question_base="Snüf",    # Where? (at)
    question_redup="Snüfsnüf",  # Where through?
    question_umlaut="Snïf",     # Where going?
)

TEMPORAL = AdpositionSet(
    base="Slë",              # At a time
    reduplicated="Slëslë",   # Throughout duration
    umlaut="Slæ",            # Completion time
    question_base="Slëf",    # What time?
    question_redup="Slëfslë",   # What time period?
    question_umlaut="Slæf",     # What time did it end?
)


# ===========================================================================
# Copula
# ===========================================================================

COPULA = {
    "identity": "Zon",    # Connected nouns are identical
    "list_end": "Zen",    # Ends identity list
    "exist": "Lake",      # Existential ("exists")
}


# ===========================================================================
# Convenience accessors
# ===========================================================================

def yes(emphasis: int = 0) -> str:
    """Return yes particle at given emphasis level (0-3)."""
    return [YES.base, YES.reduplicated, YES.umlaut, YES.redup_umlaut][min(emphasis, 3)]


def no(emphasis: int = 0) -> str:
    """Return no particle at given emphasis level (0-3)."""
    return [NO.base, NO.reduplicated, NO.umlaut, NO.redup_umlaut][min(emphasis, 3)]


def question(word: str) -> str:
    """Append question particle Shu to a word/phrase."""
    return f"{word} {QUESTION_PARTICLES['what']}"


def spatial_at(location: str) -> str:
    """Mark a location with the 'at' adposition."""
    return f"{SPATIAL.base} {location}"


def temporal_at(time: str) -> str:
    """Mark a time with the 'at' adposition."""
    return f"{TEMPORAL.base} {time}"
