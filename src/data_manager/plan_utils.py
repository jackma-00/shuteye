import os
import json
from datetime import time

from src.common.config import PLAN_PATH
from src.common.models import SleepPlan


default_plan = SleepPlan(
    tib=0,
    bedtime=time(0, 0),
    wake_time=time(0, 0),
)


def load_plan(path: str = PLAN_PATH) -> SleepPlan:
    if not os.path.exists(path):
        save_plan(default_plan, path)
        return default_plan

    with open(path, "r") as f:
        data = json.load(f)

    return SleepPlan.from_dict(data)


def save_plan(plan: SleepPlan, path: str = PLAN_PATH):
    with open(path, "w") as f:
        json.dump(plan.to_dict(), f, indent=4)


def update_wake_time(new_wake_time: time, path: str = PLAN_PATH):
    plan = load_plan(path)
    plan.wake_time = new_wake_time
    save_plan(plan, path)
