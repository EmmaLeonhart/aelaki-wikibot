# Aelaki Morphology Inventory

A consolidated inventory of every morphological rule, affix, and paradigm extracted from all sources. This serves as the specification for a Python grammar generator.

---

## 1. Phonological Inventory

### Vowels (8)
| Vowel | IPA | Gender association | Collective form |
|-------|-----|-------------------|-----------------|
| i | /i/ | Child (collective) | -- |
| ih/I | /ɪ/ | -- | -- |
| e | /e/ | Female (collective) | -- |
| ae | /æ/ | Male (collective) | -- |
| u | /u/ | Child (singular) | i |
| eu/U | /ʊ/ | -- | -- |
| o | /o/ | Female (singular) | e |
| a | /a/ | Male (singular) | ae |

### Umlaut (Fronting) Mappings
| Base | Fronted |
|------|---------|
| a | ae |
| o | oe |
| u | u (with umlaut) |

### Collective Vowel Shifts (Nouns/Numbers)
| Base | Collective |
|------|-----------|
| u | i |
| o | e |
| a | ae |
| schwa | ae |

### Consonants (34+)
Clicks: p!, t!, k!
Implosives: b', d', g'
Affricates: pf, bv, ch, dzh, kx, ggx
Fricatives: f, v, s, z, sh, zh, x, gx, gh, h
Nasals: m, n, ng, m', n', ngl'
Stops: p, b, t, d, k, g
Liquids: l, r
Glides: w, y

---

## 2. Root Templates

### Triconsonantal (Primary)
Pattern: C1-V1-C2-V2-C3
Example: d-a-p-a-z (shoot)

### Tetraconsonantal (Transitive verbs)
Pattern: C1-a-C2-u-C3-Vm-C4-Ve
Where Vm and Ve are gender vowels
Example: k-m-d-r (worship/ritual)

---

## 3. Four Core Operations

### Base Form
- Triconsonantal: C1V1C2V2C3 (no change)
- Tetraconsonantal: C1-a-C2-u-C3-Vm-C4-Ve

### Reduplication
- Tri: C1V1**C2V1**C2V2C3 (insert C2+V1 copy)
- Tetra: C1-a-C2-u-**C2-u**-C3-Vm-C4-Ve (duplicate C2-u)

### Umlaut (Fronting)
- Tri: front all vowels per umlaut map
- Tetra nouns: u->i, o->e, a->ae (collective shift)

### Zero-Infix
- Tri: C1V1**f**C2V2C3 (insert /f/ before C2)
- Tetra nouns: add -f after each vowel (uf, of, af)
- Constraint: never on inanimate nouns (already contain /f/)
- Constraint: never on yes/no particles Su/Fu

---

## 4. Gender System

### Four Genders
| Gender | Sg vowel | Coll vowel | Biology | Notes |
|--------|----------|-----------|---------|-------|
| Child | u | i | Pre-reproductive | Default for fractions |
| Female | o | e | Early reproductive | Default for even numbers |
| Male | a | ae | Late reproductive | Default for odd numbers, negation |
| Inanimate | if | -- | Non-living/mass | Cannot be agent; no /f/ infix |

---

## 5. Person Consonants

| Person | Consonant | Usage |
|--------|-----------|-------|
| 1st | th | Speaker |
| 2nd | j | Addressee |
| 3rd | sh | Other animate |
| 4th | k | Obviative/default |

---

## 6. Ki-Syllable System (~50 clitics)

### Predicate-Final Position (Free clitics)
| Person | Gender | Sg | Pl | Coll | Zero |
|--------|--------|----|----|------|------|
| 1st | Child | thu | thuthu | thi | thuf |
| 1st | Female | tho | thotho | the | thof |
| 1st | Male | tha | thatha | thae | thaf |
| 2nd | Child | ju | juju | ji | juf |
| 2nd | Female | jo | jojo | je | jof |
| 2nd | Male | ja | jaja | jae | jaf |
| 3rd | Child | shu | shushu | shi | shuf |
| 3rd | Female | sho | shosho | she | shof |
| 3rd | Male | sha | shasha | shae | shaf |
| 4th | Child | ku | kuku | ki | kuf |
| 4th | Female | ko | koko | ke | kof |
| 4th | Male | ka | kaka | kae | kaf |
| -- | Inan. | -- | -- | -- | if / ifif |

