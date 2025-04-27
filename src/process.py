from datetime import datetime
import json

from .event import Event


class Process(Event):
    def __init__(self, name: str, stages: list[str]):
        super().__init__(name=name)
        self._stage_ordered: list = stages
        self._stages: dict[str, Event | None] = {stage: None for stage in stages}
        self._current_stage_idx = -1
        self._current_stage: str = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "ts_start": self.ts_start,
            "ts_end": self.ts_end,
            "duration": self.ts_end - self.ts_start if self.is_stopped() else None,
            "stages": {k: v.to_dict() if v is not None else None 
                    for k, v in self._stages.items()},
        }
    
    def __repr__(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> 'Process':
        stages = data["stages"]  # type: dict[str, Event]
        process = cls(name=data["name"], stages=list(stages.keys()))
        process.ts_start = data["ts_start"]
        process.ts_end = data.get("ts_end")

        for stage_name, stage_data in stages.items():
            if stage_data is None:
                process._stages[stage_name] = None
            else:
                process._stages[stage_name] = Event.from_dict(stage_data)

        return process

    @classmethod
    def from_json(cls, json_str: str) -> 'Process':
        data = json.loads(json_str)
        return cls.from_dict(data)

    def stage(self, stage_name: str) -> Event:
        if stage_name not in self._stages:
            raise ValueError(f'Invalid stage name: {stage_name}')

        return self._stages[stage_name]

    def stop(self):
        self.ts_end = datetime.now().timestamp()
        if self._current_stage:
            current_event = self._stages[self._current_stage]
            if current_event and current_event.ts_end is None:
                current_event.ts_end = datetime.now().timestamp()
            self._current_stage = None

    def start_stage(self, stage_name: str) -> Event:
        self.stage(stage_name)

        if self._current_stage_idx >= len(self._stage_ordered) - 1:
            raise ValueError(f'All stages are stopped')

        if self._current_stage_idx == self._stage_ordered.index(stage_name):
            raise ValueError(f'Current stage can not be restarted')

        if self._current_stage_idx + 1 != self._stage_ordered.index(stage_name):
            raise ValueError(f'Previous stage is not stopped')

        if self._current_stage_idx > -1:
            self._stages[self._stage_ordered[self._current_stage_idx]].ts_end = datetime.now().timestamp()

        self._stages[stage_name] = Event(name=stage_name)
        self._current_stage_idx += 1

        return self._stages[stage_name]

    def stop_stage(self, stage_name: str) -> Event:
        stage = self.stage(stage_name)
        if stage and stage.ts_end is None:
            stage.ts_end = datetime.now().timestamp()
            if self._current_stage == stage:
                self._current_stage = None
                self._current_stage_idx = self._stage_ordered.index(stage_name)

        return stage
