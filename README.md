# Aelaki Merged

A consolidated archive of all documentation, implementations, and reference materials for **Aelaki** (also written Allochy) -- a constructed language (conlang) designed for a science fiction setting on a ringworld called Gaiad/Ngorno.

## About Aelaki

Aelaki is a linguistically sophisticated conlang featuring:

- **Non-concatenative (templatic) morphology** -- words are built from triconsonantal roots with vowel patterns inserted to convey meaning, similar to Semitic languages
- **Four morphological operations**: base form, reduplication (plural/imperfective), umlaut/fronting (collective/perfective-completed), and zero-infix (negation)
- **Four grammatical genders**: Child, Female, Male, and Inanimate -- reflecting the speakers' biology as sequential hermaphrodites
- **Rich evidentiality system**: 21+ evidential/mood combinations marking how the speaker knows what they're saying (visual, hearsay, inferential, mythical, intentional, optative, deliberative, etc.)
- **Base-60 number system** with a base-12 subsystem and 6 semantic roles (cardinal, ordinal, partitive, fractional, collective, adverbial)
- **16 converb types** in two classes (prefix converbs retain TAM, suffix converbs consume TAM)
- **Head-marking morphology** with a 6-case system and ~50 Ki-syllable agreement clitics

## Python Grammar Generator (`aelaki/`)

A complete Python implementation of Aelaki morphology. Generate grammatically correct words and sentences from consonantal roots.

```python
from aelaki import TriRoot, TetraRoot, Gender, Number, Person
from aelaki.nouns import build_noun
from aelaki.verbs import conjugate_transitive, StemTemplate, Evidential
from aelaki.numerals import all_roles
from aelaki.phrases import NounPhrase, VerbPhrase, Clause

# Generate a noun: k-m-d-r in masculine singular
build_noun(TetraRoot("k", "m", "d", "r"), Gender.MALE, Number.SINGULAR)
# => "kamudara"

# Conjugate a transitive verb with past visual evidential
conjugate_transitive(
    TetraRoot("k", "m", "d", "r"), StemTemplate.TELIC_IMPERFECT,
    Evidential.PAST_VISUAL,
    subj_person=Person.THIRD, subj_gender=Gender.MALE,
    obj_person=Person.FOURTH, obj_gender=Gender.FEMALE,
)
# => "shakamdorshëoko"

# All six numeral roles for 5
all_roles(5)
# => {'cardinal': 'Tan', 'ordinal': 'Talon', 'partitive': 'Tatan',
#     'fractional': 'Tanfel', 'collective': 'Tæn', 'adverbial': 'Tante'}
```

### Modules

| Module | What it does |
|--------|-------------|
| `phonology` | Vowel/consonant inventories, umlaut maps, sandhi rules |
| `roots` | TriRoot (3-consonant) and TetraRoot (4-consonant) classes |
| `morphology` | 4 core operations: base, reduplication, umlaut, zero-infix |
| `gender` | Gender, Number, Person enums with vowel mappings |
| `person` | Ki-syllable system (~50 clitics), case marking |
| `nouns` | Noun stem building for tri/tetra roots, all 4 numbers |
| `possession` | Alienable and inalienable possession constructions |
| `numerals` | Base-12/60 system with all 6 semantic roles |
| `verbs` | 11 stem templates, 21 evidentials, polypersonal agreement |
| `stative_verbs` | 7 aspect prefixes with continuous doubling |
| `adjectives` | 4 degrees, 8-way TAM, noun agreement |
| `adverbs` | 4 degree alternations, 19 tense-evidential combinations |
| `converbs` | Class I prefix (6 types) and Class II suffix (10 types) |
| `particles` | Yes/no, connectives, switch reference, questions, adpositions |
| `phrases` | NounPhrase, VerbPhrase, Clause with VSO word order |
| `lexicon` | Documented vocabulary roots with glosses |

### Running Tests

```bash
python -m pytest tests/ -v
```

108 tests covering morphology, nouns, verbs, numerals, converbs, and phrase composition.

## Repository Structure

```
aelaki-merged/
├── aelaki/                         # ** Python grammar generator **
│   ├── phonology.py ... phrases.py #   15 modules, 108 tests
│   └── lexicon.py
│
├── tests/                          # Test suite
│   ├── test_morphology.py
│   ├── test_nouns.py
│   ├── test_verbs.py
│   ├── test_numerals.py
│   ├── test_converbs.py
│   └── test_phrases.py
│
├── analysis/                       # Cross-source analysis
│   ├── SOURCE_COMPARISON.md        # Discrepancies between all sources
│   ├── MORPHOLOGY_INVENTORY.md     # Consolidated rule specification
│   └── PYTHON_IMPLEMENTATION_PLAN.md
│
├── docs/                           # Exported documents and spreadsheets
│   ├── Aelaki Grammar Guide.docx   # ** Most authoritative grammar reference **
│   ├── Aelaki proto language.docx
│   └── *.xlsx                      # Converbs, TAM, Proto-verbs tables
│
├── aelaki-sharp/                   # C# implementation (64 commits history)
├── aelaki-split/                   # Markdown docs & worldbuilding (4 commits)
├── wiki/                           # MediaWiki XML export
├── discord/                        # Discord message exports (JSON + assets)
└── README.md
```

## Key References

| Resource | Location | Notes |
|----------|----------|-------|
| **Authoritative Grammar** | `docs/Aelaki Grammar Guide.docx` | The primary, most up-to-date grammar reference |
| Grammar Guide (Markdown) | `aelaki-split/Aelaki Grammar Guide.md` | Extensive markdown version (~31k lines) |
| **Python Generator** | `aelaki/` | Full grammar implementation with tests |
| Source Comparison | `analysis/SOURCE_COMPARISON.md` | Where sources agree and disagree |
| C# Implementation | `aelaki-sharp/` | Reference implementation (.NET 8.0) |
| Worldbuilding | `aelaki-split/worldbuilding/` | Setting, religion, related languages |
| Discord Messages | `discord/` | 2,399 messages from conlangs server |

## Origins

This repository merges two previously separate repositories:

- **aelaki-sharp** -- A C# console application that programmatically generates Aelaki words and sentences according to the language's grammatical rules (64 commits of history preserved)
- **aelaki-split** -- Markdown documentation, Python tools, and worldbuilding materials (4 commits of history preserved)

Root-level documents (Google Docs/Sheets exports, wiki XML dump, and Discord message archives) were added separately.
