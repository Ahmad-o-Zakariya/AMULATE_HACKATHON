from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .planner_types import TimeBlock, UnscheduledTask, PlanResult

class Task(BaseModel):
    id: str
    title: str
    priority: int = Field(ge=1, le=5)
    estimated_minutes: int
    status: str  # pending | scheduled | completed


class CalendarEvent(BaseModel):
    title: str
    start: datetime
    end: datetime
    task_id: Optional[str] = None


class UserPreferences(BaseModel):
    work_start_hour: int = 9
    work_end_hour: int = 18
    lunch_hour: int = 13
    focus_hours: List[int] = [9, 10, 11]


class AgentState(BaseModel):
    # Core memory
    tasks: List[Task] = []
    calendar_events: List[CalendarEvent] = []
    user_preferences: UserPreferences = UserPreferences()
    user_input: Optional[str] = None

    # Intent handling
    intent: Optional[str] = None
    intent_data: Optional[Dict] = None

    # Planning results
    planned_schedule: Optional[List[TimeBlock]] = None
    unscheduled_tasks: Optional[List[UnscheduledTask]] = None

    # User-facing output
    last_action_summary: str = ""