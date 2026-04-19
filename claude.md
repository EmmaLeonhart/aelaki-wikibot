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

## Three Co-Authoritative Sources (read STATUS.md pinned #1)
- `grammar/*.wiki`, `data lake/Aelaki_Grammar_Guide.md` (megadoc), and `aelaki/*.py` are three peers to **synthesize**, not reconcile. Long-term goal: retire the megadoc by folding it into wiki + Python.
- **Python wins over the megadoc on morphology Python actually implements** (shape of inflected forms = current state of the language).
- **Megadoc wins over Python on existence claims.** If the megadoc says X exists and Python doesn't implement it, X exists — Python is just incomplete. Don't prune real grammar to match the builders.
- **Wiki is the explanatory layer.** Megadoc topic without a wiki page → make a wiki page. Python behaviour the megadoc explains → add *why* comments to Python.
- **Audits produce reports, not commits.** Operator resolves discrepancies manually, one at a time.

## Lexicon Gender Distribution
- **Inanimate = uncountable**: In Aelaki, inanimate gender represents uncountable/mass nouns (water, air, sand), not merely lifeless things. Countable nouns use child/female/male genders.
- **Target ratio**: ~10% inanimate, ~30% each for child/female/male
- `normalize_lexicon.py` runs every pipeline cycle to enforce this ratio by redistributing excess inanimate nouns
- `generate_random_words.py` uses weighted random (30/30/30/10) for new noun genders
- Future: Use Wiktionary countability data instead of random assignment (see todo.md)

## Wiki Page Interlinking (Critical)
- **Every `grammar/*.wiki` page must have at least one incoming link from another page in the same directory.** The `delete_orphaned_pages.py` job deletes any orphaned page with no incoming links. Creating or populating a wiki page without also adding at least one `[[PageName]]` link to it from a sibling page will cause the new page to be swept on the next pipeline run.
- When adding a new page, immediately grep for a natural parent/sibling page (e.g. `Converbs.wiki` for a new converb-related page) and add a `[[link]]` or a `See also` entry.
- When populating a previously-empty page, same rule applies — check `git grep '[[PageName]]'` before committing and add at least one incoming link if none exist.
- `User:EmmaBot` is maintained by `update_bot_status.py` and sits in the `User:` namespace, which is excluded from the orphan sweep; it does not need explicit incoming links.
- Before committing a wiki change, run `python wiki-scripts/check_wiki_orphans.py` — it reports exactly the pages that `delete_orphaned_pages.py` would sweep, without hitting the live wiki.

## Discord Citation Format
- When wiki content draws on a message from the conlangs-server discord corpus, cite inline as italic: ''(source: Discord conlangs-server, YYYY-MM-DD)''. Established on `grammar/Switch_references.wiki`. Do not invent competing conventions.

## Workflow Guidelines
- **Commit early and often.** Every meaningful change should be committed with a clear, descriptive summary.
- **One STATUS.md / todo.md item per commit.** Work through the queue atomically — finish an item, commit it in isolation, move to the next. Bundling multiple unrelated items into one commit makes the history harder to read and harder to revert.
- **Keep this claude.md up to date** with architectural decisions and conventions.
- **Update README.md** when structure or content changes significantly.
- **Active work queue lives in `STATUS.md`.** `todo.md` is the long-tail backlog.
