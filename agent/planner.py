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

    # Determine earliest allowed start time
        earliest_allowed = None
        if task.time_constraint == "after_lunch":
            earliest_allowed = _today_at(prefs.lunch_hour) + timedelta(hours=1)

    # Filter free slots based on constraint FIRST
        eligible_slots = []
        for start, end in free_slots:
            if earliest_allowed and end <= earliest_allowed:
                continue
            eligible_slots.append((start, end))

    # Try focus-hour slots first
        focus_slots = []
        for start, end in eligible_slots:
            effective_start = max(start, earliest_allowed) if earliest_allowed else start
            if effective_start.hour in prefs.focus_hours:
                focus_slots.append((start, end))

        candidate_slots = focus_slots + [
            s for s in eligible_slots if s not in focus_slots
        ]

        for slot in candidate_slots:
            slot_start, slot_end = slot
            start_time = max(slot_start, earliest_allowed) if earliest_allowed else slot_start

            available_minutes = int((slot_end - start_time).total_seconds() // 60)
            if task.estimated_minutes > available_minutes:
                continue

            end_time = start_time + timedelta(minutes=task.estimated_minutes)

            schedule.append(
            TimeBlock(
                start=start_time,
                end=end_time,
                task_id=task.id,
                title=task.title,
                )
            )

            task.status = "scheduled"

        # Update free slots
            free_slots.remove(slot)
            if slot_start < start_time:
                free_slots.append((slot_start, start_time))
            if end_time < slot_end:
                free_slots.append((end_time, slot_end))

            placed = True
            break

        if not placed:
            unscheduled.append(
                UnscheduledTask(
                    task_id=task.id,
                    title=task.title,
                    reason="Insufficient time or time constraint."
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
