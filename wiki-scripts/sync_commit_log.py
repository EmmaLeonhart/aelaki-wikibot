#!/usr/bin/env python3
"""
sync_commit_log.py
==================
Generates and pushes [[Git commit log]] — a wiki page listing all git
commits with links to GitHub, so version categories are navigable.

Usage:
    python wiki-scripts/sync_commit_log.py              # dry-run
    python wiki-scripts/sync_commit_log.py --apply      # push to wiki
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import connect, safe_save

PAGE_TITLE = "Git commit log"
REPO_URL = "https://github.com/EmmaLeonhart/aelaki-wikibot"


def get_commits() -> list[dict]:
    """Get all git commits oldest-first as list of dicts."""
    fmt = "%H%n%h%n%ai%n%s"  # full hash, short hash, date, subject
    out = subprocess.check_output(
        ["git", "log", "--reverse", f"--format={fmt}"],
        cwd=os.path.join(os.path.dirname(__file__), ".."),
        text=True,
    )
    lines = out.strip().split("\n")
    commits = []
    for i in range(0, len(lines), 4):
        if i + 3 >= len(lines):
            break
        commits.append({
            "hash": lines[i],
            "short": lines[i + 1],
            "date": lines[i + 2],
            "subject": lines[i + 3],
        })
    return commits


def generate_page(commits: list[dict]) -> str:
    """Generate wikitext for the commit log page."""
    lines = [
        "This page lists git commits from the "
        f"[{REPO_URL} aelaki-wikibot] repository.",
        "",
        "Short hashes are used in [[Category:Word pages|word page]] version "
        "categories (e.g. <nowiki>[[Category:Words abc1234]]</nowiki>).",
        "",
        '{| class="wikitable"',
        "! Date !! Hash !! Lemma category !! Non-lemma category !! Message",
    ]

    for c in commits:
        url = f"{REPO_URL}/commit/{c['hash']}"
        date = c["date"].split(" ")[0]  # just YYYY-MM-DD
        short = c["short"]
        lemma_cat = f"[[:Category:Words {short}|Words {short}]]"
        nonlemma_cat = f"[[:Category:Non-lemma forms {short}|Non-lemma {short}]]"
        # Escape wiki markup in subject
        subj = c["subject"].replace("|", "{{!}}").replace("[[", "<nowiki>[[</nowiki>")
        lines.append(f"|-\n| {date} || [{url} {short}] || {lemma_cat} || {nonlemma_cat} || {subj}")

    lines.append("|}")
    lines.append("")
    lines.append("[[Category:git synced pages]]")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate git commit log wiki page")
    parser.add_argument("--apply", action="store_true", help="Push to wiki")
    parser.add_argument("--run-tag", default="", help="Run tag for edit summary")
    args = parser.parse_args()

    commits = get_commits()
    text = generate_page(commits)

    if not args.apply:
        print(text[:2000])
        print(f"\n... ({len(text)} chars, {len(commits)} commits)")
        return

    run_tag_suffix = f" {args.run_tag}" if args.run_tag else ""
    site = connect()
    page = site.pages[PAGE_TITLE]
    saved = safe_save(page, text,
                      f"Bot: update git commit log{run_tag_suffix}")
    if saved:
        print(f"Updated [[{PAGE_TITLE}]] ({len(commits)} commits)")
    else:
        print(f"No changes to [[{PAGE_TITLE}]]")


if __name__ == "__main__":
    main()
