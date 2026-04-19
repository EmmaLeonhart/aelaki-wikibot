# Python Grammar Generator - Implementation Plan

## Goal
Build a Python program that can generate all grammatical forms of Aelaki words from roots, producing correct morphology for nouns, verbs, adjectives, adverbs, numerals, converbs, and full phrases.

## Why the Existing Code Is Insufficient

### Existing Python Script (`aelaki-split/aelaki_morphology.py`)
- Only implements 4 basic operations (base, reduplication, umlaut, zero-infix) on triconsonantal roots
- Hardcoded to 5-character strings (C1V1C2V2C3)
- No support for multi-character consonants (sh, th, ng, kx, etc.)
- No gender, number, person, or case morphology
- No verb conjugation, evidentiality, or TAM
- No Ki-syllable system
- No converbs, adjectives, adverbs, or numerals
- Essentially a proof-of-concept for one small piece of the grammar

### Existing C# Code (`aelaki-sharp/`)
- Much more complete but has gaps (no inanimate gender, no stative verb prefixes, no day prefixes)
- Only tetraconsonantal roots for nouns/verbs
- Several NotImplementedException stubs for triconsonantal forms
- Mixed/duplicated enum definitions across files
- Hardcoded demo rather than general-purpose API

## Proposed Python Module Structure

```
aelaki/
    __init__.py
    phonology.py          # Vowel maps, consonant inventory, umlaut, sandhi rules
    roots.py              # Root class (tri/tetra), validation, consonant extraction
    morphology.py         # 4 core operations: base, reduplication, umlaut, zero-infix
    gender.py             # Gender enum, vowel mappings, agreement rules
    person.py             # Person/number enums, Ki-syllable tables
    nouns.py              # Noun stem building, plurality, case marking
    possession.py         # Alienable/inalienable possession
    verbs.py              # Verb stem templates, evidentiality, TAM
    stative_verbs.py      # Stative verb prefixes (Ho-, Nu-, Ni-, Lu-, etc.)
    adjectives.py         # Adjective agreement, TAM subset
    adverbs.py            # Adverb formation, tense agreement
    converbs.py           # Class I (prefix) and Class II (suffix) converbs
    numerals.py           # Base-12/60 system, all 6 semantic roles
    particles.py          # Small words, connectives, question particles, adpositions
    phrases.py            # NounPhrase, VerbPhrase, Clause composition
    lexicon.py            # Known roots with glosses

tests/
    test_morphology.py    # Core 4 operations against documented examples
    test_nouns.py         # Noun paradigm tables
    test_verbs.py         # Verb conjugation against C# reference output
    test_numerals.py      # Number generation 1-120+
    test_converbs.py      # All converb types
    test_phrases.py       # Full sentence generation
```

## Implementation Priority

### Phase 1: Core Foundation
1. `phonology.py` - Vowel/consonant inventories, umlaut maps, zero-infix rules
2. `roots.py` - Root parsing supporting multi-character consonants
3. `morphology.py` - 4 core operations for both tri and tetra roots
4. `gender.py` + `person.py` - Enums and lookup tables

### Phase 2: Nominals
5. `nouns.py` - Stem building for tri + tetra, all 4 pluralities
6. `possession.py` - Inalienable and alienable constructions
7. `numerals.py` - Full base-12/60 system with all 6 roles

### Phase 3: Verbals
8. `verbs.py` - All 11 templates, evidentiality, subject/object marking
9. `stative_verbs.py` - Prefix system
10. `adjectives.py` - Agreement rules, limited TAM
11. `adverbs.py` - Formation and tense agreement

### Phase 4: Complex Structures
12. `converbs.py` - Both classes
13. `particles.py` - All small words
14. `phrases.py` - NP, VP, Clause composition
15. `lexicon.py` - Known vocabulary

### Phase 5: Validation
16. Test against C# output for same inputs
17. Test against documented examples in grammar guide
18. Test against Discord example sentences

## Key Design Decisions

### Multi-character consonant support
Roots must be stored as lists of strings, not single characters:
```python
root = ["sh", "a", "k", "a", "r"]  # NOT "shakar"
# Or better:
root = Root(consonants=["sh", "k", "r"], vowels=["a", "a"])
```

### Template engine
Verb templates should be parsed patterns, not string manipulation:
```python
template = Template("1-a-2-3-e-4")  # tetraconsonantal
stem = template.apply(root, helper_vowel="e")
```

### Enum-based features
```python
class Gender(Enum):
    CHILD = "child"
    FEMALE = "female"
    MALE = "male"
    INANIMATE = "inanimate"

class Person(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
```

### Ki-syllable lookup
```python
ki = KiSyllable(person=Person.FIRST, gender=Gender.CHILD, number=Number.SINGULAR)
ki.predicate_final  # "thu"
ki.word_final       # "uth"
```

## Open Questions for the Author

1. **Which case system is current?** The grammar guide uses Ki-based case marking; the worldbuilding declensions use suffix-based (-bhi, -na, -bu, -dzh, -z, -go). Are both valid for different historical stages?

2. **Triconsonantal noun templates?** The C# code only implements tetraconsonantal nouns (BuildStemTetra). What's the triconsonantal noun template?

3. **Inanimate verb restrictions?** Grammar says inanimate can't be agent of dynamic verbs. Can it be agent of stative verbs?

4. **Object marking (voicing)?** Discord mentions object marking voices last consonant + changes V2 to /i/. How does this interact with the Ki-suffix system?

5. **Proto-Aelaki vs Modern Aelaki?** The worldbuilding docs have a different conjugation system (exu-bha, exu-dibv). Is this proto-Aelaki or a dialect?
