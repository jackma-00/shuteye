import pandas as pd
from datetime import timedelta, datetime

from src.common.config import LOG_PATH, PLAN_PATH
from src.common.models import SleepPlan
from src.data_manager.plan_utils import load_plan, save_plan
from src.data_manager.log_utils import read_log_csv


def initialize_sleep_plan(df: pd.DataFrame, default_plan: SleepPlan) -> SleepPlan:
    """Create the first sleep plan after baseline logs."""
    avg_tst = df["tst"].mean()
    tib = int(max(avg_tst + 30, 330))  # minutes, min 5.5h (330m)

    plan = SleepPlan(
        tib=tib,
        wake_time=default_plan.wake_time,
    )

    plan.update_bedtime

    save_plan(plan, PLAN_PATH)
    return plan


def adjust_sleep_plan(
    df: pd.DataFrame, current_plan: SleepPlan
) -> tuple[SleepPlan, float]:
    """
    Adjust plan based on last 5 days' average SE.
    """
    avg_se = df["se"].mean()
    tib = current_plan.tib

    if avg_se > 90:
        tib += 15
    elif 70 <= avg_se < 85:
        tib -= 15
    elif avg_se < 70:
        avg_tst = df["tst"].mean()
        tib = int(max(avg_tst + 30, 330))  # minutes, min 5.5h (330m)

    new_plan = SleepPlan(
        tib=tib,
        wake_time=current_plan.wake_time,
    )
    
    # recompute bedtime from wake time and updated TIB
    new_plan.update_bedtime
   
    save_plan(new_plan, PLAN_PATH)
    return new_plan, avg_se


# Compute new plan
# df = read_log_csv(LOG_PATH)
# curr_plan = load_plan(PLAN_PATH)

# curr_plan = initialize_sleep_plan(df, curr_plan)
# print(f"Initialized plan: {curr_plan.to_dict()}")

# new_plan, avg_se = adjust_sleep_plan(df, curr_plan)
# print(f"New plan: {new_plan.to_dict()}, avg SE: {avg_se:.1f}%")
