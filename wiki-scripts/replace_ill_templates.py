#!/usr/bin/env python3
"""Replace {{ill|...}} interlanguage templates with plain [[wikilinks]].

The {{ill}} ("interlanguage link") template is used on Wikipedia and mirrors
imported from there to show a red local link plus a link to the same article
on a foreign-language Wikipedia. On aelaki.miraheze.org it is cruft from
scraped source material — we want plain [[Target]] or [[Target|Display]]
links instead.

Rules:
    {{ill|Target}}                           -> [[Target]]
    {{ill|Target|...|lt=Display|...}}        -> [[Target|Display]]
    {{ill|Target|...}}  (no lt=)             -> [[Target]]
    {{ill|...|1=Target|...}}                 -> Target overrides positional
    Named-only parameters (qq=, WD=, en=)    -> ignored

Run with --apply to write changes.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path


ILL_RE = re.compile(r"\{\{\s*ill\s*\|([^{}]*)\}\}", re.IGNORECASE)


def convert_one(match: re.Match) -> str:
    body = match.group(1)
    parts = [p.strip() for p in body.split("|")]
    positional: list[str] = []
    named: dict[str, str] = {}
    for p in parts:
        if "=" in p:
            k, _, v = p.partition("=")
            named[k.strip().lower()] = v.strip()
        else:
            positional.append(p)
    target = named.get("1") or (positional[0] if positional else "")
    display = named.get("lt")
    target = target.strip()
    if not target:
        return match.group(0)  # malformed; leave untouched
    if display and display.strip() and display.strip() != target:
        return f"[[{target}|{display.strip()}]]"
    return f"[[{target}]]"


def process_file(path: Path, apply: bool) -> int:
    text = path.read_text(encoding="utf-8")
    new_text, n = ILL_RE.subn(convert_one, text)
    if n == 0 or new_text == text:
        return 0
    if apply:
        path.write_text(new_text, encoding="utf-8")
    return n


def main() -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="Actually write changes (default: dry-run count).")
    parser.add_argument("path", nargs="?", default="grammar",
                        help="Directory to scan (default: grammar/).")
    args = parser.parse_args()

    root = Path(args.path)
    total_files = 0
    total_subs = 0
    for wiki in sorted(root.glob("*.wiki")):
        n = process_file(wiki, args.apply)
        if n:
            total_files += 1
            total_subs += n
            print(f"  {wiki.name}: {n}")

    verb = "replaced" if args.apply else "would replace"
    print(f"\n{verb} {total_subs} {{{{ill}}}} template(s) across {total_files} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
