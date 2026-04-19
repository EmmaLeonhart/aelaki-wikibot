# aelaki-wikibot — Work Queue

**This file is a queue, not a state snapshot.** When an item is done, delete it. Finished work lives in `git log` and commit messages. The long-tail backlog and the unresolved questions now live on the wiki:

- `grammar/To-do_list.wiki` — [[To-do list]], mechanical implementation items.
- `grammar/Unresolved_questions.wiki` — [[Unresolved questions]], documentation contradictions between wiki / megadoc / Python that need an operator ruling.

Both pages are linked from `grammar/Aelaki.wiki`'s "Helping with the project" section. The operator edits those pages directly; this repo syncs them via `wiki-scripts/sync_grammar_pages.py`.

## Currently in flight

1. **Generate a Converbs section on every verb word page.** `wiki-scripts/create_word_pages.py` currently writes v1 word pages with no converb table. Extend the verb branch so every verb lemma's word page gets a "Converbs" section at the bottom: a table of Class I prefix converbs (all nine `ConverbPrefixType` entries from `aelaki/converbs.py:22`) and Class II suffix converbs (nine entries in `ConverbSuffixType` at `aelaki/converbs.py:107`), each cell built by calling the appropriate `build_prefix_converb_*` / `build_suffix_converb_*` function with a canonical 3sg.M subject. Rows link to `[[Converbs]]` and to dedicated type pages where they exist (currently only `[[Instrumental]]`).

## Pinned corrections (I keep dropping these)

1. **Three co-authoritative sources, synthesized manually.** `grammar/*.wiki`, `data lake/Aelaki_Grammar_Guide.md` (the megadoc), and `aelaki/*.py` are three peer sources. The long-term goal is to synthesize them into one coherent grammar and eventually retire the megadoc by folding its content into wiki + Python. Specific directional rules:
   - **Python wins over the megadoc on morphology Python actually implements.** Where Python and megadoc disagree on the *shape* of an inflected form, Python's output is the current language.
   - **Megadoc wins over Python on existence claims.** If the megadoc says a category/prefix/construction exists and Python doesn't implement it, that thing exists — Python is incomplete, not authoritative.
   - **Wiki is the explanatory layer.** New wiki pages, *why* comments in Python.
   - **Audits surface discrepancies; don't auto-edit either side.** The operator decides case by case. Discrepancies land on [[Unresolved questions]], not in a commit.

2. **Don't create orphan wiki pages.** The bot pipeline sweeps orphans. Every new page or expanded-from-empty page needs at least one incoming `[[link]]` from a sibling grammar page before it goes into a commit. Check with `python wiki-scripts/check_wiki_orphans.py` before committing.

3. **Discord citation format is inline italic.** ''(source: Discord conlangs-server, YYYY-MM-DD)'' — established by `grammar/Switch_references.wiki`. Keep this convention; do not invent a new one.

4. **aelaki-sharp is not in the data lake and does not get deleted.** Outdated is not the same as bloat.

5. **Inanimate = uncountable.** Target lexicon ratio is ~10% inanimate / ~30% each for child/female/male. `normalize_lexicon.py` enforces this every pipeline cycle.

6. **Pipeline runs on GitHub Actions, not locally.** `cleanup-loop.yml` authenticates via `secrets.WIKI_PASSWORD` / `vars.WIKI_USERNAME`. Local `python wiki-scripts/foo.py` invocations are for debugging only.

7. **`?` is a real consonant now.** Glottal stop. Originally a parse-failure placeholder, consolidated in `aelaki/phonology.py:80`.

8. **Don't push manually. Rebase only.** A session-scoped cron handles the push. Running `git push` by hand bypasses that gate and leaves nothing for the scheduled cron to carry at end of session.

## Pointers

- Python morphology source of truth: `aelaki/*.py`.
- Wiki reference, synced bidirectionally: `grammar/*.wiki` via `wiki-scripts/sync_grammar_pages.py`.
- Bot scripts: `wiki-scripts/`.
- Offline orphan audit: `python wiki-scripts/check_wiki_orphans.py`.
- Discord corpus (primary-source attestations): `data lake/all_aelaki_messages.md`, `data lake/topic_*.md`, `data lake/dictionary.md`.
- Megadoc: `data lake/docs/Aelaki Grammar Guide.docx` + `data lake/Aelaki_Grammar_Guide.md`.
- C# port (outdated, offline): `aelaki-sharp/`.
