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
- **Inanimate nouns should be rare**: only ~5-10% of nouns should be inanimate gender
- The auto-generated nouns in `aelaki/lexicon.json` were overgenerated as inanimate (~27% currently); new nouns should default to child/female/male distribution
- When generating or assigning noun genders, distribute roughly equally among child, female, and male; only use inanimate for genuinely non-living, non-agentive things

## Workflow Guidelines
- **Commit early and often.** Every meaningful change should be committed with a clear, descriptive summary.
- **Keep this claude.md up to date** with architectural decisions and conventions.
- **Update README.md** when structure or content changes significantly.
