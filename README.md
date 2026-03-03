# Aelaki Merged

A consolidated archive of all documentation, implementations, and reference materials for **Aelaki** (also written Allochy) -- a constructed language (conlang) designed for a science fiction setting on a ringworld called Gaiad/Ngorno.

## About Aelaki

Aelaki is a linguistically sophisticated conlang featuring:

- **Non-concatenative (templatic) morphology** -- words are built from triconsonantal roots with vowel patterns inserted to convey meaning, similar to Semitic languages
- **Four morphological operations**: base form, reduplication (plural/imperfective), umlaut/fronting (collective/perfective-completed), and zero-infix (negation)
- **Four grammatical genders**: Child, Female, Male, and Inanimate -- reflecting the speakers' biology as sequential hermaphrodites
- **Rich evidentiality system**: 16+ evidential combinations marking how the speaker knows what they're saying (visual, hearsay, inferential, mythical, etc.)
- **Base-60 number system** with a base-12 subsystem
- **17 converb types** for complex clause chaining
- **Head-marking morphology** with a 6-case system

## Repository Structure

```
aelaki-merged/
├── docs/                           # Exported documents and spreadsheets
│   ├── Aelaki Grammar Guide.docx   # ** Most authoritative grammar reference **
│   ├── Aelaki proto language.docx   # Proto-Aelaki reconstruction
│   ├── Aelaki Converbs.xlsx         # Converb paradigm tables
│   ├── Aelaki Tense Aspect Mood.xlsx# TAM system tables
│   └── Proto-aelaki verbs.xlsx      # Proto-Aelaki verb inventory
│
├── aelaki-sharp/                    # C# implementation of Aelaki morphology
│   ├── Aelaki.sln                   # .NET 8.0 solution
│   └── General console/            # Console app with noun, verb, adjective,
│       ├── Program.cs               #   converb, number, and phrase generation
│       ├── Noun.cs                  #   implementing the full templatic system
│       ├── TransitiveVerb.cs
│       ├── AelakiNumber.cs
│       └── ...
│
├── aelaki-split/                    # Markdown documentation and Python tools
│   ├── Aelaki Grammar Guide.md      # Comprehensive grammar guide (~31k lines)
│   ├── aelaki_morphology.py         # Python morphological transformer
│   ├── worldbuilding/               # 17 files covering:
│   │   ├── aelaki.md                #   - Language roots, lexicon, conjugations
│   │   ├── aelaki_roots.md          #   - Related languages (Ngornese, Aelyaki)
│   │   ├── ringworld_gaiad.md       #   - Ringworld setting and cosmology
│   │   ├── aelateun_religion.md     #   - Religion and creation myths
│   │   ├── the_divine_60.md         #   - Sexagenary calendar system
│   │   └── ...                      #   - Culture, ecology, test sentences
│   └── README.md
│
├── wiki/                            # MediaWiki export
│   └── Aelaki+Wiki-20260303071909.xml
│
├── discord/                         # Personal message exports from conlangs
│   ├── Conlangs Discord Network.zip #   Discord server (author's messages only)
│   └── ...
│
└── README.md                        # This file
```

## Key References

| Resource | Location | Notes |
|----------|----------|-------|
| **Authoritative Grammar** | `docs/Aelaki Grammar Guide.docx` | The primary, most up-to-date grammar reference |
| Grammar Guide (Markdown) | `aelaki-split/Aelaki Grammar Guide.md` | Extensive markdown version (~31k lines) |
| TAM Tables | `docs/Aelaki Tense Aspect Mood.xlsx` | Tense/aspect/mood paradigm tables |
| Converb Tables | `docs/Aelaki Converbs.xlsx` | All 17 converb types |
| Proto-Aelaki | `docs/Aelaki proto language.docx` | Historical reconstruction |
| Worldbuilding | `aelaki-split/worldbuilding/` | Setting, religion, related languages |
| C# Implementation | `aelaki-sharp/` | Programmatic morphology generator |
| Python Morphology | `aelaki-split/aelaki_morphology.py` | Triconsonantal root transformer |

## Origins

This repository merges two previously separate repositories:

- **aelaki-sharp** -- A C# console application that programmatically generates Aelaki words and sentences according to the language's grammatical rules (64 commits of history preserved)
- **aelaki-split** -- Markdown documentation, Python tools, and worldbuilding materials (4 commits of history preserved)

Root-level documents (Google Docs/Sheets exports, wiki XML dump, and Discord message archives) were added separately.
