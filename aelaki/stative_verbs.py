"""Stative verb prefix system for Aelaki.

Stative verbs have a special prefix system that modifies aspect.
Each prefix can be doubled for continuous/progressive meaning.

Base stative has only two aspects:
- Standard (base vowels)
- Gnomic (umlaut vowels - universal truths)
"""

from __future__ import annotations
from enum import Enum

from .phonology import apply_umlaut


class StativePrefix(Enum):
    """Stative verb aspect prefixes."""
    NONE = ""              # Base form
    PROBABLE = "ho"        # About to / probable
    INCHOATIVE = "nü"     # Start to / began
    CESSATIVE = "nï"      # Stop / finished
    RESUMPTIVE = "lu"      # Resume / remember
    REPETITIVE_CESS = "li" # Re-stop / re-forget
    ALMOST = "ko"          # Nearly / almost
    ALMOST_CESS = "ke"     # Almost stopped


# Doubled prefix for continuous aspect
CONTINUOUS_PREFIXES: dict[StativePrefix, str] = {
    StativePrefix.NONE: "",
    StativePrefix.PROBABLE: "hoho",
    StativePrefix.INCHOATIVE: "nünü",
    StativePrefix.CESSATIVE: "nïnï",
    StativePrefix.RESUMPTIVE: "lulu",
    StativePrefix.REPETITIVE_CESS: "lili",
    StativePrefix.ALMOST: "koko",
    StativePrefix.ALMOST_CESS: "keke",
}

# Semantic glosses
STATIVE_GLOSSES: dict[StativePrefix, tuple[str, str]] = {
    StativePrefix.NONE:            ("standard",              "standard (continuous)"),
    StativePrefix.PROBABLE:        ("probable / about to",   "keeps being about to"),
    StativePrefix.INCHOATIVE:      ("begin / start to",      "in process of beginning"),
    StativePrefix.CESSATIVE:       ("stop / finish",         "in process of stopping"),
    StativePrefix.RESUMPTIVE:      ("resume / remember",     "in process of resuming"),
    StativePrefix.REPETITIVE_CESS: ("re-stop / re-forget",   "keeps re-stopping"),
    StativePrefix.ALMOST:          ("almost / nearly",       "keeps almost doing"),
    StativePrefix.ALMOST_CESS:     ("almost stopped",        "keeps almost stopping"),
}


def build_stative_stem(
    base_stem: str,
    prefix: StativePrefix = StativePrefix.NONE,
    gnomic: bool = False,
    continuous: bool = False,
) -> str:
    """Build a stative verb stem with prefix and aspect.

    Args:
        base_stem: The base verb stem (e.g., "zoduk" for "know")
        prefix: Aspect prefix (inchoative, cessative, etc.)
        gnomic: If True, apply umlaut for gnomic/universal aspect
        continuous: If True, double the prefix for continuous meaning
    """
    # Apply gnomic umlaut if needed
    stem = apply_umlaut(base_stem) if gnomic else base_stem

    # Apply prefix
    if continuous:
        pfx = CONTINUOUS_PREFIXES[prefix]
    else:
        pfx = prefix.value

    return pfx + stem


def stative_paradigm(base_stem: str) -> dict[str, str]:
    """Generate the full stative prefix paradigm for a stem.

    Returns dict with keys like "probable", "inchoative_continuous", etc.
    """
    results: dict[str, str] = {}

    for prefix in StativePrefix:
        name = prefix.name.lower()
        # Standard
        results[name] = build_stative_stem(base_stem, prefix, gnomic=False)
        # Gnomic
        results[f"{name}_gnomic"] = build_stative_stem(base_stem, prefix, gnomic=True)
        # Continuous
        if prefix != StativePrefix.NONE:
            results[f"{name}_continuous"] = build_stative_stem(
                base_stem, prefix, gnomic=False, continuous=True)
            results[f"{name}_gnomic_continuous"] = build_stative_stem(
                base_stem, prefix, gnomic=True, continuous=True)

    return results
