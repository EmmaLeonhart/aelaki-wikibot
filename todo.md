# Aelaki TODO

## getting status.md working

We need a status.md like C:\Users\Immanuelle\Documents\Github\Sutra and C:\Users\Immanuelle\Documents\Github\order.life 

So go over its claude.md and status.md and maybe todo.md to figure the stuff out. We want to begin powering through our todo.md and status.md in the way that is intended instead of letting these documents go stale and add bloat.

## Clean up the data lake

We are currently working on this. auditing the discord stuff in data lake and the megadoc. We hope to eventyually get them deleted since the wiki and grammar stuff are the primary source of truth, not sure if we can get to this today but I hope we can. Compression is a bitch and might lose what we are doing

## Potentially outdated wiki material

The commit 4db8259de2771511cbf6aaa11edbd6c1993a933b 

docs(wiki): migrate data-lake xlsx tables into Converbs/TAM/Aelaki
Three spreadsheets in data lake/docs/ held content that was not
adequately mirrored on the wiki. Folded each into the appropriate
grammar page so the xlsx files could be removed.

appears to have added potentially outdated information into the wiki pages. Not the biggest concern but it needs to be audited based on the current grammar later. Remember that the python files are the biggest source of truth for us right now

## Manual Analysis Needed

- [ ] Parse **Sægetlæræchïfïshë** into morphemes — appears in the car crash glossed sentence as `SIM.CONV-HOD-be_hit.COMP-INAN.4p-VIS.PAST` but likely has nonstandard romanization. Needs manual analysis to determine correct root and morpheme boundaries. (Source: discord 2025-06-04)

## aelaki-sharp (C# library)

- [ ] Bring `aelaki-sharp/` in line with canonical wiki grammar — the C# morphology library is an outdated snapshot from before several consolidations (unified back-to-front vowel shift, inanimate gender behaviour, Ki-syllable tables, stative-verb prefixes). Intended to eventually be published as a .NET library; not in the data lake. Needs a pass that diff's each module against `grammar/*.wiki` / `aelaki/` and updates accordingly.

## Phonology / Vowel Grid

