from datetime import datetime


class Stopwatch:
    time_start: datetime = None
    time_end: datetime = None
    delta: datetime = None

    def __int__(self):
        pass

    def start(self):
        self.time_start = datetime.now()
        return self

    def tick(self, pattern: str = "%H:%M:%S") -> str:
        if self.time_start is None:
            raise ValueError("")
        self.time_end = datetime.now()
        self.delta = datetime(year=1, month=1, day=1) + (self.time_end - self.time_start)
        return self.delta.strftime(pattern)

    def tick_seconds(self):
        return self.time_end - self.time_start
