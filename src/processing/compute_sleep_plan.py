import pandas as pd
import numpy as np

from src.common.config import PLAN_PATH, DELTA_UP, DELTA_DOWN, BUFFER, MIN_TIB
from src.common.models import SleepPlan
from src.common.exceptions import PlanUpdateError
from src.data_manager.plan_utils import save_plan


def initialize_sleep_plan(df: pd.DataFrame, default_plan: SleepPlan) -> SleepPlan:
    """Create the first sleep plan after baseline logs."""
    try:
        avg_tst = df["tst"].mean()
        tib = int(max(avg_tst + 30, 330))  # minutes, min 5.5h (330m)

        plan = SleepPlan(
            tib=tib,
            wake_time=default_plan.wake_time,
        )

        plan.update_bedtime

        save_plan(plan, PLAN_PATH)
        return plan
    except Exception as e:
        raise PlanUpdateError(f"Failed to initialize sleep plan: {e}")


def adjust_sleep_plan_se_only(
    df: pd.DataFrame, current_plan: SleepPlan
) -> tuple[SleepPlan, float]:
    """
    Adjust plan based on last 5 days' average SE.
    """
    try:
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
    except Exception as e:
        raise PlanUpdateError(f"Failed to update sleep plan: {e}")


def adjust_sleep_plan_se_tst_clipped(
    df: pd.DataFrame, current_plan: SleepPlan
) -> tuple[SleepPlan, float, float]:
    """
    Adjust plan based on last 5 days' average SE and clipped weighted TST.
    Clips TST values to a window relative to current TIB before averaging.
    """
    try:
        avg_se = df["se"].mean()

        tib = current_plan.tib
        lower_bound = 0.7 * tib
        upper_bound = 1.2 * tib

        # Clip TST values relative to TIB
        clipped_tst = df["tst"].clip(lower=lower_bound, upper=upper_bound)

        # Weighted average of clipped TST (recent nights weigh more)
        # weights = np.linspace(1, 2, len(clipped_tst))
        # weighted_tst = np.average(clipped_tst, weights=weights)
        # FIXME: Attempt simpler unweighted average for now
        avg_tst = np.average(clipped_tst)

        # Adjust TIB based on SE and weighted TST
        if avg_se > 90:
            # Very good efficiency → allow slight extension, but never below weighted TST
            tib = max(tib + DELTA_UP, avg_tst)
        elif 85 <= avg_se <= 90:
            # Good efficiency → maintain TIB, but bump up if consistently sleeping more
            tib = max(tib, avg_tst)
        elif 70 <= avg_se < 85:
            if avg_tst > tib:
                # Sleeping more than prescribed TIB but efficiency is low → trim
                tib -= DELTA_DOWN
            else:
                # Sleeping less than prescribed TIB but still inefficient → trim cautiously
                tib = min(tib - DELTA_DOWN, avg_tst + BUFFER)
        else:  # avg_se < 70
            # Poor efficiency → restrict TIB close to actual sleep, add buffer, enforce floor
            tib = max(avg_tst + BUFFER, MIN_TIB)

        tib = int(tib)

        # Create new plan
        new_plan = SleepPlan(
            tib=tib,
            wake_time=current_plan.wake_time,
        )
        new_plan.update_bedtime

        save_plan(new_plan, PLAN_PATH)
        return new_plan, avg_se, avg_tst
    except Exception as e:
        raise PlanUpdateError(f"Failed to update sleep plan: {e}")


# Compute new plan
# df = read_log_csv(LOG_PATH)
# curr_plan = load_plan(PLAN_PATH)

# curr_plan = initialize_sleep_plan(df, curr_plan)
# print(f"Initialized plan: {curr_plan.to_dict()}")

# new_plan, avg_se = adjust_sleep_plan(df, curr_plan)
# print(f"New plan: {new_plan.to_dict()}, avg SE: {avg_se:.1f}%")
