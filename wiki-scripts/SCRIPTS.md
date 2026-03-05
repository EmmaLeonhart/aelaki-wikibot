# Aelaki Wikibot Scripts

## Overview

Bot scripts for maintaining and expanding the [Aelaki Wiki](https://aelaki.miraheze.org).
Based on patterns from [shintowiki-scripts](https://github.com/Emma-Leonhart/shintowiki-scripts/).

## Prerequisites

1. Python 3.11+ with `mwclient` installed:
   ```
   pip install mwclient
   ```

2. Bot password created at https://aelaki.miraheze.org/wiki/Special:BotPasswords

3. Environment variables set:
   ```
   set AELAKI_WIKI_USERNAME=YourUser@AelakiBot
   set AELAKI_WIKI_PASSWORD=your-generated-password
   ```

## Scripts

| Script | Status | Description |
|--------|--------|-------------|
| `create_word_pages.py` | **CI** | Creates `word:LEMMA` pages (runs via GitHub Actions) |
| `update_bot_status.py` | **CI** | Updates `User:EmmaBot` with pipeline run metadata |
| `word_page_loop.sh` | **CI** | Orchestrates the word page bot pipeline |
| `generate_random_words.py` | **CI** | Generates new lexicon entries from Wiktionary lemmas |
| `create_wanted_categories.py` | **CI** | Creates missing categories from Special:WantedCategories |
| `create_word_articles.py` | Ready | Creates wiki articles for each root word in the lexicon |
| `sync_lexicon_page.py` | Ready | Syncs the roots summary table to a wiki page |

### create_word_pages.py (CI — GitHub Actions)

Creates `word:LEMMA` pages on aelaki.miraheze.org. Each page contains:
- Lead paragraph with word class, gloss, and gender
- Overview table (root consonants, word class, gloss)
- Inflection table from `aelaki_forms.csv`
- Categories and `{{wordpage|v1}}` version footer

Runs automatically via GitHub Actions on push, daily schedule, or manual dispatch.
Creates 10 pages per run; state file tracks progress across runs.

```bash
# Preview (dry-run, no login needed)
python create_word_pages.py --limit 5

# Create 10 pages
python create_word_pages.py --apply --limit 10

# Create specific words
python create_word_pages.py --apply --keys "debh,bva,zoduk"
```

### update_bot_status.py (CI — GitHub Actions)

Updates `User:EmmaBot` on the wiki with:
- UTC timestamp of the pipeline run
- Trigger type (push commit, daily schedule, manual dispatch)
- Link to the GitHub Actions workflow run

Template file: `EmmaBot.wiki`

### generate_random_words.py (CI — GitHub Actions)

Grows the lexicon automatically. Each run:
1. Fetches English lemmas from Wiktionary categories (nouns 40%, verbs 40%, adjectives 10%, adverbs 10%)
2. Generates unique triconsonantal (or tetraconsonantal for transitive verbs) roots
3. Computes citation forms using the Aelaki morphology engine
4. Appends new entries to `aelaki/lexicon.json` (skips duplicate glosses)

**State modified:** `aelaki/lexicon.json`

### create_wanted_categories.py (CI — GitHub Actions)

Creates missing category pages listed on `Special:WantedCategories`. Each page contains only `[[Category:Bot created categories]]`. No local state file; writes directly to the wiki.

### word_page_loop.sh (CI — GitHub Actions)

Shell orchestrator that runs the full pipeline in order:
1. `generate_random_words.py` — grow the lexicon with ~100 new entries
2. `update_bot_status.py` — declare the run on the wiki
3. `create_wanted_categories.py` — create any missing category pages
4. `create_word_pages.py` — upgrade old pages and create new word pages

Builds a run tag from GitHub Actions environment variables (run ID, event type) for wiki edit summaries.

### create_word_articles.py

Creates one wiki article per documented root word (nouns, verbs, adjectives, adverbs).
Each article includes:
- Root consonants and word class
- English gloss and inherent gender (if applicable)
- Full inflection table from `aelaki_forms.csv`
- Links to related grammar pages
- Categories: `[[Category:Aelaki nouns]]`, `[[Category:Aelaki vocabulary]]`, etc.

```bash
# Preview what would be created (dry-run, no login needed)
python create_word_articles.py --dry-run

# Create all word articles
python create_word_articles.py --apply

# Create only the first 5
python create_word_articles.py --apply --limit 5

# Create specific words only
python create_word_articles.py --apply --keys "ae,bva,debh"

# Overwrite existing pages
python create_word_articles.py --apply --overwrite
```

Supports resumption via `.state` file — safe to interrupt and re-run.

### sync_lexicon_page.py

Maintains a machine-readable roots table on `Aelaki Lexicon/Roots`.
Uses bot markers (`<!-- BOT:ROOTS-TABLE-START -->`) so the table can be
updated without disturbing hand-written content on the same page.

```bash
# Preview changes
python sync_lexicon_page.py --dry-run

# Apply changes
python sync_lexicon_page.py --apply

# Target a different page
python sync_lexicon_page.py --apply --page "Aelaki roots/Table"
```

## Conventions

All scripts follow these patterns (from shintowiki-scripts):

- **Dry-run by default** — pass `--apply` to actually edit the wiki
- **State files** for resumable operations (`.state` extension, gitignored)
- **JSONL logging** for audit trails (`.log` extension, gitignored)
- **1.5s throttle** between edits (Miraheze standard)
- **Windows Unicode fix** included in all scripts
- **Environment variables** for credentials (never hardcoded)

## File Structure

```
wiki-scripts/
├── API.md                      # API access patterns documentation
├── SCRIPTS.md                  # This file
├── EmmaBot.wiki                # Template for User:EmmaBot status page
├── config.py                   # Connection settings and constants
├── utils.py                    # Shared bot utilities
├── word_page_loop.sh           # CI orchestrator (GitHub Actions)
├── generate_random_words.py    # Lexicon growth from Wiktionary (CI)
├── create_word_pages.py        # word:LEMMA page creation (CI)
├── update_bot_status.py        # Bot status page updater (CI)
├── create_wanted_categories.py # Missing category creation (CI)
├── create_word_articles.py     # Article generation script
├── sync_lexicon_page.py        # Lexicon page sync script
├── create_word_pages.state     # Tracks completed word page keys (committed by CI)
├── version_history.txt         # Ordered version categories (committed by CI)
└── *.log                       # Run logs (gitignored)

aelaki/
└── lexicon.json                # Master lexicon (grown by CI each run)

.github/workflows/
└── word-pages.yml              # GitHub Actions workflow for word page bot
```

## GitHub Actions Setup

The word page bot runs via `.github/workflows/word-pages.yml`.

**Triggers:**
- Every push to `master` (except `*.state` file changes)
- Daily at 00:00 UTC (cron schedule)
- Manual dispatch (`workflow_dispatch`)

**Required repository configuration:**
1. **Variable** `WIKI_USERNAME` — bot-password username (e.g. `EmmaBot@EmmaBot`)
2. **Secret** `WIKI_PASSWORD` — bot password from `Special:BotPasswords`

Set these at: `Settings > Secrets and variables > Actions`

## CI Pipeline State Management

The GitHub Actions workflow modifies three files that are committed back to the repository after each run. The commit message uses `[skip ci]` to prevent infinite trigger loops.

### State files committed by CI

| File | Modified by | Purpose |
|------|------------|---------|
| `wiki-scripts/create_word_pages.state` | `create_word_pages.py` | Tracks which lexicon keys have already had wiki pages created, one key per line. Prevents duplicate page creation across runs. |
| `aelaki/lexicon.json` | `generate_random_words.py` | The master lexicon. Each CI run fetches ~100 random English words from Wiktionary and generates new Aelaki entries (roots, citation forms, glosses). New entries are appended to the appropriate section (nouns, verbs, adjectives, adverbs). |
| `wiki-scripts/version_history.txt` | `create_word_pages.py` | Ordered list of version category names (e.g. `Words fb8fd09`). Each entry corresponds to a git commit hash. Used to track which word pages need upgrading when the page template changes. |

### How the state cycle works

1. **`generate_random_words.py`** runs first — fetches English lemmas from Wiktionary categories, generates Aelaki roots with citation forms, and appends new entries to `aelaki/lexicon.json`. This grows the lexicon by ~100 entries per run.

2. **`update_bot_status.py`** updates `User:EmmaBot` on the wiki with the current run's timestamp, trigger type, and a link to the GitHub Actions run. (No local state file — writes directly to the wiki.)

3. **`create_wanted_categories.py`** queries `Special:WantedCategories` on the wiki and creates any missing category pages. (No local state file — writes directly to the wiki.)

4. **`create_word_pages.py`** runs in two phases:
   - **Phase 1 (Upgrade):** Reads `version_history.txt` to find word pages tagged with older commit hashes. Regenerates those pages with the current template and re-tags them with the current commit's version category. Up to `WIKI_EDIT_LIMIT` pages are upgraded per run.
   - **Phase 2 (Create):** Iterates the lexicon alphabetically, skipping keys already listed in `create_word_pages.state`. Creates new `word:LEMMA` pages on the wiki and appends each completed key to the state file. Up to `WIKI_EDIT_LIMIT` new pages are created per run.

5. **Commit step:** After all scripts finish, the workflow stages `*.state`, `aelaki/lexicon.json`, and `wiki-scripts/version_history.txt`, then commits and pushes with the message `chore(state): update word page bot state [skip ci]`.

### Concurrency and safety

- The workflow uses `concurrency: { group: word-page-bot, cancel-in-progress: false }` to ensure only one instance runs at a time without cancelling in-progress runs.
- The `paths-ignore: ["**/*.state"]` filter prevents the state commit from re-triggering the workflow.
- `WIKI_EDIT_LIMIT` (default 100) caps the total wiki edits per run to stay within Miraheze rate limits.
- All wiki edits use a 1.5-second throttle between API calls.
