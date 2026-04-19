# aelaki-wikibot — Work Queue

**This file is a queue, not a state snapshot.** When an item is done, delete it. Finished work lives in `git log` and commit messages.

The work here is **keeping the Aelaki conlang coherent and the wiki at aelaki.miraheze.org an accurate reference** — Python as the implementation source of truth, the wiki as the public-facing grammar reference, and a bot pipeline that keeps the two in sync while auto-generating word pages for every lemma. The question each queue item answers is: *what does it take to make the language and its wiki a finished, consistent artifact?*

## Queued work

1. **Audit the 4db8259d xlsx→wiki migration against current Python.** During the data-lake cleanup three xlsx tables from `data lake/docs/` were folded into `Converbs.wiki`, `TAM.wiki`, and `Aelaki.wiki`. Those xlsx sources were snapshots from before several grammar consolidations (unified vowel shift, inanimate-gender behavior, Ki-syllable tables, stative-verb prefixes). The migrated content may contain claims that no longer hold. Diff each page's tables against `aelaki/converbs.py`, `aelaki/verbs.py`, `aelaki/phonology.py`, `aelaki/gender.py`. Python wins when they disagree. Known conflict so far: Converbs.wiki lists 8 Class I prefixes; `aelaki/converbs.py` has 6.

2. **Parse Sægetlæræchïfïshë.** Appears in the 2025-06-04 car-crash discord sentence and is reproduced in `grammar/Random_sentences.wiki`. Nonstandard romanization (or pre-consolidation romanization); needs a manual morpheme decomposition before it can be fed through `aelaki/` or used as a worked example on `grammar/Verb.wiki`. The discord gloss was `SIM.CONV-HOD-be_hit.COMP-INAN.4p-VIS.PAST` but the surface does not match that skeleton with any current verb root.

3. **Clarify the status of ë (e-diaeresis) in the vowel grid.** ë appears in evidential suffixes (`-shë`, `-shëm`, `-shëlon`) and the temporal adposition (`Slë`) but is not in the vowel grid in `phonology.py`. The umlaut pair ''Slë → Slæ'' suggests ë shifts like ə (to æ) rather than like plain e (front, would not shift). Decide: is ë a spelling variant of ə, a grid-distinct vowel, or a special case restricted to these morphemes? Then update `VOWELS`, `VOWEL_SHIFT_MAP`, and `apply_umlaut()` accordingly.

4. **Expand the thin grammar wiki pages.** Twelve pages sit at 15–29 lines and are substantively under-specified: Positive, Present, Quirky_optative, Collective, Comparative, Deliberative, First_person_nouns, Mythic, Superlative, Contact_influence, Imperative, Plural. Six more (30–44 lines) are moderate: Adpositions, Copula, Pseudopronouns, Word_order (now expanded), Negative, Optative. Every expansion should cite `aelaki/*.py` as the source of truth and pull attestations from `data lake/all_aelaki_messages.md` or `data lake/topic_*.md` where available, with inline ''(source: Discord conlangs-server, YYYY-MM-DD)'' citations.

5. **Structural wiki improvements.** No pedagogical "Getting started" page or learning path exists. Complex-syntax coverage (subordination, coordination, multi-clause) is thin — the new `Switch_references.wiki` is a first pass but `Basic_syntax.wiki` is still a 3-line stub. `Questions.wiki` needs more example-sentence coverage. These are discoverability, not correctness, but the wiki is the language's public face so they matter.

6. **Word-page bot v2 format.** `wiki-scripts/create_word_pages.py` currently generates a v1 word page template. v2 should add: pronunciation / phonetic transcription, etymology linking to proto-Aelaki roots, example sentences drawn from `data lake/all_aelaki_messages.md`, grouped-by-TAM verb inflection tables, possession paradigms for nouns, cross-links between morphologically related lemmas (e.g. `bsl` noun ↔ `bsl_adj` adjective). Needs a companion `update_word_pages.py` that finds pages tagged `{{wordpage|v1}}` and regenerates them with v2.

7. **Automatic new-word ingestion from discord corpus.** `data lake/dictionary.md` and `data lake/topic_*.md` hold ~120 unique Aelaki word forms. Extend `extract_discord_aelaki.py` (or a successor) to identify forms not yet in `aelaki/lexicon.py`, propose them with best-guess roots + gender, and feed them into the lexicon so the bot can create their word pages on the next run. Goal: every documented form on discord has a `word:LEMMA` page.

8. **State-file audits.** `create_word_pages.state` may hold stale entries from renamed keys (e.g. `dzhbhr → jbhr`). A general review of all pipeline state files (`*.state`, `*.last`) and their failure modes under `set -euo pipefail` is overdue. Annual reconciliation is already wired (`reconcile_state.py`) but other state files have not had the same pass.

9. **Bring aelaki-sharp in line with canonical grammar.** The C# morphology library is an outdated snapshot from before the unified back-to-front vowel shift, inanimate-gender behavior, Ki-syllable tables, and stative-verb prefixes were consolidated. Intended to eventually ship as a .NET library. Not in the data lake. Diff each module against `aelaki/*.py` and update module by module.

## Pinned corrections (I keep dropping these)

1. **`aelaki/*.py` is the source of truth.** When wiki, xlsx, or discord disagree with Python, Python wins. The only exception is when the disagreement reveals a Python bug — in which case fix Python, not the docs.

2. **Don't create orphan wiki pages.** The bot pipeline sweeps orphans. Every new page or expanded-from-empty page needs at least one incoming `[[link]]` from a sibling grammar page before it goes into a commit. Check with `git grep` before committing.

3. **Discord citation format is inline italic.** ''(source: Discord conlangs-server, YYYY-MM-DD)'' — established by `grammar/Switch_references.wiki`. Keep this convention; do not invent a new one.

4. **aelaki-sharp is not in the data lake and does not get deleted.** It is slated to become a real .NET library, just not yet. Outdated is not the same as bloat.

5. **Inanimate = uncountable.** Target lexicon ratio is ~10% inanimate / ~30% each for child/female/male. `normalize_lexicon.py` enforces this every pipeline cycle. Never reintroduce random inanimate assignment for countable nouns.

6. **Pipeline runs on GitHub Actions, not locally.** `cleanup-loop.yml` authenticates via `secrets.WIKI_PASSWORD` / `vars.WIKI_USERNAME`. Local `python wiki-scripts/foo.py` invocations are for debugging only.

7. **`?` is a real consonant now.** Glottal stop. Originally a parse-failure placeholder, but the roots containing it were liked enough that it stayed. Lexicon generation should pick it like any other consonant. Consolidated in `aelaki/phonology.py:80`.

8. **Don't push manually.** A cron push handles it. If a push is needed earlier, reschedule the cron, don't run `git push` by hand.

## Pointers

- Python morphology source of truth: `aelaki/*.py`.
- Wiki reference, synced bidirectionally: `grammar/*.wiki` via `wiki-scripts/sync_grammar_pages.py`.
- Bot scripts: `wiki-scripts/`.
- Offline orphan audit: `python wiki-scripts/check_wiki_orphans.py` — run before any commit that adds or empties a grammar page. Output mirrors `delete_orphaned_pages.py` sweep semantics.
- Discord corpus (primary-source attestations): `data lake/all_aelaki_messages.md`, `data lake/topic_*.md`, `data lake/dictionary.md`.
- Remaining docx: `data lake/docs/Aelaki Grammar Guide.docx` (authoritative original, not yet folded).
- C# port (outdated, offline): `aelaki-sharp/`.
- Full backlog and checkbox history: `todo.md`.
