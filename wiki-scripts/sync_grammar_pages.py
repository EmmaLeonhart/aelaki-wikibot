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
import time

# Allow running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import THROTTLE
from utils import connect, safe_save

GRAMMAR_DIR = os.path.join(os.path.dirname(__file__), "..", "grammar")
STATE_FILE = os.path.join(GRAMMAR_DIR, "_sync_state.json")
CATEGORY = "Aelaki grammar"


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
# Category member enumeration (recursive)
# ---------------------------------------------------------------------------

def get_category_pages(site, category_name: str, seen: set[str] | None = None) -> list[dict]:
    """Recursively list all pages in a category and its subcategories.

    Returns list of dicts with 'title' and 'ns' keys.
    """
    if seen is None:
        seen = set()
    if category_name in seen:
        return []
    seen.add(category_name)

    pages = []
    cat = site.categories[category_name]
    for member in cat.members():
        title = member.name
        ns = member.namespace
        if ns == 14:  # Category namespace — recurse
            sub_name = title.replace("Category:", "", 1)
            pages.extend(get_category_pages(site, sub_name, seen))
            # Also include the category page itself if it has content
            pages.append({"title": title, "ns": ns})
        else:
            pages.append({"title": title, "ns": ns})
    return pages


# ---------------------------------------------------------------------------
# Pull: wiki -> local
# ---------------------------------------------------------------------------

def pull(site, state: dict, verbose: bool = True) -> int:
    """Pull grammar pages from the wiki into local files.

    Returns number of files updated.
    """
    os.makedirs(GRAMMAR_DIR, exist_ok=True)
    pages = get_category_pages(site, CATEGORY)
    if not pages:
        print("No pages found in Category:Aelaki grammar.")
        return 0

    updated = 0
    titles_seen = set()

    for pinfo in pages:
        title = pinfo["title"]
        if title in titles_seen:
            continue
        titles_seen.add(title)

        page = site.pages[title]
        if not page.exists:
            continue

        text = page.text()
        if not text or not text.strip():
            continue

        revid = page.revision
        filename = title_to_filename(title)
        filepath = os.path.join(GRAMMAR_DIR, filename)

        # Check if content changed since last sync
        old_meta = state.get(title, {})
        if old_meta.get("revid") == revid and os.path.exists(filepath):
            if verbose:
                print(f"  unchanged: {title}")
            # Still record in state
            state[title] = {"file": filename, "revid": revid}
            continue

        # Write file
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
