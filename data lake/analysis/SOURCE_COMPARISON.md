# Aelaki Source Comparison & Discrepancy Analysis

This document compares the morphological rules across all sources in this repository to identify agreements, contradictions, and gaps. The goal is to establish what a definitive Python implementation should follow.

## Sources Analyzed

| Source | Location | Authority | Scope |
|--------|----------|-----------|-------|
| **Grammar Guide (docx)** | `docs/Aelaki Grammar Guide.docx` | **PRIMARY** (per author) | Full grammar |
| **Grammar Guide (md)** | `aelaki-split/Aelaki Grammar Guide.md` | High | Full grammar (~31k lines) |
| **C# Implementation** | `aelaki-sharp/General console/` | Medium (code = testable) | Nouns, verbs, numbers, converbs, adjectives |
| **Worldbuilding docs** | `aelaki-split/worldbuilding/` | Medium (supplementary) | Lexicon, declensions, conjugations, history |
| **Discord messages** | `discord/` (5 JSON files) | Low-Medium (informal, evolving) | Design rationale, edge cases, corrections |
| **Python script** | `aelaki-split/aelaki_morphology.py` | Low (minimal scope) | 4 core operations only |

---

## 1. ROOT SYSTEM

### Agreement
All sources agree on triconsonantal roots as the primary system: C1-V1-C2-V2-C3.

### Discrepancy: Triconsonantal vs Tetraconsonantal
- **C# code**: Implements tetraconsonantal (4-consonant) roots as primary for nouns and transitive verbs. Template: C1-a-C2-u-C3-vm-C4-ve
- **Markdown grammar**: Documents triconsonantal as primary. Tetraconsonantal mentioned but not extensively.
- **Discord**: States transitive verbs use tetraconsonantal roots, intransitive use triconsonantal.
- **Worldbuilding docs**: Show triconsonantal roots with some tetraconsonantal examples (Ngornese k-m-d-r).

**Resolution**: The language likely uses BOTH. Triconsonantal for intransitive verbs and basic nouns; tetraconsonantal for transitive verbs. The C# code focuses on transitive verbs (hence tetra). Python implementation should support both.

---

## 2. FOUR CORE MORPHOLOGICAL OPERATIONS

### Strong Agreement
All sources agree on four operations:

| Operation | Pattern | Meaning |
|-----------|---------|---------|
| Base | C1V1C2V2C3 | Singular/perfective-incomplete/positive |
| Reduplication | C1V1C2V1C2V2C3 | Plural/imperfective/comparative |
| Umlaut | C1(front)C2(front)C3 | Collective/perfective-completed/superlative |
| Zero-infix | C1V1fC2V2C3 | Negation/zero quantity |

### Minor discrepancy: Zero-infix placement
- **Python script**: Places /f/ before V2: `C1V1C2fV2C3`
- **Markdown grammar**: Places /f/ before C2: `C1V1fC2V2C3`
- **C# code (nouns)**: Adds -f AFTER vowels: `uf`, `of`, `af` (different mechanism)

**Resolution**: The markdown grammar's rule (`C1V1fC2V2C3`) appears to be the documented standard for verbs/adjectives. The C# noun system uses a different surface realization (vowel+f) which may be a noun-specific pattern.

### Resolved: Umlaut vowel mappings (UNIFIED)
Earlier sources showed different mappings for "phonological umlaut" vs "collective shift". These have been **unified into a single back-to-front vowel shift** used across all grammatical contexts (verbs, adjectives, nouns, numbers):

| Back | Front |
|------|-------|
| u | i |
| ü | ï |
| o | e |
| a | æ |
| ə | æ |

Front vowels (i, ï, e, æ) are unchanged. The same shift applies whether the context is verbal umlaut (perfective-completed), noun collective, numeral collective, adjective superlative, or adverb superlative.

---

## 3. GENDER SYSTEM

### Agreement on 3 animate genders
All sources agree: Child, Female, Male (based on sequential hermaphroditism).