### Word-Final Position (Bound suffixes)
| Person | Gender | Sg | Pl | Coll | Zero |
|--------|--------|----|----|------|------|
| 1st | Child | uth | uthuth | ith | ufuth |
| 1st | Female | oth | othoth | eth | ofoth |
| 1st | Male | ath | athath | aeth | athaf |
| 2nd | Child | uj | ujuj | ij | ufuj |
| 2nd | Female | oj | ojoj | ej | ofoj |
| 2nd | Male | aj | ajaj | aej | ajaf |
| 3rd | Child | ush | ushush | ish | ufush |
| 3rd | Female | osh | oshosh | esh | ofosh |
| 3rd | Male | ash | ashash | aesh | ashaf |
| 4th | Child | u | -- | i | uf |
| 4th | Female | o | -- | e | of |
| 4th | Male | a | -- | ae | ak |
| -- | Inan. | if | ifif | -- | -- |

---

## 7. Case System (6 Cases)

| Case | Function | Ki position | Notes |
|------|----------|-------------|-------|
| Agent | Subject of active verb | Predicate-final | No inanimate |
| Patient | Subject of stative / Object | Word-final (least marked) | Default case |
| Possessive | Genitive | + -l suffix | Usually dropped |
| Instrumental | Instrument/comitative/locative | Complex Ki | Context-dependent |
| Dative | Indirect object/benefactive | + -n suffix | Ablative with zero number |
| Speaker | Information source | + -oro suffix | Non-visual evidentials |

### Agreement Hierarchy
Agent > Dative > Patient > Instrumental > Possessive > Speaker

---

## 8. Verb Templates (Transitive, Tetraconsonantal)

| Name | Pattern | Meaning |
|------|---------|---------|
| Telic Perfect | 1-a-2-3-e-4 | Completed goal-oriented action |
| Telic Imperfect | 1-a-2-3-o-4 | Ongoing goal-oriented action |
| Atelic Perfect | 1-a-2-v-3-e-4 | Completed unbounded action |
| Atelic Imperfect | 1-a-2-v-3-o-4 | Ongoing unbounded action |
| Telic Perfect (n) | 1-a-2-3-v-3-e-4 | Extended telic |
| Habitual Imperfect | 1-a-2-3-v-3-o-4 | Habitual/iterative |
| Telic Perfect ** | 1-a-2-3-v-2-3-e-4 | Complex telic |
| Gnomic Imperfect | 1-a-2-3-v-2-3-o-4 | Universal truths |
| Atelic Perfect ** | 1-a-2-v-3-v-2-v-3-e-4 | Complex atelic completed |
| Atelic Imperfect ** | 1-a-2-v-3-v-2-v-3-o-4 | Complex atelic ongoing |
| Imperative | ala-1-a-2-a-3-4-o | Commands |

Where: 1,2,3,4 = root consonants; v = helper vowel (varies by evidential); a,e,o = structural

---

## 9. Evidentiality System

### Basic Evidentials
| Evidential | Helper vowel | Suffix | Gloss |
|-----------|-------------|--------|-------|
| None (visual present) | e | -- | Default present |
| Present | u (umlaut) | -nu | Explicit present |
| Past visual | schwa | -she | Witnessed past |
| Hearsay | o | -ro | Reported/auditory |
| Inferential | u | -mu | Inferred |
| Mythical | -- | -sher | Legendary past |

### Stacked Combinations (12)
Primary + Secondary suffix concatenation: -nu-she, -she-ro, -ro-mu, etc.

