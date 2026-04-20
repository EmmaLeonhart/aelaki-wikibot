#!/usr/bin/env python3
"""
sync_image_pages.py
===================
One-way pull: walk [[Category:Images]] on aelaki.miraheze.org and save
every File: description page to ``images/imagewikitext/<filename>.wiki``
in this repo.

File:Example.png  →  images/imagewikitext/Example.png.wiki

Local files whose titles have left the category are removed so the
directory mirrors the live category. This is intentionally pull-only:
File: descriptions are generally wiki-authored, and pushing local edits
back would require conflict detection we don't need for a bulk import.

Usage:
    python sync_image_pages.py              # dry-run
    python sync_image_pages.py --apply      # write / delete local files
"""
from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import connect

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "images", "imagewikitext")
CATEGORY = "Images"


def title_to_filename(title: str) -> str:
    """File:Foo bar.png → Foo_bar.png.wiki."""
    name = title.split(":", 1)[1] if ":" in title else title
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.replace(" ", "_")
    name = re.sub(r"_+", "_", name).strip("_")
    return name + ".wiki"


def iter_image_pages(site):
    """Yield (title, text) for every page in Category:Images (File: ns only)."""
    params = {
        "generator": "categorymembers",
        "gcmtitle": f"Category:{CATEGORY}",
        "gcmnamespace": "6",  # File:
        "gcmlimit": "max",
        "prop": "revisions",
        "rvprop": "ids|content",
        "rvslots": "main",
        "formatversion": "2",
    }
    while True:
        result = site.api("query", **params)
        pages = result.get("query", {}).get("pages", [])
        for p in pages:
            if p.get("missing"):
                continue
            revs = p.get("revisions") or []
            if not revs:
                continue
            text = revs[0].get("slots", {}).get("main", {}).get("content", "")
            yield p["title"], text or ""
        if "continue" in result:
            params.update(result["continue"])
        else:
            break


def main():
    parser = argparse.ArgumentParser(description="Sync [[Category:Images]] pages to images/imagewikitext/")
    parser.add_argument("--apply", action="store_true",
                        help="Actually write / delete local files (default is dry-run)")
    args = parser.parse_args()

    if args.apply:
        os.makedirs(IMAGE_DIR, exist_ok=True)

    site = connect()

    pulled = 0
    unchanged = 0
    seen_files: set[str] = set()

    for title, text in iter_image_pages(site):
        filename = title_to_filename(title)
        filepath = os.path.join(IMAGE_DIR, filename)
        seen_files.add(filename)

        existing_text: str | None = None
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                existing_text = f.read()

        if existing_text == text:
            unchanged += 1
            continue

        if args.apply:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"  pulled: {title} -> {filename}", flush=True)
        else:
            print(f"  would pull: {title} -> {filename}", flush=True)
        pulled += 1

    # Cull local files whose titles have left Category:Images. Without this,
    # pages removed from the category would linger locally forever.
    removed = 0
    if os.path.isdir(IMAGE_DIR):
        for f in os.listdir(IMAGE_DIR):
            if not f.endswith(".wiki"):
                continue
            if f in seen_files:
                continue
            path = os.path.join(IMAGE_DIR, f)
            if args.apply:
                os.remove(path)
                print(f"  removed: {f} (no longer in Category:Images)", flush=True)
            else:
                print(f"  would remove: {f} (no longer in Category:Images)", flush=True)
            removed += 1

    verb = "Pulled" if args.apply else "Would pull"
    print(f"\n{verb}: {pulled} | unchanged: {unchanged} | removed: {removed} | total in category: {len(seen_files)}")


if __name__ == "__main__":
    main()
