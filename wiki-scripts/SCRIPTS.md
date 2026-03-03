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

### word_page_loop.sh (CI — GitHub Actions)

Shell orchestrator that runs the full pipeline:
1. `update_bot_status.py` — declare the run on the wiki
2. `create_word_pages.py` — create word pages

Builds a run tag from GitHub Actions environment variables (commit SHA, event type, run ID).

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
├── create_word_pages.py        # word:LEMMA page creation (CI)
├── update_bot_status.py        # Bot status page updater (CI)
├── create_word_articles.py     # Article generation script
├── sync_lexicon_page.py        # Lexicon page sync script
├── *.state                     # Resume state (gitignored)
└── *.log                       # Run logs (gitignored)

.github/workflows/
└── word-pages.yml              # GitHub Actions workflow for word page bot
```

## GitHub Actions Setup

The word page bot runs via `.github/workflows/word-pages.yml`.

**Triggers:**
- Every push (except `*.state` file changes)
- Daily at 00:00 UTC
- Manual dispatch

**Required repository configuration:**
1. **Variable** `WIKI_USERNAME` — bot-password username (e.g. `EmmaBot@EmmaBot`)
2. **Secret** `WIKI_PASSWORD` — bot password from `Special:BotPasswords`

Set these at: `Settings > Secrets and variables > Actions`
