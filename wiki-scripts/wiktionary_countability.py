"""Check noun countability via Wiktionary API.

Uses the Category:English_uncountable_nouns category to determine
whether an English noun is uncountable (mass noun).
"""

import json
import time
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

WIKTIONARY_API = "https://en.wiktionary.org/w/api.php"
UNCOUNTABLE_CATEGORY = "Category:English uncountable nouns"


def check_uncountable(words: list[str]) -> set[str]:
    """Check which words are in Category:English_uncountable_nouns.

    Returns a set of lowercase words that are uncountable.
    Batches requests (50 titles per API call).
    """
    uncountable = set()
    batch_size = 50

    for i in range(0, len(words), batch_size):
        batch = words[i:i + batch_size]
        params = {
            "action": "query",
            "titles": "|".join(batch),
            "prop": "categories",
            "clcategories": UNCOUNTABLE_CATEGORY,
            "format": "json",
        }
        url = f"{WIKTIONARY_API}?{urlencode(params)}"
        req = Request(url, headers={"User-Agent": "AelakiWordBot/1.0"})

        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (URLError, OSError):
            # If API is unavailable, skip this batch
            continue

        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "categories" in page:
                uncountable.add(page["title"].lower())

        # Respect rate limits between batches
        if i + batch_size < len(words):
            time.sleep(0.5)

    return uncountable
