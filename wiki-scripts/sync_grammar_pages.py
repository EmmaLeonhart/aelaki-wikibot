#!/usr/bin/env python3
"""
sync_grammar_pages.py
=====================
Bidirectional sync of grammar documentation pages between
the Aelaki wiki (Category:Aelaki grammar + subcategories)
and the local ``grammar/`` directory.

Direction of sync:
  --pull   : wiki  -> local files  (fetch latest from wiki)
  --push   : local files -> wiki   (upload changed files to wiki)
  --sync   : pull then push        (default)

The grammar pages live in the repo so they can be edited easily
with Claude Code and other local tools, then pushed back to the
wiki automatically by the CI pipeline.

File layout::

    grammar/
      _sync_state.json        # title <-> filename + revid metadata
      Aelaki_grammar.wiki     # page wikitext
      Nouns.wiki
      ...

Usage::

    python wiki-scripts/sync_grammar_pages.py --pull
    python wiki-scripts/sync_grammar_pages.py --push --apply
    python wiki-scripts/sync_grammar_pages.py --sync --apply
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Allow running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import connect, safe_save

GRAMMAR_DIR = os.path.join(os.path.dirname(__file__), "..", "grammar")
STATE_FILE = os.path.join(GRAMMAR_DIR, "_sync_state.json")
CATEGORY = "Aelaki grammar"
SYNC_CATEGORY = "git synced pages"

# Titles we will never sync, regardless of which category surfaced them.
# Word:/Lexeme:/Item:/Property: pages are generated and managed by the
# word-page and Wikibase pipelines; pulling them into grammar/ was what
# turned an 8-minute sync step into a multi-hour mass download after a
# user tagged [[Category:Ringworld]] (which contains thousands of Word:
# pages) with [[Category:git synced pages]].
_TITLE_SKIP_PREFIXES = ("Word:", "Lexeme:", "Item:", "Property:")

# Hard cap on how many pages a single pull is allowed to touch. If the
# category walk exceeds this, something has gone wrong (usually recursion
# into an unrelated category tree) and we abort rather than commit a huge
# spurious changeset.
_PULL_PAGE_CAP = 500

# Git-synced pages are authored locally; they must never carry the
# wanted-pages stub category. If a stub was ever pulled into a local file
# (e.g. before create_wanted_pages.py learned to skip synced titles), strip
# the category at push time so the wiki heals on the next sync.
_WANTED_CATEGORY_RE = re.compile(
    r"\s*\[\[\s*Category\s*:\s*Created from Wanted Pages\s*\]\]\s*",
    re.IGNORECASE,
)


def strip_wanted_category(text: str) -> tuple[str, bool]:
    """Remove [[Category:Created from Wanted Pages]]. Returns (text, stripped)."""
    new_text, n = _WANTED_CATEGORY_RE.subn("\n", text)
    return (new_text, n > 0)


# ---------------------------------------------------------------------------
# Filename <-> title mapping
# ---------------------------------------------------------------------------

def title_to_filename(title: str) -> str:
    """Convert a wiki page title to a safe local filename."""
    # Strip namespace prefix if present (e.g., "Category:Foo" -> "Category_Foo")
    name = re.sub(r'[<>:"/\\|?*]', '_', title)
    name = name.replace(' ', '_')
    # Collapse multiple underscores
    name = re.sub(r'_+', '_', name).strip('_')
    return name + ".wiki"


def filename_to_title(filename: str, state: dict) -> str | None:
    """Look up the original page title from the state metadata."""
    for title, meta in state.items():
        if meta.get("file") == filename:
            return title
    return None


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    """Load sync state (title -> {file, revid})."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    """Persist sync state."""
    os.makedirs(GRAMMAR_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Category member enumeration (recursive, batched)
# ---------------------------------------------------------------------------

def iter_category_with_revisions(site, category_name: str, namespaces: str = "0|14"):
    """Yield (title, ns, revid, text) for every page in Category:<category_name>.

    Uses ``generator=categorymembers`` + ``prop=revisions`` so each page
    comes back with its latest revid and wikitext in a single batched API
    call (with continuation). This is the same pattern as
    shintowiki-scripts/shinto_miraheze/sync_need_translation.py and avoids
    the per-page ``page.text()`` round-trip that the old implementation
    relied on.
    """
    params = {
        "generator": "categorymembers",
        "gcmtitle": f"Category:{category_name}",
        "gcmnamespace": namespaces,
        "gcmlimit": "max",
        "prop": "revisions",
        "rvprop": "ids|content",
        "rvslots": "main",
        "formatversion": "2",
    }
    while True:
        result = site.api("query", **params)
        pages = result.get("query", {}).get("pages", [])
        for page in pages:
            if page.get("missing"):
                continue
            revs = page.get("revisions") or []
            if not revs:
                continue
            rev = revs[0]
            revid = rev.get("revid")
            text = rev.get("slots", {}).get("main", {}).get("content", "")
            if revid is None:
                continue
            yield page["title"], page.get("ns", 0), revid, text
        if "continue" in result:
            params.update(result["continue"])
        else:
            break


def walk_category(site, category_name: str, seen: set[str] | None = None,
                  namespaces: str = "0|14", recurse: bool = True,
                  cap: int = _PULL_PAGE_CAP) -> dict[str, tuple[int, int, str]]:
    """Collect pages below a category.

    Returns a dict mapping title -> (ns, revid, text). When ``recurse`` is
    true, subcategories are descended into and their pages are included
    too; the subcategory page itself is also kept so category descriptions
    stay in sync.

    Titles whose prefix matches ``_TITLE_SKIP_PREFIXES`` are dropped so
    tagging a broad parent category with ``[[Category:git synced pages]]``
    cannot drag in thousands of generated word/lexeme pages. The hard cap
    is an additional safety net: if more than ``cap`` pages are collected
    we raise, because the sync was never meant to download whole namespaces.
    """
    if seen is None:
        seen = set()
    if category_name in seen:
        return {}
    seen.add(category_name)

    collected: dict[str, tuple[int, int, str]] = {}
    for title, ns, revid, text in iter_category_with_revisions(
            site, category_name, namespaces=namespaces):
        if title.startswith(_TITLE_SKIP_PREFIXES):
            continue
        collected[title] = (ns, revid, text)
        if len(collected) > cap:
            raise RuntimeError(
                f"Category walk of [[Category:{category_name}]] exceeded "
                f"{cap} pages — refusing to continue. Likely cause: a broad "
                f"parent category was tagged for sync. Fix by untagging or "
                f"narrowing the category."
            )
        if recurse and ns == 14:
            sub_name = title.split(":", 1)[1] if ":" in title else title
            collected.update(walk_category(
                site, sub_name, seen, namespaces, recurse=True, cap=cap))
    return collected


# ---------------------------------------------------------------------------
# Pull: wiki -> local
# ---------------------------------------------------------------------------

def pull(site, state: dict, verbose: bool = True) -> int:
    """Pull grammar pages from the wiki into local files.

    Walks both Category:Aelaki grammar (recursively) and Category:git synced
    pages so any page opted into sync — whether by living in the grammar
    tree or by being tagged directly — gets its local copy refreshed.

    Returns number of files updated.
    """
    os.makedirs(GRAMMAR_DIR, exist_ok=True)
    # Grammar tree: recurse (small, well-known set of subcategories).
    # Sync-tag category: do NOT recurse — subcategory contents are not
    # implicitly owned by the sync, and recursing there is what caused the
    # Ringworld-category mass-pull incident. Include template namespace (10)
    # so tagged templates (and tagged categories) sync alongside main pages;
    # the point of the opt-in tag is editing descriptions in git.
    collected = walk_category(site, CATEGORY, recurse=True)
    collected.update(walk_category(
        site, SYNC_CATEGORY, recurse=False, namespaces="0|10|14"))
    if not collected:
        print("No pages found in Category:Aelaki grammar or Category:git synced pages.")
        return 0

    updated = 0
    titles_seen = set(collected.keys())

    for title, (ns, revid, text) in collected.items():
        if not text or not text.strip():
            continue

        filename = title_to_filename(title)
        filepath = os.path.join(GRAMMAR_DIR, filename)

        old_meta = state.get(title, {})
        if old_meta.get("revid") == revid and os.path.exists(filepath):
            if verbose:
                print(f"  unchanged: {title}")
            state[title] = {"file": filename, "revid": revid}
            continue

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        state[title] = {"file": filename, "revid": revid}
        updated += 1
        if verbose:
            print(f"  pulled: {title} -> {filename}")

    # Clean up state entries for pages no longer in category
    removed = [t for t in state if t not in titles_seen]
    for t in removed:
        old_file = os.path.join(GRAMMAR_DIR, state[t].get("file", ""))
        if os.path.exists(old_file):
            os.remove(old_file)
            print(f"  removed: {t} (no longer in category)")
        del state[t]

    print(f"Pull complete: {updated} files updated, {len(titles_seen)} total pages.")
    return updated


# ---------------------------------------------------------------------------
# Discover: find pages in [[Category:git synced pages]] not yet tracked
# ---------------------------------------------------------------------------

def discover(site, state: dict, verbose: bool = True) -> int:
    """Find pages in Category:git synced pages that aren't tracked yet.

    Downloads their content and adds them to the sync state so future
    runs will keep them in sync.

    Returns number of new pages adopted.
    """
    os.makedirs(GRAMMAR_DIR, exist_ok=True)
    adopted = 0

    for title, ns, revid, text in iter_category_with_revisions(
            site, SYNC_CATEGORY, namespaces="0|10|14"):
        if title in state:
            if verbose:
                print(f"  already tracked: {title}")
            continue

        if not text or not text.strip():
            continue

        filename = title_to_filename(title)
        filepath = os.path.join(GRAMMAR_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        state[title] = {"file": filename, "revid": revid}
        adopted += 1
        print(f"  adopted: {title} -> {filename}")

    print(f"Discover complete: {adopted} new pages adopted for syncing.")
    return adopted


# ---------------------------------------------------------------------------
# Push: local -> wiki
# ---------------------------------------------------------------------------

def push(site, state: dict, apply: bool = False, run_tag: str = "",
         verbose: bool = True) -> int:
    """Push local grammar files back to the wiki.

    Only pushes files that differ from the wiki's current content.
    Returns number of pages updated.
    """
    if not os.path.isdir(GRAMMAR_DIR):
        print("No grammar/ directory found. Run --pull first.")
        return 0

    updated = 0
    run_tag_suffix = f" ({run_tag})" if run_tag else ""

    for filename in sorted(os.listdir(GRAMMAR_DIR)):
        if not filename.endswith(".wiki"):
            continue

        filepath = os.path.join(GRAMMAR_DIR, filename)
        title = filename_to_title(filename, state)
        if title is None:
            # New file not in state — derive title from filename
            title = filename.replace(".wiki", "").replace("_", " ")
            print(f"  new file (no state): {filename} -> {title}")

        with open(filepath, "r", encoding="utf-8") as f:
            local_text = f.read()

        local_text, stripped = strip_wanted_category(local_text)
        if stripped:
            print(f"  stripped wanted-pages category from: {title}", flush=True)

        page = site.pages[title]
        try:
            wiki_text = page.text() if page.exists else ""
        except Exception:
            wiki_text = ""

        if local_text.rstrip() == wiki_text.rstrip():
            if verbose:
                print(f"  unchanged: {title}")
            continue

        if apply:
            summary = f"Bot: sync grammar page from repo{run_tag_suffix}"
            saved = safe_save(page, local_text, summary)
            if saved:
                # Update revid in state
                page = site.pages[title]  # re-fetch for new revid
                state[title] = {"file": filename, "revid": page.revision}
                updated += 1
                print(f"  pushed: {title}")
            else:
                print(f"  FAILED to push: {title}")
        else:
            print(f"  would push: {title}")
            updated += 1

    action = "pushed" if apply else "would push"
    print(f"Push complete: {updated} pages {action}.")
    return updated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Sync grammar pages between wiki and repo.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pull", action="store_true", help="Pull wiki pages to local files.")
    group.add_argument("--push", action="store_true", help="Push local files to wiki.")
    group.add_argument("--sync", action="store_true", help="Pull then push (default).")
    parser.add_argument("--apply", action="store_true", help="Actually write to wiki (push/sync only).")
    parser.add_argument("--run-tag", default="", help="Run tag for edit summaries.")
    parser.add_argument("--quiet", action="store_true", help="Only print changes.")
    args = parser.parse_args()

    # Default to sync if nothing specified
    do_pull = args.pull or args.sync or (not args.pull and not args.push)
    do_push = args.push or args.sync or (not args.pull and not args.push)

    site = connect()
    state = load_state()

    if do_pull:
        print("=== DISCOVER: adopt new pages from Category:git synced pages ===")
        discover(site, state, verbose=not args.quiet)
        save_state(state)

        print("=== PULL: wiki -> local ===")
        pull(site, state, verbose=not args.quiet)
        save_state(state)

    if do_push:
        print("=== PUSH: local -> wiki ===")
        push(site, state, apply=args.apply, run_tag=args.run_tag,
             verbose=not args.quiet)
        save_state(state)


if __name__ == "__main__":
    main()
