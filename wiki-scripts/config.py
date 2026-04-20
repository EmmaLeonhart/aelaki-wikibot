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
#
# Numbers were raised from 1.0/2.0 to 2.0/5.0 after repeated long workflow
# runs: we would rather the pipeline take longer than put sustained load
# on shared Miraheze infrastructure. Creation is the expensive write
# (polynomial in link-table size), so it gets the larger gap.
THROTTLE = 2.0
CREATE_THROTTLE = 5.0

# MediaWiki maxlag parameter (seconds). When replication lag exceeds this,
# the API returns an error and we back off — this is the server's preferred
# way to cooperate with bots during peak load. See utils.connect().
MAX_LAG = 5

# Page creation is polynomial in the existing link-table size, so we cap the
# number of new pages the bot can create. Two caps apply:
#   - CREATIONS_PER_RUN: hard ceiling for a single pipeline run. Resets when
#     the "Prepare" step in word-pages.yml deletes create_run_budget.state
#     at startup. Default 100 (production); the workflow overrides via
#     WIKI_CREATIONS_PER_RUN to 20 for development (push-triggered) runs.
#   - CREATIONS_PER_DAY: single rolling cap per UTC day, shared across every
#     run (dev push + prod cron). Persisted in create_budget.state, committed
#     by the workflow so it survives between runs on the same day. Production
#     cron fires at the end of the UTC day and eats whatever budget is left.
# See utils._consume_creation_budget.
CREATIONS_PER_RUN = int(os.getenv("WIKI_CREATIONS_PER_RUN", "100"))
CREATIONS_PER_DAY = int(os.getenv("WIKI_CREATIONS_PER_DAY", "200"))

BOT_UA = "AelakiBot/1.0 (User:AelakiBot; aelaki.miraheze.org)"

# Namespace numbers (Aelaki wiki specific)
NS_MAIN = 0
NS_TALK = 1
NS_TEMPLATE = 10
NS_CATEGORY = 14
NS_LEXEME = 146
NS_ITEM = 860
NS_PROPERTY = 862