### Discrepancy: 3 vs 4 genders
- **Markdown grammar**: 4 genders (Child, Female, Male, **Inanimate**)
- **C# code**: 3 genders only (Child, Feminine, Masculine) -- no Inanimate
- **Discord**: Confirms 3 animate genders; inanimate is special class
- **Worldbuilding**: Documents 4 genders with Inanimate having vowel "if"

**Resolution**: Inanimate exists as a 4th gender but behaves differently (no agent of dynamic verbs, no zero-infix, special Ki markers). The C# code omits it likely because it wasn't needed for the demo sentences. Python should implement all 4.

### Gender vowel mappings

| Gender | C# (mid,end) | Grammar (sg) | Grammar (coll) |
|--------|--------------|--------------|-----------------|
| Child | u, u | u | i |
| Female | o, o | o | e |
| Male | a, a | a | ae |
| Inanimate | -- | if | -- |

Agreement across sources for singular forms. Collective vowels consistent.

---

## 4. NUMBER/PLURALITY

### Agreement
4 numbers: Singular, Plural, Collective, Zero.

### Plural formation
- **C# (nouns)**: Reduplicates C2-u segment: C1-a-C2-u-**C2-u**-C3-vm-C4-ve
- **Markdown grammar**: Inserts C2V1 after first V1: C1V1**C2V1**C2V2C3
- **Discord**: Confirms "middle consonant reduplication"

**Resolution**: Same principle, different notation. The C# implements it for tetraconsonantal roots while the grammar documents it for triconsonantal. Both reduplicate C2+vowel.

---

## 5. PERSON SYSTEM

### Agreement
4 persons with consonant markers:
- 1st: th
- 2nd: j
- 3rd: sh
- 4th: k (or empty in some positions)

All sources agree on these consonants.

---

## 6. VERB SYSTEM

### Stem templates (transitive, tetraconsonantal)
The C# code documents 11 stem templates. The markdown grammar documents a compatible but differently-organized system. Key templates match:

| C# Name | C# Pattern | Grammar Equivalent |
|---------|-----------|-------------------|
| Telic Perfect | 1-a-2-3-e-4 | Telic perfect |
| Telic Imperfect | 1-a-2-3-o-4 | Continuative |
| Atelic Perfect | 1-a-2-v-3-e-4 | Atelic perfect |
| Imperative | ala-1-a-2-a-3-4-o | Imperative (SOV frozen) |

### Evidentiality

**Major discrepancy in suffix inventory:**

| C# | Markdown Grammar | Discord |
|----|-----------------|---------|
| -nu (present) | unmarked | -- |
| -she (past visual) | -she (witnessed) | -sh' (visual past) |
| -ro (hearsay) | -ro (auditory/reported) | -ro (hearsay) |
| -mu (inferential) | -mu (inferred) | -mu (inferential) |
| -- | -sher (mythical past) | -sher (mythical) |
| -- | -ng (intention) | -ng (intention) |
| -- | -ya (optative) | -ya (optative) |
| -- | -yam (deliberative) | -yam (deliberative) |

**Resolution**: C# only implements 5 basic evidentials (None/Present/Past/Hearsay/Inferential) plus 12 stacked combinations. The grammar documents a richer system with mythical past, intention, optative, and deliberative moods. Python should implement the full grammar system.

### Day prefixes
- **Grammar**: go- (hodiernal), goki- (hesternal/crastinal)
- **C#**: Not implemented
- **Discord**: Confirms go-, goki-, with circumfix go-...-n for hodiernal

---

## 7. CASE SYSTEM

### Significant source variation

| Source | Cases | Markers |
|--------|-------|---------|
| **Grammar (md)** | 6: Agent, Patient, Possessive, Instrumental, Dative, Speaker | Ki-syllable based |
| **Worldbuilding (declensions)** | 7: Subject(-bhi), Object(-na), Intransitive, Inalienable(-bu), Alienable(-dzh), Instrumental(-z), Vocative(-go) | Suffix-based |
| **Discord** | Unmarked, Oblique, Inalienable possessor | Minimal |

