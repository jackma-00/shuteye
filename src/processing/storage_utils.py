import os
import json
import pandas as pd
from datetime import datetime

from src.common.config import PLAN_PATH

cols = ["date", "bedtime", "wakeup", "onset", "awake", "tib", "tst", "se"]


def read_log_csv(path):
    df = pd.read_csv(path, header=None, names=cols)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["bedtime"] = pd.to_datetime(df["bedtime"], errors="coerce").dt.time
    df["wakeup"] = pd.to_datetime(df["wakeup"], errors="coerce").dt.time
    for c in ["onset", "awake", "tib", "tst", "se"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    return df


def load_plan(path=PLAN_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No plan found at {path}")

    with open(path, "r") as f:
        data = json.load(f)

    # Convert fields back to proper types
    plan = {
        "tib": int(data["tib"]),
        "bedtime": datetime.strptime(data["bedtime"], "%H:%M:%S").time(),
        "wake_time": datetime.strptime(data["wake_time"], "%H:%M:%S").time(),
    }
    return plan


def save_plan(plan, path=PLAN_PATH):
    # Convert time objects to string before saving
    serializable_plan = {
        "tib": plan["tib"],
        "bedtime": plan["bedtime"].strftime("%H:%M:%S"),
        "wake_time": plan["wake_time"].strftime("%H:%M:%S"),
    }

    with open(path, "w") as f:
        json.dump(serializable_plan, f, indent=4)
