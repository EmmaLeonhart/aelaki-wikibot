#!/usr/bin/env python3
"""Generate random Aelaki words from English lemmas via Wiktionary API.

Fetches English words from Wiktionary categories and generates Aelaki entries
with triconsonantal roots and phonologically correct citation forms.
Each run adds NEW entries, skipping duplicates by gloss.

Usage:
    python wiki-scripts/generate_random_words.py [--count 100] [--dry-run]
"""

import argparse
import json
import random
import re
import string
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from aelaki.phonology import CONSONANTS
from aelaki.roots import TriRoot, TetraRoot
from aelaki.gender import Gender, Number, Person
from aelaki.nouns import build_noun
from aelaki.verbs import (
    conjugate_intransitive_active,
    conjugate_intransitive_stative,
    conjugate_transitive,
    StemTemplate,
)
from aelaki.adjectives import realize_adjective
from aelaki.adverbs import realize_adverb

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WIKTIONARY_API = "https://en.wiktionary.org/w/api.php"
LEXICON_PATH = PROJECT_ROOT / "aelaki" / "lexicon.json"

CATEGORIES = {
    "nouns":      ("English_nouns",       0.40),
    "verbs":      ("English_verbs",       0.40),
    "adjectives": ("English_adjectives",  0.10),
    "adverbs":    ("English_adverbs",     0.10),
}

CONSONANT_LIST = sorted(CONSONANTS)
GENDERS = [Gender.CHILD, Gender.FEMALE, Gender.MALE, Gender.INANIMATE]
# Mostly active verbs, some stative
VERB_CLASSES = ["verb_active", "verb_active", "verb_active", "verb_stative"]

# ---------------------------------------------------------------------------
# Wiktionary fetching
# ---------------------------------------------------------------------------

def fetch_lemmas(category: str, count: int) -> list[str]:
    """Fetch English lemmas from a Wiktionary category.

    Uses a random starting sort key for variety across runs.
    Returns filtered candidates (lowercase, single-word, no digits/hyphens).
    """
    # Wiktionary normalizes sort keys to uppercase; use a random 2-letter
    # prefix for variety across runs.
    prefix = random.choice(string.ascii_uppercase) + random.choice(
        string.ascii_uppercase
    )

    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": str(min(count * 5, 500)),
        "cmstartsortkeyprefix": prefix,
        "cmnamespace": "0",
        "format": "json",
    }

    url = f"{WIKTIONARY_API}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "AelakiWordBot/1.0"})

    with urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    members = data.get("query", {}).get("categorymembers", [])
    titles = [m["title"] for m in members]

    # Filter: lowercase only, single word, alphabetic, at least 3 chars
    valid = []
    for title in titles:
        if not title or title[0].isupper():
            continue
        if not re.match(r"^[a-z]+$", title):
            continue
        if len(title) < 3:
            continue
        valid.append(title)

    random.shuffle(valid)
    return valid

# ---------------------------------------------------------------------------
# Lexicon I/O
# ---------------------------------------------------------------------------

