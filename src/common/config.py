import os


# API Key
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Paths
LOG_PATH = os.environ.get("TEST_LOG_PATH", "data/log.csv")
PLAN_PATH = os.environ.get("TEST_PLAN_PATH", "data/plan.json")

# Conversation states
BEDTIME, WAKEUP, ONSET, AWAKE, EARLIEST_WAKE = range(5)

# Sleep Plan
INIT_WINDOW = 3
WINDOW_LENGTH = 5
