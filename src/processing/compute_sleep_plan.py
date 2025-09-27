import pandas as pd
from datetime import timedelta, datetime

from src.common.config import LOG_PATH, PLAN_PATH, INIT_WINDOW, WINDOW_LENGTH

from src.processing.storage_utils import read_log_csv, load_plan, save_plan


def initialize_sleep_plan(df, earliest_wake="07:00:00"):
    """
    After 1-2 weeks of baseline logs, create first sleep plan.
    earliest_wake: string HH:MM:SS (earliest typical wake time)
    """
    avg_tst = df["tst"].mean()
    tib = max(avg_tst + 30, 330)  # minutes, min 5.5h (330m)
    wake_time = pd.to_datetime(earliest_wake).time()
    wake_dt = datetime.combine(datetime.today(), wake_time)
    bed_dt = wake_dt - timedelta(minutes=tib)
    bedtime = bed_dt.time()
    return {
        "bedtime": bedtime.strftime("%H:%M:%S"),
        "wake_time": wake_time.strftime("%H:%M:%S"),
        "tib": int(tib),
    }


def adjust_sleep_plan(df, current_plan):
    """
    Adjust plan based on last week's average SE.
    """
    avg_se = df["se"].mean()
    new_plan = current_plan.copy()

    if avg_se > 90:
        new_plan["tib"] += 15
    elif 70 <= avg_se < 85:
        new_plan["tib"] -= 15
    elif avg_se < 70:
        avg_tst = df["tst"].mean()
        new_plan["tib"] = int(max(avg_tst + 30, 330))  # minutes, min 5.5h (330m))

    # recompute bedtime from wake time and TIB
    wake_dt = datetime.combine(datetime.today(), new_plan["wake_time"])
    bed_dt = wake_dt - timedelta(minutes=new_plan["tib"])
    new_plan["bedtime"] = bed_dt.time()

    return new_plan, avg_se


if __name__ == "__main__":
    df = read_log_csv(LOG_PATH)

    if len(df) == INIT_WINDOW:
        plan = initialize_sleep_plan(df.tail(WINDOW_LENGTH), earliest_wake="08:00:00")
        print("Initial Sleep Plan:", plan)
        save_plan(plan, PLAN_PATH)
        print(f"Plan saved to {PLAN_PATH}")
    elif len(df) > 5:
        # load existing plan
        plan = load_plan(PLAN_PATH)
        print("Current Plan:", plan)

        # adjust plan weekly
        new_plan, avg_se = adjust_sleep_plan(df.tail(WINDOW_LENGTH), plan)
        print("Adjusted Plan:", new_plan, "based on avg SE =", avg_se)

        # save adjusted plan
        save_plan(new_plan, PLAN_PATH)
        print(f"Plan saved to {PLAN_PATH}")