def load_lexicon() -> dict:
    with open(LEXICON_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_lexicon(lexicon: dict) -> None:
    with open(LEXICON_PATH, "w", encoding="utf-8") as f:
        json.dump(lexicon, f, indent=2, ensure_ascii=False)
        f.write("\n")


def existing_glosses(lexicon: dict) -> set[str]:
    """Collect all existing glosses (normalized) to avoid duplicates."""
    glosses = set()
    for section in ("verbs", "nouns", "adjectives", "adverbs"):
        for entry in lexicon.get(section, {}).values():
            raw = entry["gloss"].replace(" (auto-generated)", "")
            glosses.add(raw.lower())
    return glosses


def existing_keys(lexicon: dict) -> set[str]:
    """Collect all existing root keys across all sections."""
    keys = set()
    for section in ("verbs", "nouns", "adjectives", "adverbs"):
        keys.update(lexicon.get(section, {}).keys())
    return keys

# ---------------------------------------------------------------------------
# Root generation
# ---------------------------------------------------------------------------

def generate_root_key(
    used_keys: set[str], n_consonants: int = 3
) -> tuple[list[str], str]:
    """Generate a unique root from the consonant inventory.

    Uses random.choices (with replacement) so roots like d-d-k are possible,
    but rejects roots where ALL consonants are identical.
    """
    for _ in range(1000):
        consonants = random.choices(CONSONANT_LIST, k=n_consonants)
        if len(set(consonants)) == 1:
            continue
        key = "".join(consonants)
        if key not in used_keys:
            return consonants, key
    raise RuntimeError("Could not generate unique root after 1000 attempts")

# ---------------------------------------------------------------------------
# Citation-form builders
# ---------------------------------------------------------------------------

def build_noun_citation(root: TriRoot, gender: Gender) -> str:
    return build_noun(root, gender, Number.SINGULAR, Person.FOURTH)


def build_verb_citation(root: TriRoot, verb_class: str) -> str:
    """Build verb citation: 4th person (unmarked), present."""
    if verb_class == "verb_stative":
        return conjugate_intransitive_stative(
            root, v1="a", v2="a",
            subj_person=Person.FOURTH,
            subj_gender=Gender.MALE,
            subj_number=Number.SINGULAR,
        )
    # verb_active (default)
    return conjugate_intransitive_active(
        root, v1="a", v2="a",
        subj_person=Person.FOURTH,
        subj_gender=Gender.MALE,
        subj_number=Number.SINGULAR,
    )


def build_transitive_citation(root: TetraRoot) -> str:
    return conjugate_transitive(
        root,
        template=StemTemplate.TELIC_PERFECT,
        subj_person=Person.FOURTH,
        subj_gender=Gender.MALE,
        subj_number=Number.SINGULAR,
    )


def build_adj_citation(root: TriRoot) -> str:
    return realize_adjective(
        root,
        noun_person=Person.FOURTH,
        noun_gender=Gender.MALE,
        noun_number=Number.SINGULAR,
    )


def build_adv_citation(root: TriRoot) -> str:
    return realize_adverb(root, v1="a", v2="a")

# ---------------------------------------------------------------------------
# Entry generation
# ---------------------------------------------------------------------------

def _make_entry(word: str, word_type: str, used_keys: set[str]):
    """Create a single lexicon entry. Returns (section, key, entry_dict)."""
    gloss = f"{word} (auto-generated)"

    if word_type == "nouns":
        consonants, key = generate_root_key(used_keys)
        root = TriRoot(*consonants)
        gender = random.choice(GENDERS)
        citation = build_noun_citation(root, gender)
        entry = {
            "root": consonants,
            "class": "noun",
            "gloss": gloss,
            "gender": gender.value,
            "citation_form": citation,
        }
        return "nouns", key, entry

    if word_type == "verbs":
        # ~15% chance of transitive (tetra root)
        if random.random() < 0.15:
            consonants, key = generate_root_key(used_keys, n_consonants=4)
            root = TetraRoot(*consonants)
            citation = build_transitive_citation(root)
            entry = {
                "root": consonants,
                "class": "verb_transitive",
                "gloss": gloss,
                "citation_form": citation,
            }
        else:
            verb_class = random.choice(VERB_CLASSES)
            consonants, key = generate_root_key(used_keys)
            root = TriRoot(*consonants)
            citation = build_verb_citation(root, verb_class)
            entry = {
                "root": consonants,
                "class": verb_class,
                "gloss": gloss,
                "citation_form": citation,
            }
        return "verbs", key, entry

    if word_type == "adjectives":
        consonants, key = generate_root_key(used_keys)
        root = TriRoot(*consonants)
        citation = build_adj_citation(root)
        entry = {
            "root": consonants,
            "class": "adjective",
            "gloss": gloss,
            "citation_form": citation,
        }
        return "adjectives", key, entry

    if word_type == "adverbs":
        consonants, key = generate_root_key(used_keys)
        root = TriRoot(*consonants)
        citation = build_adv_citation(root)
        entry = {
            "root": consonants,
            "class": "adverb",
            "gloss": gloss,
            "citation_form": citation,
        }
        return "adverbs", key, entry

    raise ValueError(f"Unknown word type: {word_type}")


def generate_entries(count: int, dry_run: bool = False) -> int:
    """Fetch lemmas, generate Aelaki entries, and write to lexicon.json.

    Returns the number of entries added.
    """
    lexicon = load_lexicon()
    known_glosses = existing_glosses(lexicon)
    used_keys = existing_keys(lexicon)

    # Per-category targets
    targets = {}
    for word_type, (_cat, ratio) in CATEGORIES.items():
        targets[word_type] = max(1, round(count * ratio))

    added = 0

    for word_type, (category, _ratio) in CATEGORIES.items():
        target = targets[word_type]

        try:
            candidates = fetch_lemmas(category, target)
        except (URLError, OSError) as exc:
            print(f"Warning: failed to fetch {word_type}: {exc}")
            continue

        type_added = 0
        for word in candidates:
            if type_added >= target:
                break

            if word.lower() in known_glosses:
                continue

            section, key, entry = _make_entry(word, word_type, used_keys)

            if dry_run:
                print(f"  [{section}] {key}: {entry['gloss']} -> {entry['citation_form']}")
            else:
                lexicon[section][key] = entry

            used_keys.add(key)
            known_glosses.add(word.lower())
            type_added += 1
            added += 1

    if not dry_run and added > 0:
        save_lexicon(lexicon)
        print(f"Added {added} entries to {LEXICON_PATH}")
    elif dry_run:
        print(f"\nDry run: would add {added} entries")
    else:
        print("No new entries to add")

    return added

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate random Aelaki words from English lemmas"
    )
    parser.add_argument(
        "--count", type=int, default=100,
        help="Number of words to generate (default: 100)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print entries without writing to lexicon",
    )
    args = parser.parse_args()

    generate_entries(args.count, args.dry_run)


if __name__ == "__main__":
    main()
