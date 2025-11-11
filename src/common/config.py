import os


# API Key
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Paths
LOG_PATH = os.environ.get("TEST_LOG_PATH", "data/log.csv")
PLAN_PATH = os.environ.get("TEST_PLAN_PATH", "data/plan.json")

# Conversation states
BEDTIME, WAKEUP, ONSET, AWAKE, EARLIEST_WAKE, EARLIEST_BEDTIME = range(6)

# Sleep Plan
INIT_WINDOW = 7
UPDATE_WINDOW = 5
DELTA_UP = 15
DELTA_DOWN = 15
BUFFER = 30
MIN_TIB = 330  # 5.5h floor
MIN_TIB_CONSERVATIVE = 480  # 8h floor
