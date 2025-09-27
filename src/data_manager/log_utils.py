import os
import pandas as pd
from datetime import datetime, time

from src.common.config import LOG_PATH, INIT_WINDOW, WINDOW_LENGTH
from src.common.exceptions import EntrySaveError
from src.common.models import LogEntry


cols = ["date", "bedtime", "wakeup", "onset", "awake", "tib", "tst", "se"]


def read_log_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, header=None, names=cols)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["bedtime"] = pd.to_datetime(
        df["bedtime"], format="%H:%M", errors="coerce"
    ).dt.time
    df["wakeup"] = pd.to_datetime(df["wakeup"], format="%H:%M", errors="coerce").dt.time
    for c in ["onset", "awake", "tib", "tst", "se"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    return df


def enough_data_for_first_plan() -> bool:
    if not os.path.exists(LOG_PATH):
        return False
    df = read_log_csv(LOG_PATH)
    return len(df) == INIT_WINDOW


def ready_for_new_plan() -> bool:
    if not os.path.exists(LOG_PATH):
        return False
    df = read_log_csv(LOG_PATH)
    return len(df) > INIT_WINDOW and (len(df) - INIT_WINDOW) % WINDOW_LENGTH == 0


# def add_new_entry(
#     date_str: str, t_bed: pd.Timestamp, t_wake: pd.Timestamp, onset: int, awake: int
# ) -> str:
#     try:
#         # If wake is before bedtime, assume next day
#         if t_wake <= t_bed:
#             t_wake += pd.Timedelta(days=1)

#         tib = int((t_wake - t_bed).total_seconds() // 60)  # time in bed (minutes)
#         tst = tib - (onset + awake)  # total sleep time
#         se = int((tst / tib) * 100) if tib > 0 else 0  # sleep efficiency %

#         # Save bedtime/wakeup as HH:MM format in CSV
#         bedtime_str = t_bed.strftime("%H:%M")
#         wakeup_str = t_wake.strftime("%H:%M")

#         new_row = [date_str, bedtime_str, wakeup_str, onset, awake, tib, tst, se]

#         # Create file with header if not exists
#         if not os.path.exists(LOG_PATH):
#             with open(LOG_PATH, "w") as f:
#                 f.write(",".join(map(str, new_row)))
#         else:
#             with open(LOG_PATH, "a") as f:
#                 f.write("\n" + ",".join(map(str, new_row)))

#         hours, minutes = divmod(tst, 60)
#         return f"✅ New entry added — you slept for {hours}h {minutes}m with an efficiency of {se}%"

#     except Exception as e:
#         raise EntrySaveError(f"❌ Failed to save entry: {e}")


def add_new_entry(t_bed: time, t_wake: time, onset: int, awake: int) -> str:
    try:
        log_entry = LogEntry(
            date=datetime.now().date(),
            bedtime=t_bed,
            wakeup=t_wake,
            onset=onset,
            awake=awake,
        )

        log_entry.compute_metrics
        new_row = log_entry.to_csv_row()

        # Create file with header if not exists
        if not os.path.exists(LOG_PATH):
            with open(LOG_PATH, "w") as f:
                f.write(new_row)
        else:
            with open(LOG_PATH, "a") as f:
                f.write("\n" + new_row)

        hours, minutes = divmod(log_entry.tst, 60)
        return f"✅ New entry added — you slept for {hours}h {minutes}m with an efficiency of {log_entry.se}%"

    except Exception as e:
        raise EntrySaveError(f"❌ Failed to save entry: {e}")
