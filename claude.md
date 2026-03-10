# aelaki-merged

## Project Description
Consolidated archive of all Aelaki constructed language materials. Aelaki is a conlang with non-concatenative templatic morphology, set in a ringworld science fiction universe.

## Repository Structure
- `docs/` -- Authoritative documents: grammar guide (.docx, **primary reference**), proto-language, converb/TAM/verb spreadsheets
- `aelaki-sharp/` -- C# .NET 8.0 implementation of Aelaki morphology (noun, verb, adjective, converb, number generation)
- `aelaki-split/` -- Markdown grammar guide (~31k lines), Python morphology script, worldbuilding docs (17 files)
- `wiki/` -- MediaWiki XML export of Aelaki wiki
- `discord/` -- Personal message exports from a conlangs Discord server (author's messages only)

## Key Facts
- The `.docx` grammar guide in `docs/` is the **most authoritative** reference for the language
- The markdown grammar guide in `aelaki-split/` is extensive but may diverge from the docx
- `aelaki-sharp/` and `aelaki-split/` were imported via `git subtree` with full history preserved

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
