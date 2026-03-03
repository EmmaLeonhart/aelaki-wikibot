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
USERNAME = os.getenv("AELAKI_WIKI_USERNAME", "")
PASSWORD = os.getenv("AELAKI_WIKI_PASSWORD", "")

# Bot behaviour
THROTTLE = 1.5          # seconds between edits (standard for Miraheze)
BOT_UA = "AelakiBot/1.0 (User:AelakiBot; aelaki.miraheze.org)"

# Namespace numbers (Aelaki wiki specific)
NS_MAIN = 0
NS_TALK = 1
NS_TEMPLATE = 10
NS_CATEGORY = 14
NS_LEXEME = 146
NS_ITEM = 860
NS_PROPERTY = 862
