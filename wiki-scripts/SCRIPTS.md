# Aelaki Wikibot Scripts

## Overview

Bot scripts for maintaining and expanding the [Aelaki Wiki](https://aelaki.miraheze.org).
Based on patterns from [shintowiki-scripts](https://github.com/).

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
| `create_word_articles.py` | Ready | Creates wiki articles for each root word in the lexicon |
| `sync_lexicon_page.py` | Ready | Syncs the roots summary table to a wiki page |

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
├── config.py                   # Connection settings and constants
├── utils.py                    # Shared bot utilities
├── create_word_articles.py     # Article generation script
├── sync_lexicon_page.py        # Lexicon page sync script
├── *.state                     # Resume state (gitignored)
└── *.log                       # Run logs (gitignored)
```
