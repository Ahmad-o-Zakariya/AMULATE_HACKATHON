from dataclasses import dataclass
from datetime import datetime
from typing import List

# Data structures



@dataclass
class TimeBlock:
    start: datetime
    end: datetime
    task_id: str
    title: str


@dataclass
class UnscheduledTask:
    task_id: str
    title: str
    reason: str

@dataclass
class PlanResult:
    schedule: List[TimeBlock]
    unscheduled: List[UnscheduledTask]
    summary: str
    