**Resolution**: This is a MAJOR discrepancy. The worldbuilding declensions appear to be from an older/different stage of the language (uses distinct case suffixes -bhi, -na, etc.) while the grammar guide uses Ki-syllable agreement markers. The Discord messages suggest a more minimal system. The docx grammar guide should be authoritative here.

---

## 8. NUMERAL SYSTEM

### Strong agreement between C# and grammar

| Number | C# Cardinal | Grammar Cardinal |
|--------|------------|-----------------|
| 1 | Pan | Pan |
| 2 | Bal | Bal |
| 3 | Bhan | Bhan |
| ... | ... | ... |
| 12 | Nger | Nger |
| 60 | Vibhi | Vibhi |

All six semantic roles (cardinal, ordinal, partitive, fractional, collective, adverbial) match between C# and grammar.

### Minor discrepancy: Gender of numbers
- **Grammar**: Even=female, odd=male (except 1,10 = child)
- **C#**: Implements gender vowel replacement but doesn't enforce the even/odd rule explicitly

---

## 9. CONVERBS

### C# vs Grammar
C# documents 17 converb types. Grammar organizes them into 2 classes:
- **Class I (prefix, keep TAM)**: ki- (purposive), ha- (causal), sa- (conditional), ra- (concessive), mu- (instrumental), ne- (adversative)
- **Class II (suffix, consume TAM)**: -shelon, -mulon, -lon, -ndor, -lok, -rum, -wom, -sef, -vai

The C# code mixes both classes into a single enum. Grammar is more systematic.

### Discrepancy: ne- (adversative)
- Grammar lists ne- (adversative, "instead of") as Class I converb
- C# does not include adversative

### Discrepancy: tu-/mutu (simulative)
- C# lists tu- as prefix converb
- Grammar lists -mutu as suffix form

---

## 10. POSSESSION

### Agreement on core distinction
All sources agree: inalienable (body parts, kin) vs alienable (property).

### Formation rules vary
- **C# (tetra nouns)**: Inalienable = C1+GV+PC+rest+ng; Alienable = GV+PC+C1+rest+n
- **Grammar**: Inalienable = infix after C1 + -ng suffix; Alienable = prefix + optional -n
- **Discord**: Inalienable uses circumfix around possessor + infix on possessed

These are compatible descriptions of the same phenomenon, just at different levels of abstraction.

---

## 11. STATIVE VERB PREFIXES (Grammar-only feature)

The markdown grammar documents an extensive prefix system for stative verbs that is NOT in the C# code:

| Prefix | Meaning |
|--------|---------|
| Ho- | probable/about to |
| Nu- | inchoative (start to) |
| Ni- | cessative (stop) |
| Lu- | resumptive (resume) |
| Li- | repetitive cessative |
| Ko- | almost/nearly |
| Ke- | almost cessative |

Each can be doubled for continuous aspect (NuNu-, KoKo-, etc.)

---

## 12. FEATURES FOUND ONLY IN DISCORD

The Discord messages contain design rationale and features not documented elsewhere:
- Definiteness is inflected into nouns (not articles)
- Noun incorporation possible for 1st person only
- Hodiernal tense described as "notoriously vague and passive-aggressive"
- Object marking voices last consonant + changes V2 to /i/
- All monosyllabic proto-language words had affixes added that became part of roots
- 50% of verb roots begin with CH-, 30% end with -P (folk etymology regularization)
- Compound words are "nightmares" due to morphological complexity -- genitives/converbs preferred

---

## Summary: Priority for Python Implementation

The docx grammar guide is authoritative. Where it conflicts with other sources:
1. Use grammar guide rules for the core system
2. Use C# code to verify algorithmic details (it's tested/runnable)
3. Use worldbuilding declensions cautiously (may represent older stage)
4. Use Discord for design intent and edge case clarification
5. The existing Python script only covers 4 basic operations -- needs complete rewrite
