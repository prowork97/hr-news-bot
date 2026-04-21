import os

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

DB_PATH = "storage.db"
MAX_POST_LENGTH = 4000
