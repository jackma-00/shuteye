import os
import pandas as pd

from src.common.config import LOG_PATH
from src.common.exceptions import EntrySaveError


def add_new_entry(date_str, t_bed, t_wake, onset, awake):
    try:
        # If wake is before bedtime, assume next day
        if t_wake <= t_bed:
            t_wake += pd.Timedelta(days=1)

        tib = int((t_wake - t_bed).total_seconds() // 60)  # time in bed (minutes)
        tst = tib - (onset + awake)  # total sleep time
        se = int((tst / tib) * 100) if tib > 0 else 0  # sleep efficiency %

        # Save bedtime/wakeup as HH:MM format in CSV
        bedtime_str = t_bed.strftime("%H:%M")
        wakeup_str = t_wake.strftime("%H:%M")

        new_row = [date_str, bedtime_str, wakeup_str, onset, awake, tib, tst, se]

        # Create file with header if not exists
        if not os.path.exists(LOG_PATH):
            with open(LOG_PATH, "w") as f:
                f.write(",".join(map(str, new_row)))
        else:
            with open(LOG_PATH, "a") as f:
                f.write("\n" + ",".join(map(str, new_row)))

        hours, minutes = divmod(tst, 60)
        return f"✅ New entry added — you slept for {hours}h {minutes}m with an efficiency of {se}%"

    except Exception as e:
        raise EntrySaveError(f"❌ Failed to save entry: {e}")
