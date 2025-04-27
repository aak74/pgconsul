from datetime import datetime


class Event:
    name: str
    ts_start: float
    ts_end: float | None = None

    def __init__(self, name: str):
        self.name = name
        self.ts_start = datetime.now().timestamp()

    def to_dict(self):
        return {
            "name": self.name,
            "ts_start": self.ts_start,
            "ts_end": self.ts_end,
            "duration": self.ts_end - self.ts_start if self.is_stopped() else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """Create Event from dictionary representation"""
        event = cls(name=data["name"])
        event.ts_start = data["ts_start"]
        if "ts_end" in data:
            event.ts_end = data["ts_end"]
        return event

    def start(self):
        self.ts_start = datetime.now().timestamp()

    def stop(self):
        self.ts_end = datetime.now().timestamp()

    def is_started(self) -> bool:
        return self.ts_start != None

    def is_stopped(self) -> bool:
        return self.ts_end != None