### Mood Suffixes
| Mood | Suffix | Notes |
|------|--------|-------|
| Intention | -ng | 1st person only; 2nd=imperative; 3rd/4th=jussive |
| Optative | -ya | Hodiernal/future/crastinal |
| Deliberative | -yam | Future/crastinal; "should I?" |

### Day Prefixes
| Prefix | Meaning |
|--------|---------|
| (none) | Unmarked time |
| go- | Hodiernal (today) |
| goki- | Hesternal (yesterday) / Crastinal (tomorrow) |

### Hodiernal Sandhi
Before suffixes -rum, -she, -shem, -yam: insert -nk-
Example: zada- -> zadank-

---

## 10. Stative Verb Prefixes

| Prefix | Meaning | Double form |
|--------|---------|-------------|
| Ho- | Probable/about to | HoHo- (continuous) |
| Nu- | Inchoative (begin) | NuNu- (process of beginning) |
| Ni- | Cessative (stop) | NiNi- (process of stopping) |
| Lu- | Resumptive (resume) | LuLu- (process of resuming) |
| Li- | Repetitive cessative | LiLi- (continuous) |
| Ko- | Almost/nearly | KoKo- (keeps almost) |
| Ke- | Almost cessative | KeKe- (continuous) |

---

## 11. Converbs

### Class I: Prefix Converbs (retain full TAM)
| Prefix | Meaning |
|--------|---------|
| ki- | Purposive ("in order to") |
| ha- | Causal ("because") |
| sa- | Conditional ("if/when") |
| ra- | Concessive ("even though") |
| mu- | Instrumental ("by means of") |
| ne- | Adversative ("instead of") |

### Class II: Suffix Converbs (consume TAM)
| Suffix | Meaning |
|--------|---------|
| -shelon | Before (posterior) |
| -mulon | After/once (anterior) |
| -lon | Right after (sequential) |
| -ndor | Until (terminative) |
| -lok | Where (locative) |
| -mutu | As though (simulative) |
| -rum | For sake of (beneficiary) |
| -wom | Together with (comitative) |
| -sef | Except for (exceptive) |
| -vai | Only if/when (restrictive) |

---

## 12. Numeral System

### Base-12 Cardinals (1-12)
| # | Cardinal | Ordinal | Partitive | Fractional | Collective | Adverbial |
|---|----------|---------|-----------|-----------|-----------|----------|
| 1 | Pan | Sekon | Papan | Golo | Paen | Pante |
| 2 | Bal | Kezon | Babal | Kalakel | Bael | Balte |
| 3 | Bhan | Bhalon | Bhabhan | Bhavel | Bhaen | Bhante |
| 4 | Mal | Malon | Mamal | Malfel | Mael | Malte |
| 5 | Tan | Talon | Tatan | Tanfel | Taen | Tante |
| 6 | Dal | Dalon | Dadal | Dalfel | Dael | Dalte |
| 7 | Dhan | Dhanon | Dhadhan | Dhanfel | Dhaen | Dhante |
| 8 | Nal | Nalon | Nanal | Nalfel | Nael | Nalte |
| 9 | Kan | Kanon | Kakan | Kanfel | Kaen | Kante |
| 10 | Gal | Galon | Gagal | Galfel | Gael | Galte |
| 11 | Ghan | Ghanon | Ghaghan | Ghanfel | Ghaen | Ghante |
| 12 | Nger | Ngeron | Ngenger | Ngerfel | Nger | Ngerte |

### Composites
- 13-59: Dozens prefix + Units (e.g., NgerPan = 13, BalNger = 24)
- 60: Vibhi (special form)
- 61+: Vibhi + Cardinal(remainder)
- 120+: Cardinal(sixties) + Vibhi + Cardinal(remainder)

### Gender Agreement
- Even numbers: female gender vowels
- Odd numbers (except 1): male gender vowels
- 1, 10, powers of 10: child gender vowels
- Fractions: always child gender

---

## 13. Possession

### Inalienable (body parts, kin, inherent properties)
- **On possessed noun**: Infix after C1 = gender vowel + person consonant
- **Suffix**: -ng
- Template: C1 + V(gender) + C(person) + rest + ng

