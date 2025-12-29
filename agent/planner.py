from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import List, Tuple
from .state import AgentState, Task
from .planner_types import TimeBlock, UnscheduledTask, PlanResult

# Helper utilities

def _today_at(hour: int) -> datetime:
    """Return today's datetime at a given hour."""
    return datetime.combine(date.today(), datetime.min.time()).replace(hour=hour)


def _slot_duration_minutes(slot: Tuple[datetime, datetime]) -> int:
    return int((slot[1] - slot[0]).total_seconds() // 60)


def _fits(task: Task, slot: Tuple[datetime, datetime]) -> bool:
    return task.estimated_minutes <= _slot_duration_minutes(slot)


# Core planner

def plan_day(state: AgentState) -> PlanResult:
    """
    Deterministically plan the current day.
    No LLM usage. Fully explainable.
    """

    schedule: List[TimeBlock] = []
    unscheduled: List[UnscheduledTask] = []

    prefs = state.user_preferences

    # 1. Build work window
    work_start = _today_at(prefs.work_start_hour)
    work_end = _today_at(prefs.work_end_hour)

    if work_end <= work_start:
        return PlanResult(
            schedule=[],
            unscheduled=[
                UnscheduledTask(
                    task_id="*",
                    title="*",
                    reason="Invalid work window configuration."
                )
            ],
            summary="Planning failed due to invalid work hours."
        )

    # 2. Block lunch (1 hour)
    lunch_start = _today_at(prefs.lunch_hour)
    lunch_end = lunch_start + timedelta(hours=1)

    # 3. Compute free slots
    free_slots: List[Tuple[datetime, datetime]] = []

    if lunch_start > work_start:
        free_slots.append((work_start, min(lunch_start, work_end)))

    if lunch_end < work_end:
        free_slots.append((max(lunch_end, work_start), work_end))

    # Remove zero-length slots
    free_slots = [s for s in free_slots if s[1] > s[0]]

    # 4. Select pending tasks
    pending_tasks = [
        t for t in state.tasks if t.status == "pending"
    ]

    # Sort: high priority first, then shorter tasks
    pending_tasks.sort(
        key=lambda t: (-t.priority, t.estimated_minutes)
    )

    # 5. Attempt scheduling
    for task in pending_tasks:
        placed = False

        # Try focus-hour slots first
        focus_slots = []
        for start, end in free_slots:
            if start.hour in prefs.focus_hours:
                focus_slots.append((start, end))

        candidate_slots = focus_slots + [
            s for s in free_slots if s not in focus_slots
        ]

        for slot in candidate_slots:
            if _fits(task, slot):
                start_time = slot[0]
                end_time = start_time + timedelta(minutes=task.estimated_minutes)

                schedule.append(
                    TimeBlock(
                        start=start_time,
                        end=end_time,
                        task_id=task.id,
                        title=task.title,
                    )
                )

                # Update task status
                task.status = "scheduled"

                # Shrink or remove the used slot
                free_slots.remove(slot)
                if end_time < slot[1]:
                    free_slots.append((end_time, slot[1]))

                placed = True
                break

        if not placed:
            unscheduled.append(
                UnscheduledTask(
                    task_id=task.id,
                    title=task.title,
                    reason="Insufficient continuous free time."
                )
            )

    # 6. Summary
    summary_lines = []

    if schedule:
        summary_lines.append(
            f"Scheduled {len(schedule)} task(s) within available work hours."
        )

    if unscheduled:
        summary_lines.append(
            f"{len(unscheduled)} task(s) could not be scheduled due to time constraints."
        )

    if not summary_lines:
        summary_lines.append("No tasks were scheduled.")

    summary = " ".join(summary_lines)

    return PlanResult(
        schedule=schedule,
        unscheduled=unscheduled,
        summary=summary,
    )
