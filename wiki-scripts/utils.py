"""
utils.py
========
Shared utilities for Aelaki wikibot scripts.
Adapted from shintowiki-scripts patterns.
"""
import io
import json
import os
import sys
import time
import datetime as dt

import mwclient

from config import (
    WIKI_URL, WIKI_PATH, USERNAME, PASSWORD, BOT_UA,
    THROTTLE, CREATE_THROTTLE,
)

# ---------------------------------------------------------------------------
# Windows Unicode fix (always include)
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def connect() -> mwclient.Site:
    """Connect and log in to aelaki.miraheze.org. Returns the Site object."""
    if not USERNAME or not PASSWORD:
        raise RuntimeError(
            "Set AELAKI_WIKI_USERNAME and AELAKI_WIKI_PASSWORD environment variables.\n"
            "Create a bot password at https://aelaki.miraheze.org/wiki/Special:BotPasswords"
        )
    site = mwclient.Site(WIKI_URL, path=WIKI_PATH, clients_useragent=BOT_UA)
    site.login(USERNAME, PASSWORD)
    # Verify login
    try:
        ui = site.api("query", meta="userinfo")
        logged_user = ui["query"]["userinfo"].get("name", USERNAME)
        print(f"Logged in as {logged_user}", flush=True)
    except Exception:
        print("Logged in (could not fetch username via API, but login succeeded).", flush=True)
    return site


# ---------------------------------------------------------------------------
# Write throttling
# ---------------------------------------------------------------------------
# All write operations (edit, create, move, delete) must go through
# _wait_for_write_slot before calling the mwclient write method. The gate is
# pre-operation so a burst cannot sneak past it at script start, and the
# timestamp is process-global so mixing helpers (e.g. safe_save then
# delete_page) still respects the gap.

_last_write_ts: float = 0.0


def _wait_for_write_slot(heavy: bool = False) -> None:
    """Block until the configured gap has elapsed since the last write.

    heavy=True uses CREATE_THROTTLE (for page creation, which is more
    expensive for the wiki farm than editing an existing page).
    """
    global _last_write_ts
    min_gap = CREATE_THROTTLE if heavy else THROTTLE
    elapsed = time.monotonic() - _last_write_ts
    if elapsed < min_gap:
        time.sleep(min_gap - elapsed)
    _last_write_ts = time.monotonic()


# ---------------------------------------------------------------------------
# Safe save with edit-conflict handling
# ---------------------------------------------------------------------------

def safe_save(page, text: str, summary: str) -> bool:
    """Save a page, handling edit conflicts and no-change cases.

    Returns True if the page was actually edited.
    """
    try:
        current = page.text()
    except Exception:
        current = None

    if current is not None and current.rstrip() == text.rstrip():
        return False  # nothing changed

    # A None current means we couldn't read the page — treat as a create
    # (the heavier throttle is the safer default when in doubt).
    is_create = current is None or not page.exists

    for attempt in range(3):
        _wait_for_write_slot(heavy=is_create)
        try:
            page.save(text, summary=summary)
            return True
        except mwclient.errors.APIError as e:
            if e.code == "editconflict" and attempt < 2:
                print(f"  Edit conflict (retry {attempt + 1}/3): {page.name}")
                time.sleep(3)
                # Re-fetch is caller's responsibility for content changes;
                # for create-only pages this retry is usually enough.
            else:
                raise
    return False


def save_page(page, text: str, summary: str) -> None:
    """Rate-limited raw save. Use when the caller has already decided the
    page needs updating (e.g. stage-line updates on User:EmmaBot). Prefer
    safe_save for idempotent writes that should skip unchanged pages."""
    _wait_for_write_slot(heavy=not page.exists)
    page.save(text, summary=summary)


def delete_page(page, reason: str) -> None:
    """Rate-limited page deletion."""
    _wait_for_write_slot()
    page.delete(reason=reason)


def move_page(site, old_title: str, new_title: str, reason: str, *, leave_redirect: bool = True) -> bool:
    """Move (rename) a wiki page from old_title to new_title.

    Returns True if the move succeeded.
    """
    old_page = site.pages[old_title]
    if not old_page.exists:
        return False
    new_page = site.pages[new_title]
    if new_page.exists:
        return False  # target already exists
    # A move creates a page at the new title, so use the create throttle.
    _wait_for_write_slot(heavy=True)
    old_page.move(new_title, reason=reason, no_redirect=not leave_redirect)
    return True


def create_page(site, title: str, text: str, summary: str, overwrite: bool = False) -> bool:
    """Create a page if it doesn't already exist.

    If overwrite=True, replaces existing content.
    Returns True if the page was created/updated.
    """
    page = site.pages[title]
    if page.exists and not overwrite:
        return False
    return safe_save(page, text, summary)


# ---------------------------------------------------------------------------
# State management (for resumable jobs)
# ---------------------------------------------------------------------------

def load_state(path: str) -> set[str]:
    """Load set of completed titles from a state file."""
    completed = set()
    if not os.path.exists(path):
        return completed
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                completed.add(s)
    return completed


def append_state(path: str, title: str) -> None:
    """Append a completed title to the state file."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(title + "\n")


# ---------------------------------------------------------------------------
# JSONL logging
# ---------------------------------------------------------------------------

def append_log(path: str, data: dict) -> None:
    """Append a JSON log entry with UTC timestamp."""
    payload = dict(data)
    payload["ts_utc"] = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Progress counter
# ---------------------------------------------------------------------------

class Progress:
    """Simple counter for tracking bot run statistics."""

    def __init__(self):
        self.processed = 0
        self.created = 0
        self.skipped = 0
        self.errors = 0

    def summary(self) -> str:
        return (
            f"Processed: {self.processed} | Created: {self.created} | "
            f"Skipped: {self.skipped} | Errors: {self.errors}"
        )
