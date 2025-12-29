from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


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
    focus_hours: List[int] = [9, 10, 11, 14, 15, 16]
    lunch_hour: int = 13


class AgentState(BaseModel):
    tasks: List[Task] = []
    calendar_events: List[CalendarEvent] = []
    user_preferences: UserPreferences = UserPreferences()
    last_action_summary: str = ""
