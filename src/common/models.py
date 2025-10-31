from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from typing import Optional


@dataclass
class SleepPlan:
    tib: Optional[int] = None  # target Time in bed in minutes
    bedtime: Optional[time] = None
    wake_time: Optional[time] = None

    def to_dict(self) -> dict:
        return {
            "tib": self.tib,
            "bedtime": self.bedtime.strftime("%H:%M"),
            "wake_time": self.wake_time.strftime("%H:%M"),
        }

    @staticmethod
    def from_dict(data: dict) -> "SleepPlan":
        return SleepPlan(
            tib=int(data["tib"]),
            bedtime=datetime.strptime(data["bedtime"], "%H:%M").time(),
            wake_time=datetime.strptime(data["wake_time"], "%H:%M").time(),
        )

    @property
    def time_in_bed(self) -> None:
        if self.bedtime is None or self.wake_time is None:
            raise ValueError("bedtime and wake_time must be set to compute tib")
        bt = datetime.combine(datetime.today(), self.bedtime)
        wt = datetime.combine(datetime.today(), self.wake_time)
        if wt <= bt:  # handle crossing midnight
            bt -= timedelta(days=1)
        self.tib = int((wt - bt).total_seconds() // 60)

    @property
    def update_bedtime(self) -> None:
        if self.tib is None or self.wake_time is None:
            raise ValueError("tib and wake_time must be set to update bedtime")
        wt = datetime.combine(datetime.today(), self.wake_time)
        bt = wt - timedelta(minutes=self.tib)
        self.bedtime = bt.time()

    @property
    def update_wake_time(self) -> None:
        if self.tib is None or self.bedtime is None:
            raise ValueError("tib and bedtime must be set to update wake_time")
        bt = datetime.combine(datetime.today(), self.bedtime)
        wt = bt + timedelta(minutes=self.tib)
        self.wake_time = wt.time()


@dataclass
class LogEntry:
    date: date  # calendar date of entry
    bedtime: time  # time went to bed
    wakeup: time  # time woke up
    onset: int  # sleep onset latency (minutes)
    awake: int  # minutes awake after sleep onset
    tib: Optional[int] = None  # time in bed (minutes)
    tst: Optional[int] = None  # total sleep time (minutes)
    se: Optional[int] = None  # sleep efficiency (%)

    def to_csv_row(self) -> str:
        """Serialize to a single CSV row (no header)."""
        return ",".join(
            map(
                str,
                [
                    self.date.isoformat(),
                    self.bedtime.strftime("%H:%M"),
                    self.wakeup.strftime("%H:%M"),
                    self.onset,
                    self.awake,
                    self.tib,
                    self.tst,
                    self.se,
                ],
            )
        )

    @property
    def compute_metrics(self) -> None:
        """Compute tib, tst, se based on bedtime, wakeup, onset, awake."""
        bt = datetime.combine(self.date, self.bedtime)
        wt = datetime.combine(self.date, self.wakeup)
        if wt <= bt:  # handle crossing midnight
            bt -= timedelta(days=1)
        self.tib = int((wt - bt).total_seconds() // 60)  # time in bed (minutes)
        self.tst = self.tib - (self.onset + self.awake)  # total sleep time
        self.se = (
            int((self.tst / self.tib) * 100) if self.tib > 0 else 0
        )  # sleep efficiency %


plan = SleepPlan(tib=402, wake_time=datetime.strptime("06:45", "%H:%M").time())
plan.update_bedtime
print(plan.bedtime)
