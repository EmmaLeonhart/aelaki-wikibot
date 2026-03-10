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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LEXICON_PATH = PROJECT_ROOT / "aelaki" / "lexicon.json"
TARGET_INANIMATE_RATIO = 0.10
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
    """Redistribute excess inanimate nouns. Returns count of changes."""
    lexicon = load_lexicon()
    nouns = lexicon.get("nouns", {})

    # Count current gender distribution
    total = len(nouns)
    inanimate_keys = [k for k, v in nouns.items() if v.get("gender") == "inanimate"]
    inanimate_count = len(inanimate_keys)
    target_count = max(1, round(total * TARGET_INANIMATE_RATIO))

    print(f"Nouns: {total} total, {inanimate_count} inanimate ({inanimate_count/total*100:.1f}%)")
    print(f"Target: {target_count} inanimate ({TARGET_INANIMATE_RATIO*100:.0f}%)")

    if inanimate_count <= target_count:
        print("Already at or below target. Nothing to do.")
        # Clear any stale old_citation_form entries
        cleared = _clear_stale_migrations(nouns, set())
        if cleared and not dry_run:
            save_lexicon(lexicon)
            print(f"Cleared {cleared} stale old_citation_form entries.")
        return 0

    excess = inanimate_count - target_count
    print(f"Need to reassign {excess} inanimate nouns.")

    # Sort for deterministic ordering, then pick which ones to reassign
    # Use a global seed so the selection is stable
    rng = random.Random(42)
    # Only reassign auto-generated nouns (not hand-curated ones)
    auto_inanimate = [k for k in inanimate_keys
                      if "(auto-generated)" in nouns[k].get("gloss", "")]
    # If not enough auto-generated, fall back to all inanimate
    if len(auto_inanimate) < excess:
        candidates = sorted(inanimate_keys)
    else:
        candidates = sorted(auto_inanimate)

    rng.shuffle(candidates)
    to_reassign = candidates[:excess]
    to_reassign_set = set(to_reassign)

    changes = 0
    for key in to_reassign:
        entry = nouns[key]

        # Skip entries already being migrated (old_citation_form set this run)
        if entry.get("old_citation_form"):
            # Already has an old_citation_form — check if gender already changed
            if entry["gender"] != "inanimate":
                continue

        # Deterministic gender assignment per root key
        key_rng = random.Random(deterministic_seed(key))
        new_gender = key_rng.choice(ANIMATE_GENDERS)

        root = entry["root"]
        if len(root) != 3:
            print(f"  SKIP {key}: non-triconsonantal root ({len(root)} consonants)")
            continue

        old_citation = entry.get("citation_form", "")
        new_citation = compute_citation_form(root, new_gender)

        if dry_run:
            print(f"  {key}: {entry['gender']} -> {new_gender.value} "
                  f"({old_citation} -> {new_citation})")
        else:
            entry["gender"] = new_gender.value
            entry["old_citation_form"] = old_citation
            entry["citation_form"] = new_citation

        changes += 1

    # Clear stale old_citation_form on entries NOT being changed
    cleared = _clear_stale_migrations(nouns, to_reassign_set)

    if not dry_run and (changes > 0 or cleared > 0):
        save_lexicon(lexicon)

    print(f"\n{'Would reassign' if dry_run else 'Reassigned'} {changes} nouns.")
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
