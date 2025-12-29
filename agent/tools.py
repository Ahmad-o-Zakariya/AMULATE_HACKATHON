import json
from .prompts import INTENT_EXTRACTION_PROMPT
from datetime import datetime, timedelta
from uuid import uuid4
from .state import Task, CalendarEvent, AgentState
from .llm import get_llm

llm = get_llm(
    temperature=0.2,
    max_tokens=256,
)


def parse_intent(user_input: str) -> dict:
    response = llm.invoke(
        INTENT_EXTRACTION_PROMPT.format(input=user_input)
    )
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"intent": "unknown"}

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