### Alienable (transferable property, abstract relations)
- **On possessed noun**: Prefix = gender vowel + person consonant
- **Optional suffix**: -n
- Template: V(gender) + C(person) + root + n

---

## 14. Adjective System

Template (stative): C1-o-C2-a-C3-GV-PC-GV
- Agrees with head noun in gender, number, person
- Supports 8-way TAM (4 evidentials x 2 tenses: general + hodiernal go-)
- No goki- prefix allowed on adjectives
- Comparative: reduplication
- Superlative: umlaut
- Negation: zero-infix

---

## 15. Adverbs

Template: ROOT + -te
- Must agree with verbal tense
- Four stem alternations: base, comparative (C2 redup), superlative (umlaut), negative (f-infix)
- Hodiernal sandhi: insert -nk- before TAM suffixes

---

## 16. Small Words & Particles

### Affirmatives/Negatives
| Base | Redup | Umlaut | Redup+Umlaut | Meaning |
|------|-------|--------|--------------|---------|
| Su | Susu | Si | Sisi | Yes (escalating certainty) |
| Fu | Fufu | Fi | Fifi | No (escalating certainty) |

### Connectives
| Form | Meaning |
|------|---------|
| Zuzu | And (list continues) |
| Zu | And (list ends, non-exhaustive) |
| Zi | And (exhaustive list) |
| Zuf | And NOT / excluding |

### Switch Reference
| Form | Meaning |
|------|---------|
| No | Switch to known referent |
| Nono | Introduce new referent |
| Ne | Merge referents (topic unifier) |
| Nof | Negate/except this referent |

### Question Particles
| Form | Meaning |
|------|---------|
| Shu | What / yes-no question |
| Shushu | Discuss (explain) |
| Shi | Give final answer |

### Adpositions (Spatial)
| Form | Meaning |
|------|---------|
| Snu | At |
| Snusnu | Through |
| Sni | Final location (goal) |
| Snuf | Where? |

### Adpositions (Temporal)
| Form | Meaning |
|------|---------|
| Sle | At a time |
| Slesle | Throughout duration |
| Slae | Completion time |
| Slef | What time? |

---

## 17. Clause Structure

### Default word order: V(S)(O)
- Historical: SVO
- Modern: pro-drop; verb-initial
- Imperative: frozen S-O-V morphology

### Argument marking on verb
| Verb type | Prefix Ki (left) | Suffix Ki (right) |
|-----------|-----------------|------------------|
| Transitive | Subject | Object |
| Intransitive (active) | Subject | -- |
| Intransitive (stative) | -- | Subject |

---

## 18. Vocabulary Roots (From All Sources)

### Core verb roots documented with glosses
bva (drink), upf (eat), p'ar (bite), euvel (suck), bha (see), dibv (hear), zo (know), agh (think), eux (smell), aed (fear), gho (live), of (die), bvaedh (kill), xaen (hunt), dhe (hit), nd'i (cut), gi (stab), bhi (scratch), gihch (dig), aech (swim), iht' (fly), sae (walk), ae (come), vog (sit), ihggx (stand), dzhe (turn), apf (fall), och (give), kxeugh (hold), ig (squeeze), euw (rub), udh (wash), u (pull), i (push), geb (throw), ghih (tie), ma'el (give birth), aexel (age)

### Core noun roots
ae (head), idzh (ear), euf (eye), dedh (nose), on (mouth), bi (tooth), adzh (tongue), b'eb (hand), mb'ihb' (foot), gu (belly), oz (guts), ich (heart), uch (liver), id (hair), vibh (horn), dihw (tail), t'ub' (sun), pu (moon), o (star), sugh (water), rekx (rain), lu (river), gu (lake), nek (sea), d'o (stone), ach (earth), lih (cloud), wihd' (fire), fedzh (wind), nd'iw (snow), go (ice), debh (tree), igy (fruit), omb' (seed), tae (leaf), aggx (root), geup (bark), gheugh (flower), deg (grass)
