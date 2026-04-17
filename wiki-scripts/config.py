"""
config.py
=========
Connection settings for aelaki.miraheze.org wikibot.

Credentials are read from environment variables. Set them before running:
    set AELAKI_WIKI_USERNAME=YourBot
    set AELAKI_WIKI_PASSWORD=your-bot-password

Or create a .env file (never commit this!) and load it manually.
"""
import os

# Wiki connection
WIKI_URL = "aelaki.miraheze.org"
WIKI_PATH = "/w/"

# Credentials from environment (set via Special:BotPasswords on the wiki)
# GitHub Actions uses WIKI_USERNAME / WIKI_PASSWORD; local uses AELAKI_WIKI_*
USERNAME = os.getenv("WIKI_USERNAME", "") or os.getenv("AELAKI_WIKI_USERNAME", "")
PASSWORD = os.getenv("WIKI_PASSWORD", "") or os.getenv("AELAKI_WIKI_PASSWORD", "")

# Bot behaviour — rate limits for write operations (reads are untouched).
# THROTTLE applies to edits, moves, and deletes. CREATE_THROTTLE applies to
# page creations, which are more expensive for the Miraheze wiki farm.
# See utils._wait_for_write_slot — throttle is enforced before the write,
# so bursts at script start or across helpers cannot bypass it.
THROTTLE = 1.0
CREATE_THROTTLE = 2.0
BOT_UA = "AelakiBot/1.0 (User:AelakiBot; aelaki.miraheze.org)"

# Namespace numbers (Aelaki wiki specific)
NS_MAIN = 0
NS_TALK = 1
NS_TEMPLATE = 10
NS_CATEGORY = 14
NS_LEXEME = 146
NS_ITEM = 860
NS_PROPERTY = 862
