#!/usr/bin/env python3
"""Normalize the Aelaki lexicon.

Idempotent script that runs every pipeline cycle to enforce lexicon invariants:
- Redistributes excess inanimate nouns to child/female/male (target: ~10% inanimate)
- Sets old_citation_form on changed entries for page-move tracking
- Clears old_citation_form on entries not being changed this run (stale migrations)

Uses deterministic seeding per root key so redistributions are stable across runs.

Usage:
    python wiki-scripts/normalize_lexicon.py [--dry-run]
"""

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from aelaki.phonology import CONSONANTS
from aelaki.roots import TriRoot
from aelaki.gender import Gender, Number, Person
from aelaki.nouns import build_noun
from wiktionary_countability import check_uncountable

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEXICON_PATH = PROJECT_ROOT / "aelaki" / "lexicon.json"
ANIMATE_GENDERS = [Gender.CHILD, Gender.FEMALE, Gender.MALE]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def deterministic_seed(root_key: str) -> int:
    """Create a stable seed from a root key so gender assignment is repeatable."""
    return int(hashlib.sha256(root_key.encode()).hexdigest(), 16) % (2**32)


def compute_citation_form(root_consonants: list[str], gender: Gender) -> str:
    """Compute the noun citation form (4th person singular) for a given gender."""
    root = TriRoot(*root_consonants[:3])
    return build_noun(root, gender, Number.SINGULAR, Person.FOURTH)


def load_lexicon() -> dict:
    with open(LEXICON_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_lexicon(lexicon: dict) -> None:
    with open(LEXICON_PATH, "w", encoding="utf-8") as f:
        json.dump(lexicon, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def normalize(dry_run: bool = False) -> int:
    """Assign noun genders based on Wiktionary countability. Returns count of changes.

    Uncountable nouns (per Category:English_uncountable_nouns) become inanimate.
    Countable nouns that are currently inanimate get reassigned to an animate gender.
    Only auto-generated nouns are touched; hand-curated entries are left alone.
    """
    lexicon = load_lexicon()
    nouns = lexicon.get("nouns", {})

    # Collect auto-generated nouns and their English glosses
    auto_nouns = {}
    for key, entry in nouns.items():
        gloss = entry.get("gloss", "")
        if "(auto-generated)" in gloss:
            word = gloss.replace(" (auto-generated)", "").strip()
            auto_nouns[key] = word

    total = len(nouns)
    inanimate_count = sum(1 for v in nouns.values() if v.get("gender") == "inanimate")
    print(f"Nouns: {total} total, {inanimate_count} inanimate ({inanimate_count/total*100:.1f}%)")
    print(f"Auto-generated nouns to check: {len(auto_nouns)}")

    if not auto_nouns:
        cleared = _clear_stale_migrations(nouns, set())
        if cleared and not dry_run:
            save_lexicon(lexicon)
        return 0

    # Batch-check countability via Wiktionary
    unique_words = list(set(auto_nouns.values()))
    uncountable = check_uncountable(unique_words)
    print(f"Wiktionary: {len(uncountable)} uncountable out of {len(unique_words)} checked")

    changes = 0
    changed_keys = set()

    for key, word in auto_nouns.items():
        entry = nouns[key]
        current_gender = entry.get("gender")
        should_be_inanimate = word.lower() in uncountable

        root = entry["root"]
        if len(root) != 3:
            continue

        if should_be_inanimate and current_gender != "inanimate":
            # Countable→uncountable: make inanimate
            old_citation = entry.get("citation_form", "")
            new_citation = compute_citation_form(root, Gender.INANIMATE)
            if dry_run:
                print(f"  {key}: {current_gender} -> inanimate ({word})")
            else:
                entry["gender"] = "inanimate"
                entry["old_citation_form"] = old_citation
                entry["citation_form"] = new_citation
            changes += 1
            changed_keys.add(key)

        elif not should_be_inanimate and current_gender == "inanimate":
            # Uncountable→countable: make animate
            key_rng = random.Random(deterministic_seed(key))
            new_gender = key_rng.choice(ANIMATE_GENDERS)
            old_citation = entry.get("citation_form", "")
            new_citation = compute_citation_form(root, new_gender)
            if dry_run:
                print(f"  {key}: inanimate -> {new_gender.value} ({word})")
            else:
                entry["gender"] = new_gender.value
                entry["old_citation_form"] = old_citation
                entry["citation_form"] = new_citation
            changes += 1
            changed_keys.add(key)

    # Clear stale old_citation_form on entries NOT being changed
    cleared = _clear_stale_migrations(nouns, changed_keys)

    if not dry_run and (changes > 0 or cleared > 0):
        save_lexicon(lexicon)

    new_inanimate = sum(1 for v in nouns.values() if v.get("gender") == "inanimate")
    print(f"\n{'Would change' if dry_run else 'Changed'} {changes} nouns "
          f"based on Wiktionary countability.")
    print(f"Inanimate nouns: {inanimate_count} -> {new_inanimate}")
    if cleared:
        print(f"Cleared {cleared} stale old_citation_form entries.")

    return changes


def _clear_stale_migrations(nouns: dict, active_keys: set) -> int:
    """Clear old_citation_form on entries not in the active migration set."""
    cleared = 0
    for key, entry in nouns.items():
        if key not in active_keys and entry.get("old_citation_form"):
            del entry["old_citation_form"]
            cleared += 1
    return cleared


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Normalize Aelaki lexicon (redistribute inanimate nouns)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print changes without writing to lexicon",
    )
    args = parser.parse_args()
    normalize(args.dry_run)


if __name__ == "__main__":
    main()
