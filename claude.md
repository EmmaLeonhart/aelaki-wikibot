# aelaki-merged

## Project Description
Consolidated archive of all Aelaki constructed language materials. Aelaki is a conlang with non-concatenative templatic morphology, set in a ringworld science fiction universe.

## Repository Structure
- `grammar/` -- `*.wiki` pages, synced bidirectionally with aelaki.miraheze.org via `sync_grammar_pages.py`. **Authoritative reference** for the language today.
- `aelaki/` -- Python morphology engine used by the word-page pipeline (phonology, roots, person, nouns, verbs, etc.).
- `aelaki-sharp/` -- C# .NET 8.0 morphology library. Outdated snapshot from before recent consolidations; kept because it's slated to become a real .NET library. See `todo.md` for the update task.
- `wiki-scripts/` -- MediaWiki bot scripts that maintain aelaki.miraheze.org (create/update word pages, delete orphans, sync commit log).
- `data lake/` -- Lower-authority source materials kept for reference: `docs/` (original Google Docs as .docx + TAM/converb/verb spreadsheets), `discord/` (conlangs-server message exports), and anything else being audited before deletion.

## Key Facts
- The **live wiki** (mirrored to `grammar/*.wiki`) is the authoritative reference. The `.docx` guides in `data lake/docs/` are the original source that seeded it.
- `aelaki/` drives the pipeline; `aelaki-sharp/` is a sibling implementation that has drifted out of sync with the current grammar.

## Lexicon Gender Distribution
- **Inanimate = uncountable**: In Aelaki, inanimate gender represents uncountable/mass nouns (water, air, sand), not merely lifeless things. Countable nouns use child/female/male genders.
- **Target ratio**: ~10% inanimate, ~30% each for child/female/male
- `normalize_lexicon.py` runs every pipeline cycle to enforce this ratio by redistributing excess inanimate nouns
- `generate_random_words.py` uses weighted random (30/30/30/10) for new noun genders
- Future: Use Wiktionary countability data instead of random assignment (see todo.md)

## Workflow Guidelines
- **Commit early and often.** Every meaningful change should be committed with a clear, descriptive summary.
- **Keep this claude.md up to date** with architectural decisions and conventions.
- **Update README.md** when structure or content changes significantly.
