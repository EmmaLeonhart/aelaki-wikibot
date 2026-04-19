#!/usr/bin/env python3
"""
check_wiki_orphans.py
=====================
Offline audit for orphaned pages in grammar/*.wiki.

A page is "orphaned" if no other page in the directory links to it via
any of the following forms:
  - [[PageName]]
  - [[PageName|display text]]
  - [[PageName#section]]
  - {{ill|PageName|...}}   (first arg = local target)
  - #REDIRECT [[Target]]   (counts as an incoming link to Target)

Category and namespace links ([[Category:X]], [[User:X]], [[File:X]],
[[Image:X]]) are ignored — they're not content links.

Matches the semantics of MediaWiki's Lonelypages special page closely
enough to predict what delete_orphaned_pages.py would sweep. Runs
without any wiki API calls.

Usage:
    python wiki-scripts/check_wiki_orphans.py            # report
    python wiki-scripts/check_wiki_orphans.py --json     # machine-readable
    python wiki-scripts/check_wiki_orphans.py --strict   # exit 1 if any orphans
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

GRAMMAR_DIR = Path(__file__).resolve().parent.parent / "grammar"

# [[Target]] or [[Target|display]] or [[Target#section]]
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")

# {{ill|Target|...}} — interlanguage link template, first arg is local target
ILL_RE = re.compile(r"\{\{\s*ill\s*\|\s*([^|}]+?)\s*(?:\||\}\})")

# Namespace-prefixed links we don't count as content incoming links.
IGNORED_NS_PREFIXES = (
    "category:", "user:", "user talk:", "file:", "image:",
    "mediawiki:", "template:", "talk:",
    # interwiki prefixes occasionally appearing in [[...]]
    "en:", "ja:", "de:", "fr:", "zh:", "ko:", "vi:", "ru:", "es:",
    "cdo:", "gan:", "hak:", "za:", "zh_classical:", "zh_min_nan:", "zh_yue:",
)


def normalize(title: str) -> str:
    """Wiki titles are case-insensitive on first char and use _ ≡ space."""
    t = title.strip().replace(" ", "_")
    if not t:
        return t
    return t[0].upper() + t[1:]


def page_key(filename: str) -> str:
    """grammar/Foo_bar.wiki → 'Foo_bar'."""
    return filename[:-5] if filename.endswith(".wiki") else filename


def is_ignored_target(target: str) -> bool:
    lower = target.lower()
    return any(lower.startswith(p) for p in IGNORED_NS_PREFIXES)


REDIRECT_RE = re.compile(r"^\s*#REDIRECT\b", re.IGNORECASE | re.MULTILINE)


def is_redirect(text: str) -> bool:
    return bool(REDIRECT_RE.match(text))


# Matches the PROTECTED_PREFIXES / PROTECTED_TITLES in delete_orphaned_pages.py.
# Category_*.wiki files in this repo represent the Category: namespace on the
# live wiki and are never swept by the orphan job.
PROTECTED_PAGE_PREFIXES = ("Category_", "User_", "Template_", "MediaWiki_")
PROTECTED_EXACT = {"Main_Page"}


def is_protected_page(page_key: str) -> bool:
    if page_key in PROTECTED_EXACT:
        return True
    return any(page_key.startswith(p) for p in PROTECTED_PAGE_PREFIXES)


def extract_outgoing_links(text: str) -> set[str]:
    """Return normalized page titles this page links to."""
    out = set()
    for m in WIKILINK_RE.finditer(text):
        target = m.group(1).strip()
        if not target or is_ignored_target(target):
            continue
        out.add(normalize(target))
    for m in ILL_RE.finditer(text):
        target = m.group(1).strip()
        if target and not is_ignored_target(target):
            out.add(normalize(target))
    return out


def load_pages(grammar_dir: Path) -> dict[str, str]:
    """Return {page_key: text} for every *.wiki in the directory."""
    pages = {}
    for path in sorted(grammar_dir.glob("*.wiki")):
        pages[page_key(path.name)] = path.read_text(encoding="utf-8")
    return pages


def build_link_graph(pages: dict[str, str]) -> dict[str, set[str]]:
    """Return {target_page: {source_pages...}} over all local pages."""
    # Normalize keys once so they match extracted targets.
    normalized_keys = {normalize(k): k for k in pages}
    incoming: dict[str, set[str]] = {k: set() for k in pages}

    for source_key, text in pages.items():
        for target_norm in extract_outgoing_links(text):
            original = normalized_keys.get(target_norm)
            if original and original != source_key:
                incoming[original].add(source_key)
    return incoming


def classify_orphans(
    pages: dict[str, str], incoming: dict[str, set[str]]
) -> dict[str, list[str]]:
    """Split no-incoming pages into buckets matching the delete job's semantics."""
    sweep = []       # would be deleted by delete_orphaned_pages.py
    protected = []   # no incoming links but in a protected namespace
    redirects = []   # no incoming links but marked #REDIRECT (Lonelypages skips these)

    for key, sources in incoming.items():
        if sources:
            continue
        if is_redirect(pages[key]):
            redirects.append(key)
        elif is_protected_page(key):
            protected.append(key)
        else:
            sweep.append(key)

    return {
        "sweep": sorted(sweep),
        "protected": sorted(protected),
        "redirects": sorted(redirects),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline orphan audit for grammar/*.wiki")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 if any sweep-eligible orphans found")
    parser.add_argument("--all", action="store_true",
                        help="Also list protected/redirect orphans (normally hidden)")
    parser.add_argument("--dir", default=str(GRAMMAR_DIR), help="Grammar directory to scan")
    args = parser.parse_args()

    grammar_dir = Path(args.dir)
    if not grammar_dir.is_dir():
        print(f"ERROR: {grammar_dir} is not a directory", file=sys.stderr)
        return 2

    pages = load_pages(grammar_dir)
    incoming = build_link_graph(pages)
    buckets = classify_orphans(pages, incoming)

    if args.json:
        print(json.dumps({
            "total_pages": len(pages),
            "sweep_count": len(buckets["sweep"]),
            **buckets,
        }, indent=2))
    else:
        print(f"Scanned {len(pages)} pages in {grammar_dir}")
        print(f"{len(buckets['sweep'])} pages would be swept by delete_orphaned_pages.py:")
        for name in buckets["sweep"]:
            print(f"  {name}")
        if args.all:
            print(f"\n{len(buckets['protected'])} protected orphans (namespace excluded from sweep):")
            for name in buckets["protected"]:
                print(f"  {name}")
            print(f"\n{len(buckets['redirects'])} redirect orphans (Lonelypages excludes redirects):")
            for name in buckets["redirects"]:
                print(f"  {name}")

    if args.strict and buckets["sweep"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