- [ ] Clarify the status of **ë** (e-diaeresis) in the vowel system — it appears frequently in evidential suffixes (`-shë`, `-shëm`, `-shëlon`) and the temporal adposition (`Slë`), but is absent from the vowel grid and `VOWEL_SHIFT_MAP` in `phonology.py`. The umlaut pair `Slë → Slæ` suggests ë behaves like **ə** (schwa, shifting to æ), not like plain **e** (which is already front and wouldn't shift). Need to decide: is ë a spelling variant of ə, a distinct vowel that belongs in the grid, or just plain e with the adposition being a special case? Once decided, update `VOWELS`, `VOWEL_SHIFT_MAP`, and `apply_umlaut()` accordingly.

## Morphology Bugs

- [x] Fix `ki_word_final()` in `aelaki/person.py` — stative verb suffix now elides leading vowel when stem ends in vowel (CV instead of VCV). Also added `ë` to VOWELS set. (Fixed in b470777)
- [x] Correct declensions on inanimate nouns — inanimate now only generates 4th person forms (person is meaningless for inanimate), and tables show simplified Number/Form layout instead of redundant 4-person columns

## Word Pages Bot (EmmaBot)

Bot creates `word:LEMMA` pages on aelaki.miraheze.org via GitHub Actions.
Based on: https://github.com/Emma-Leonhart/shintowiki-scripts/

### Current (v1)
- [x] Create `create_word_pages.py` — generates word pages from `aelaki/lexicon.py` + `aelaki_forms.csv`
- [x] Create `update_bot_status.py` — updates `User:EmmaBot` with run metadata (trigger, timestamp, workflow URL)
- [x] Set up GitHub Actions workflow — runs on push, daily at 00:00 UTC, and manual dispatch
- [x] Pages tagged with `{{wordpage|v1}}` for version tracking
- [x] 10 words per run, state file tracks progress across runs

### Pipeline fixes (2026-03-23)
- [x] Fix `commit_state()` glob patterns — `*.last` pattern fails when no `.last` files exist, killing pipeline under `set -euo pipefail`
- [x] Fix `commit_state()` rebase — stash unstaged changes before `git pull --rebase` to prevent "You have unstaged changes" failures
- [x] Full git history checkout — `fetch-depth: 0` so `sync_commit_log.py` gets all commits, not just shallow clone
- [x] Move git commit log sync to Step 0.05 — runs early so version categories are navigable before word page phases
- [x] Skip non-existent version categories — `cat.exists` check before iterating, avoids ~170+ wasted API calls

### State File Audit
- [x] Annual reconciliation step added (`reconcile_state.py`) — rebuilds state from `page.exists` checks, runs first time 2026-03-22 then Jan 1 each year
- [ ] Audit `create_word_pages.state` for stale entries from renamed keys (e.g. `dzhbhr` → `jbhr`)
- [ ] General audit of all pipeline state files and their failure modes

### Planned: Page Format Updates (v2+)
- [ ] Write `update_word_pages.py` — finds all pages with `{{wordpage|v1}}` and regenerates them with the v2 format
- [ ] Add pronunciation / phonetic transcription section
- [ ] Add etymology section linking to proto-Aelaki roots
- [ ] Add example sentences from Discord corpus
- [ ] Richer inflection tables: group by TAM/evidential for verbs, show possession paradigm for nouns
- [ ] Cross-link related words (e.g. `bsl` noun ↔ `bsl_adj` adjective)

### Wiktionary Countability Detection
- [x] Use Wiktionary API to detect noun countability (countable vs uncountable)
- [x] Countable nouns → animate gender (child/female/male, evenly distributed)
- [x] Uncountable nouns → inanimate gender (mass nouns, substances, abstractions)
- [x] Replace random gender assignment in `generate_random_words.py` with countability-based logic
- [x] Backfill existing auto-generated nouns with countability data

### Orphaned Pages Cleanup (2027+)
- [x] `delete_orphaned_pages.py` is in the pipeline, year-gated to 2027+
- [x] Deletes any orphaned page with no incoming links (not just word: pages)
- [x] Protected namespaces excluded: User, User talk, Category, Template, MediaWiki, and Main Page

### Planned: Automatic New Word Creation
- [ ] Parse `discord/extracted/dictionary.md` to discover words not yet in `aelaki/lexicon.py`
- [ ] Extract new roots from Discord messages automatically (extend `extract_discord_aelaki.py`)
- [ ] Feed new words into lexicon.py programmatically, then let the bot create their pages
- [ ] Goal: every documented Aelaki word gets a `word:LEMMA` page automatically

## Grammar Wiki Pages

Wiki grammar reference at `grammar/*.wiki`, synced bidirectionally via `sync_grammar_pages.py`.

### Completed pages
- [x] Noun.wiki — root structure, gender, number, person, case
- [x] Verb.wiki — verb classes, stem formation, TAM, evidentiality, agreement
- [x] Phonology.wiki — vowel/consonant inventory, processes, historical changes
- [x] Adjective.wiki — expanded with agreement, degree, stative verb relationship
- [x] All evidential pages (Visual, Auditory, Hearsay, Inferential)
- [x] All stative aspect pages (Inchoative, Cessative, Resumptive, Almost, Repetitive)
- [x] All case pages (Agent, Patient, Dative, Instrumental, Possessive, Speaker)
- [x] All gender pages (Child, Female, Male, Inanimate)
- [x] Ki_syllables, Converbs, Stative_verbs, Numerals, Adverb, Word_order

### Missing pages to create
- [ ] Cohortative.wiki — "let us..." construction, referenced in Optative and Intentional but no page
- [ ] Realis.wiki — realis mood, referenced in Converbs but no page
- [ ] TAM.wiki — tense-aspect-mood system overview page, widely referenced

### Thin pages to expand (15-29 lines)
- [ ] Positive.wiki (21 lines) — needs comprehensive mood paradigms and contrastive examples
- [ ] Present.wiki (21 lines) — minimal, needs formation details and tense interaction
- [ ] Quirky_optative.wiki (21 lines) — needs examples and detailed paradigms
- [ ] Collective.wiki (22 lines) — has evolution section but needs syntax/agreement details
- [ ] Comparative.wiki (25 lines) — only two examples, needs all word classes covered
- [ ] Deliberative.wiki (25 lines) — minimal, needs usage contexts and full paradigms
- [ ] First_person_nouns.wiki (25 lines) — very sparse, barely covers the topic
- [ ] Mythic.wiki (25 lines) — brief, needs usage patterns with hearsay
- [ ] Superlative.wiki (25 lines) — parallel expansion needed alongside Comparative
- [ ] Contact_influence.wiki (28 lines) — needs more language contact examples
- [ ] Imperative.wiki (28 lines) — needs more examples and mood interactions
- [ ] Plural.wiki (29 lines) — references Aelaki_plural for details, could be more self-contained

### Moderate pages that could benefit from expansion (30-44 lines)
- [ ] Adpositions.wiki (34 lines) — needs paradigmatic tables and more examples
- [ ] Copula.wiki (33 lines) — could expand on irregular forms and historical development
- [ ] Pseudopronouns.wiki (35 lines) — could expand with more usage context
- [ ] Word_order.wiki (43 lines) — could add historical development section
- [ ] Negative.wiki (33 lines) — could add more on /f/ infix interaction with different word classes
- [ ] Optative.wiki (35 lines) — could add more on mood distinctions

### Structural improvements
- [ ] Add pedagogical "Getting started" page or learning path
- [ ] Add complex syntax coverage — subordination, coordination, multi-clause constructions
- [ ] Expand Questions.wiki with more examples of complex question formations
