import os


# API Key
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Paths
LOG_PATH = "data/log.csv"
PLAN_PATH = "data/plan.json"

# Conversation states
BEDTIME, WAKEUP, ONSET, AWAKE = range(4)

# Sleep Plan
INIT_WINDOW = 3
WINDOW_LENGTH = 5
