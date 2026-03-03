# API access patterns — Aelaki Wiki

This document records exactly how aelaki.miraheze.org is accessed by bot scripts.
Adapted from the [shintowiki-scripts](https://github.com/) API patterns.

---

## Table of contents

1. [aelaki.miraheze.org (mwclient)](#1-aelakimirahezeorg--mwclient)
2. [Wikibase Lexeme API](#2-wikibase-lexeme-api)
3. [Authentication summary](#3-authentication-summary)
4. [Rate limiting reference](#4-rate-limiting-reference)

---

## 1. aelaki.miraheze.org — mwclient

### Connection + login

```python
import mwclient

WIKI_URL  = "aelaki.miraheze.org"
WIKI_PATH = "/w/"
USERNAME  = os.getenv("AELAKI_WIKI_USERNAME")
PASSWORD  = os.getenv("AELAKI_WIKI_PASSWORD")

site = mwclient.Site(
    WIKI_URL,
    path=WIKI_PATH,
    clients_useragent="AelakiBot/1.0 (User:AelakiBot; aelaki.miraheze.org)"
)
site.login(USERNAME, PASSWORD)
```

### Verify login

```python
try:
    ui = site.api('query', meta='userinfo')
    logged_user = ui['query']['userinfo'].get('name', USERNAME)
    print(f"Logged in as {logged_user}")
except Exception:
    print("Logged in (could not fetch username via API, but login succeeded).")
```

### Core operations

```python
# Read a page
page = site.pages["Page title"]
text = page.text()
exists = page.exists

# Save / edit a page
page.save(new_text, summary="Bot: edit summary here")

# Iterate all pages in a namespace
for page in site.allpages(namespace=0):  # 0 = Main
    ...

# Iterate members of a category
cat = site.categories["Aelaki vocabulary"]
for page in cat:
    print(page.name, page.namespace)

# Direct API call
result = site.api('query', meta='userinfo')
```

### Namespace numbers (Aelaki wiki)

| Namespace | Number |
|-----------|--------|
| Main (articles) | 0 |
| Talk | 1 |
| Template | 10 |
| Category | 14 |
| Lexeme | 146 |
| Lexeme talk | 147 |
| Module | 828 |
| Item | 860 |
| Property | 862 |

### Throttling

```python
import time
THROTTLE = 1.5   # seconds between edits — standard for Miraheze
time.sleep(THROTTLE)
```

### Windows Unicode fix (always include on Windows)

```python
import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## 2. Wikibase Lexeme API

The Aelaki wiki has Wikibase with Lexeme support (namespace 146-147).
Lexemes L1-L75 already exist.

### Read a lexeme

```python
import requests, json

API = "https://aelaki.miraheze.org/w/api.php"

r = session.get(API, params={
    'action': 'wbgetentities',
    'ids': 'L1',
    'format': 'json'
})
entity = r.json()['entities']['L1']
```

### Add senses (auto-generate IDs)

```python
edit_data = {
    'senses': [{
        'add': '',  # Empty string = auto-generate ID
        'glosses': {
            'en': {'language': 'en', 'value': 'New sense gloss'}
        }
    }]
}

r = session.post(API, data={
    'action': 'wbeditentity',
    'id': 'L1',
    'data': json.dumps(edit_data),
    'token': csrf_token,
    'format': 'json'
})
```

### Add forms (auto-generate IDs)

```python
edit_data = {
    'forms': [{
        'add': '',
        'representations': {
            'mis': {'language': 'mis', 'value': 'new-form'}
        },
        'grammaticalFeatures': []
    }]
}
```

### Key discoveries

- **`"add": ""` syntax** is required for creating new senses/forms (auto-generates IDs)
- **Fixed ID syntax** `{'id': 'L1-S2'}` only works for modifying existing senses
- `wbladsense` and `wbladdform` endpoints do NOT exist on this wiki
- Works for L1-L69; L70-L75 may have special restrictions

---

## 3. Authentication summary

| Service | Library | Auth type |
|---------|---------|-----------|
| aelaki.miraheze.org | mwclient | Bot password (env vars) |
| Wikibase API | requests | Session with CSRF token |

**Bot passwords** are created at `Special:BotPasswords` on the wiki.
Format: `Username@BotName` with the generated password.

**Environment variables:**
- `AELAKI_WIKI_USERNAME` — Bot account name (e.g., `YourUser@AelakiBot`)
- `AELAKI_WIKI_PASSWORD` — Bot password from Special:BotPasswords

---

## 4. Rate limiting reference

| Target | Throttle | Notes |
|--------|----------|-------|
| aelaki.miraheze.org edits | 1.5 s | Standard for all scripts |
| aelaki.miraheze.org reads | none | Reading doesn't count |
| Wikibase API writes | 1.5 s | Same as regular edits |

General rule for Miraheze: stay under ~40 edits/minute.

---

## Minimal working template

```python
"""
script_name.py
==============
One-line description.
"""
import os, sys, time, io
import mwclient

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKI_URL  = "aelaki.miraheze.org"
WIKI_PATH = "/w/"
USERNAME  = os.getenv("AELAKI_WIKI_USERNAME", "")
PASSWORD  = os.getenv("AELAKI_WIKI_PASSWORD", "")
THROTTLE  = 1.5
BOT_UA    = "AelakiBot/1.0 (User:AelakiBot; aelaki.miraheze.org)"

site = mwclient.Site(WIKI_URL, path=WIKI_PATH, clients_useragent=BOT_UA)
site.login(USERNAME, PASSWORD)
print("Logged in.", flush=True)

def main():
    for page in site.allpages(namespace=0):
        text = page.text()
        new_text = text  # modify as needed
        if new_text != text:
            page.save(new_text, summary="Bot: description")
            time.sleep(THROTTLE)

if __name__ == "__main__":
    main()
```

---

## Not used

- **pywikibot** — all access is via mwclient or raw requests
- **OAuth** — not used; mwclient handles session cookies
