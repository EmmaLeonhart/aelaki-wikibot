"""Fix irregular noun roots in lexicon.json.

Fills in missing consonants (?), assigns genders (child/female/male),
and generates standard citation forms for nouns that were incorrectly irregular.

Standard triconsonantal noun citation forms (4th person singular):
  child:     C1-a-C2-u-C3-u
  female:    C1-a-C2-o-C3-o
  male:      C1-a-C2-a-C3-a
  inanimate: C1-a-C2-ïf-C3-ïf
"""

import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GENDER_VOWELS = {
    "child": "u",
    "female": "o",
    "male": "a",
    "inanimate": "ïf",
}


def citation_form(root, gender):
    """Generate standard triconsonantal citation form: C1-a-C2-V-C3-V."""
    v = GENDER_VOWELS[gender]
    c1, c2, c3 = root
    return f"{c1}a{c2}{v}{c3}{v}"


# Define fixes: old_key -> (new_root, gender, gloss, extra_fields)
# Consonants derived from word forms where possible; gaps filled with
# phonologically reasonable consonants from the standard inventory.
FIXES = {
    # Body parts (previously all had ? placeholders)
    "ae": {
        "new_key": "hwy",
        "root": ["h", "w", "y"],
        "gender": "child",
        "gloss": "head",
    },
    "euf": {
        "new_key": "vlf",
        "root": ["v", "l", "f"],
        "gender": "female",
        "gloss": "eye",
    },
    "on": {
        "new_key": "gwn",
        "root": ["g", "w", "n"],
        "gender": "male",
        "gloss": "mouth",
    },
    "ich": {
        "new_key": "rcht",
        "root": ["r", "ch", "t"],
        "gender": "child",
        "gloss": "heart",
    },
    "uch": {
        "new_key": "lchd",
        "root": ["l", "ch", "d"],
        "gender": "female",
        "gloss": "liver",
    },
    # Celestial / nature nouns
    "t'ub'": {
        "new_key": "tbr",
        "root": ["t", "b", "r"],
        "gender": "inanimate",  # keep existing
        "gloss": "sun (archaic/proto)",
    },
    "pu": {
        "new_key": "prv",
        "root": ["p", "r", "v"],
        "gender": "male",
        "gloss": "moon",
    },
    "lu": {
        "new_key": "lds",
        "root": ["l", "d", "s"],
        "gender": "inanimate",  # keep existing
        "gloss": "river",
    },
    "nek": {
        "new_key": "nvk",
        "root": ["n", "v", "k"],
        "gender": "inanimate",  # keep existing
        "gloss": "sea",
    },
    # Animals / beings
    "maomao": {
        "new_key": "mlm",
        "root": ["m", "l", "m"],
        "gender": "child",
        "gloss": "maomao (bear-sized companion)",
    },
    "dzhabho": {
        "new_key": "dzhbhr",
        "root": ["dzh", "bh", "r"],
        "gender": "female",
        "gloss": "bird",
    },
    # People
    "sanash": {
        "new_key": "snsh",
        "root": ["s", "n", "sh"],
        "gender": "male",
        "gloss": "king",
    },
    # Body / misc (user explicitly requested these two)
    "gar": {
        "new_key": "gthr",
        "root": ["g", "th", "r"],
        "gender": "child",
        "gloss": "body",
    },
    "gnk": {
        "new_key": "gnk",  # same key, just fix form
        "root": ["g'", "n", "k"],
        "gender": "male",
        "gloss": "sky fungus",
    },
}


def main():
    with open("aelaki/lexicon.json", "r", encoding="utf-8") as f:
        lexicon = json.load(f)

    nouns = lexicon["nouns"]

    for old_key, fix in FIXES.items():
        if old_key not in nouns:
            print(f"WARNING: key '{old_key}' not found in nouns, skipping")
            continue

        # Build new entry
        new_entry = {
            "root": fix["root"],
            "class": "noun",
            "gloss": fix["gloss"],
            "gender": fix["gender"],
            "citation_form": citation_form(fix["root"], fix["gender"]),
        }

        new_key = fix["new_key"]
        cf = new_entry["citation_form"]

        # Remove old entry
        del nouns[old_key]

        # Add new entry
        nouns[new_key] = new_entry

        print(f"  {old_key:12s} -> {new_key:8s}  root={fix['root']}  "
              f"gender={fix['gender']:10s}  citation={cf}")

    # Write back
    with open("aelaki/lexicon.json", "w", encoding="utf-8") as f:
        json.dump(lexicon, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Updated {len(FIXES)} noun entries.")


if __name__ == "__main__":
    main()
