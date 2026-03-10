# Aelaki TODO

## Manual Analysis Needed

- [ ] Parse **Sægetlæræchïfïshë** into morphemes — appears in the car crash glossed sentence as `SIM.CONV-HOD-be_hit.COMP-INAN.4p-VIS.PAST` but likely has nonstandard romanization. Needs manual analysis to determine correct root and morpheme boundaries. (Source: discord 2025-06-04)

## Word Pages Bot (EmmaBot)

Bot creates `word:LEMMA` pages on aelaki.miraheze.org via GitHub Actions.
Based on: https://github.com/Emma-Leonhart/shintowiki-scripts/

### Current (v1)
- [x] Create `create_word_pages.py` — generates word pages from `aelaki/lexicon.py` + `aelaki_forms.csv`
- [x] Create `update_bot_status.py` — updates `User:EmmaBot` with run metadata (trigger, timestamp, workflow URL)
- [x] Set up GitHub Actions workflow — runs on push, daily at 00:00 UTC, and manual dispatch
- [x] Pages tagged with `{{wordpage|v1}}` for version tracking
- [x] 10 words per run, state file tracks progress across runs

### Known Issues (wiki under maintenance)
- [ ] Correct declensions on inanimate nouns — declension forms for inanimate nouns need to be fixed, but the wiki is currently undergoing maintenance so this should wait until the wiki is back up
- [ ] Clean up commit `edceed7` — this commit only upgraded existing word pages but did not add new ones, so the impact is limited; however the upgrade may have produced inconsistent page content. Review and fix affected pages once the wiki is working again

### Planned: Page Format Updates (v2+)
- [ ] Write `update_word_pages.py` — finds all pages with `{{wordpage|v1}}` and regenerates them with the v2 format
- [ ] Add pronunciation / phonetic transcription section
- [ ] Add etymology section linking to proto-Aelaki roots
- [ ] Add example sentences from Discord corpus
- [ ] Richer inflection tables: group by TAM/evidential for verbs, show possession paradigm for nouns
- [ ] Cross-link related words (e.g. `bsl` noun ↔ `bsl_adj` adjective)

### Planned: Wiktionary Countability Detection
- [ ] Use Wiktionary API to detect noun countability (countable vs uncountable)
- [ ] Countable nouns → animate gender (child/female/male, evenly distributed)
- [ ] Uncountable nouns → inanimate gender (mass nouns, substances, abstractions)
- [ ] Replace random gender assignment in `generate_random_words.py` with countability-based logic
- [ ] Backfill existing auto-generated nouns with countability data

### Planned: Automatic New Word Creation
- [ ] Parse `discord/extracted/dictionary.md` to discover words not yet in `aelaki/lexicon.py`
- [ ] Extract new roots from Discord messages automatically (extend `extract_discord_aelaki.py`)
- [ ] Feed new words into lexicon.py programmatically, then let the bot create their pages
- [ ] Goal: every documented Aelaki word gets a `word:LEMMA` page automatically
