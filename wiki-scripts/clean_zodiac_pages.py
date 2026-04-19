#!/usr/bin/env python3
"""Strip Wikipedia-import cruft from Yang_*/Yin_* sexagenary pages.

These pages were scraped from Wikipedia mirrors and carry baggage that
does not render on aelaki.miraheze.org:

  * Three identical ``<!--interwikis from wikidata-->`` header lines at
    the very top (dedupe to one).
  * Wikipedia-only templates — ``{{infobox Chinese}}``,
    ``{{Sexagenary cycle}}``, ``{{prefix|qq=}}``, ``{{intitle|qq=}}``,
    ``{{translated page|...}}`` — none of which exist locally.
  * A malformed ``<!-- == ... -->`` pronunciation block whose ``==``
    header sits inside the HTML comment.
  * Free-floating body interwikis scattered between sections — often
    bleed-over from neighbouring pages in the scrape (e.g. Fire Rat
    interwikis sitting on the Water Dog page).
  * Duplicate ``<!--jawiki derived wikidata interwikis-->`` and
    ``<!--zhwiki derived wikidata interwikis-->`` blocks that just repeat
    the clean top-of-file list.

The clean top-of-file ``<!--interwikis from wikidata-->`` line is the
only trustworthy interwiki source; we keep exactly one copy and delete
the rest of the body interwikis.

Run with --apply to write changes.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path


# Top-of-file Wikidata interwiki header (keep one, drop duplicates).
HEADER_RE = re.compile(
    r"^(<!--interwikis from wikidata-->[^\n]*\n)(?:<!--interwikis from wikidata-->[^\n]*\n)+",
    re.MULTILINE,
)

# Wikipedia-only templates. These are single-line and never contain
# nested templates in the scraped pages, so a non-greedy [^{}]* body is
# safe. {{wikidata link}} and {{nihongo}} are kept — wikidata link is
# the local convention for linking a page to its Wikidata item, and
# nihongo wraps Japanese-script names that we want to preserve inline.
WIKIPEDIA_TEMPLATE_NAMES = (
    "infobox Chinese",
    "Sexagenary cycle",
    "prefix",
    "intitle",
    "in title",
    "translated page",
    "otheruses",
    "otheruseslist",
    "merge",
    "main",
    "kotobank",
    "short description",
    "distinguish",
    "more footnotes",
    "more footnotes needed",
    "italic title",
    "shinto shrine",
    "hiyoshi faith",
    "reflist",
    "references",
    "notelist",
    "cite web",
    "cite book",
    "cite journal",
    "cite wikisource",
    "citation needed",
    "cn",
    "efn",
    "bare url pdf",
    "anchors",
    "Hiragana",
)
WIKIPEDIA_TEMPLATE_RE = re.compile(
    r"\{\{\s*(?:" + "|".join(re.escape(n) for n in WIKIPEDIA_TEMPLATE_NAMES)
    + r")\s*(?:\|[^{}]*)?\}\}",
    re.IGNORECASE,
)

# Content-preserving wrappers — render to their first textual argument
# so the wrapped text survives on aelaki.
#   {{transliteration|LANG|TEXT}}  -> TEXT
#   {{unicode|TEXT}}               -> TEXT
#   {{lang|CODE|TEXT|...}}         -> TEXT
#   {{lang-xx|TEXT}}               -> TEXT
TRANSLITERATION_RE = re.compile(
    r"\{\{\s*transliteration\s*\|\s*[^|{}]*\|([^|{}]*?)(?:\|[^{}]*)?\}\}",
    re.IGNORECASE,
)
UNICODE_TEMPLATE_RE = re.compile(
    r"\{\{\s*unicode\s*\|([^|{}]*?)(?:\|[^{}]*)?\}\}",
    re.IGNORECASE,
)
LANG_CODE_RE = re.compile(
    r"\{\{\s*lang\s*\|\s*[^|{}]*\|([^|{}]*?)(?:\|[^{}]*)?\}\}",
    re.IGNORECASE,
)
LANG_XX_RE = re.compile(
    r"\{\{\s*lang-[a-z-]+\s*\|([^|{}]*?)(?:\|[^{}]*)?\}\}",
    re.IGNORECASE,
)

# {{ISBN|NNN-N-NNN-NNNNN-N}} -> "ISBN NNN-N-NNN-NNNNN-N"
ISBN_TEMPLATE_RE = re.compile(
    r"\{\{\s*ISBN\s*\|\s*([0-9X\-\s]+?)(?:\s*\|[^{}]*)?\}\}",
    re.IGNORECASE,
)

# <ref>...</ref> citation tags (Wikipedia footnotes) plus self-closing
# <ref name="..." /> references. Drop entirely — they reference Wikipedia
# sources and render as red numbers on a wiki without {{reflist}}.
REF_TAG_RE = re.compile(r"<ref\b[^>]*?/>|<ref\b[^>]*?>.*?</ref>",
                        re.IGNORECASE | re.DOTALL)

# Bare "<!--Xwiki derived wikidata interwikis-->" comments left behind
# when my earlier cleanup stripped the interwikis that followed them.
BARE_DERIVED_COMMENT_RE = re.compile(
    r"^<!--\s*[a-z]+wiki derived wikidata interwikis\s*-->\s*\n",
    re.IGNORECASE | re.MULTILINE,
)

# Malformed pronunciation block: HTML comment that opens before a ``==``
# header and closes after the list. The scraped form always looks like
# "<!--\n==\n* ...\n-->". We drop the whole comment.
MALFORMED_COMMENT_RE = re.compile(r"<!--\s*\n==\n.*?-->\s*", re.DOTALL)

# Meta "please transliterate" and repeated-title commented breadcrumbs.
META_COMMENT_RE = re.compile(
    r"<!--please transliterate[^>]*?-->(?:<!--[^>]*?-->)*\s*",
    re.IGNORECASE,
)

# Language codes that appear as free-floating interwiki links in these
# pages. These are stripped when they are the whole line; they remain
# inside the kept top-of-file header line because that line starts with
# the comment marker.
INTERWIKI_CODES = (
    "af", "ar", "cdo", "ceb", "de", "en", "eo", "es", "fa", "fr",
    "hak", "id", "it", "ja", "ko", "nds", "pt", "ru", "th", "uk",
    "vi", "za", "zh", "zh-min-nan", "zh-yue",
)
INTERWIKI_LINE_RE = re.compile(
    r"^\s*(?:\[\[(?:" + "|".join(INTERWIKI_CODES) + r"):[^\[\]\n]*?\]\]\s*)+$",
    re.MULTILINE,
)

# Duplicate "<!--jawiki derived wikidata interwikis-->" and
# "<!--zhwiki derived wikidata interwikis-->" blocks plus the interwiki
# lines that follow each marker.
DERIVED_INTERWIKI_BLOCK_RE = re.compile(
    r"<!--(?:jawiki|zhwiki) derived wikidata interwikis-->\s*\n"
    r"(?:\s*\[\[(?:" + "|".join(INTERWIKI_CODES) + r"):[^\[\]\n]*?\]\]\s*\n?)+",
    re.IGNORECASE,
)

# Empty bullet lines left behind when we removed a template that was
# the entire bullet body (e.g. "* {{prefix|qq=}}"). Empty headings are
# intentionally preserved — the operator may be keeping them as
# placeholders for future content.
EMPTY_BULLET_RE = re.compile(r"^\*\s*$\n?", re.MULTILINE)

# Wikipedia-scrape maintenance categories that have no counterpart on
# aelaki.miraheze.org. "translated pages with valid <lang> interwikis"
# is written by the scrape pipeline, "Wikidata has short description"
# is an enwiki housekeeping bucket, and "WikiProject Japanese Calendar"
# is an enwiki WikiProject.
WIKIPEDIA_MAINTENANCE_CATEGORY_RE = re.compile(
    r"^\[\[\s*Category\s*:\s*"
    r"(?:translated pages with valid [a-z-]+ interwikis"
    r"|Wikidata has short description"
    r"|WikiProject Japanese Calendar)"
    r"\s*\]\]\s*\n?",
    re.IGNORECASE | re.MULTILINE,
)

# Year-only interwiki links like "[[:en:2149|2149]]" — both halves are
# the same digit string. These render as enwiki interwiki links, but
# the year tables already link plain [[YYYY]] elsewhere, so collapse to
# plain text. Non-year [[:en:...]] links (concepts) are left alone.
EN_YEAR_LINK_RE = re.compile(r"\[\[:en:(\d+)\|\1\]\]")


def clean(text: str) -> tuple[str, int]:
    """Return (cleaned_text, number_of_substitutions)."""
    n = 0
    # 1. Collapse triplicate header.
    text, k = HEADER_RE.subn(r"\1", text)
    n += k
    # 2. Drop duplicate derived-interwiki blocks (before scraping free
    #    interwikis, so their preamble comments go with them).
    text, k = DERIVED_INTERWIKI_BLOCK_RE.subn("", text)
    n += k
    # 3. Drop <ref>...</ref> and self-closing <ref /> footnotes. Run
    #    before template removal so that a <ref> whose body contains a
    #    {{cite web}} gets removed whole instead of leaving debris.
    text, k = REF_TAG_RE.subn("", text)
    n += k
    # 4. Strip Wikipedia-only templates.
    text, k = WIKIPEDIA_TEMPLATE_RE.subn("", text)
    n += k
    # 5. Unwrap content-preserving templates (transliteration/unicode)
    #    so the wrapped text survives. {{lang|CODE|TEXT}} and
    #    {{lang-xx|TEXT}} are intentionally left in place — the scraped
    #    usages are all named-param style ("|c=丙午|p=bǐngwǔ"), which
    #    this kind of simple unwrap mangles.
    text, k = TRANSLITERATION_RE.subn(r"\1", text)
    n += k
    text, k = UNICODE_TEMPLATE_RE.subn(r"\1", text)
    n += k
    # 6. Replace {{ISBN|...}} with "ISBN ..." prose form.
    text, k = ISBN_TEMPLATE_RE.subn(r"ISBN \1", text)
    n += k
    # 7. Drop malformed comment blocks, meta comments, and bare
    #    "<!--Xwiki derived wikidata interwikis-->" markers left behind.
    text, k = MALFORMED_COMMENT_RE.subn("", text)
    n += k
    text, k = META_COMMENT_RE.subn("", text)
    n += k
    text, k = BARE_DERIVED_COMMENT_RE.subn("", text)
    n += k
    # 5. Strip free-floating interwiki lines anywhere in the body. The
    #    kept top-of-file header line starts with "<!--interwikis from
    #    wikidata-->" and is not matched by INTERWIKI_LINE_RE because of
    #    its comment prefix.
    text, k = INTERWIKI_LINE_RE.subn("", text)
    n += k
    # 6. Drop empty bullets left by removed templates.
    text, k = EMPTY_BULLET_RE.subn("", text)
    n += k
    # 7. Drop Wikipedia-scrape maintenance categories.
    text, k = WIKIPEDIA_MAINTENANCE_CATEGORY_RE.subn("", text)
    n += k
    # 8. Collapse enwiki year interwikis "[[:en:YYYY|YYYY]]" -> "YYYY".
    text, k = EN_YEAR_LINK_RE.subn(r"\1", text)
    n += k
    # 9. Collapse runs of 2+ spaces in prose to a single space.
    #    Preserve line-initial indentation by only touching runs that
    #    are not at the very start of a line.
    text, k = re.subn(r"(?<=\S)  +", " ", text)
    n += k
    # 10. Collapse runs of blank lines introduced by the deletions.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 11. Trim trailing whitespace before final newline.
    text = text.rstrip() + "\n"
    return text, n


def process_file(path: Path, apply: bool) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n = clean(text)
    if new_text == text:
        return 0
    if apply:
        path.write_text(new_text, encoding="utf-8")
    return n


def main() -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Actually write changes (default: dry-run).")
    parser.add_argument("path", nargs="?", default="grammar",
                        help="Directory to scan (default: grammar/).")
    parser.add_argument("--glob", default="{Yang,Yin}_*.wiki",
                        help="Glob pattern (default: Yang_*/Yin_* pages).")
    args = parser.parse_args()

    root = Path(args.path)
    patterns = args.glob
    # Expand brace-style {a,b} glob since Path.glob doesn't support it.
    if "{" in patterns and "}" in patterns:
        pre, rest = patterns.split("{", 1)
        opts, post = rest.split("}", 1)
        globs = [pre + opt + post for opt in opts.split(",")]
    else:
        globs = [patterns]

    total_files = 0
    total_subs = 0
    for pat in globs:
        for wiki in sorted(root.glob(pat)):
            n = process_file(wiki, args.apply)
            if n:
                total_files += 1
                total_subs += n
                print(f"  {wiki.name}: {n} substitution(s)")

    verb = "cleaned" if args.apply else "would clean"
    print(f"\n{verb} {total_subs} item(s) across {total_files} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
