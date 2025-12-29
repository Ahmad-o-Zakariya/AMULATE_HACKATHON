import json
from .prompts import INTENT_EXTRACTION_PROMPT
from datetime import datetime, timedelta
from uuid import uuid4
from .state import Task, CalendarEvent, AgentState
from .llm import get_llm
import re

llm = get_llm(
    temperature=0.2,
    max_tokens=256,
)


def parse_intent(user_input: str) -> dict:
    response = llm.invoke(
        INTENT_EXTRACTION_PROMPT.format(input=user_input)
    )

    try:
        parsed = json.loads(response.content)
    except json.JSONDecodeError:
        parsed = {"intent": "unknown"}

    intent = parsed.get("intent", "unknown")
    normalized = user_input.lower()

    # ---- intent fallback ----
    if intent == "unknown":
        if any(p in normalized for p in [
            "plan my day",
            "schedule my day",
            "organize my day",
            "plan today",
            "organize today",
        ]):
            intent = "plan_day"

    #initialize FIRST
    preference_detected = False

    # ---- preference extraction ----
    if intent in ("unknown", "update_preferences"):
        # work hours: "from 10 to 6"
        match = re.search(r"from\s+(\d{1,2})\s+to\s+(\d{1,2})", normalized)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))

            # Normalize common AM–PM work range.
            if end <= start:
                end += 12

            parsed["work_start_hour"] = start
            parsed["work_end_hour"] = end
            preference_detected = True


        # lunch: "lunch is at 2"
        match = re.search(r"lunch\s+(is\s+)?at\s+(\d{1,2})", normalized)
        if match:
            parsed["lunch_hour"] = int(match.group(2))
            preference_detected = True

    #force intent if preferences were found
    if preference_detected:
        parsed["intent"] = "update_preferences"
    else:
        parsed["intent"] = intent

    if parsed["intent"] in ("unknown", "schedule_task"):
        if any(phrase in normalized for phrase in [
            "add a task",
            "add",
            "schedule a task",
            "schedule",
            "i need to",
        ]):
            parsed["intent"] = "schedule_task"

            # duration: "2 hour"
            match = re.search(r"(\d+)\s*hour", normalized)
            if match:
                parsed["duration_minutes"] = int(match. group(1)) * 60

            # priority
            if "high priority" in normalized:
                parsed["priority"] = 5
            elif "low priority" in normalized:
                parsed["priority"] = 1

            # title fallback
            parsed.setdefault("title", user_input)
            
    return parsed




def add_task(state: AgentState, title, priority, duration) -> AgentState:
    task = Task(
        id=str(uuid4()),
        title=title,
        priority=priority or 3,
        estimated_minutes=duration or 60,
        status="pending"
    )
    state.tasks.append(task)
    return state


def schedule_task_after_lunch(state: AgentState, task: Task) -> AgentState:
    lunch = state.user_preferences.lunch_hour
    start = datetime.now().replace(hour=lunch + 1, minute=0, second=0)
    end = start + timedelta(minutes=task.estimated_minutes)

    event = CalendarEvent(
        title=task.title,
        start=start,
        end=end,
        task_id=task.id
    )

    state.calendar_events.append(event)
    task.status = "scheduled"
    return state

def update_preferences(state: AgentState, intent_data: dict) -> AgentState:
    prefs = state.user_preferences

    if intent_data.get("work_start_hour") is not None:
        prefs.work_start_hour = intent_data["work_start_hour"]

    if intent_data.get("work_end_hour") is not None:
        prefs.work_end_hour = intent_data["work_end_hour"]

    if intent_data.get("lunch_hour") is not None:
        prefs.lunch_hour = intent_data["lunch_hour"]

    if intent_data.get("focus_hours") is not None:
        prefs.focus_hours = intent_data["focus_hours"]

    state.last_action_summary = (
        f"Preferences updated: work {prefs.work_start_hour}–{prefs.work_end_hour}, "
        f"lunch at {prefs.lunch_hour}."
    )

    return state
